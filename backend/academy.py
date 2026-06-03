"""Agentic Design Patterns Academy — special game modes.
Capstone Simulator: assemble an agent architecture from pattern blocks and get
deterministic validation. Dojo & Clinic banks are derived from content (engine).
No AI key required."""
from __future__ import annotations

from typing import Any, Dict, List

# Pattern blocks the user can drag into an architecture (Architecture Lab / Capstone)
BLOCKS: List[dict] = [
    {"id": "prompt-chain", "label": "Prompt Chain", "icon": "link"},
    {"id": "router", "label": "Router", "icon": "route"},
    {"id": "parallel", "label": "Parallel Worker", "icon": "split"},
    {"id": "reflection", "label": "Reflection Loop", "icon": "refresh-ccw"},
    {"id": "tool", "label": "Tool Call", "icon": "wrench"},
    {"id": "planner", "label": "Planner", "icon": "map"},
    {"id": "multi-agent", "label": "Multi-Agent Team", "icon": "users"},
    {"id": "memory", "label": "Memory Store", "icon": "database"},
    {"id": "rag", "label": "RAG Retriever", "icon": "search"},
    {"id": "human-gate", "label": "Human Approval Gate", "icon": "user-check"},
    {"id": "guardrail", "label": "Guardrail", "icon": "shield"},
    {"id": "evaluator", "label": "Evaluator", "icon": "clipboard-check"},
    {"id": "monitor", "label": "Monitor", "icon": "activity"},
    {"id": "prioritizer", "label": "Prioritizer", "icon": "list-ordered"},
]

# Capstone templates: each requires a set of pattern blocks to be 'production-shaped'.
CAPSTONES: List[dict] = [
    {
        "id": "support-workflow", "title": "AI Customer Support Workflow",
        "brief": "Classify a request, ground the answer, keep it safe, and confirm risky actions.",
        "required": ["router", "rag", "guardrail", "human-gate", "evaluator"],
        "nice": ["memory", "monitor"],
        "why": {"router": "classify billing/tech/cancellation",
                "rag": "ground answers in policy docs",
                "guardrail": "block unsafe or unsupported replies",
                "human-gate": "confirm refunds/cancellations",
                "evaluator": "score reply quality before sending"},
    },
    {
        "id": "research-assistant", "title": "Research Assistant",
        "brief": "Plan the research, retrieve grounded evidence, reflect, and ground every claim.",
        "required": ["planner", "rag", "reflection", "guardrail", "memory"],
        "nice": ["parallel", "evaluator"],
        "why": {"planner": "sequence the investigation",
                "rag": "retrieve grounded sources",
                "reflection": "critique and improve the draft",
                "guardrail": "reject unsupported claims",
                "memory": "retain findings across steps"},
    },
    {
        "id": "coding-agent", "title": "Coding Agent Workflow",
        "brief": "Plan, use tools, self-review, evaluate, and gate risky actions.",
        "required": ["planner", "tool", "reflection", "evaluator", "human-gate"],
        "nice": ["memory", "guardrail"],
        "why": {"planner": "break the task into steps",
                "tool": "run code / call APIs",
                "reflection": "review and fix its own code",
                "evaluator": "score against tests/rubric",
                "human-gate": "approve risky changes"},
    },
    {
        "id": "risk-review", "title": "Risk Review Agent",
        "brief": "Ground decisions in evidence, enforce policy, require human sign-off, and monitor.",
        "required": ["rag", "guardrail", "human-gate", "evaluator", "monitor"],
        "nice": ["memory", "prioritizer"],
        "why": {"rag": "ground on policy/regulation",
                "guardrail": "enforce compliance",
                "human-gate": "human sign-off on decisions",
                "evaluator": "score decisions against criteria",
                "monitor": "watch for drift in production"},
    },
    {
        "id": "automation-team", "title": "Multi-Agent Business Automation Team",
        "brief": "A coordinated team: plan, do specialized work, review, and stay safe.",
        "required": ["planner", "multi-agent", "tool", "guardrail", "evaluator"],
        "nice": ["memory", "monitor", "human-gate"],
        "why": {"planner": "coordinate the workflow",
                "multi-agent": "specialist agents (research/build/review)",
                "tool": "take real actions",
                "guardrail": "keep actions safe",
                "evaluator": "quality-check the output"},
    },
]
CAPSTONE_MAP = {c["id"]: c for c in CAPSTONES}


def validate_capstone(capstone_id: str, selected: List[str]) -> dict:
    c = CAPSTONE_MAP.get(capstone_id)
    if not c:
        return {"ok": False, "passed": False, "feedback": "Unknown capstone."}
    sel = set(selected or [])
    required = set(c["required"])
    missing = required - sel
    extra = sel - required - set(c["nice"])
    covered = required & sel
    score = round(100 * len(covered) / len(required)) if required else 0
    passed = len(missing) == 0
    feedback = []
    label = {b["id"]: b["label"] for b in BLOCKS}
    for m in missing:
        feedback.append(f"Missing {label.get(m, m)} — {c['why'].get(m, 'needed for this system')}.")
    if extra:
        feedback.append("Extra blocks add risk/cost without need: " + ", ".join(label.get(e, e) for e in extra) + ".")
    if passed and not feedback:
        feedback.append("Production-shaped! Every essential pattern is in place.")
    return {
        "ok": True, "passed": passed, "score": score,
        "missing": list(missing), "covered": list(covered),
        "xp": 120 if passed else max(10, score // 2),
        "feedback": feedback,
    }
