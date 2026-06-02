#!/usr/bin/env python3
"""
AgentForge Quest — Content Pipeline
Parses the ai-engineering-from-scratch repo (phases/*/*/docs/en.md) into a
deterministic game-content JSON used by the backend. No secrets, no network.

Each repo phase -> a WORLD. Each lesson (en.md) -> a LEVEL with generated missions.
Key Terms table (Term | what people say | what it actually means) powers
quizzes, myth-buster cards and spaced-repetition review cards.

Run: python scripts/build_content.py
Output: backend/game_content.json
"""
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PHASES = REPO / "phases"
OUT = REPO / "backend" / "game_content.json"

PHASE_RE = re.compile(r"^(\d+)-(.+)$")
LESSON_RE = re.compile(r"^(\d+)-(.+)$")

# ---------- helpers ----------

def title_case(slug: str) -> str:
    words = slug.replace("_", "-").split("-")
    small = {"and", "for", "of", "to", "the", "a", "in", "vs"}
    out = []
    for i, w in enumerate(words):
        if w.lower() in {"ai", "ml", "nlp", "llm", "llms", "gpu", "api", "apis",
                          "rag", "rl", "rlhf", "dpo", "sft", "bpe", "mcp", "cv",
                          "json", "lora", "gan", "vae", "cnn", "rnn", "gpt"}:
            out.append(w.upper())
        elif w.lower() in small and i != 0:
            out.append(w.lower())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def section(md: str, heading: str) -> str:
    """Return raw text under a '## heading' until the next '## '."""
    pattern = re.compile(r"^##\s+" + re.escape(heading) + r"\s*$", re.M)
    m = pattern.search(md)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s+", md[start:], re.M)
    end = start + nxt.start() if nxt else len(md)
    return md[start:end].strip()


def first_paragraphs(text: str, n: int = 2) -> str:
    # strip code blocks and diagrams
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    paras = [p for p in paras if not p.startswith("|") and not p.startswith("#")]
    return "\n\n".join(paras[:n]).strip()


def bullet_list(text: str, limit: int = 6):
    items = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^[-*]\s+(.+)$", line)
        if m:
            items.append(clean_inline(m.group(1)))
    return items[:limit]


def numbered_list(text: str, limit: int = 6):
    items = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^\d+\.\s+(.+)$", line)
        if m:
            items.append(clean_inline(m.group(1)))
    return items[:limit]


def clean_inline(s: str) -> str:
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s.strip()


def first_code_block(text: str):
    m = re.search(r"```(\w+)?\n(.*?)```", text, flags=re.S)
    if not m:
        return None
    lang = m.group(1) or "text"
    code = m.group(2).rstrip()
    # keep it short for mobile
    lines = code.splitlines()
    if len(lines) > 26:
        code = "\n".join(lines[:26]) + "\n# ..."
    return {"lang": lang, "code": code}


def parse_key_terms(md: str):
    block = section(md, "Key Terms")
    terms = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        term, myth, reality = cells[0], cells[1], cells[2]
        if term.lower() in ("term", "") or set(term) <= set("-:"):
            continue
        reality = clean_inline(reality).strip('"').strip()
        myth = clean_inline(myth).strip('"').strip()
        term = clean_inline(term)
        if term and reality:
            terms.append({"term": term, "myth": myth, "reality": reality})
    return terms


def parse_meta(md: str):
    meta = {}
    for key in ("Type", "Languages", "Prerequisites", "Time"):
        m = re.search(r"\*\*" + key + r":\*\*\s*(.+)", md)
        if m:
            meta[key.lower()] = clean_inline(m.group(1).strip())
    return meta


def tagline(md: str):
    m = re.search(r"^>\s*(.+)$", md, re.M)
    return clean_inline(m.group(1)) if m else ""


def lesson_title(md: str):
    m = re.search(r"^#\s+(.+)$", md, re.M)
    return clean_inline(m.group(1)) if m else ""


def est_minutes(meta):
    t = meta.get("time", "")
    m = re.search(r"(\d+)", t)
    if m:
        mins = int(m.group(1))
        # compress long sessions into ADHD micro-loops for the *level* estimate
        return max(4, min(7, round(mins / 15)))
    return 5

# ---------- world theming ----------
WORLD_THEME = {
    0: ("Forge Outpost", "Boot up your workshop and tools.", "Setup & Tooling"),
    1: ("Vector Vale", "Master the math that powers every model.", "Math Foundations"),
    2: ("Pattern Plains", "Teach machines to find signal in noise.", "ML Fundamentals"),
    3: ("Neural Nexus", "Wire up networks that learn.", "Deep Learning Core"),
    4: ("Vision Citadel", "Give machines eyes.", "Computer Vision"),
    5: ("Lexicon Reach", "From words to meaning.", "NLP"),
    6: ("Echo Caverns", "Sound, speech and audio.", "Speech & Audio"),
    7: ("Attention Spire", "The transformer, from the inside.", "Transformers"),
    8: ("Genesis Gardens", "Models that create.", "Generative AI"),
    9: ("Reward Reaches", "Learning by trial and reward.", "Reinforcement Learning"),
    10: ("Crucible Core", "Build an LLM from raw tokens up.", "LLMs From Scratch"),
    11: ("Prompt Bazaar", "Engineer LLMs into reliable products.", "LLM Engineering"),
    12: ("Fusion Atelier", "Blend text, vision and more.", "Multimodal AI"),
    13: ("Toolsmith Hall", "Give agents real-world tools.", "Tools & Protocols"),
    14: ("Agent Sanctum", "Where loops become agents.", "Agent Engineering"),
    15: ("Autonomy Frontier", "Systems that act on their own.", "Autonomous Systems"),
    16: ("Swarm Bastion", "Many agents, one mission.", "Multi-Agent & Swarms"),
    17: ("Production Bulwark", "Ship and scale to the real world.", "Infrastructure & Production"),
    18: ("Alignment Sanctum", "Keep powerful systems safe.", "Ethics, Safety & Alignment"),
    19: ("Capstone Arena", "Prove everything you've forged.", "Capstone Projects"),
}

# Skill branch mapping by phase for the skill tree
WORLD_SKILL = {
    0: "deployment", 1: "product-thinking", 2: "product-thinking", 3: "product-thinking",
    4: "retrieval", 5: "prompt-design", 6: "tool-use", 7: "product-thinking",
    8: "prompt-design", 9: "agent-routing", 10: "product-thinking", 11: "prompt-design",
    12: "retrieval", 13: "tool-use", 14: "agent-routing", 15: "safety",
    16: "orchestration", 17: "deployment", 18: "safety", 19: "evaluation",
}


def build():
    worlds = []
    all_levels = 0
    for pdir in sorted(PHASES.iterdir()):
        if not pdir.is_dir():
            continue
        pm = PHASE_RE.match(pdir.name)
        if not pm:
            continue
        pid = int(pm.group(1))
        wname, wtag, short = WORLD_THEME.get(pid, (title_case(pm.group(2)), "", title_case(pm.group(2))))

        levels = []
        for ldir in sorted(pdir.iterdir()):
            if not ldir.is_dir():
                continue
            en = ldir / "docs" / "en.md"
            if not en.exists():
                continue
            lm = LESSON_RE.match(ldir.name)
            order = int(lm.group(1)) if lm else 0
            md = en.read_text(encoding="utf-8", errors="ignore")

            meta = parse_meta(md)
            terms = parse_key_terms(md)
            objectives = bullet_list(section(md, "Learning Objectives"), 4)
            problem = first_paragraphs(section(md, "The Problem"), 2)
            concept = first_paragraphs(section(md, "The Concept"), 2)
            exercises = numbered_list(section(md, "Exercises"), 4)
            code = first_code_block(section(md, "Build It"))
            title = lesson_title(md) or title_case(lm.group(2) if lm else ldir.name)
            tag = tagline(md)

            level = {
                "id": f"{pid:02d}-{ldir.name}",
                "world_id": pid,
                "order": order,
                "title": title,
                "tagline": tag,
                "type": meta.get("type", "Learn"),
                "languages": meta.get("languages", ""),
                "prerequisites": meta.get("prerequisites", ""),
                "estimated_minutes": est_minutes(meta),
                "objectives": objectives,
                "problem": problem,
                "concept": concept,
                "code": code,
                "exercises": exercises,
                "key_terms": terms,
                "source_path": f"phases/{pdir.name}/{ldir.name}/docs/en.md",
            }
            levels.append(level)
            all_levels += 1

        if not levels:
            continue
        levels.sort(key=lambda x: x["order"])
        worlds.append({
            "id": pid,
            "name": wname,
            "short": short,
            "tagline": wtag,
            "skill": WORLD_SKILL.get(pid, "product-thinking"),
            "order": pid,
            "level_count": len(levels),
            "levels": levels,
        })

    worlds.sort(key=lambda x: x["order"])
    data = {
        "version": 1,
        "title": "AgentForge Quest",
        "world_count": len(worlds),
        "level_count": all_levels,
        "worlds": worlds,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Worlds: {len(worlds)}  Levels: {all_levels}")
    kt = sum(len(l['key_terms']) for w in worlds for l in w['levels'])
    print(f"Key terms (review/quiz source): {kt}")


if __name__ == "__main__":
    build()
