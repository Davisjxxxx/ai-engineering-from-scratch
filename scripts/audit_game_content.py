#!/usr/bin/env python3
"""Content quality validator for AgentForge Quest game_content.json.

Scores every level and classifies as:
  - full_interactive: rich terms + 3 labs + debug
  - partial: at least one enrichment
  - bare: no enrichment beyond auto-generated missions

Usage:
  python scripts/audit_game_content.py
  python scripts/audit_game_content.py --json  # machine-readable output
"""

import json
import sys
from pathlib import Path

CONTENT_PATH = Path(__file__).resolve().parent.parent / "backend" / "game_content.json"


def is_rich_term(t: dict) -> bool:
    """A term is 'rich' if it has scenario, analogy, or common_trap data."""
    return bool(t.get("scenario") or t.get("analogy") or t.get("common_trap"))


def audit_level(lv: dict) -> dict:
    terms = lv.get("key_terms", [])
    rich_terms = [t for t in terms if is_rich_term(t)]
    labs = lv.get("labs", [])
    debugs = lv.get("debugs", [])

    has_order = any(l.get("kind") == "order" for l in labs)
    has_select = any(l.get("kind") == "select" for l in labs)
    has_repair = any(l.get("kind") == "repair" for l in labs)
    has_debug = len(debugs) > 0
    has_hints = any(
        l.get("hint1") or (dbg.get("hint1") if isinstance(dbg, dict) else False)
        for l in labs for dbg in debugs
    ) or any(l.get("hint1") or l.get("hint2") for l in labs)

    lab_count = sum([has_order, has_select, has_repair])

    # Test-out readiness: can the test_out_quiz generator produce scenario/trap questions?
    test_out_ready = len(rich_terms) >= 3

    # Boss exists if the level's term data can generate one (auto-generated)
    has_boss = len(terms) >= 3

    score = 0
    if len(rich_terms) >= 3:
        score += 1  # rich terms
    if has_order:
        score += 1
    if has_select:
        score += 1
    if has_repair:
        score += 1
    if has_debug:
        score += 1

    if score >= 4:
        classification = "full_interactive"
    elif score >= 1:
        classification = "partial"
    else:
        classification = "bare"

    return {
        "id": lv["id"],
        "title": lv["title"],
        "classification": classification,
        "score": score,
        "key_terms_total": len(terms),
        "rich_terms": len(rich_terms),
        "has_order_lab": has_order,
        "has_select_lab": has_select,
        "has_repair_lab": has_repair,
        "has_debug": has_debug,
        "has_hints": has_hints,
        "has_boss": has_boss,
        "test_out_ready": test_out_ready,
    }


def main():
    data = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    results = []
    for w in data["worlds"]:
        for lv in w["levels"]:
            results.append(audit_level(lv))

    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))
        return

    full = [r for r in results if r["classification"] == "full_interactive"]
    partial = [r for r in results if r["classification"] == "partial"]
    bare = [r for r in results if r["classification"] == "bare"]

    print(f"=== AgentForge Quest Content Quality Audit ===")
    print(f"Total levels: {len(results)}")
    print(f"  Full interactive: {len(full)} ({100*len(full)//len(results)}%)")
    print(f"  Partial:          {len(partial)} ({100*len(partial)//len(results)}%)")
    print(f"  Bare:             {len(bare)} ({100*len(bare)//len(results)}%)")
    print()
    print(f"Levels with rich key_terms (>=3):  {sum(1 for r in results if r['rich_terms'] >= 3)}")
    print(f"Levels with order labs:            {sum(1 for r in results if r['has_order_lab'])}")
    print(f"Levels with select labs:           {sum(1 for r in results if r['has_select_lab'])}")
    print(f"Levels with repair labs:           {sum(1 for r in results if r['has_repair_lab'])}")
    print(f"Levels with debug missions:        {sum(1 for r in results if r['has_debug'])}")
    print(f"Levels with hints:                 {sum(1 for r in results if r['has_hints'])}")
    print(f"Levels test-out ready:             {sum(1 for r in results if r['test_out_ready'])}")

    if bare:
        print(f"\n=== Bare levels ({len(bare)}) ===")
        for r in bare[:10]:
            print(f"  {r['id']}: terms={r['rich_terms']}/{r['key_terms_total']}")
        if len(bare) > 10:
            print(f"  ... and {len(bare) - 10} more")


if __name__ == "__main__":
    main()
