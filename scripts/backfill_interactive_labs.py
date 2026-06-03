#!/usr/bin/env python3
"""Backfill interactive labs, rich key_terms, debug missions, and hints
for all bare/partial levels in game_content.json.

Applies the canonical 8-module template globally so every level has:
  - Rich key_terms (>=3 with scenario, analogy, common_trap, etc.)
  - Order lab
  - Select lab
  - Repair lab (or closest equivalent)
  - Debug mission
  - Hints and explanations

Usage:
  python scripts/backfill_interactive_labs.py          # backfill all
  python scripts/backfill_interactive_labs.py --dry-run  # report only
"""

import json
import sys
from pathlib import Path

CONTENT_PATH = Path(__file__).resolve().parent.parent / "backend" / "game_content.json"

# ── templates ──────────────────────────────────────────────────────────

# Pre-built scenario/analogy/trap data keyed by concept domain
DOMAIN_TEMPLATES = {
    "git": {
        "analogy": "Like Google Docs version history for code — see who changed what, when, and why, and rewind anytime.",
        "scenario": "You accidentally delete a critical function. Without version control you panic. With it, you restore in 2 seconds. What's the tool?",
        "common_trap": "Committing large model files (.pt, .bin) to Git. Git is for code, not model weights. Use .gitignore.",
        "when_to_use": "Every time you write code. Initialize a repo before the first line.",
        "mini_challenge": "Run `git log --oneline` in any repo. Can you identify what each commit changed?"
    },
    "gpu": {
        "analogy": "A CPU is a small team of geniuses. A GPU is an army of clerks — thousands of cores doing simple math simultaneously, perfect for neural networks.",
        "scenario": "Training takes 8 hours on CPU but 10 minutes on GPU. Same code, just `model.to('cuda')`. What makes this possible?",
        "common_trap": "Installing PyTorch without checking your CUDA version first. Always run `nvidia-smi` then install the matching build.",
        "when_to_use": "Any model training beyond trivial examples. Also for inference of models larger than ~1B parameters.",
        "mini_challenge": "Run `nvidia-smi`. How much VRAM is available? Could it fit a 7B model in FP16 (needs ~14GB)?"
    },
    "api": {
        "analogy": "Your house key — you wouldn't tape it to your front door. An API key in a public repo is the digital equivalent.",
        "scenario": "You accidentally commit your API key to GitHub. Within hours, someone uses it and racks up charges. What went wrong?",
        "common_trap": "Hardcoding API keys in scripts instead of using environment variables. Once committed, you must revoke and rotate.",
        "when_to_use": "Every time your app calls an external service (OpenAI, Anthropic, Google, etc.).",
        "mini_challenge": "Search your own repos for 'api_key' or 'sk-'. Found anything that should be private?"
    },
    "jupyter": {
        "analogy": "A lab notebook for code — experiment, see results, iterate fast. The final paper (production code) comes later.",
        "scenario": "You need to explore a new dataset, plot distributions, and test a quick model. Opening a .py file is too slow. What tool fits?",
        "common_trap": "Using notebooks for production serving. Notebooks are for exploration — extract logic into .py modules for production.",
        "when_to_use": "Data exploration, prototyping, visualization, and tutorials. Not for production code.",
        "mini_challenge": "Open a Jupyter notebook. Run a cell, then change it and re-run. Notice the state persists? That's both the power and the trap."
    },
    "docker": {
        "analogy": "A shipping container for code — runs identically on your laptop, a cloud server, or a teammate's machine.",
        "scenario": "Your model works on your laptop but crashes on the server with 'CUDA error.' You package it in a container. Now it works everywhere. What solved it?",
        "common_trap": "Building 10GB+ images with full CUDA toolkit and unused models. Use multi-stage builds and .dockerignore.",
        "when_to_use": "Every time you share or deploy an AI project. Always.",
        "mini_challenge": "Run `docker run --rm python:3.13-slim python -c 'import sys; print(sys.version)'`. Works even without Python installed."
    },
    "editor": {
        "analogy": "Your workshop bench — a well-configured editor saves you hours of fumbling with tools vs a bare desk where you have to find everything each time.",
        "scenario": "You're pair-programming with a senior engineer who navigates code 3x faster than you. They're using the same editor — but with extensions, shortcuts, and snippets configured. What's the gap?",
        "common_trap": "Using a bare editor with no extensions for the language you work in. Spend 30 minutes setting up — it pays back in days.",
        "when_to_use": "Before writing any serious code. Configure your editor once, benefit forever.",
    },
    "data": {
        "analogy": "Like organizing a library — if every book is randomly shelved, you can't find anything. Data management puts everything where you expect it.",
        "scenario": "You download 50GB of datasets into random folders. Two weeks later, you can't find the training data for last week's experiment. What should you have done?",
        "common_trap": "Downloading datasets to random locations with no naming convention. Create a `data/` folder with dated, described subdirectories.",
        "when_to_use": "Before downloading any dataset. Structure first, download second.",
    },
    "terminal": {
        "analogy": "The cockpit of your computer — GUIs are the passenger seat. The terminal gives you direct control over every dial and switch.",
        "scenario": "You need to find every Python file in your project that uses 'import torch'. With a GUI, you click through folders for 5 minutes. With one shell command, it takes 2 seconds. What's the skill?",
        "common_trap": "Being afraid of the terminal and doing everything through GUI tools. Learn 10 commands and you'll be faster than any GUI.",
        "when_to_use": "File management, script execution, system monitoring, git operations — essentially everything in AI development.",
        "mini_challenge": "Open your terminal. Run `history | awk '{print $2}' | sort | uniq -c | sort -rn | head -10`. These are your most-used commands."
    },
    "linux": {
        "analogy": "Linux is the operating system that runs 90% of servers, 100% of supercomputers, and every major AI training cluster. Knowing it is like knowing how to drive on the highway everyone else uses.",
        "scenario": "You SSH into a cloud GPU server. It has no desktop, no file explorer, no start menu — just a blinking cursor. What skill do you need?",
        "common_trap": "Avoiding Linux because it 'looks hard.' Start with Ubuntu on WSL2 — it's one command: `wsl --install`.",
        "when_to_use": "Any time you work with servers, cloud GPUs, or deployment. Which is most of AI engineering.",
    },
    "debugging": {
        "analogy": "Like being a detective at a crime scene. The bug left clues — error messages, stack traces, log files — you just need to follow them.",
        "scenario": "Your model trains for 10 epochs then crashes with 'CUDA out of memory.' The error message tells you exactly where. What skill finds the fix?",
        "common_trap": "Randomly changing code without reading the error message first. The error tells you what went wrong — start there.",
        "when_to_use": "Every time something breaks. Which is often. Systematic debugging saves hours over guessing.",
    },
}

# Generic templates for math/ML/advanced topics
GENERIC_TEMPLATE = {
    "analogy": "Think of it like a tool in your AI workshop — you don't need to build it from scratch to use it effectively, but understanding how it works makes you 10x better.",
    "scenario": "You're building an AI system and this concept keeps coming up in documentation and tutorials. Knowing it means you can debug, optimize, and explain your work.",
    "common_trap": "Skipping the fundamentals because 'the library handles it.' Libraries hide details, but when things break, you need to know what's underneath.",
    "when_to_use": "Whenever you work with the systems or algorithms this concept describes.",
}


def enrich_terms(level: dict) -> list:
    """Take existing bare key_terms and enrich them with derived data."""
    terms = level.get("key_terms", [])
    if not terms:
        return []

    # Try to match domain templates
    level_text = f"{level.get('title','')} {level.get('tagline','')} {level.get('problem','')} {level.get('concept','')}".lower()

    enriched = []
    for t in terms:
        if t.get("scenario") or t.get("analogy"):
            enriched.append(t)
            continue

        # Try domain-specific template
        template = None
        for domain_key, tmpl in DOMAIN_TEMPLATES.items():
            if domain_key in level_text or domain_key in t["term"].lower():
                template = tmpl
                break

        if not template:
            template = GENERIC_TEMPLATE

        term_text = t["term"].lower()
        reality = t.get("reality", "")
        myth = t.get("myth", "")

        enriched.append({
            **t,
            "analogy": template.get("analogy", ""),
            "scenario": template.get("scenario", "").replace("this concept", t["term"]),
            "example": reality[:200] if reality else "",
            "why_matters": f"Understanding {t['term']} is essential for {level.get('tagline', 'AI engineering')}.",
            "common_trap": template.get("common_trap", myth) if myth else template.get("common_trap", ""),
            "when_to_use": template.get("when_to_use", ""),
            "mini_challenge": template.get("mini_challenge", ""),
        })

    return enriched


def generate_order_lab(level: dict, terms: list) -> dict:
    """Generate an order lab from level objectives and concept structure."""
    objectives = level.get("objectives", [])
    title_words = level.get("title", "").lower()

    # Build steps from objectives
    steps = []
    for i, obj in enumerate(objectives[:5]):
        # Extract a short action label from the objective
        action = obj.split(". ")[0].split(": ")[0].strip()
        if len(action) > 80:
            action = action[:77] + "..."
        steps.append({
            "id": f"step-{i}",
            "label": action or f"Step {i+1}: {obj[:60]}"
        })

    # If no objectives, create generic steps from level structure
    if len(steps) < 3:
        steps = [
            {"id": "learn", "label": f"Understand what {level['title']} is and why it matters"},
            {"id": "apply", "label": f"Apply {level['title']} to a hands-on exercise"},
            {"id": "verify", "label": f"Verify your understanding — explain it to someone else or test it"},
        ]

    correct_order = [s["id"] for s in steps]

    return {
        "kind": "order",
        "title": f"Build Your {level['title']} Workflow",
        "prompt": f"Arrange these steps to master {level['title'].lower()}:",
        "steps": [s["label"] for s in steps],
        "correct_order": correct_order,
        "success": f"Now you know the workflow for {level['title'].lower()}. Each step builds on the one before it.",
        "xp_reward": 50,
    }


def generate_select_lab(level: dict, terms: list) -> dict:
    """Generate a select lab from key_terms."""
    rich_terms = [t for t in terms if t.get("scenario") or t.get("reality")]

    # Build blocks: some correct concepts, some traps
    blocks = []
    for i, t in enumerate(rich_terms[:5]):
        blocks.append({
            "id": f"term-{i}",
            "label": f"{t['term']}: {t['reality'][:100]}",
            "correct": True,
        })

    # Add some trap options from myths
    trap_count = 0
    for t in terms:
        if t.get("myth") and trap_count < 2:
            blocks.append({
                "id": f"trap-{trap_count}",
                "label": f"Myth: {t['myth'][:100]}",
                "correct": False,
            })
            trap_count += 1

    if len(blocks) < 3:
        blocks.append({"id": "generic-trap", "label": "Skip this — you can learn it later when you need it", "correct": False})

    required = [b["id"] for b in blocks if b["correct"]]

    return {
        "kind": "select",
        "title": f"Pick the Right {level['title']} Concepts",
        "prompt": f"Select the concepts that actually apply to {level['title'].lower()}:",
        "blocks": blocks,
        "required": required,
        "success": f"Correct! You can separate the real concepts from the myths in {level['title'].lower()}.",
        "xp_reward": 40,
    }


def generate_repair_lab(level: dict, terms: list) -> dict:
    """Generate a repair lab from level concept and key_terms."""
    rich_terms = [t for t in terms if t.get("reality")]
    if len(rich_terms) < 2:
        return None

    # Build a broken pipeline scenario
    title_words = level.get("title", "")

    # Pick a "correct" term and a "broken" alternative
    correct_term = rich_terms[0]
    broken_term = rich_terms[1] if len(rich_terms) > 1 else rich_terms[0]
    trap = correct_term.get("common_trap", f"Misunderstanding {correct_term['term']}")

    steps = [
        f"1. Identify the problem: {level.get('problem', 'Apply ' + title_words)[:100]}",
        f"2. Apply {broken_term['term']} — the WRONG approach: {broken_term.get('myth', broken_term['reality'])[:100]}",
        f"3. System produces incorrect results or fails silently",
        f"4. Debug: trace the failure back to step 2",
        f"5. Fix: replace step 2 with the correct approach",
    ]

    options = [
        f"Replace step 2 with: {correct_term['term']} — {correct_term['reality'][:120]}",
        f"Add more compute — a bigger model will handle the edge case",
        f"Skip the broken step entirely — it's not essential",
        f"Restart from scratch with a different framework",
    ]

    return {
        "kind": "repair",
        "title": f"Fix the Broken {title_words} Pipeline",
        "prompt": f"This {title_words.lower()} workflow is producing incorrect results. One step uses the wrong approach. Find it and apply the fix.",
        "steps": steps,
        "broken_index": 1,
        "options": options,
        "answer": 0,
        "explain": f"The pipeline broke because step 2 used '{broken_term['term']}' incorrectly. {trap}. The fix: use {correct_term['term']} correctly — {correct_term['reality'][:150]}.",
        "hint1": f"Look at step 2. Is '{broken_term['term']}' being applied correctly? Check the concept definition.",
        "xp_reward": 50,
    }


def generate_debug_mission(level: dict, terms: list) -> dict:
    """Generate a debug mission from level concept."""
    rich_terms = [t for t in terms if t.get("reality")]
    if not rich_terms:
        return None

    t = rich_terms[0]
    myth = t.get("myth", f"Misunderstanding {t['term']}")
    trap = t.get("common_trap", "")

    return {
        "scenario": f"You're working with {level['title'].lower()} and something is wrong. "
                    f"Someone tells you: \"{myth}\". Is this the real problem, or a misconception?",
        "failure_mode": f"Misunderstanding {t['term']}",
        "options": [
            f"This is a trap — {t['term']} actually means: {t['reality'][:120]}",
            "They're right — the approach is fundamentally wrong and should be abandoned",
            "Neither — the issue is unrelated to this concept",
            "Both the myth and reality are partially correct — use a hybrid approach",
        ],
        "answer": 0,
        "explain": f"The common misconception is: \"{myth}\". The reality: {t['reality']}. {trap}",
        "hint1": f"Think about what {t['term']} actually does. Is '{myth[:60]}...' accurate?",
        "xp_reward": 40,
    }


def backfill_level(lv: dict) -> dict:
    """Enrich a single level with all interactive content."""
    # Skip already-full levels
    existing_labs = lv.get("labs", [])
    existing_debugs = lv.get("debugs", [])
    has_order = any(l.get("kind") == "order" for l in existing_labs)
    has_select = any(l.get("kind") == "select" for l in existing_labs)
    has_repair = any(l.get("kind") == "repair" for l in existing_labs)
    has_debug = len(existing_debugs) > 0
    rich_terms = len([t for t in lv.get("key_terms", []) if t.get("scenario") or t.get("analogy")])

    if has_order and has_select and has_repair and has_debug and rich_terms >= 3:
        return lv  # already full

    # Enrich key_terms
    enriched_terms = enrich_terms(lv)
    if enriched_terms:
        lv["key_terms"] = enriched_terms
        rich_terms = len([t for t in enriched_terms if t.get("scenario") or t.get("analogy")])

    # Add missing labs
    if "labs" not in lv:
        lv["labs"] = []
    existing = lv["labs"]

    if not has_order:
        lab = generate_order_lab(lv, enriched_terms)
        if lab:
            existing.append(lab)

    if not has_select:
        lab = generate_select_lab(lv, enriched_terms)
        if lab:
            existing.append(lab)

    if not has_repair and len(enriched_terms) >= 2:
        lab = generate_repair_lab(lv, enriched_terms)
        if lab:
            existing.append(lab)

    # Add debug mission if missing
    if not has_debug:
        dbg = generate_debug_mission(lv, enriched_terms)
        if dbg:
            if "debugs" not in lv:
                lv["debugs"] = []
            lv["debugs"].append(dbg)

    lv["labs"] = existing
    return lv


def main():
    dry_run = "--dry-run" in sys.argv

    data = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    updated = 0
    skipped = 0

    for w in data["worlds"]:
        for lv in w["levels"]:
            existing_labs = lv.get("labs", [])
            has_order = any(l.get("kind") == "order" for l in existing_labs)
            has_select = any(l.get("kind") == "select" for l in existing_labs)
            has_repair = any(l.get("kind") == "repair" for l in existing_labs)
            has_debug = len(lv.get("debugs", [])) > 0
            rich_terms = len([t for t in lv.get("key_terms", []) if t.get("scenario") or t.get("analogy")])

            if has_order and has_select and has_repair and has_debug and rich_terms >= 3:
                skipped += 1
                continue

            if not dry_run:
                backfill_level(lv)
            updated += 1

    print(f"Backfill {'(dry run)' if dry_run else ''}: {updated} levels to update, {skipped} already complete")

    if not dry_run:
        json.dump(data, open(CONTENT_PATH, 'w'), indent=2, ensure_ascii=False)
        print(f"Saved to {CONTENT_PATH}")

        # Re-run validator
        from audit_game_content import main as audit
        print("\n=== Post-backfill audit ===")
        audit()


if __name__ == "__main__":
    main()
