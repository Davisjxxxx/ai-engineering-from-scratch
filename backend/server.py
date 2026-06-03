"""AgentForge Quest — FastAPI backend.
Anonymous device-based profiles. Content is generated/static; only player
progress lives in MongoDB. Works fully without any API key."""
from __future__ import annotations

import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from challenges import (BADGES, BADGE_MAP, CHALLENGES, LAB_SCENARIOS,
                        public_challenge, simulate_agent, live_agent,
                        validate_challenge)
from content import LEVEL_COMPLETE_BONUS, SKILL_BRANCHES, engine
from models import (AgentBuildPayload, BrainDumpCreate, ChallengeAttempt,
                    MissionCompletePayload, NotificationPrefsPayload,
                    ProfileSettings, ReviewGrade, now_utc, today_str)

load_dotenv(Path(__file__).resolve().parent / ".env")

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="AgentForge Quest API")
api = app  # routes use /api prefix explicitly

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------- helpers
def device_id(x_device_id: Optional[str], request: Request) -> str:
    did = x_device_id or request.query_params.get("device_id")
    if not did:
        raise HTTPException(status_code=400, detail="Missing X-Device-Id")
    return did


def level_from_xp(total_xp: int):
    """Returns (level, xp_into_level, xp_for_this_level)."""
    need = 300
    lvl = 1
    remaining = total_xp
    while remaining >= need:
        remaining -= need
        lvl += 1
        need = int(need * 1.25)
    return lvl, remaining, need


async def get_profile(did: str) -> dict:
    doc = await db.profiles.find_one({"device_id": did})
    if not doc:
        doc = {
            "device_id": did,
            "total_xp": 0,
            "streak_count": 0,
            "longest_streak": 0,
            "last_active_date": None,
            "focus_mode_enabled": False,
            "reduced_motion_enabled": False,
            "sound_enabled": True,
            "badges": [],
            "challenges_solved": [],
            "reviews_done": 0,
            "created_at": now_utc().isoformat(),
        }
        await db.profiles.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


async def completed_mission_ids(did: str) -> set:
    cur = db.mission_progress.find({"device_id": did, "status": "completed"}, {"mission_id": 1})
    return {d["mission_id"] async for d in cur}


async def completed_level_ids(did: str, done: Optional[set] = None) -> set:
    if done is None:
        done = await completed_mission_ids(did)
    out = set()
    fork_level_ids = [lv["id"] for fk in engine.forks for lv in fk["levels"]]
    for lid in list(engine.level_order) + fork_level_ids:
        mids = engine.mission_ids_for_level(lid)
        if mids and all(m in done for m in mids):
            out.add(lid)
    return out


UNLOCK_ALL = os.environ.get("UNLOCK_ALL", "false").strip().lower() in ("1", "true", "yes")


def is_unlocked(level_id: str, completed_levels: set) -> bool:
    # TEST MODE: when UNLOCK_ALL is set, everything is open for full-access QA.
    # On deploy, set UNLOCK_ALL=false to restore per-world progressive unlock.
    if UNLOCK_ALL:
        return True
    # Every world's first level is open; later levels unlock when the previous
    # level in the SAME world is completed. Worlds are freely explorable.
    if level_id in engine.first_in_world:
        return True
    if level_id in engine.fork_first:
        return True
    prev = engine.prev_in_world.get(level_id) or engine.fork_prev.get(level_id)
    return prev is None or prev in completed_levels


async def bump_streak(did: str, profile: dict) -> dict:
    today = today_str()
    last = profile.get("last_active_date")
    streak = profile.get("streak_count", 0)
    if last == today:
        pass
    elif last == (now_utc().date() - timedelta(days=1)).strftime("%Y-%m-%d"):
        streak += 1
    else:
        streak = 1
    longest = max(profile.get("longest_streak", 0), streak)
    await db.profiles.update_one(
        {"device_id": did},
        {"$set": {"streak_count": streak, "longest_streak": longest, "last_active_date": today}},
    )
    profile["streak_count"] = streak
    profile["longest_streak"] = longest
    profile["last_active_date"] = today
    return profile


async def award_xp(did: str, amount: int) -> int:
    res = await db.profiles.find_one_and_update(
        {"device_id": did}, {"$inc": {"total_xp": amount}}, return_document=True
    )
    return res.get("total_xp", amount) if res else amount


async def recompute_badges(did: str) -> List[str]:
    profile = await get_profile(did)
    done = await completed_mission_ids(did)
    levels = await completed_level_ids(did, done)
    earned = set(profile.get("badges", []))

    def add(b):
        if b in BADGE_MAP:
            earned.add(b)

    if len(done) >= 1: add("first-spark")
    if any(m.endswith("::boss") for m in done): add("boss-slayer")
    if levels: add("level-cleared")
    if profile.get("streak_count", 0) >= 3: add("streak-3")
    if profile.get("streak_count", 0) >= 7: add("streak-7")
    if len(profile.get("challenges_solved", [])) >= 3: add("arena-fighter")
    if await db.agent_builds.count_documents({"device_id": did}) >= 1: add("agent-architect")
    if profile.get("reviews_done", 0) >= 10: add("memory-keeper")
    if profile.get("total_xp", 0) >= 1000: add("xp-1000")
    # world conqueror
    for w in engine.worlds:
        if w["levels"] and all(lv["id"] in levels for lv in w["levels"]):
            add("world-conqueror"); break

    new = earned - set(profile.get("badges", []))
    if new:
        await db.profiles.update_one({"device_id": did}, {"$set": {"badges": list(earned)}})
    return list(new)


def profile_public(profile: dict) -> dict:
    lvl, into, need = level_from_xp(profile.get("total_xp", 0))
    return {
        "device_id": profile["device_id"],
        "total_xp": profile.get("total_xp", 0),
        "level": lvl,
        "xp_into_level": into,
        "xp_for_level": need,
        "streak_count": profile.get("streak_count", 0),
        "longest_streak": profile.get("longest_streak", 0),
        "last_active_date": profile.get("last_active_date"),
        "focus_mode_enabled": profile.get("focus_mode_enabled", False),
        "reduced_motion_enabled": profile.get("reduced_motion_enabled", False),
        "sound_enabled": profile.get("sound_enabled", True),
        "badges": profile.get("badges", []),
        "challenges_solved": profile.get("challenges_solved", []),
        "reviews_done": profile.get("reviews_done", 0),
    }


# ----------------------------------------------------------------- routes
@api.get("/api/health")
async def health():
    providers = {"deepseek": bool(os.environ.get("DEEPSEEK_API_KEY", "").strip())}
    return {"status": "ok", "worlds": engine.data["world_count"],
            "levels": engine.data["level_count"], "providers": providers}


@api.get("/api/profile")
async def read_profile(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    profile = await get_profile(did)
    return profile_public(profile)


@api.put("/api/profile/settings")
async def update_settings(payload: ProfileSettings, request: Request,
                          x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    await get_profile(did)
    await db.profiles.update_one({"device_id": did}, {"$set": payload.model_dump()})
    return profile_public(await get_profile(did))


@api.get("/api/campaign")
async def campaign(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    profile = await get_profile(did)
    done = await completed_mission_ids(did)
    levels_done = await completed_level_ids(did, done)
    worlds = engine.campaign()
    for w in worlds:
        for lv in w["levels"]:
            mids = engine.mission_ids_for_level(lv["id"])
            comp = sum(1 for m in mids if m in done)
            lv["missions_completed"] = comp
            lv["completed"] = lv["id"] in levels_done
            lv["unlocked"] = is_unlocked(lv["id"], levels_done)
            lv["progress"] = round(100 * comp / len(mids)) if mids else 0
        w["completed_levels"] = sum(1 for lv in w["levels"] if lv["completed"])
        w["unlocked"] = any(lv["unlocked"] for lv in w["levels"])
    return {"profile": profile_public(profile), "worlds": worlds,
            "next_action": await next_best_action(did, done, levels_done)}


@api.get("/api/levels/{level_id}")
async def level_detail(level_id: str, request: Request,
                       x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    detail = engine.level_detail(level_id)
    if not detail:
        raise HTTPException(404, "Level not found")
    done = await completed_mission_ids(did)
    levels_done = await completed_level_ids(did, done)
    detail["unlocked"] = is_unlocked(level_id, levels_done)
    prog = {d["mission_id"]: d async for d in db.mission_progress.find({"device_id": did, "mission_id": {"$in": [m["id"] for m in detail["missions"]]}})}
    for m in detail["missions"]:
        p = prog.get(m["id"])
        m["status"] = p["status"] if p else "not_started"
        m["attempts"] = p.get("attempts", 0) if p else 0
        m["best_score"] = p.get("score", 0) if p else 0
    detail["completed"] = level_id in levels_done
    return detail


@api.post("/api/missions/{mission_id}/complete")
async def complete_mission(mission_id: str, payload: MissionCompletePayload,
                           request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    level_id = mission_id.split("::")[0]
    detail = engine.level_detail(level_id)
    if not detail:
        raise HTTPException(404, "Unknown mission")
    mission = next((m for m in detail["missions"] if m["id"] == mission_id), None)
    if not mission:
        raise HTTPException(404, "Unknown mission")

    existing = await db.mission_progress.find_one({"device_id": did, "mission_id": mission_id})
    already = existing and existing.get("status") == "completed"
    attempts = (existing.get("attempts", 0) if existing else 0) + 1
    best = max(existing.get("score", 0) if existing else 0, payload.score)

    await db.mission_progress.update_one(
        {"device_id": did, "mission_id": mission_id},
        {"$set": {"status": "completed", "level_id": level_id, "score": best,
                  "completed_at": now_utc().isoformat(),
                  "completed_steps": payload.completed_steps,
                  "total_steps": payload.total_steps},
         "$setOnInsert": {"device_id": did, "mission_id": mission_id},
         "$inc": {"attempts": 1}},
        upsert=True,
    )

    xp_gained = 0
    profile = await get_profile(did)
    profile = await bump_streak(did, profile)
    if not already:
        xp_gained = mission["xp_reward"]
        # retry-after-failure / comeback nudge bonus
        await award_xp(did, xp_gained)

    # level completion bonus
    done = await completed_mission_ids(did)
    level_just_completed = False
    bonus = 0
    mids = engine.mission_ids_for_level(level_id)
    if mids and all(m in done for m in mids):
        lc = await db.level_complete.find_one({"device_id": did, "level_id": level_id})
        if not lc:
            await db.level_complete.insert_one({"device_id": did, "level_id": level_id,
                                                "completed_at": now_utc().isoformat()})
            bonus = LEVEL_COMPLETE_BONUS
            await award_xp(did, bonus)
            level_just_completed = True
            # seed review cards for this level
            await seed_reviews(did, level_id)

    new_badges = await recompute_badges(did)
    profile = await get_profile(did)
    return {
        "ok": True,
        "xp_gained": xp_gained + bonus,
        "level_complete_bonus": bonus,
        "level_just_completed": level_just_completed,
        "already_completed": already,
        "attempts": attempts,
        "new_badges": [BADGE_MAP[b] for b in new_badges],
        "profile": profile_public(profile),
    }


async def next_best_action(did: str, done: set, levels_done: set) -> dict:
    """Always surface ONE clear next action."""
    for lid in engine.level_order:
        if not is_unlocked(lid, levels_done):
            continue
        mids = engine.mission_ids_for_level(lid)
        for mid in mids:
            if mid not in done:
                detail = engine.level_detail(lid)
                m = next(mm for mm in detail["missions"] if mm["id"] == mid)
                return {"kind": "mission", "level_id": lid, "level_title": detail["title"],
                        "mission_id": mid, "mission_title": m["title"], "mission_type": m["type"],
                        "estimated_minutes": m["estimated_minutes"],
                        "label": f"Continue: {m['title']}"}
    # everything done -> review
    return {"kind": "review", "label": "Sharpen your skills in the Review Deck"}


# ----------------------------------------------------------------- forks
@api.get("/api/forks")
async def list_forks():
    return [engine.fork_summary(fk["id"]) for fk in engine.forks]


@api.get("/api/forks/{fork_id}")
async def fork_detail(fork_id: str, request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    detail = engine.fork_detail(fork_id)
    if not detail:
        raise HTTPException(404, "Fork not found")
    done = await completed_mission_ids(did)
    levels_done = await completed_level_ids(did, done)
    for lv in detail["levels"]:
        mids = engine.mission_ids_for_level(lv["id"])
        comp = sum(1 for m in mids if m in done)
        lv["missions_completed"] = comp
        lv["completed"] = lv["id"] in levels_done
        lv["unlocked"] = is_unlocked(lv["id"], levels_done)
        lv["progress"] = round(100 * comp / len(mids)) if mids else 0
    detail["completed_levels"] = sum(1 for lv in detail["levels"] if lv["completed"])
    return detail


# ----------------------------------------------------------------- daily
@api.get("/api/daily")
async def daily(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    done = await completed_mission_ids(did)
    levels_done = await completed_level_ids(did, done)
    nba = await next_best_action(did, done, levels_done)
    idx = now_utc().date().toordinal() % len(CHALLENGES)
    challenge = public_challenge(CHALLENGES[idx])
    due = await due_review_count(did)
    return {"next_action": nba, "daily_challenge": challenge, "reviews_due": due,
            "date": today_str()}


# ----------------------------------------------------------------- challenges
@api.get("/api/challenges")
async def list_challenges(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    profile = await get_profile(did)
    solved = set(profile.get("challenges_solved", []))
    return [{**public_challenge(c), "solved": c["id"] in solved} for c in CHALLENGES]


@api.post("/api/challenges/{challenge_id}/attempt")
async def attempt_challenge(challenge_id: str, body: ChallengeAttempt, request: Request,
                            x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    result = validate_challenge(challenge_id, body.answer)
    if result.get("passed"):
        profile = await get_profile(did)
        solved = set(profile.get("challenges_solved", []))
        first = challenge_id not in solved
        solved.add(challenge_id)
        await db.profiles.update_one({"device_id": did}, {"$set": {"challenges_solved": list(solved)}})
        await bump_streak(did, profile)
        if first:
            await award_xp(did, result.get("xp", 0))
        new_badges = await recompute_badges(did)
        result["new_badges"] = [BADGE_MAP[b] for b in new_badges]
        result["profile"] = profile_public(await get_profile(did))
        result["first_solve"] = first
    return result


# ----------------------------------------------------------------- agent lab
@api.get("/api/lab/scenarios")
async def lab_scenarios():
    return LAB_SCENARIOS


@api.post("/api/lab/run")
async def lab_run(payload: AgentBuildPayload, request: Request,
                  x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    build = payload.model_dump()
    result = simulate_agent(build, payload.scenario_id)
    if payload.live:
        live = await live_agent(build, payload.scenario_id)
        if live:
            result["live"] = live
        else:
            result["live"] = {"mode": "unavailable",
                              "note": "Live mode needs DEEPSEEK_API_KEY. Showing mocked run."}
    profile = await get_profile(did)
    await bump_streak(did, profile)
    return result


@api.get("/api/lab/builds")
async def list_builds(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    cur = db.agent_builds.find({"device_id": did}).sort("created_at", -1)
    out = []
    async for d in cur:
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out


@api.post("/api/lab/builds")
async def save_build(payload: AgentBuildPayload, request: Request,
                     x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    build = payload.model_dump()
    result = simulate_agent(build, payload.scenario_id)
    doc = {"device_id": did, **build, "test_results": result,
           "created_at": now_utc().isoformat()}
    res = await db.agent_builds.insert_one(doc)
    await recompute_badges(did)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return doc


@api.delete("/api/lab/builds/{build_id}")
async def delete_build(build_id: str, request: Request,
                       x_device_id: Optional[str] = Header(None)):
    from bson import ObjectId
    did = device_id(x_device_id, request)
    await db.agent_builds.delete_one({"_id": ObjectId(build_id), "device_id": did})
    return {"ok": True}


# ----------------------------------------------------------------- brain dump
@api.get("/api/braindump")
async def list_braindump(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    cur = db.braindump.find({"device_id": did}).sort("created_at", -1)
    out = []
    async for d in cur:
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out


@api.post("/api/braindump")
async def add_braindump(payload: BrainDumpCreate, request: Request,
                        x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    doc = {"device_id": did, "content": payload.content, "tags": payload.tags,
           "status": "open", "created_at": now_utc().isoformat()}
    res = await db.braindump.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return doc


@api.put("/api/braindump/{item_id}/status")
async def update_braindump(item_id: str, request: Request, status: str = "archived",
                           x_device_id: Optional[str] = Header(None)):
    from bson import ObjectId
    did = device_id(x_device_id, request)
    await db.braindump.update_one({"_id": ObjectId(item_id), "device_id": did},
                                  {"$set": {"status": status}})
    return {"ok": True, "status": status}


@api.delete("/api/braindump/{item_id}")
async def delete_braindump(item_id: str, request: Request,
                           x_device_id: Optional[str] = Header(None)):
    from bson import ObjectId
    did = device_id(x_device_id, request)
    await db.braindump.delete_one({"_id": ObjectId(item_id), "device_id": did})
    return {"ok": True}


# ----------------------------------------------------------------- review (SM-2)
async def seed_reviews(did: str, level_id: str):
    seeds = engine.review_seeds_for_level(level_id)
    for s in seeds:
        exists = await db.review_state.find_one({"device_id": did, "card_id": s["card_id"]})
        if exists:
            continue
        await db.review_state.insert_one({
            "device_id": did, "card_id": s["card_id"], "level_id": level_id,
            "ease": 2.5, "interval": 0, "reps": 0,
            "due_at": now_utc().isoformat(),
        })


async def due_review_count(did: str) -> int:
    now = now_utc().isoformat()
    return await db.review_state.count_documents({"device_id": did, "due_at": {"$lte": now}})


@api.get("/api/review/due")
async def review_due(request: Request, x_device_id: Optional[str] = Header(None), limit: int = 12):
    did = device_id(x_device_id, request)
    now = now_utc().isoformat()
    seed_map = engine.review_seed_map()
    cur = db.review_state.find({"device_id": did, "due_at": {"$lte": now}}).sort("due_at", 1).limit(limit)
    cards = []
    async for d in cur:
        seed = seed_map.get(d["card_id"])
        if not seed:
            continue
        cards.append({**seed, "ease": d["ease"], "interval": d["interval"], "reps": d["reps"]})
    total = await db.review_state.count_documents({"device_id": did})
    return {"cards": cards, "due_count": len(cards), "total_cards": total}


@api.post("/api/review/{card_id}/grade")
async def grade_review(card_id: str, body: ReviewGrade, request: Request,
                       x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    state = await db.review_state.find_one({"device_id": did, "card_id": card_id})
    if not state:
        state = {"ease": 2.5, "interval": 0, "reps": 0}
    q = max(0, min(5, body.quality))
    ease = state["ease"] + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    ease = max(1.3, ease)
    reps = state.get("reps", 0)
    if q < 3:
        reps = 0
        interval = 0  # show again soon (same session)
    else:
        reps += 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 3
        else:
            interval = round(state.get("interval", 1) * ease)
    due = now_utc() + timedelta(days=interval) if interval > 0 else now_utc() + timedelta(minutes=2)
    await db.review_state.update_one(
        {"device_id": did, "card_id": card_id},
        {"$set": {"ease": ease, "interval": interval, "reps": reps,
                  "due_at": due.isoformat(), "level_id": card_id.split("::")[0]},
         "$setOnInsert": {"device_id": did, "card_id": card_id}},
        upsert=True,
    )
    await db.profiles.update_one({"device_id": did}, {"$inc": {"reviews_done": 1}})
    profile = await get_profile(did)
    await bump_streak(did, profile)
    if q >= 3:
        await award_xp(did, 8)
    new_badges = await recompute_badges(did)
    return {"ok": True, "next_interval_days": interval,
            "new_badges": [BADGE_MAP[b] for b in new_badges],
            "profile": profile_public(await get_profile(did))}


@api.post("/api/review/seed-all")
async def seed_all_reviews(request: Request, x_device_id: Optional[str] = Header(None)):
    """Make all earned (completed-level) cards available; also called lazily."""
    did = device_id(x_device_id, request)
    levels_done = await completed_level_ids(did)
    for lid in levels_done:
        await seed_reviews(did, lid)
    return {"ok": True, "seeded_levels": len(levels_done)}


# ----------------------------------------------------------------- skill tree
@api.get("/api/skills")
async def skill_tree(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    done = await completed_mission_ids(did)
    levels_done = await completed_level_ids(did, done)
    # map worlds -> skills, compute progress
    branch_levels = {b["id"]: {"total": 0, "done": 0} for b in SKILL_BRANCHES}
    for w in engine.worlds:
        skill = w["skill"]
        if skill not in branch_levels:
            branch_levels[skill] = {"total": 0, "done": 0}
        for lv in w["levels"]:
            branch_levels[skill]["total"] += 1
            if lv["id"] in levels_done:
                branch_levels[skill]["done"] += 1
    out = []
    for b in SKILL_BRANCHES:
        st = branch_levels.get(b["id"], {"total": 0, "done": 0})
        pct = round(100 * st["done"] / st["total"]) if st["total"] else 0
        tier = 0 if pct == 0 else (1 if pct < 50 else (2 if pct < 100 else 3))
        out.append({**b, "total": st["total"], "done": st["done"],
                    "progress": pct, "tier": tier,
                    "unlocked": st["done"] > 0 or st["total"] == 0})
    return out


# ----------------------------------------------------------------- badges
@api.get("/api/badges")
async def badges(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    profile = await get_profile(did)
    earned = set(profile.get("badges", []))
    return [{**b, "earned": b["id"] in earned} for b in BADGES]


# ----------------------------------------------------------------- notifications
@api.get("/api/notifications/preferences")
async def get_notif_prefs(request: Request, x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    doc = await db.notif_prefs.find_one({"device_id": did})
    if not doc:
        prefs = NotificationPrefsPayload().model_dump()
        await db.notif_prefs.insert_one({"device_id": did, **prefs})
        return {**prefs, "push_supported": False, "status": "coming_soon"}
    doc.pop("_id", None)
    doc.pop("device_id", None)
    return {**doc, "push_supported": False, "status": "coming_soon"}


@api.put("/api/notifications/preferences")
async def put_notif_prefs(payload: NotificationPrefsPayload, request: Request,
                          x_device_id: Optional[str] = Header(None)):
    did = device_id(x_device_id, request)
    await db.notif_prefs.update_one({"device_id": did},
                                    {"$set": {"device_id": did, **payload.model_dump()}},
                                    upsert=True)
    return {**payload.model_dump(), "push_supported": False, "status": "coming_soon"}


@app.on_event("startup")
async def startup():
    await db.mission_progress.create_index([("device_id", 1), ("mission_id", 1)], unique=True)
    await db.review_state.create_index([("device_id", 1), ("card_id", 1)], unique=True)
    await db.profiles.create_index("device_id", unique=True)
