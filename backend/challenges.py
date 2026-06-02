"""Challenge Arena, Agent Lab simulation, deterministic validators and badges.
Everything works WITHOUT any API key (mocked). Optional live mode uses DeepSeek
if DEEPSEEK_API_KEY is set, but the game never requires it."""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------- Challenges
# Each challenge is deterministic and validated server-side. UI renders by `kind`.
CHALLENGES: List[dict] = [
    {
        "id": "fix-bad-prompt",
        "skill": "prompt-design",
        "title": "Repair the Broken Prompt",
        "scenario": "This prompt keeps producing junk. A reliable prompt needs four pillars. Select every pillar that is MISSING.",
        "broken_state": "\"Summarize this.\"",
        "kind": "select-multiple",
        "options": ["Role / persona", "Clear task", "Constraints", "Output format", "A random emoji"],
        "answer": [0, 2, 3],
        "hints": ["A bare verb isn't a task spec.", "How long? What structure? Who is speaking?"],
        "explain": "Strong prompts declare a role, a precise task, constraints, and an explicit output format. 'Summarize this' has only a vague task.",
        "xp": 40,
    },
    {
        "id": "route-task",
        "skill": "agent-routing",
        "title": "Route the Request",
        "scenario": "A user writes: 'My invoice charged me twice, refund one.' Which specialist agent should the router pick?",
        "broken_state": "Router is sending everything to the FAQ bot.",
        "kind": "select-one",
        "options": ["FAQ Bot", "Billing & Refunds Agent", "Marketing Copywriter", "Image Generator"],
        "answer": 1,
        "hints": ["Match intent to capability.", "This is a money + account action."],
        "explain": "Refund/billing intents must route to the Billing agent that can verify the charge and trigger a (confirmed) refund.",
        "xp": 35,
    },
    {
        "id": "add-missing-tool",
        "skill": "tool-use",
        "title": "Equip the Right Tool",
        "scenario": "The agent must answer 'What is 18.5% of $2,430?' but keeps hallucinating numbers. Which tool fixes this?",
        "broken_state": "Agent has: [web_search, send_email]",
        "kind": "select-one",
        "options": ["calculator", "image_generator", "calendar", "translator"],
        "answer": 0,
        "hints": ["LLMs are unreliable at exact arithmetic.", "Offload the math."],
        "explain": "Exact arithmetic should be delegated to a calculator tool instead of trusting token prediction.",
        "xp": 30,
    },
    {
        "id": "repair-json",
        "skill": "debugging",
        "title": "Repair Malformed JSON",
        "scenario": "Downstream parsing crashes. Fix the JSON so it is valid and keeps keys: name, tools, safe.",
        "broken_state": "{ 'name': 'router', tools: [search, calc], safe: True, }",
        "kind": "edit-json",
        "required_keys": ["name", "tools", "safe"],
        "hints": ["JSON uses double quotes.", "No trailing commas. true/false are lowercase.", "Strings inside arrays need quotes too."],
        "explain": "Valid JSON needs double-quoted keys/strings, lowercase booleans, and no trailing commas.",
        "xp": 45,
    },
    {
        "id": "stop-hallucination",
        "skill": "safety",
        "title": "Stop the Hallucination",
        "scenario": "Asked for a citation it doesn't have, which response is the SAFE one to ship?",
        "broken_state": "Model wants to sound confident.",
        "kind": "select-one",
        "options": [
            "Invent a plausible-looking citation and DOI.",
            "Say it cannot verify a source and offer to search.",
            "Answer confidently with no source.",
            "Refuse and end the conversation.",
        ],
        "answer": 1,
        "hints": ["Confidence is not correctness.", "Admitting uncertainty beats fabricating."],
        "explain": "When grounding is missing, the model should disclose uncertainty and offer a retrieval step rather than fabricate.",
        "xp": 40,
    },
    {
        "id": "add-safety-check",
        "skill": "safety",
        "title": "Gate the Dangerous Action",
        "scenario": "An agent wants to run `rm -rf /data` to 'clean up'. What must happen first?",
        "broken_state": "autonomy = full, confirmation = off",
        "kind": "select-one",
        "options": [
            "Execute immediately to save time",
            "Require explicit human confirmation before any destructive action",
            "Log it and run anyway",
            "Retry three times",
        ],
        "answer": 1,
        "hints": ["Destructive + irreversible = human in the loop.", "Confirm before external side effects."],
        "explain": "Irreversible or destructive actions require a human confirmation gate. Autonomy must be bounded.",
        "xp": 40,
    },
    {
        "id": "add-eval-criteria",
        "skill": "evaluation",
        "title": "Design the Eval",
        "scenario": "You shipped a support-reply agent. Select every criterion a good eval should score.",
        "broken_state": "Current eval: 'looks good to me'",
        "kind": "select-multiple",
        "options": ["Factual accuracy", "Follows required format", "Safety / policy compliance", "Resolves the user's intent", "Uses the most words"],
        "answer": [0, 1, 2, 3],
        "hints": ["Vibes are not metrics.", "Wordiness is not a quality signal."],
        "explain": "Evals should measure accuracy, format compliance, safety, and task resolution — never raw length.",
        "xp": 40,
    },
    {
        "id": "fix-memory-misuse",
        "skill": "memory",
        "title": "Fix the Memory Leak (of Context)",
        "scenario": "An agent pastes the ENTIRE chat history into every call and blows the context window. Best fix?",
        "broken_state": "memory = dump everything, every turn",
        "kind": "select-one",
        "options": [
            "Increase temperature",
            "Summarize older turns and retrieve only relevant memories",
            "Delete all memory each turn",
            "Add more tools",
        ],
        "answer": 1,
        "hints": ["Not all history is relevant now.", "Summarize + retrieve."],
        "explain": "Use rolling summaries plus relevance-based retrieval instead of dumping raw history every call.",
        "xp": 35,
    },
    {
        "id": "prevent-autonomous",
        "skill": "safety",
        "title": "Bound the Autonomy",
        "scenario": "A research agent can loop forever spawning sub-tasks. What prevents runaway behavior?",
        "broken_state": "max_steps = ∞",
        "kind": "select-multiple",
        "options": ["Max-iteration / step budget", "Cost ceiling", "Human approval for external actions", "Faster GPU"],
        "answer": [0, 1, 2],
        "hints": ["Bound loops, money, and side effects.", "Hardware doesn't bound behavior."],
        "explain": "Runaway autonomy is bounded by step limits, cost ceilings, and human approval gates — not faster hardware.",
        "xp": 45,
    },
]

CHALLENGE_MAP = {c["id"]: c for c in CHALLENGES}


def public_challenge(c: dict) -> dict:
    return {k: v for k, v in c.items() if k not in ("answer", "required_keys", "explain")}


def validate_challenge(challenge_id: str, answer: Any) -> dict:
    c = CHALLENGE_MAP.get(challenge_id)
    if not c:
        return {"ok": False, "passed": False, "feedback": "Unknown challenge."}
    kind = c["kind"]
    passed = False
    feedback = ""
    if kind == "select-one":
        passed = answer == c["answer"]
    elif kind == "select-multiple":
        try:
            passed = sorted(answer) == sorted(c["answer"])
        except Exception:
            passed = False
    elif kind == "edit-json":
        try:
            parsed = json.loads(answer if isinstance(answer, str) else json.dumps(answer))
            passed = all(k in parsed for k in c["required_keys"])
            if not passed:
                feedback = "Valid JSON, but missing required keys: " + ", ".join(c["required_keys"])
        except Exception as e:
            passed = False
            feedback = f"Not valid JSON yet: {str(e)[:80]}"
    return {
        "ok": True,
        "passed": passed,
        "xp": c["xp"] if passed else 0,
        "explain": c["explain"],
        "feedback": ("Solved! " + c["explain"]) if passed else (feedback or "Not quite — check the hints and retry. No penalty."),
    }


# ---------------------------------------------------------------- Agent Lab
LAB_SCENARIOS: List[dict] = [
    {
        "id": "calc-helper",
        "title": "The Number Cruncher",
        "brief": "Build an agent that answers exact math questions reliably and only acts when confident.",
        "task": "What is the compound interest on $5,000 at 6% for 3 years?",
        "required_tools": ["calculator"],
        "available_tools": ["calculator", "web_search", "send_email", "calendar", "code_runner"],
        "needs_memory": False,
        "needs_format": True,
    },
    {
        "id": "support-agent",
        "title": "The Support Triage",
        "brief": "Build a support agent that retrieves context before answering and confirms before refunds.",
        "task": "Customer: 'I was double charged, please refund one.'",
        "required_tools": ["knowledge_base", "billing_api"],
        "available_tools": ["knowledge_base", "billing_api", "calculator", "image_generator", "web_search"],
        "needs_memory": True,
        "needs_format": True,
    },
    {
        "id": "research-agent",
        "title": "The Bounded Researcher",
        "brief": "Build a research agent that searches, remembers findings, and never loops forever.",
        "task": "Summarize the top 3 risks of autonomous agents with sources.",
        "required_tools": ["web_search"],
        "available_tools": ["web_search", "calculator", "memory_store", "send_email", "code_runner"],
        "needs_memory": True,
        "needs_format": True,
    },
]
LAB_MAP = {s["id"]: s for s in LAB_SCENARIOS}

_ROLE_RE = re.compile(r"\b(you are|act as|role|assistant|agent|specialist|expert)\b", re.I)
_TASK_RE = re.compile(r"\b(task|goal|answer|help|do|produce|generate|summari|classif|resolve)\b", re.I)
_CONSTRAINT_RE = re.compile(r"\b(only|never|always|must|do not|don't|limit|max|confirm|verify|cite)\b", re.I)
_FORMAT_RE = re.compile(r"\b(json|format|bullet|list|step|markdown|table|schema|structure|output)\b", re.I)


def simulate_agent(build: dict, scenario_id: Optional[str]) -> dict:
    """Deterministic, mocked agent run with scored validation + a fake trace."""
    scenario = LAB_MAP.get(scenario_id) if scenario_id else None
    prompt = build.get("prompt", "") or ""
    tools = [t.lower() for t in build.get("tools", [])]
    memory = build.get("memory_config", "none")

    checks = []

    has_role = bool(_ROLE_RE.search(prompt))
    has_task = bool(_TASK_RE.search(prompt))
    has_constraints = bool(_CONSTRAINT_RE.search(prompt))
    has_format = bool(_FORMAT_RE.search(prompt))
    checks.append({"label": "Prompt declares a role", "ok": has_role})
    checks.append({"label": "Prompt states a task", "ok": has_task})
    checks.append({"label": "Prompt sets constraints", "ok": has_constraints})
    checks.append({"label": "Prompt specifies output format", "ok": has_format})

    if scenario:
        missing = [t for t in scenario["required_tools"] if t not in tools]
        checks.append({
            "label": f"Has required tools ({', '.join(scenario['required_tools'])})",
            "ok": len(missing) == 0,
            "detail": ("Missing: " + ", ".join(missing)) if missing else "All present",
        })
        if scenario["needs_memory"]:
            checks.append({"label": "Memory configured for multi-turn context", "ok": memory not in ("none", "")})
    else:
        checks.append({"label": "At least one tool equipped", "ok": len(tools) > 0})

    passed = sum(1 for c in checks if c["ok"])
    total = len(checks)
    score = round(100 * passed / total) if total else 0
    verdict = "pass" if score >= 80 else ("warn" if score >= 50 else "fail")

    # Build a believable, MOCKED execution trace
    trace = [
        {"step": "observe", "text": f"Received task: {scenario['task'] if scenario else build.get('name','custom task')}"},
        {"step": "think", "text": "Decomposing request and selecting a tool..." if tools else "No tools available — answering directly."},
    ]
    if tools:
        trace.append({"step": "act", "text": f"Invoking tool `{tools[0]}` with parsed arguments."})
        trace.append({"step": "observe", "text": f"Tool `{tools[0]}` returned a result (mocked)."})
    if scenario and any(t in ("billing_api",) for t in tools):
        trace.append({"step": "guard", "text": "Destructive/billing action detected — requesting human confirmation before proceeding."})
    trace.append({"step": "answer", "text": "Returning a structured response." if has_format else "Returning a free-text response."})

    feedback = []
    if not has_role: feedback.append("Add a role line (e.g. 'You are a billing specialist...').")
    if not has_constraints: feedback.append("Add constraints (e.g. 'Only refund after verifying the charge').")
    if not has_format: feedback.append("Specify an output format (e.g. 'Reply as JSON with fields ...').")
    if scenario:
        missing = [t for t in scenario["required_tools"] if t not in tools]
        if missing: feedback.append("Equip required tools: " + ", ".join(missing) + ".")
        if scenario["needs_memory"] and memory in ("none", ""):
            feedback.append("Turn on memory so the agent keeps multi-turn context.")
    if not feedback:
        feedback.append("Clean build. This agent is production-shaped.")

    return {
        "mode": "mock",
        "score": score,
        "verdict": verdict,
        "checks": checks,
        "trace": trace,
        "output": _mock_output(scenario, has_format),
        "feedback": feedback,
        "xp": 50 if verdict == "pass" else (20 if verdict == "warn" else 5),
    }


def _mock_output(scenario: Optional[dict], structured: bool) -> str:
    if scenario and scenario["id"] == "support-agent":
        body = {
            "intent": "refund_duplicate_charge",
            "action": "await_human_confirmation",
            "message": "I see two identical charges. I can refund one once you confirm — shall I proceed?",
        }
    elif scenario and scenario["id"] == "calc-helper":
        body = {"answer": "$5,955.08", "tool_used": "calculator", "confidence": "high"}
    else:
        body = {"summary": "3 key risks identified", "sources": ["mocked-source-1", "mocked-source-2"]}
    return json.dumps(body, indent=2) if structured else "; ".join(f"{k}: {v}" for k, v in body.items())


async def live_agent(build: dict, scenario_id: Optional[str]) -> Optional[dict]:
    """Optional DeepSeek (OpenAI-compatible) live run. Returns None if unavailable."""
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        return None
    import httpx
    base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    scenario = LAB_MAP.get(scenario_id) if scenario_id else None
    task = scenario["task"] if scenario else build.get("name", "Help the user.")
    system = build.get("prompt") or "You are a helpful AI engineering agent."
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": task},
                ], "temperature": 0.3, "max_tokens": 400},
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return {"mode": "live-error", "error": str(e)[:160]}
    return {"mode": "live", "output": content}


# ---------------------------------------------------------------- Badges
BADGES: List[dict] = [
    {"id": "first-spark", "title": "First Spark", "description": "Complete your first mission.", "icon": "sparkles"},
    {"id": "level-cleared", "title": "Level Cleared", "description": "Finish your first full level.", "icon": "flag"},
    {"id": "boss-slayer", "title": "Boss Slayer", "description": "Defeat your first boss.", "icon": "swords"},
    {"id": "streak-3", "title": "On Fire", "description": "Hit a 3-day streak.", "icon": "flame"},
    {"id": "streak-7", "title": "Unstoppable", "description": "Hit a 7-day streak.", "icon": "zap"},
    {"id": "arena-fighter", "title": "Arena Fighter", "description": "Solve 3 arena challenges.", "icon": "shield"},
    {"id": "agent-architect", "title": "Agent Architect", "description": "Save your first agent build.", "icon": "bot"},
    {"id": "memory-keeper", "title": "Memory Keeper", "description": "Review 10 cards.", "icon": "brain"},
    {"id": "xp-1000", "title": "Rising Forgemaster", "description": "Earn 1,000 total XP.", "icon": "trophy"},
    {"id": "world-conqueror", "title": "World Conqueror", "description": "Complete every level in a world.", "icon": "crown"},
]
BADGE_MAP = {b["id"]: b for b in BADGES}
