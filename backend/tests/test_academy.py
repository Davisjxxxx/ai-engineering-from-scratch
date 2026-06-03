"""Agentic Design Patterns Academy — backend API tests.

Covers:
- /api/paths lists campaign + agentic-patterns
- /api/academy/agentic-patterns home (21 nodes / 4 groups)
- chapter level detail (adp-01 6 missions; adp-02 4 missions; adp-05/14/18/19 6 missions)
- mission complete -> XP, chapter completion bonus, review-card seeding
- Dojo & Clinic bank + result XP
- Capstone list + validate (pass & fail)
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"

DID = f"TEST_{uuid.uuid4().hex[:12]}"
HEADERS = {"X-Device-Id": DID, "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update(HEADERS)
    return sess


# --------------------------------------------------------------- paths
def test_paths_lists_both(s):
    r = s.get(f"{API}/paths")
    assert r.status_code == 200, r.text
    data = r.json()
    # accept list or dict with paths
    paths = data if isinstance(data, list) else data.get("paths", [])
    ids = {p.get("id") for p in paths}
    assert "campaign" in ids
    assert "agentic-patterns" in ids
    # find agentic-patterns and check counts
    adp = next(p for p in paths if p["id"] == "agentic-patterns")
    # some shapes include a node_count or chapter_count
    txt = str(adp).lower()
    assert "agentic" in txt or "pattern" in txt


# --------------------------------------------------------------- academy home
def test_academy_home(s):
    r = s.get(f"{API}/academy/agentic-patterns")
    assert r.status_code == 200, r.text
    d = r.json()
    assert "groups" in d
    groups = d["groups"]
    assert len(groups) == 4
    expected_groups = {"foundations", "orchestration", "reliability", "advanced"}
    got_groups = {g.get("id") or g.get("key") or g.get("slug") for g in groups}
    assert expected_groups <= got_groups, f"Got groups {got_groups}"

    # count nodes
    total_nodes = 0
    for g in groups:
        nodes = g.get("nodes") or g.get("chapters") or []
        total_nodes += len(nodes)
        for n in nodes:
            assert n["unlocked"] is True  # UNLOCK_ALL
            assert "progress" in n
            assert "mastery_score" in n or "mastery" in n
    assert total_nodes == 21, f"Expected 21 nodes, got {total_nodes}"

    assert "overall_mastery" in d
    assert "next_action" in d


# --------------------------------------------------------------- chapter detail
def test_chapter_adp01_missions(s):
    r = s.get(f"{API}/levels/adp-01")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["unlocked"] is True
    miss_ids = [m["id"].split("::")[-1] for m in d["missions"]]
    assert set(miss_ids) == {"briefing", "mentalmodel", "drill", "lab", "debug", "boss"}, miss_ids


def test_chapter_adp02_short_missions(s):
    r = s.get(f"{API}/levels/adp-02")
    assert r.status_code == 200, r.text
    miss_ids = [m["id"].split("::")[-1] for m in r.json()["missions"]]
    assert "briefing" in miss_ids
    assert "mentalmodel" in miss_ids
    assert "drill" in miss_ids
    assert "boss" in miss_ids
    # No lab/debug for non-flagship chapters
    assert "lab" not in miss_ids
    assert "debug" not in miss_ids


@pytest.mark.parametrize("cid", ["adp-05", "adp-14", "adp-18", "adp-19"])
def test_chapters_with_lab_debug(s, cid):
    r = s.get(f"{API}/levels/{cid}")
    assert r.status_code == 200, r.text
    miss_ids = [m["id"].split("::")[-1] for m in r.json()["missions"]]
    assert "lab" in miss_ids, f"{cid} missing lab"
    assert "debug" in miss_ids, f"{cid} missing debug"


# --------------------------------------------------------------- mission completion + bonus + review seeds
def test_complete_adp01_full_flow(s):
    detail = s.get(f"{API}/levels/adp-01").json()
    mids = [m["id"] for m in detail["missions"]]
    before_xp = s.get(f"{API}/profile").json()["total_xp"]

    last = None
    for mid in mids:
        rr = s.post(f"{API}/missions/{mid}/complete",
                    json={"score": 100, "completed_steps": 1, "total_steps": 1})
        assert rr.status_code == 200, f"{mid}: {rr.text}"
        last = rr.json()
        assert last["ok"] is True

    assert last["level_just_completed"] is True
    assert last["level_complete_bonus"] > 0
    after_xp = last["profile"]["total_xp"]
    assert after_xp > before_xp

    # Verify lab mission credit specifically (55 XP target)
    # We can't know exactly which mission yielded what without diff, but ensure persistence
    detail2 = s.get(f"{API}/levels/adp-01").json()
    assert detail2["completed"] is True
    for m in detail2["missions"]:
        assert m["status"] == "completed"

    # Review cards seeded for adp-01
    due = s.get(f"{API}/review/due").json()
    assert due["due_count"] >= 1


# --------------------------------------------------------------- dojo
def test_dojo_bank(s):
    r = s.get(f"{API}/academy/agentic-patterns/dojo")
    assert r.status_code == 200, r.text
    d = r.json()
    rounds = d.get("rounds") or d.get("questions") or d.get("items") or []
    assert 1 <= len(rounds) <= 10
    for q in rounds:
        assert "options" in q or "choices" in q


def test_dojo_result_correct(s):
    r = s.post(f"{API}/academy/agentic-patterns/dojo/result", json={"correct": True})
    assert r.status_code == 200, r.text
    d = r.json()
    # accept any positive XP indicator
    assert d.get("ok") is True or d.get("xp", 0) > 0 or "profile" in d


# --------------------------------------------------------------- clinic
def test_clinic_bank(s):
    r = s.get(f"{API}/academy/agentic-patterns/clinic")
    assert r.status_code == 200, r.text
    d = r.json()
    cases = d.get("cases") or d.get("items") or []
    assert len(cases) >= 1


def test_clinic_result(s):
    r = s.post(f"{API}/academy/agentic-patterns/clinic/result", json={"correct": True})
    assert r.status_code == 200, r.text


# --------------------------------------------------------------- capstones
def test_capstones_list(s):
    r = s.get(f"{API}/academy/capstones/list")
    assert r.status_code == 200, r.text
    d = r.json()
    blocks = d.get("blocks") or []
    capstones = d.get("capstones") or []
    assert len(blocks) == 14, f"expected 14 blocks got {len(blocks)}"
    assert len(capstones) == 5, f"expected 5 capstones got {len(capstones)}"


def test_capstone_validate_pass(s):
    r = s.post(f"{API}/academy/capstones/support-workflow/validate",
               json={"selected": ["router", "rag", "guardrail", "human-gate", "evaluator"]})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["passed"] is True
    assert d.get("score") == 100
    assert d.get("xp") == 120


def test_capstone_validate_fail(s):
    r = s.post(f"{API}/academy/capstones/support-workflow/validate",
               json={"selected": ["router", "rag"]})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["passed"] is False
    assert "missing" in d or "feedback" in d
