"""Content engine: loads generated game_content.json and turns each repo
lesson into a playable LEVEL with deterministic, ADHD-friendly missions,
quizzes and spaced-repetition review cards. No network, no secrets."""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Dict, List, Optional

CONTENT_PATH = Path(__file__).resolve().parent / "game_content.json"

# Mission XP values — motivating, not childish.
XP = {
    "briefing": 20,
    "concept": 25,
    "decode": 40,
    "mythbuster": 35,
    "build": 50,
    "boss": 80,
}
LEVEL_COMPLETE_BONUS = 60
TEST_OUT_THRESHOLD = 0.9  # must score 90%+ to unlock via test-out
TEST_OUT_QUESTION_COUNT = 10

SKILL_BRANCHES = [
    {"id": "prompt-design", "name": "Prompt Design", "icon": "wand-sparkles"},
    {"id": "tool-use", "name": "Tool Use", "icon": "wrench"},
    {"id": "memory", "name": "Memory", "icon": "brain"},
    {"id": "retrieval", "name": "Retrieval", "icon": "search"},
    {"id": "agent-routing", "name": "Agent Routing", "icon": "route"},
    {"id": "orchestration", "name": "Multi-Agent Orchestration", "icon": "network"},
    {"id": "evaluation", "name": "Evaluation", "icon": "clipboard-check"},
    {"id": "debugging", "name": "Debugging", "icon": "bug"},
    {"id": "safety", "name": "Safety", "icon": "shield"},
    {"id": "deployment", "name": "Deployment", "icon": "rocket"},
    {"id": "product-thinking", "name": "Product Thinking", "icon": "lightbulb"},
]


def _seed(s: str) -> random.Random:
    h = int(hashlib.sha256(s.encode()).hexdigest(), 16)
    return random.Random(h)


class ContentEngine:
    def __init__(self):
        raw = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
        self.data = raw
        self.worlds: List[dict] = raw["worlds"]
        self.levels_by_id: Dict[str, dict] = {}
        self.level_order: List[str] = []  # global progression order
        self.world_term_pool: Dict[int, List[dict]] = {}
        # Per-world progression: first level of each world is always open;
        # later levels unlock when the previous level IN THE SAME WORLD is done.
        self.first_in_world: set = set()
        self.prev_in_world: Dict[str, Optional[str]] = {}
        for w in self.worlds:
            pool = []
            ordered = sorted(w["levels"], key=lambda x: x["order"])
            for i, lv in enumerate(ordered):
                self.levels_by_id[lv["id"]] = lv
                self.level_order.append(lv["id"])
                pool.extend(lv.get("key_terms", []))
                if i == 0:
                    self.first_in_world.add(lv["id"])
                    self.prev_in_world[lv["id"]] = None
                else:
                    self.prev_in_world[lv["id"]] = ordered[i - 1]["id"]
            self.world_term_pool[w["id"]] = pool

        # ---- Fork content (alternative learning paths, e.g. MIT 18.06) ----
        self.forks: List[dict] = []
        self.fork_by_id: Dict[str, dict] = {}
        self.fork_first: set = set()
        self.fork_prev: Dict[str, Optional[str]] = {}
        self.anchor_forks: Dict[str, List[str]] = {}  # anchor_level_id -> [fork_id]
        fork_path = CONTENT_PATH.parent / "fork_content.json"
        if fork_path.exists():
            fdata = json.loads(fork_path.read_text(encoding="utf-8"))
            for fk in fdata.get("forks", []):
                self.forks.append(fk)
                self.fork_by_id[fk["id"]] = fk
                self.anchor_forks.setdefault(fk["anchor_level_id"], []).append(fk["id"])
                ordered = sorted(fk["levels"], key=lambda x: x["order"])
                for i, lv in enumerate(ordered):
                    self.levels_by_id[lv["id"]] = lv  # fork levels are addressable too
                    if i == 0:
                        self.fork_first.add(lv["id"])
                        self.fork_prev[lv["id"]] = None
                    else:
                        self.fork_prev[lv["id"]] = ordered[i - 1]["id"]

        # ---- Academy learning paths (e.g. Agentic Design Patterns) ----
        self.academy_paths: List[dict] = []
        self.academy_by_id: Dict[str, dict] = {}
        self.academy_first: set = set()
        self.academy_prev: Dict[str, Optional[str]] = {}
        ac_path = CONTENT_PATH.parent / "academy_content.json"
        if ac_path.exists():
            adata = json.loads(ac_path.read_text(encoding="utf-8"))
            for path in adata.get("paths", []):
                self.academy_paths.append(path)
                self.academy_by_id[path["id"]] = path
                ordered = sorted(path["chapters"], key=lambda x: x["number"])
                for i, ch in enumerate(ordered):
                    self.levels_by_id[ch["id"]] = ch  # chapters are addressable levels
                    if i == 0:
                        self.academy_first.add(ch["id"])
                        self.academy_prev[ch["id"]] = None
                    else:
                        self.academy_prev[ch["id"]] = ordered[i - 1]["id"]

    # ---------- campaign ----------
    def campaign(self) -> List[dict]:
        out = []
        for w in self.worlds:
            out.append({
                "id": w["id"],
                "name": w["name"],
                "short": w["short"],
                "tagline": w["tagline"],
                "skill": w["skill"],
                "order": w["order"],
                "level_count": w["level_count"],
                "levels": [{
                    "id": lv["id"],
                    "title": lv["title"],
                    "tagline": lv["tagline"],
                    "type": lv["type"],
                    "order": lv["order"],
                    "estimated_minutes": lv["estimated_minutes"],
                    "mission_count": len(self._missions(lv)),
                    "term_count": len(lv.get("key_terms", [])),
                } for lv in w["levels"]],
            })
        return out

    def prev_level_id(self, level_id: str) -> Optional[str]:
        try:
            idx = self.level_order.index(level_id)
        except ValueError:
            return None
        return self.level_order[idx - 1] if idx > 0 else None

    def first_level_id(self) -> str:
        return self.level_order[0]

    # ---------- distractor helper ----------
    def _distractors(self, level: dict, correct: str, rng: random.Random, n: int = 3) -> List[str]:
        pool = [t["reality"] for t in level.get("key_terms", []) if t["reality"] != correct]
        if len(pool) < n:
            wpool = [t["reality"] for t in self.world_term_pool.get(level["world_id"], [])
                     if t["reality"] != correct and t["reality"] not in pool]
            rng.shuffle(wpool)
            pool.extend(wpool)
        # de-dup preserve order
        seen, uniq = set(), []
        for p in pool:
            if p not in seen:
                seen.add(p); uniq.append(p)
        rng.shuffle(uniq)
        return uniq[:n]

    # ---------- mission generation ----------
    def _missions(self, level: dict) -> List[dict]:
        rng = _seed(level["id"])
        terms = level.get("key_terms", [])
        missions: List[dict] = []

        # 1. BRIEFING
        why = level.get("problem") or level.get("concept") or ""
        missions.append({
            "id": f"{level['id']}::briefing",
            "type": "briefing",
            "title": "Mission Briefing",
            "objective": "Lock in why this skill matters before you build.",
            "estimated_minutes": 2,
            "xp_reward": XP["briefing"],
            "payload": {
                "tagline": level["tagline"],
                "why_it_matters": _shorten(why, 320),
                "objectives": level.get("objectives", [])[:4],
                "languages": level.get("languages", ""),
            },
        })

        # 2. CONCEPT flip cards (myth -> reality)
        if terms:
            cards = [{
                "term": t["term"],
                "front": t["myth"] or f"What is {t['term']}?",
                "back": t["reality"],
            } for t in terms[:6]]
            missions.append({
                "id": f"{level['id']}::concept",
                "type": "concept",
                "title": "Concept Cards",
                "objective": "Flip each card. Bust the myth, keep the reality.",
                "estimated_minutes": 3,
                "xp_reward": XP["concept"],
                "payload": {"cards": cards},
            })

        # 3. DECODE quiz (what does X actually mean?)
        quiz_terms = terms[:5]
        if len(self.world_term_pool.get(level["world_id"], [])) >= 4 and quiz_terms:
            questions = []
            for t in quiz_terms:
                opts = self._distractors(level, t["reality"], rng, 3) + [t["reality"]]
                opts = list(dict.fromkeys(opts))
                if len(opts) < 2:
                    continue
                rng.shuffle(opts)
                questions.append({
                    "q": f"What does \u201c{t['term']}\u201d actually mean?",
                    "options": opts,
                    "answer": opts.index(t["reality"]),
                    "explain": f"{t['term']}: {t['reality']}",
                })
            if questions:
                missions.append({
                    "id": f"{level['id']}::decode",
                    "type": "quiz",
                    "title": "Decode Challenge",
                    "objective": "Pick the real meaning. Retry freely, no penalty.",
                    "estimated_minutes": 4,
                    "xp_reward": XP["decode"],
                    "payload": {"questions": questions},
                })

        # 4. MYTH-BUSTER mini-game (true vs hype)
        if len(terms) >= 2:
            rounds = []
            for t in terms[:5]:
                if not t["myth"]:
                    continue
                statements = [
                    {"text": t["reality"], "truth": True},
                    {"text": f"\u201c{t['myth']}\u201d \u2014 the hype version", "truth": False},
                ]
                rng.shuffle(statements)
                rounds.append({"term": t["term"], "statements": statements})
            if rounds:
                missions.append({
                    "id": f"{level['id']}::mythbuster",
                    "type": "mythbuster",
                    "title": "Myth Buster",
                    "objective": "Tap the accurate statement, not the hype.",
                    "estimated_minutes": 3,
                    "xp_reward": XP["mythbuster"],
                    "payload": {"rounds": rounds},
                })

        # 5. BUILD / LAB (code trace + explain-like-building)
        if level.get("code"):
            missions.append({
                "id": f"{level['id']}::build",
                "type": "build",
                "title": "Build It",
                "objective": "Read the working pattern, then commit it to memory.",
                "estimated_minutes": 5,
                "xp_reward": XP["build"],
                "payload": {
                    "concept": _shorten(level.get("concept", ""), 360),
                    "code": level["code"],
                    "exercises": level.get("exercises", [])[:3],
                },
            })

        # 6. BOSS gauntlet
        boss_qs = []
        for t in terms[:6]:
            opts = self._distractors(level, t["reality"], rng, 3) + [t["reality"]]
            opts = list(dict.fromkeys(opts))
            if len(opts) < 2:
                continue
            rng.shuffle(opts)
            boss_qs.append({
                "q": f"Boss check \u2014 {t['term']}: which is correct?",
                "options": opts,
                "answer": opts.index(t["reality"]),
                "explain": t["reality"],
            })
        if boss_qs:
            missions.append({
                "id": f"{level['id']}::boss",
                "type": "boss",
                "title": f"Boss: {level['title']}",
                "objective": "Clear the gauntlet to seal this skill.",
                "estimated_minutes": 5,
                "xp_reward": XP["boss"],
                "payload": {
                    "questions": boss_qs,
                    "pass_threshold": max(1, int(len(boss_qs) * 0.6)),
                    "recap": level.get("objectives", [])[:4],
                },
            })

        return missions

    def level_detail(self, level_id: str) -> Optional[dict]:
        lv = self.levels_by_id.get(level_id)
        if not lv:
            return None
        missions = lv["missions"] if lv.get("missions") else self._missions(lv)
        out = {
            "id": lv["id"],
            "world_id": lv["world_id"],
            "title": lv["title"],
            "tagline": lv["tagline"],
            "type": lv["type"],
            "estimated_minutes": lv["estimated_minutes"],
            "objectives": lv.get("objectives", []),
            "source_path": lv["source_path"],
            "missions": missions,
            "total_xp": sum(m["xp_reward"] for m in missions) + LEVEL_COMPLETE_BONUS,
            "complete_bonus": LEVEL_COMPLETE_BONUS,
            "is_fork": lv.get("is_fork", False),
            "fork_id": lv.get("fork_id"),
            "is_academy": lv.get("is_academy", False),
            "path_id": lv.get("path_id"),
            "pattern": lv.get("pattern"),
            "icon": lv.get("icon"),
            "group": lv.get("group"),
        }
        # Surface available forks on the anchor level (e.g. Linear Algebra)
        if lv["id"] in self.anchor_forks:
            out["forks"] = [self.fork_summary(fid) for fid in self.anchor_forks[lv["id"]]]
        return out

    def mission_ids_for_level(self, level_id: str) -> List[str]:
        lv = self.levels_by_id.get(level_id)
        if not lv:
            return []
        if lv.get("missions"):
            return [m["id"] for m in lv["missions"]]
        return [m["id"] for m in self._missions(lv)]

    # ---------- academy paths ----------
    def learning_paths(self) -> List[dict]:
        paths = [{
            "id": "campaign", "title": "AI Engineering Quest", "kind": "campaign",
            "tagline": "The original 96-level journey from math foundations to multi-agent systems.",
            "unit_count": self.data["level_count"], "unit_label": "levels",
        }]
        for p in self.academy_paths:
            paths.append({
                "id": p["id"], "title": p["title"], "kind": "academy",
                "tagline": p["tagline"], "description": p.get("description", ""),
                "attribution": p.get("attribution", ""),
                "unit_count": p["chapter_count"], "unit_label": "patterns",
            })
        return paths

    def academy_summary(self, path_id: str) -> Optional[dict]:
        p = self.academy_by_id.get(path_id)
        if not p:
            return None
        return {"id": p["id"], "title": p["title"], "tagline": p["tagline"],
                "description": p.get("description", ""), "attribution": p.get("attribution", ""),
                "groups": p["groups"], "chapter_count": p["chapter_count"]}

    def academy_chapters(self, path_id: str) -> List[dict]:
        p = self.academy_by_id.get(path_id)
        return sorted(p["chapters"], key=lambda x: x["number"]) if p else []

    def first_academy_chapter(self, path_id: str) -> Optional[str]:
        chs = self.academy_chapters(path_id)
        return chs[0]["id"] if chs else None

    def dojo_bank(self, path_id: str = "agentic-patterns") -> List[dict]:
        bank = []
        for ch in self.academy_chapters(path_id):
            for m in ch["missions"]:
                if m["type"] == "drill":
                    for r in m["payload"]["rounds"]:
                        bank.append({"id": f"{ch['id']}-dojo", "pattern": ch["pattern"],
                                     "scenario": r["scenario"], "options": r["options"]})
        return bank

    def clinic_bank(self, path_id: str = "agentic-patterns") -> List[dict]:
        bank = []
        for ch in self.academy_chapters(path_id):
            for m in ch["missions"]:
                if m["type"] == "debug":
                    p = m["payload"]
                    bank.append({"id": f"{ch['id']}-clinic", "pattern": ch["pattern"],
                                 "scenario": p["scenario"], "broken": p.get("broken", ""),
                                 "options": p["options"], "answer": p["answer"],
                                 "failure_mode": p.get("failure_mode", ""), "explain": p["explain"]})
        return bank

    # ---------- forks ----------
    def fork_summary(self, fork_id: str) -> Optional[dict]:
        fk = self.fork_by_id.get(fork_id)
        if not fk:
            return None
        return {"id": fk["id"], "name": fk["name"], "short": fk.get("short", ""),
                "source": fk["source"], "tagline": fk["tagline"],
                "anchor_level_id": fk["anchor_level_id"], "level_count": fk["level_count"]}

    def fork_detail(self, fork_id: str) -> Optional[dict]:
        fk = self.fork_by_id.get(fork_id)
        if not fk:
            return None
        levels = sorted(fk["levels"], key=lambda x: x["order"])
        return {
            **self.fork_summary(fork_id),
            "levels": [{
                "id": lv["id"], "title": lv["title"], "tagline": lv["tagline"],
                "order": lv["order"], "type": lv["type"],
                "estimated_minutes": lv["estimated_minutes"],
                "mission_count": len(lv["missions"]),
                "youtube_id": lv.get("youtube_id"),
            } for lv in levels],
        }

    # ---------- review cards ----------
    def all_review_seeds(self) -> List[dict]:
        seeds = []
        for w in self.worlds:
            for lv in w["levels"]:
                for i, t in enumerate(lv.get("key_terms", [])):
                    seeds.append({
                        "card_id": f"{lv['id']}::card::{i}",
                        "level_id": lv["id"],
                        "world_id": w["id"],
                        "type": "concept",
                        "term": t["term"],
                        "prompt": f"What does \u201c{t['term']}\u201d actually mean?",
                        "myth": t["myth"],
                        "answer": t["reality"],
                    })
        # fork review cards (from curated concept terms)
        for fk in self.forks:
            for lv in fk["levels"]:
                for i, t in enumerate(lv.get("review_terms", [])):
                    seeds.append({
                        "card_id": f"{lv['id']}::card::{i}",
                        "level_id": lv["id"],
                        "world_id": fk["world_id"],
                        "type": "concept",
                        "term": t["term"],
                        "prompt": f"Recall: what is {t['term'].lower()}?",
                        "myth": "",
                        "answer": t["reality"],
                    })
        # academy review cards (explicit prompt/answer)
        for path in self.academy_paths:
            for ch in path["chapters"]:
                for i, c in enumerate(ch.get("review_cards", [])):
                    seeds.append({
                        "card_id": f"{ch['id']}::card::{i}",
                        "level_id": ch["id"],
                        "world_id": -1,
                        "type": "pattern",
                        "term": ch["pattern"],
                        "prompt": c["prompt"],
                        "myth": "",
                        "answer": c["answer"],
                    })
        return seeds

    def review_seeds_for_level(self, level_id: str) -> List[dict]:
        return [s for s in self.all_review_seeds() if s["level_id"] == level_id]

    def review_seed_map(self) -> Dict[str, dict]:
        return {s["card_id"]: s for s in self.all_review_seeds()}


    # ---------- test-out quiz ----------
    def test_out_quiz(self, level_id: str) -> Optional[dict]:
        """Generate a deterministic test-out quiz for a level.
        Returns up to TEST_OUT_QUESTION_COUNT questions pulled from the levelʼs
        key terms plus the world term pool. Quiz is deterministic per level_id
        and attempt seed so re-rolls are possible."""
        lv = self.levels_by_id.get(level_id)
        if not lv:
            return None
        rng = _seed(level_id)
        terms = lv.get("key_terms", [])
        world_pool = self.world_term_pool.get(lv["world_id"], [])
        candidates = list(terms) + [t for t in world_pool if t not in terms]
        if not candidates:
            return None
        questions = []
        for t in candidates[:TEST_OUT_QUESTION_COUNT * 2]:
            correct = t["reality"]
            opts = self._distractors(lv, correct, rng, 3) + [correct]
            opts = list(dict.fromkeys(opts))
            if len(opts) < 2:
                continue
            rng.shuffle(opts)
            questions.append({
                "q": f"What does “{t['term']}” actually mean?",
                "options": opts,
                "answer": opts.index(correct),
                "explain": f"{t['term']}: {correct}",
                "term": t["term"],
            })
            if len(questions) >= TEST_OUT_QUESTION_COUNT:
                break
        if len(questions) < 3:
            return None
        return {
            "level_id": level_id,
            "level_title": lv["title"],
            "threshold": TEST_OUT_THRESHOLD,
            "question_count": len(questions),
            "questions": questions,
        }



def _shorten(text: str, n: int) -> str:
    text = " ".join(text.split())
    if len(text) <= n:
        return text
    cut = text[:n]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut + "\u2026"


engine = ContentEngine()
