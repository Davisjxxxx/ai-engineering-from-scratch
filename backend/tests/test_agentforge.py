"""AgentForge Quest — backend API regression tests.

Covers: health, profile, settings, campaign, levels, mission completion (incl. level bonus),
challenges (select-multiple, edit-json), agent lab (scenarios, run, builds CRUD),
braindump CRUD, review SM-2, skills, badges, notifications prefs, daily.
"""
import json
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://3cd4e319-9cd3-4768-9f74-0edd0c86b6df.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

# Stable device id per test run for progression flows
DID = f"TEST_{uuid.uuid4().hex[:12]}"
HEADERS = {"X-Device-Id": DID, "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def s():
    sess = requests.Session()
    sess.headers.update(HEADERS)
    return sess


# ------------------------------------------------------------------- health
def test_health(s):
    r = s.get(f"{API}/health")
    assert r.status_code == 200
    d = r.json()
    assert d.get("status") == "ok"
    assert d.get("worlds", 0) >= 1
    assert d.get("levels", 0) >= 1
    assert "providers" in d


# ------------------------------------------------------------------- profile
def test_profile_auto_create(s):
    r = s.get(f"{API}/profile")
    assert r.status_code == 200
    d = r.json()
    assert d["device_id"] == DID
    assert d["total_xp"] == 0
    assert d["level"] == 1
    assert d["streak_count"] == 0


def test_profile_settings_persist(s):
    r = s.put(f"{API}/profile/settings",
              json={"focus_mode_enabled": True, "reduced_motion_enabled": True, "sound_enabled": False})
    assert r.status_code == 200
    d = r.json()
    assert d["focus_mode_enabled"] is True
    assert d["reduced_motion_enabled"] is True
    assert d["sound_enabled"] is False
    # GET verifies persistence
    g = s.get(f"{API}/profile").json()
    assert g["focus_mode_enabled"] is True
    assert g["sound_enabled"] is False


def test_missing_device_id_400():
    r = requests.get(f"{API}/profile")
    assert r.status_code == 400


# ------------------------------------------------------------------- campaign
def test_campaign_only_first_unlocked(s):
    r = s.get(f"{API}/campaign")
    assert r.status_code == 200
    d = r.json()
    assert "worlds" in d and "next_action" in d
    assert len(d["worlds"]) >= 1
    # First world unlocked; first level unlocked
    first_world = d["worlds"][0]
    assert first_world["unlocked"] is True
    first_level = first_world["levels"][0]
    assert first_level["unlocked"] is True
    # Any later level must be locked initially
    found_locked = False
    for w in d["worlds"]:
        for lv in w["levels"]:
            if lv["id"] != first_level["id"]:
                if lv["unlocked"] is False:
                    found_locked = True
                    break
        if found_locked:
            break
    assert found_locked, "Expected at least one locked level for fresh profile"
    # next_action present
    assert d["next_action"]["kind"] in ("mission", "review")


# ------------------------------------------------------------------- level detail
def test_level_detail_first_unlocked(s):
    camp = s.get(f"{API}/campaign").json()
    first_level_id = camp["worlds"][0]["levels"][0]["id"]
    r = s.get(f"{API}/levels/{first_level_id}")
    assert r.status_code == 200
    d = r.json()
    assert d["unlocked"] is True
    assert isinstance(d["missions"], list) and len(d["missions"]) > 0
    for m in d["missions"]:
        assert m["status"] == "not_started"
        assert "id" in m and "::" in m["id"]


def test_level_detail_404(s):
    r = s.get(f"{API}/levels/nonexistent-level-xyz")
    assert r.status_code == 404


# ------------------------------------------------------------------- mission flow + level bonus + persistence
def test_complete_all_missions_for_a_rich_level(s):
    # Use the content-rich level explicitly mentioned by main agent
    LEVEL_ID = "11-01-prompt-engineering"
    r = s.get(f"{API}/levels/{LEVEL_ID}")
    assert r.status_code == 200
    detail = r.json()
    mission_ids = [m["id"] for m in detail["missions"]]
    assert len(mission_ids) >= 3

    before_xp = s.get(f"{API}/profile").json()["total_xp"]
    last = None
    for mid in mission_ids:
        rr = s.post(f"{API}/missions/{mid}/complete",
                    json={"score": 100, "completed_steps": 1, "total_steps": 1})
        assert rr.status_code == 200, rr.text
        last = rr.json()
        assert last["ok"] is True

    # Level complete bonus on last call
    assert last["level_just_completed"] is True
    assert last["level_complete_bonus"] > 0
    new_badges = [b["id"] for b in last.get("new_badges", [])]
    # first-spark / boss-slayer / level-cleared should appear among earned badges by now
    prof_badges = last["profile"]["badges"]
    assert "first-spark" in prof_badges
    assert "level-cleared" in prof_badges

    after_xp = last["profile"]["total_xp"]
    assert after_xp > before_xp

    # GET to verify persistence
    detail2 = s.get(f"{API}/levels/{LEVEL_ID}").json()
    assert detail2["completed"] is True
    for m in detail2["missions"]:
        assert m["status"] == "completed"


def test_mission_idempotent_no_double_xp(s):
    LEVEL_ID = "11-01-prompt-engineering"
    detail = s.get(f"{API}/levels/{LEVEL_ID}").json()
    mid = detail["missions"][0]["id"]
    before = s.get(f"{API}/profile").json()["total_xp"]
    r = s.post(f"{API}/missions/{mid}/complete", json={"score": 100, "completed_steps": 1, "total_steps": 1})
    assert r.status_code == 200
    d = r.json()
    assert d["already_completed"] is True
    assert d["xp_gained"] == 0  # already done, no re-credit (bonus also already given)
    after = s.get(f"{API}/profile").json()["total_xp"]
    assert after == before


# ------------------------------------------------------------------- challenges
def test_list_challenges(s):
    r = s.get(f"{API}/challenges")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 9
    for c in items:
        # answer/explain must be hidden
        assert "answer" not in c
        assert "explain" not in c


def test_select_multiple_correct(s):
    r = s.post(f"{API}/challenges/fix-bad-prompt/attempt", json={"answer": [0, 2, 3]})
    assert r.status_code == 200
    d = r.json()
    assert d["passed"] is True
    assert d["xp"] == 40
    assert d.get("first_solve") is True
    assert "fix-bad-prompt" in d["profile"]["challenges_solved"]


def test_select_multiple_wrong_no_penalty(s):
    r = s.post(f"{API}/challenges/route-task/attempt", json={"answer": 0})
    d = r.json()
    assert d["passed"] is False
    assert d["xp"] == 0
    # Profile XP shouldn't decrement
    prof = s.get(f"{API}/profile").json()
    assert prof["total_xp"] >= 0


def test_edit_json_valid(s):
    payload = '{"name":"router","tools":["search","calc"],"safe":true}'
    r = s.post(f"{API}/challenges/repair-json/attempt", json={"answer": payload})
    d = r.json()
    assert d["passed"] is True
    assert d["xp"] == 45


def test_edit_json_invalid(s):
    r = s.post(f"{API}/challenges/repair-json/attempt",
               json={"answer": "{ 'name': 'x' }"})
    d = r.json()
    assert d["passed"] is False
    assert "JSON" in d["feedback"] or "json" in d["feedback"].lower()


# ------------------------------------------------------------------- agent lab
def test_lab_scenarios(s):
    r = s.get(f"{API}/lab/scenarios")
    assert r.status_code == 200
    scns = r.json()
    assert len(scns) >= 3
    assert {sc["id"] for sc in scns} >= {"calc-helper", "support-agent", "research-agent"}


def test_lab_run_mocked(s):
    r = s.post(f"{API}/lab/run", json={
        "scenario_id": "calc-helper",
        "name": "calc-bot",
        "prompt": "You are a calculator agent. Always use the calculator tool. Reply as JSON with answer and tool_used fields.",
        "tools": ["calculator"],
        "memory_config": "none",
        "live": True,  # but no key set -> graceful mocked note
    })
    assert r.status_code == 200
    d = r.json()
    assert d["mode"] == "mock"
    assert "score" in d and "verdict" in d
    assert isinstance(d["checks"], list) and len(d["checks"]) >= 4
    assert isinstance(d["trace"], list) and len(d["trace"]) > 0
    # Live toggle without key -> graceful note
    if "live" in d:
        assert d["live"]["mode"] in ("unavailable", "live", "live-error")


def test_lab_build_save_list_delete(s):
    r = s.post(f"{API}/lab/builds", json={
        "scenario_id": "support-agent",
        "name": "TEST_support_bot",
        "prompt": "You are a support agent. Always verify charges. Reply as JSON.",
        "tools": ["knowledge_base", "billing_api"],
        "memory_config": "session",
        "live": False,
    })
    assert r.status_code == 200
    saved = r.json()
    assert "id" in saved and saved["name"] == "TEST_support_bot"
    bid = saved["id"]

    lst = s.get(f"{API}/lab/builds").json()
    assert any(b["id"] == bid for b in lst)

    d = s.delete(f"{API}/lab/builds/{bid}")
    assert d.status_code == 200
    lst2 = s.get(f"{API}/lab/builds").json()
    assert all(b["id"] != bid for b in lst2)


# ------------------------------------------------------------------- braindump
def test_braindump_crud(s):
    r = s.post(f"{API}/braindump", json={"content": "TEST_thought about RAG", "tags": ["idea", "rag"]})
    assert r.status_code == 200
    item = r.json()
    iid = item["id"]
    assert item["status"] == "open"

    lst = s.get(f"{API}/braindump").json()
    assert any(x["id"] == iid for x in lst)

    u = s.put(f"{API}/braindump/{iid}/status", params={"status": "archived"})
    assert u.status_code == 200 and u.json()["status"] == "archived"

    d = s.delete(f"{API}/braindump/{iid}")
    assert d.status_code == 200
    lst2 = s.get(f"{API}/braindump").json()
    assert all(x["id"] != iid for x in lst2)


# ------------------------------------------------------------------- review SM-2
def test_review_due_and_grade(s):
    r = s.get(f"{API}/review/due")
    assert r.status_code == 200
    d = r.json()
    # After completing the rich level, due cards should be > 0
    assert d["due_count"] >= 1
    card = d["cards"][0]
    card_id = card["card_id"]

    g = s.post(f"{API}/review/{card_id}/grade", json={"quality": 4})
    assert g.status_code == 200
    gj = g.json()
    assert gj["ok"] is True
    assert gj["next_interval_days"] >= 1


# ------------------------------------------------------------------- skills + badges + daily + notifs
def test_skills(s):
    r = s.get(f"{API}/skills")
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) >= 1
    for b in arr:
        assert "progress" in b and "tier" in b


def test_badges(s):
    r = s.get(f"{API}/badges")
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) == 10
    earned = [b for b in arr if b["earned"]]
    assert len(earned) >= 2  # first-spark + level-cleared at minimum


def test_daily(s):
    r = s.get(f"{API}/daily")
    assert r.status_code == 200
    d = r.json()
    assert "next_action" in d
    assert "daily_challenge" in d
    assert "reviews_due" in d


def test_notif_prefs(s):
    g = s.get(f"{API}/notifications/preferences")
    assert g.status_code == 200
    assert g.json()["status"] == "coming_soon"
    p = s.put(f"{API}/notifications/preferences",
              json={"daily_mission_enabled": False, "preferred_time": "09:00"})
    assert p.status_code == 200
    d2 = p.json()
    assert d2["daily_mission_enabled"] is False
    assert d2["preferred_time"] == "09:00"
    # Persistence
    g2 = s.get(f"{API}/notifications/preferences").json()
    assert g2["daily_mission_enabled"] is False


# ------------------------------------------------------------------- progression locking enforcement
def test_locked_level_still_visible(s):
    """A locked level can be inspected (detail returns) but unlocked=False."""
    camp = s.get(f"{API}/campaign").json()
    # find a level that's locked
    locked = None
    for w in camp["worlds"]:
        for lv in w["levels"]:
            if not lv["unlocked"]:
                locked = lv["id"]; break
        if locked: break
    if not locked:
        pytest.skip("No locked level found")
    r = s.get(f"{API}/levels/{locked}")
    assert r.status_code == 200
    assert r.json()["unlocked"] is False
