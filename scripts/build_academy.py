#!/usr/bin/env python3
"""Build 'Agentic Design Patterns Academy' — a new interactive learning path.

Source (attribution only, NOT reproduced): "Agentic Design Patterns: A Hands-On
Guide to Building Intelligent Systems" by Antonio Gulli. All content here is an
original, transformed teaching layer (summaries, drills, labs, challenges) — no
verbatim text from the book.

Output: backend/academy_content.json
"""
import json
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
XP = {"briefing": 20, "mentalmodel": 25, "drill": 40, "lab": 55, "debug": 45, "boss": 80}

GROUPS = [
    {"id": "foundations", "name": "Foundations", "patterns": [1, 2, 3, 5, 6]},
    {"id": "orchestration", "name": "Orchestration", "patterns": [4, 7, 10, 15, 17]},
    {"id": "reliability", "name": "Reliability & Safety", "patterns": [8, 12, 13, 18, 19]},
    {"id": "advanced", "name": "Knowledge & Advanced Systems", "patterns": [9, 11, 14, 16, 20, 21]},
]

# ---- Curated, original teaching content per pattern --------------------------
# Each: name, metaphor, icon, solves, use_when, avoid_when, example, mistake,
# model_points[], drill{scenario, options[{text,correct,feedback}]}, boss[q],
# review[{prompt,answer}], optional lab{}, optional debug{}.
P = {}

P[1] = {
 "name": "Prompt Chaining", "metaphor": "An assembly line", "icon": "link",
 "solves": "Big tasks that one prompt does badly — break them into ordered steps where each output feeds the next.",
 "use_when": ["A task has clear sequential stages", "Each stage needs a focused instruction", "You want to inspect/validate between steps"],
 "avoid_when": ["The task is a single simple ask", "Stages are independent (use Parallelization)"],
 "example": "Summarize a doc → extract the action items → format them as JSON.",
 "mistake": "Letting step 1's messy output flow into step 2 without a defined structure.",
 "model_points": ["Output of each step is the input of the next", "Each link has one job and one clear format",
                  "A broken link breaks the chain — validate between steps"],
 "drill": {"scenario": "You must turn a long meeting transcript into a clean JSON list of decisions with owners and dates.",
           "options": [
             {"text": "Prompt Chaining (summarize → extract → format)", "correct": True,
              "feedback": "Right — sequential stages, each feeding the next, with a structured final step."},
             {"text": "Parallelization", "correct": False,
              "feedback": "These steps depend on each other; you can't extract before you summarize."},
             {"text": "Routing", "correct": False,
              "feedback": "There's only one task type here, nothing to route."}]},
 "boss": [
   {"q": "In a chain, what makes a link reliable?", "correct": "Its output has a defined, validated structure",
    "wrong": ["It uses the highest temperature", "It skips formatting", "It calls a random tool"],
    "explain": "Defined I/O contracts between steps keep the chain from drifting."},
   {"q": "A 3-stage pipeline keeps producing malformed final JSON. Best fix?",
    "correct": "Add a validate/format step and reject malformed intermediate output",
    "wrong": ["Merge all steps into one prompt", "Increase the model size only", "Remove the extract step"],
    "explain": "Validation between links catches errors before they cascade."}],
 "review": [
   {"prompt": "What problem does Prompt Chaining solve?", "answer": "It breaks a complex task into ordered steps, each output feeding the next."},
   {"prompt": "When should you NOT use Prompt Chaining?", "answer": "When the task is a single simple ask, or when subtasks are independent (use Parallelization)."},
   {"prompt": "Prompt Chaining failure mode?", "answer": "Unstructured output from one step corrupts the next — links must have defined I/O."},
   {"prompt": "Pattern often confused with Prompt Chaining?", "answer": "Parallelization — but chaining is sequential & dependent, parallelization is independent."},
   {"prompt": "What should you validate in a chain?", "answer": "The structure of each intermediate output before it feeds the next step."},
   {"prompt": "Real-world use of Prompt Chaining?", "answer": "Transcript → summary → action-item extraction → formatted JSON."}],
 "lab": {"kind": "order", "goal": "Assemble a content pipeline that turns a raw document into validated JSON.",
         "prompt": "Tap the steps in the correct order to build the chain.",
         "steps": [{"id": "fmt", "label": "Format & validate as JSON"},
                   {"id": "sum", "label": "Summarize the raw document"},
                   {"id": "ext", "label": "Extract the action items"}],
         "correct_order": ["sum", "ext", "fmt"],
         "success": "Summarize → Extract → Format. Each step feeds the next; the last one enforces structure."},
 "debug": {"scenario": "An agent pipeline outputs free text instead of the JSON the next system needs.",
           "broken": "step3 = 'Write a nice summary of the items.'",
           "options": ["Add an explicit output-format/schema instruction and a validation step",
                       "Raise the temperature so it's more creative",
                       "Delete the extraction step",
                       "Run the same prompt twice"],
           "answer": 0, "failure_mode": "Missing structured output",
           "explain": "The final link must declare its schema and validate — otherwise downstream parsing breaks."},
}

P[2] = {
 "name": "Routing", "metaphor": "A traffic controller", "icon": "route",
 "solves": "Many possible request types — send each to the specialist best equipped to handle it.",
 "use_when": ["Requests fall into distinct categories", "Different handlers/tools fit different intents"],
 "avoid_when": ["Every request is the same kind", "There's only one capable handler"],
 "example": "A support message could be billing, technical, or cancellation — route to the right agent.",
 "mistake": "No fallback route, so unknown intents crash or get mishandled.",
 "model_points": ["Classify the intent first", "Map each intent to a specialist", "Always have a default/fallback route"],
 "drill": {"scenario": "A customer request could be billing, technical support, or a cancellation.",
           "options": [
             {"text": "Routing", "correct": True, "feedback": "Right — classify intent, dispatch to the matching specialist, with a fallback."},
             {"text": "Prompt Chaining", "correct": False, "feedback": "Chaining runs fixed stages; it can't pick between different handlers."},
             {"text": "RAG", "correct": False, "feedback": "Retrieval helps answer, but doesn't decide which department handles the request."}]},
 "boss": [
   {"q": "What must every router include?", "correct": "A fallback/default route for unknown intents",
    "wrong": ["A calculator", "A higher temperature", "A memory store"],
    "explain": "Unclassified intents need a safe default instead of failing."},
   {"q": "A router sends refunds to the FAQ bot. Root cause?", "correct": "Intent classification is wrong/too coarse",
    "wrong": ["Too many tools", "The FAQ bot is too smart", "Memory is full"],
    "explain": "Routing quality depends on accurate intent detection."}],
 "review": [
   {"prompt": "What problem does Routing solve?", "answer": "Directing each request to the specialist handler best suited to its intent."},
   {"prompt": "When NOT to use Routing?", "answer": "When all requests are the same kind or only one handler exists."},
   {"prompt": "Routing failure mode?", "answer": "No fallback route, or misclassified intent sending work to the wrong handler."},
   {"prompt": "What must a router always have?", "answer": "A default/fallback route for unknown or low-confidence intents."},
   {"prompt": "Confused with Routing?", "answer": "Prompt Chaining — but chaining is fixed stages, routing chooses among handlers."},
   {"prompt": "Real-world Routing example?", "answer": "Triaging a support request into billing / technical / cancellation."}],
}

P[3] = {
 "name": "Parallelization", "metaphor": "A task swarm", "icon": "split",
 "solves": "Independent subtasks that waste time if run one-by-one — fan them out, then merge.",
 "use_when": ["Subtasks don't depend on each other", "Latency matters", "Results can be merged"],
 "avoid_when": ["Steps depend on previous output (use Chaining)", "Order matters"],
 "example": "Research 5 competitors at once, then merge into one comparison table.",
 "mistake": "Parallelizing dependent steps, so later tasks use stale/missing inputs.",
 "model_points": ["Split into independent units", "Run them concurrently", "Merge results into one coherent answer"],
 "drill": {"scenario": "You need to gather facts about 6 unrelated companies and combine them into a report.",
           "options": [
             {"text": "Parallelization", "correct": True, "feedback": "Right — independent lookups fan out, then a merge step combines them."},
             {"text": "Prompt Chaining", "correct": False, "feedback": "These lookups don't depend on each other — chaining would be needlessly slow."},
             {"text": "Reflection", "correct": False, "feedback": "Reflection improves one answer; it doesn't gather parallel data."}]},
 "boss": [
   {"q": "Parallelization requires subtasks to be…", "correct": "independent of each other",
    "wrong": ["sequential", "all identical", "human-approved"], "explain": "Independence is what makes concurrency safe."},
   {"q": "What step is essential after fan-out?", "correct": "A merge/aggregate step",
    "wrong": ["A delete step", "A higher temperature", "A second router"], "explain": "Results must be combined coherently."}],
 "review": [
   {"prompt": "What problem does Parallelization solve?", "answer": "Running independent subtasks concurrently to cut latency, then merging results."},
   {"prompt": "When NOT to parallelize?", "answer": "When steps depend on each other or order matters — use Prompt Chaining."},
   {"prompt": "Parallelization failure mode?", "answer": "Parallelizing dependent steps so later work uses missing/stale inputs."},
   {"prompt": "Essential final step?", "answer": "A merge/aggregation step that combines the parallel results."},
   {"prompt": "Confused with Parallelization?", "answer": "Prompt Chaining — chaining is dependent & sequential."},
   {"prompt": "Real-world Parallelization example?", "answer": "Researching multiple sources at once and merging into one report."}],
}

P[5] = {
 "name": "Tool Use", "metaphor": "An agent reaching outside itself", "icon": "wrench",
 "solves": "LLMs can't reliably compute, fetch live data, or act — give them tools and let them decide when to call.",
 "use_when": ["You need exact math, live data, or real actions", "The model alone would hallucinate the answer"],
 "avoid_when": ["The model already knows reliably", "A tool call adds risk with no benefit"],
 "example": "Use a calculator for exact arithmetic instead of trusting token prediction.",
 "mistake": "Calling tools unnecessarily, or ignoring/failing to incorporate the tool's result.",
 "model_points": ["Decide IF a tool is needed", "Pick the RIGHT tool and arguments", "Feed the result back into the answer"],
 "drill": {"scenario": "The agent must answer 'What's 18.5% of $2,430?' but keeps inventing numbers.",
           "options": [
             {"text": "Tool Use (calculator)", "correct": True, "feedback": "Right — offload exact arithmetic to a calculator tool and use its result."},
             {"text": "Reflection", "correct": False, "feedback": "Self-critique won't make token prediction good at exact math."},
             {"text": "Memory", "correct": False, "feedback": "Remembering won't compute the number reliably."}]},
 "boss": [
   {"q": "When should an agent call a tool?", "correct": "Only when the model can't reliably do it alone",
    "wrong": ["On every single turn", "Never", "Only for greetings"], "explain": "Tools add capability AND risk — call them with purpose."},
   {"q": "After a tool returns, the agent must…", "correct": "incorporate the result into its answer",
    "wrong": ["ignore it", "call the same tool again", "increase temperature"], "explain": "An unused tool result is wasted (or unsafe)."}],
 "review": [
   {"prompt": "What problem does Tool Use solve?", "answer": "Lets an agent compute, fetch live data, or act by calling external functions instead of guessing."},
   {"prompt": "When NOT to use a tool?", "answer": "When the model already knows reliably, or the call adds risk with no benefit."},
   {"prompt": "Tool Use failure mode?", "answer": "Unnecessary calls, wrong tool/args, or ignoring the returned result."},
   {"prompt": "What must happen after a tool runs?", "answer": "The result must be incorporated into the agent's response."},
   {"prompt": "Safety concern with Tool Use?", "answer": "Tools can take real actions — gate risky ones behind confirmation."},
   {"prompt": "Real-world Tool Use example?", "answer": "Calling a calculator for exact math or an API for live prices."}],
 "lab": {"kind": "select", "goal": "Equip an agent that answers exact financial questions safely.",
         "prompt": "Select ONLY the components this agent truly needs.",
         "blocks": [{"id": "calc", "label": "Calculator tool"}, {"id": "guard", "label": "Confirmation gate for risky actions"},
                    {"id": "img", "label": "Image generator"}, {"id": "incorp", "label": "Step that uses the tool's result"},
                    {"id": "spam", "label": "Mass email sender"}],
         "required": ["calc", "incorp", "guard"],
         "success": "Calculator + a step that uses its output + a confirmation gate. The image generator and mass-mailer are needless risk."},
 "debug": {"scenario": "An agent calls a web-search tool for every message, even 'hello', burning cost and adding latency.",
           "broken": "policy = always call web_search before replying",
           "options": ["Call the tool only when the query actually needs external/live info",
                       "Add a second search tool", "Increase max tokens", "Remove the answer step"],
           "answer": 0, "failure_mode": "Tool called unnecessarily",
           "explain": "Tool use should be conditional on need — not a reflex on every turn."},
}

P[6] = {
 "name": "Planning", "metaphor": "A map before the journey", "icon": "map",
 "solves": "Multi-step goals where acting blindly fails — make a plan, then execute and track it.",
 "use_when": ["The goal needs several coordinated steps", "You want to track progress and adapt"],
 "avoid_when": ["A single action solves it", "The environment changes faster than you can plan"],
 "example": "Plan: gather data → analyze → draft → review → publish, executing each in order.",
 "mistake": "Making a plan but never tracking execution state, so the agent repeats or skips steps.",
 "model_points": ["Decompose the goal into ordered steps", "Execute step by step", "Track state and re-plan on failure"],
 "drill": {"scenario": "An agent must organize a multi-step product launch with dependencies.",
           "options": [
             {"text": "Planning", "correct": True, "feedback": "Right — decompose into ordered steps, execute, and track state."},
             {"text": "Parallelization", "correct": False, "feedback": "There are dependencies, so pure fan-out would break order."},
             {"text": "Tool Use", "correct": False, "feedback": "Tools help execute steps, but you still need a plan to sequence them."}]},
 "boss": [
   {"q": "A good plan tracks…", "correct": "execution state across ordered steps",
    "wrong": ["nothing", "only the final answer", "the temperature"], "explain": "State tracking prevents repeats/skips and enables re-planning."},
   {"q": "When a step fails, the planner should…", "correct": "re-plan or trigger a fallback",
    "wrong": ["halt forever", "ignore it", "delete the goal"], "explain": "Adaptation on failure is core to planning."}],
 "review": [
   {"prompt": "What problem does Planning solve?", "answer": "Coordinating multi-step goals by decomposing, executing, and tracking progress."},
   {"prompt": "When NOT to plan?", "answer": "When one action solves it, or the world changes faster than plans hold."},
   {"prompt": "Planning failure mode?", "answer": "No execution-state tracking — the agent repeats or skips steps."},
   {"prompt": "What should a planner do on failure?", "answer": "Re-plan or trigger a fallback."},
   {"prompt": "Confused with Planning?", "answer": "Plain Tool Use — tools execute steps, planning sequences them."},
   {"prompt": "Real-world Planning example?", "answer": "An agent sequencing gather → analyze → draft → review → publish."}],
}

P[4] = {
 "name": "Reflection", "metaphor": "A self-review loop", "icon": "refresh-ccw",
 "solves": "First drafts are often wrong — have the agent critique and improve its own output.",
 "use_when": ["Quality matters more than speed", "Errors are catchable by self-review"],
 "avoid_when": ["Latency/cost is critical", "The task is trivial"],
 "example": "Draft an answer → critique it for gaps → produce an improved version.",
 "mistake": "A critique step that rubber-stamps the draft without finding real weaknesses.",
 "model_points": ["Produce a first draft", "Critique it against criteria", "Revise to fix the identified weaknesses"],
 "drill": {"scenario": "An agent's first-pass code reviews keep missing edge cases.",
           "options": [
             {"text": "Reflection", "correct": True, "feedback": "Right — add a critique-then-revise loop to catch what the first pass missed."},
             {"text": "Routing", "correct": False, "feedback": "There's one task; nothing to route."},
             {"text": "Parallelization", "correct": False, "feedback": "Running more copies in parallel won't add self-critique."}]},
 "boss": [
   {"q": "A useful reflection step must…", "correct": "identify at least one concrete weakness",
    "wrong": ["always approve the draft", "increase length", "call a tool"], "explain": "Reflection that finds nothing adds no value."},
   {"q": "Reflection trades off…", "correct": "extra latency/cost for higher quality",
    "wrong": ["safety for speed", "memory for tools", "nothing at all"], "explain": "Self-review costs time but improves results."}],
 "review": [
   {"prompt": "What problem does Reflection solve?", "answer": "Improving output quality by having the agent critique and revise its own work."},
   {"prompt": "When NOT to use Reflection?", "answer": "When latency/cost is critical or the task is trivial."},
   {"prompt": "Reflection failure mode?", "answer": "A critique that rubber-stamps the draft without finding real weaknesses."},
   {"prompt": "What must the critique step do?", "answer": "Identify at least one concrete weakness to fix."},
   {"prompt": "Reflection trade-off?", "answer": "More latency/cost in exchange for higher quality."},
   {"prompt": "Real-world Reflection example?", "answer": "Draft → self-critique for gaps → improved final answer."}],
}

P[7] = {
 "name": "Multi-Agent Collaboration", "metaphor": "A specialist team", "icon": "users",
 "solves": "One generalist agent struggles with complex work — split roles across specialists that collaborate.",
 "use_when": ["Work has distinct specialties", "A coordinator can manage handoffs"],
 "avoid_when": ["A single agent suffices", "Coordination overhead outweighs benefits"],
 "example": "Planner, researcher, builder, reviewer, and safety-checker agents working together.",
 "mistake": "Unclear handoffs, so agents duplicate work or drop tasks between them.",
 "model_points": ["Give each agent a distinct role", "Define clear handoffs", "Include a coordinator/reviewer"],
 "drill": {"scenario": "A complex report needs research, drafting, fact-checking, and a final safety review.",
           "options": [
             {"text": "Multi-Agent Collaboration", "correct": True, "feedback": "Right — distinct specialist roles with clear handoffs and a reviewer."},
             {"text": "Reflection", "correct": False, "feedback": "Reflection is one agent self-reviewing, not a team of specialists."},
             {"text": "Routing", "correct": False, "feedback": "Routing picks ONE handler; this needs several working together."}]},
 "boss": [
   {"q": "A healthy multi-agent team needs…", "correct": "distinct roles and clear handoffs",
    "wrong": ["identical agents", "no coordinator", "one giant prompt"], "explain": "Role clarity + handoffs prevent dropped/duplicated work."},
   {"q": "Who guards quality in a team?", "correct": "A reviewer/coordinator agent",
    "wrong": ["nobody", "the user only", "the calculator"], "explain": "A coordinator or reviewer keeps the team aligned."}],
 "review": [
   {"prompt": "What problem does Multi-Agent solve?", "answer": "Splitting complex work across specialist agents that collaborate."},
   {"prompt": "When NOT to go multi-agent?", "answer": "When one agent suffices or coordination overhead outweighs benefits."},
   {"prompt": "Multi-Agent failure mode?", "answer": "Unclear handoffs causing duplicated or dropped tasks."},
   {"prompt": "What roles keep a team healthy?", "answer": "Distinct specialists plus a coordinator/reviewer."},
   {"prompt": "Confused with Multi-Agent?", "answer": "Reflection (one agent) and Routing (one handler) — multi-agent is a collaborating team."},
   {"prompt": "Real-world Multi-Agent example?", "answer": "Planner + researcher + builder + reviewer + safety checker."}],
}

P[10] = {
 "name": "Model Context Protocol (MCP)", "metaphor": "A universal power outlet for tools", "icon": "plug",
 "solves": "Every tool integration is bespoke — MCP is a standard way for agents to discover and call tools/data.",
 "use_when": ["You want portable, standardized tool/data access", "Multiple agents share the same tools"],
 "avoid_when": ["A single hardcoded tool is enough", "You need a one-off prototype"],
 "example": "An agent connects to an MCP server to use any registered tool without custom glue code.",
 "mistake": "Treating MCP as 'just another API' and skipping its discovery/capability contract.",
 "model_points": ["A standard protocol, not a single API", "Agents discover capabilities", "Tools/data become plug-and-play"],
 "drill": {"scenario": "You want many agents to share the same growing set of tools without rewriting integrations.",
           "options": [
             {"text": "Model Context Protocol (MCP)", "correct": True, "feedback": "Right — a standard interface so tools are discoverable and portable."},
             {"text": "Prompt Chaining", "correct": False, "feedback": "Chaining sequences prompts; it doesn't standardize tool access."},
             {"text": "Memory", "correct": False, "feedback": "Memory stores context, not a tool-integration standard."}]},
 "boss": [
   {"q": "MCP is best described as…", "correct": "a standard protocol for tool/data access",
    "wrong": ["a single vendor API", "a memory store", "a prompt template"], "explain": "MCP standardizes how agents discover and use capabilities."},
   {"q": "Key benefit of MCP?", "correct": "portable, plug-and-play integrations",
    "wrong": ["higher temperature", "fewer guardrails", "no need for tools"], "explain": "Standardization removes bespoke glue per tool."}],
 "review": [
   {"prompt": "What problem does MCP solve?", "answer": "Standardizing how agents discover and call tools/data, replacing bespoke integrations."},
   {"prompt": "When NOT to use MCP?", "answer": "For a single hardcoded tool or a quick one-off prototype."},
   {"prompt": "MCP failure mode?", "answer": "Treating it as just another API and ignoring its discovery/capability contract."},
   {"prompt": "MCP in one line?", "answer": "A universal, standardized 'outlet' so tools are plug-and-play across agents."},
   {"prompt": "Confused with MCP?", "answer": "Plain Tool Use — MCP is the standard layer that makes tools portable."},
   {"prompt": "Real-world MCP example?", "answer": "Agents connecting to an MCP server to use any registered tool."}],
}

P[15] = {
 "name": "Inter-Agent Communication (A2A)", "metaphor": "A shared team language", "icon": "messages-square",
 "solves": "Agents from different systems can't cooperate without a common way to talk — A2A standardizes messages.",
 "use_when": ["Independent agents must coordinate", "Agents are built by different teams/vendors"],
 "avoid_when": ["All agents live in one process you control", "Simple function calls suffice"],
 "example": "A planning agent delegates a subtask to a remote research agent via a shared message format.",
 "mistake": "Ad-hoc message formats that break when an agent changes its output.",
 "model_points": ["A shared message contract", "Agents request and respond", "Interoperability across systems"],
 "drill": {"scenario": "Two agents built by different vendors must hand tasks back and forth reliably.",
           "options": [
             {"text": "Inter-Agent Communication (A2A)", "correct": True, "feedback": "Right — a standardized message contract lets independent agents interoperate."},
             {"text": "Memory", "correct": False, "feedback": "Memory holds context; it doesn't define how agents talk to each other."},
             {"text": "Reflection", "correct": False, "feedback": "Reflection is internal self-review, not cross-agent messaging."}]},
 "boss": [
   {"q": "A2A's core requirement is…", "correct": "a shared, stable message contract",
    "wrong": ["one giant prompt", "no structure", "a calculator"], "explain": "Interoperability needs an agreed message format."},
   {"q": "A2A failure mode?", "correct": "ad-hoc formats that break on change",
    "wrong": ["too much safety", "too little memory", "too few tools"], "explain": "Unstable contracts break cross-agent coordination."}],
 "review": [
   {"prompt": "What problem does A2A solve?", "answer": "Letting independent agents coordinate via a shared, standardized message format."},
   {"prompt": "When NOT to use A2A?", "answer": "When all agents live in one process and simple function calls suffice."},
   {"prompt": "A2A failure mode?", "answer": "Ad-hoc message formats that break when an agent changes."},
   {"prompt": "A2A in one line?", "answer": "A shared 'language' so agents from different systems interoperate."},
   {"prompt": "Confused with A2A?", "answer": "MCP (agent↔tools) vs A2A (agent↔agent)."},
   {"prompt": "Real-world A2A example?", "answer": "A planner delegating to a remote research agent via a common protocol."}],
}

P[17] = {
 "name": "Reasoning Techniques", "metaphor": "Showing your work", "icon": "brain-circuit",
 "solves": "Hard problems need structured thinking — techniques like step-by-step or self-consistency boost accuracy.",
 "use_when": ["Multi-step logic, math, or planning", "Accuracy matters more than tokens"],
 "avoid_when": ["Trivial lookups", "Latency-critical paths where reasoning adds little"],
 "example": "Ask the model to reason step-by-step, then sample several paths and take the majority answer.",
 "mistake": "Exposing raw chain-of-thought to users or trusting a single unchecked reasoning path.",
 "model_points": ["Make thinking explicit and structured", "Explore multiple paths when stakes are high", "Verify the conclusion"],
 "drill": {"scenario": "An agent gets multi-step word problems wrong by jumping straight to an answer.",
           "options": [
             {"text": "Reasoning Techniques (step-by-step / self-consistency)", "correct": True, "feedback": "Right — structured, multi-path reasoning improves multi-step accuracy."},
             {"text": "Routing", "correct": False, "feedback": "There's one problem type; routing doesn't add reasoning."},
             {"text": "Memory", "correct": False, "feedback": "Recall won't fix flawed in-the-moment reasoning."}]},
 "boss": [
   {"q": "Self-consistency improves accuracy by…", "correct": "sampling several reasoning paths and taking the majority",
    "wrong": ["using one fast guess", "skipping verification", "raising temperature only"], "explain": "Multiple paths + majority vote beat a single chain."},
   {"q": "A reasoning safety rule?", "correct": "don't expose raw chain-of-thought to end users",
    "wrong": ["always show it", "never verify", "remove all steps"], "explain": "Keep internal reasoning internal; share conclusions."}],
 "review": [
   {"prompt": "What problem do Reasoning Techniques solve?", "answer": "Boosting accuracy on multi-step problems via structured, explicit reasoning."},
   {"prompt": "When NOT to use heavy reasoning?", "answer": "Trivial lookups or latency-critical paths."},
   {"prompt": "Reasoning failure mode?", "answer": "Trusting a single unchecked path, or leaking raw chain-of-thought."},
   {"prompt": "What is self-consistency?", "answer": "Sampling multiple reasoning paths and taking the majority answer."},
   {"prompt": "Reasoning trade-off?", "answer": "More tokens/latency for higher accuracy."},
   {"prompt": "Real-world reasoning example?", "answer": "Step-by-step solving of a multi-constraint scheduling problem."}],
}

P[8] = {
 "name": "Memory Management", "metaphor": "A durable notebook, not a hoarder's attic", "icon": "database",
 "solves": "Agents forget across turns or drown in irrelevant history — manage what to keep, summarize, and retrieve.",
 "use_when": ["Multi-turn or long-running tasks", "Context exceeds the window"],
 "avoid_when": ["Single-shot tasks", "All context fits and stays relevant"],
 "example": "Summarize old turns and retrieve only the memories relevant to the current step.",
 "mistake": "Dumping the entire history every call, or leaking private/irrelevant memory.",
 "model_points": ["Keep relevant context, drop noise", "Summarize older history", "Retrieve memories by relevance"],
 "drill": {"scenario": "A long-running assistant blows its context window by pasting all prior turns each call.",
           "options": [
             {"text": "Memory Management (summarize + retrieve)", "correct": True, "feedback": "Right — summarize old turns and pull only relevant memories."},
             {"text": "Parallelization", "correct": False, "feedback": "Running tasks in parallel doesn't fix context bloat."},
             {"text": "Guardrails", "correct": False, "feedback": "Guardrails enforce safety, not context efficiency."}]},
 "boss": [
   {"q": "Better than dumping all history?", "correct": "Summarize old turns and retrieve by relevance",
    "wrong": ["Delete all memory", "Raise temperature", "Add more tools"], "explain": "Selective memory beats raw history dumps."},
   {"q": "A memory safety concern?", "correct": "Leaking private/irrelevant context",
    "wrong": ["Too few tokens", "Too much math", "No router"], "explain": "Memory boundaries protect privacy and relevance."}],
 "review": [
   {"prompt": "What problem does Memory Management solve?", "answer": "Keeping relevant context across turns without overflowing the window or leaking noise."},
   {"prompt": "When NOT to manage memory heavily?", "answer": "Single-shot tasks where all context fits and stays relevant."},
   {"prompt": "Memory failure mode?", "answer": "Dumping full history every call, or leaking private/irrelevant memory."},
   {"prompt": "Better strategy than full-history?", "answer": "Summarize older turns and retrieve only relevant memories."},
   {"prompt": "Memory boundary concern?", "answer": "Excluding private/irrelevant data from what you keep and retrieve."},
   {"prompt": "Real-world Memory example?", "answer": "A coding assistant summarizing earlier context and recalling only what's relevant now."}],
}

P[12] = {
 "name": "Exception Handling & Recovery", "metaphor": "Seatbelts and airbags", "icon": "shield-alert",
 "solves": "Tools fail, APIs time out, outputs malform — agents need defined failure paths, retries, and fallbacks.",
 "use_when": ["Any production agent touching tools/APIs", "Reliability matters"],
 "avoid_when": ["Throwaway demos (still risky)", "No external dependencies at all"],
 "example": "If a tool call fails, retry with backoff, then fall back to a safe default and inform the user.",
 "mistake": "No fallback after an exception — the agent hangs, loops, or crashes silently.",
 "model_points": ["Anticipate failure points", "Retry with limits/backoff", "Fall back safely and report"],
 "drill": {"scenario": "An agent freezes whenever its search API times out.",
           "options": [
             {"text": "Exception Handling & Recovery", "correct": True, "feedback": "Right — add retry-with-limit then a safe fallback path."},
             {"text": "Reflection", "correct": False, "feedback": "Self-critique doesn't handle infrastructure failures."},
             {"text": "Prioritization", "correct": False, "feedback": "Ranking tasks won't recover from a timeout."}]},
 "boss": [
   {"q": "After an exception, an agent should…", "correct": "retry within limits, then fall back safely",
    "wrong": ["loop forever", "crash silently", "ignore it"], "explain": "Bounded retries + fallback keep agents reliable."},
   {"q": "A retry must always have…", "correct": "a maximum attempt limit",
    "wrong": ["infinite attempts", "no logging", "higher temperature"], "explain": "Unbounded retries cause runaway behavior."}],
 "review": [
   {"prompt": "What problem does Exception Handling solve?", "answer": "Keeping agents reliable when tools/APIs fail via defined failure paths."},
   {"prompt": "When is it needed?", "answer": "Any production agent with external dependencies."},
   {"prompt": "Exception failure mode?", "answer": "No fallback after an error — the agent hangs, loops, or crashes silently."},
   {"prompt": "What must retries have?", "answer": "A maximum attempt limit (and ideally backoff)."},
   {"prompt": "Recovery best practice?", "answer": "Retry within limits, then fall back to a safe default and report."},
   {"prompt": "Real-world example?", "answer": "Falling back to cached data when a live API times out."}],
}

P[13] = {
 "name": "Human-in-the-Loop", "metaphor": "A co-pilot asking before risky moves", "icon": "user-check",
 "solves": "Some actions are too risky for full autonomy — require human approval at key decision points.",
 "use_when": ["Irreversible or high-impact actions", "Compliance/oversight is required"],
 "avoid_when": ["Low-stakes, fully reversible tasks", "Latency-critical automation with low risk"],
 "example": "An agent drafts a refund but waits for a human 'approve' before issuing it.",
 "mistake": "Skipping the approval gate on destructive actions, or logging no human decision.",
 "model_points": ["Identify risky/irreversible actions", "Pause for human approval", "Log the human decision"],
 "drill": {"scenario": "An agent can delete production data to 'clean up'.",
           "options": [
             {"text": "Human-in-the-Loop", "correct": True, "feedback": "Right — destructive actions require explicit human approval first."},
             {"text": "Parallelization", "correct": False, "feedback": "Concurrency has nothing to do with approval of risky actions."},
             {"text": "Routing", "correct": False, "feedback": "Routing picks a handler; it doesn't gate dangerous actions."}]},
 "boss": [
   {"q": "Risky/irreversible actions require…", "correct": "explicit human approval before execution",
    "wrong": ["instant execution", "a louder log", "more tools"], "explain": "A human gate bounds autonomy on high-impact actions."},
   {"q": "After a human decides, the agent should…", "correct": "log the decision and proceed accordingly",
    "wrong": ["forget it", "retry without approval", "escalate forever"], "explain": "Decisions must be recorded for auditability."}],
 "review": [
   {"prompt": "What problem does Human-in-the-Loop solve?", "answer": "Bounding autonomy by requiring human approval for risky actions."},
   {"prompt": "When NOT to add a human gate?", "answer": "Low-stakes, fully reversible, latency-critical tasks."},
   {"prompt": "HITL failure mode?", "answer": "Skipping approval on destructive actions or not logging the decision."},
   {"prompt": "What triggers a human gate?", "answer": "Irreversible or high-impact actions, or compliance needs."},
   {"prompt": "After approval, what's required?", "answer": "Log the human decision and proceed accordingly."},
   {"prompt": "Real-world HITL example?", "answer": "An agent waiting for human sign-off before issuing a refund."}],
}

P[18] = {
 "name": "Guardrails / Safety Patterns", "metaphor": "Bumpers on the bowling lane", "icon": "shield",
 "solves": "Agents can produce unsafe, off-policy, or harmful output/actions — guardrails constrain inputs and outputs.",
 "use_when": ["User-facing or action-taking agents", "Policy/safety/compliance applies"],
 "avoid_when": ["Never — but tune strength to the risk"],
 "example": "Block an agent from running destructive commands and refuse unsupported medical claims safely.",
 "mistake": "Guardrails too weak (let unsafe output through) or too blunt (block everything useful).",
 "model_points": ["Check inputs AND outputs", "Block or escalate unsafe actions", "Explain the refusal safely"],
 "drill": {"scenario": "An agent is about to execute a user-supplied shell command that could wipe a disk.",
           "options": [
             {"text": "Guardrails / Safety Patterns", "correct": True, "feedback": "Right — a guardrail blocks/escalates the destructive action before it runs."},
             {"text": "Memory", "correct": False, "feedback": "Remembering the command doesn't make running it safe."},
             {"text": "Parallelization", "correct": False, "feedback": "Running it in parallel is just as dangerous."}]},
 "boss": [
   {"q": "Guardrails should check…", "correct": "both inputs and outputs",
    "wrong": ["only the temperature", "nothing", "only greetings"], "explain": "Unsafe content can enter via input OR exit via output."},
   {"q": "When blocking, the agent should…", "correct": "refuse safely and explain the policy reason",
    "wrong": ["fabricate an answer", "crash", "comply anyway"], "explain": "A safe, explained refusal beats silent failure or compliance."}],
 "review": [
   {"prompt": "What problem do Guardrails solve?", "answer": "Constraining agent inputs/outputs/actions to stay safe and on-policy."},
   {"prompt": "Tuning guardrails?", "answer": "Strong enough to stop harm, not so blunt they block useful work."},
   {"prompt": "Guardrail failure mode?", "answer": "Too weak (unsafe output passes) or too blunt (everything blocked)."},
   {"prompt": "What should guardrails inspect?", "answer": "Both inputs and outputs, plus risky actions."},
   {"prompt": "How to refuse?", "answer": "Block or escalate, and explain the policy reason safely."},
   {"prompt": "Real-world Guardrail example?", "answer": "Blocking destructive shell commands and unsupported claims."}],
 "lab": {"kind": "select", "goal": "Harden an agent that takes real-world actions.",
         "prompt": "Select the guardrails this action-taking agent needs.",
         "blocks": [{"id": "in", "label": "Input check (block injections/unsafe requests)"},
                    {"id": "out", "label": "Output check (filter unsafe/unsupported content)"},
                    {"id": "gate", "label": "Confirmation gate for destructive actions"},
                    {"id": "temp", "label": "Raise temperature for creativity"},
                    {"id": "log", "label": "Audit log of blocked attempts"}],
         "required": ["in", "out", "gate", "log"],
         "success": "Input + output checks, a confirmation gate, and an audit log. Higher temperature is not a safety control."},
 "debug": {"scenario": "A 'safety' agent only checks the user's input, but the model still emits unsupported medical advice.",
           "broken": "guardrail = validate_input_only()",
           "options": ["Add an OUTPUT guardrail that filters unsafe/unsupported responses",
                       "Remove the input check", "Increase max tokens", "Trust the model's confidence"],
           "answer": 0, "failure_mode": "Guardrail too weak (output unchecked)",
           "explain": "Safety must cover outputs too — input-only checks miss unsafe generations."},
}

P[19] = {
 "name": "Evaluation & Monitoring", "metaphor": "A quality inspector on the line", "icon": "clipboard-check",
 "solves": "You can't improve what you don't measure — score agent outputs against rubrics and monitor in production.",
 "use_when": ["Before and after shipping any agent", "You need to catch regressions"],
 "avoid_when": ["Never — but match rubric depth to stakes"],
 "example": "Score support replies on accuracy, format, safety, and resolution — not on length.",
 "mistake": "No rubric ('looks good to me'), or measuring vanity metrics like word count.",
 "model_points": ["Define a clear rubric", "Score outputs objectively", "Turn failures into improvement suggestions"],
 "drill": {"scenario": "A team ships an agent and judges quality by 'it feels right'.",
           "options": [
             {"text": "Evaluation & Monitoring", "correct": True, "feedback": "Right — define a rubric, score objectively, and monitor over time."},
             {"text": "Reflection", "correct": False, "feedback": "Reflection improves one answer; evaluation measures quality systematically."},
             {"text": "Routing", "correct": False, "feedback": "Routing dispatches work; it doesn't measure quality."}]},
 "boss": [
   {"q": "A good eval scores…", "correct": "accuracy, format, safety, and task resolution",
    "wrong": ["word count", "response speed only", "vibes"], "explain": "Measure what matters, never vanity metrics."},
   {"q": "When an output fails the rubric, produce…", "correct": "a concrete improvement suggestion",
    "wrong": ["a louder error", "nothing", "a longer answer"], "explain": "Evaluation should drive improvement, not just judge."}],
 "review": [
   {"prompt": "What problem does Evaluation solve?", "answer": "Measuring agent quality against rubrics so you can improve and catch regressions."},
   {"prompt": "When to evaluate?", "answer": "Before and after shipping, and continuously in production."},
   {"prompt": "Evaluation failure mode?", "answer": "No rubric, or scoring vanity metrics like length."},
   {"prompt": "What should a rubric score?", "answer": "Accuracy, format compliance, safety, and task resolution."},
   {"prompt": "What should a failed eval produce?", "answer": "A concrete improvement suggestion."},
   {"prompt": "Real-world Evaluation example?", "answer": "Scoring support replies on accuracy/format/safety/resolution."}],
 "lab": {"kind": "select", "goal": "Design an evaluation rubric for a support-reply agent.",
         "prompt": "Select the criteria a good rubric should score.",
         "blocks": [{"id": "acc", "label": "Factual accuracy"}, {"id": "fmt", "label": "Follows required format"},
                    {"id": "safe", "label": "Safety / policy compliance"}, {"id": "res", "label": "Resolves the user's intent"},
                    {"id": "len", "label": "Uses the most words"}],
         "required": ["acc", "fmt", "safe", "res"],
         "success": "Accuracy, format, safety, and resolution — never raw word count."},
 "debug": {"scenario": "An agent's evaluation passes everything because the rubric is just 'looks good'.",
           "broken": "rubric = ['looks good to me']",
           "options": ["Define objective criteria (accuracy, format, safety, resolution) and score each",
                       "Measure response length", "Remove evaluation entirely", "Trust the model's self-rating"],
           "answer": 0, "failure_mode": "Evaluation rubric missing",
           "explain": "Vibes aren't metrics — objective, multi-criterion rubrics catch real problems."},
}

P[9] = {
 "name": "Learning & Adaptation", "metaphor": "An agent that gets better with practice", "icon": "trending-up",
 "solves": "Static agents stagnate — capture feedback and outcomes to improve behavior over time.",
 "use_when": ["Repeated tasks with feedback signals", "Performance should improve with data"],
 "avoid_when": ["One-off tasks", "No reliable feedback signal"],
 "example": "Log which answers users accepted and adapt future responses toward what works.",
 "mistake": "Adapting on noisy or biased feedback, causing drift toward the wrong behavior.",
 "model_points": ["Collect outcome/feedback signals", "Update behavior or examples", "Guard against drift"],
 "drill": {"scenario": "A recommendation agent should improve as it sees which suggestions users accept.",
           "options": [
             {"text": "Learning & Adaptation", "correct": True, "feedback": "Right — capture feedback signals and adapt behavior over time."},
             {"text": "Routing", "correct": False, "feedback": "Routing dispatches requests; it doesn't learn from outcomes."},
             {"text": "Guardrails", "correct": False, "feedback": "Guardrails constrain; they don't improve performance from feedback."}]},
 "boss": [
   {"q": "Learning needs a reliable…", "correct": "feedback/outcome signal",
    "wrong": ["higher temperature", "bigger prompt", "more tools"], "explain": "Adaptation is only as good as its signal."},
   {"q": "Main risk of adaptation?", "correct": "drift from noisy/biased feedback",
    "wrong": ["too much safety", "too little memory", "no router"], "explain": "Bad signals push behavior the wrong way."}],
 "review": [
   {"prompt": "What problem does Learning & Adaptation solve?", "answer": "Improving agent behavior over time using feedback and outcomes."},
   {"prompt": "When NOT to add learning?", "answer": "One-off tasks or when no reliable feedback signal exists."},
   {"prompt": "Learning failure mode?", "answer": "Adapting on noisy/biased feedback causing drift."},
   {"prompt": "What does adaptation require?", "answer": "A reliable feedback/outcome signal."},
   {"prompt": "How to stay safe while adapting?", "answer": "Guard against drift and validate changes."},
   {"prompt": "Real-world Learning example?", "answer": "Adapting recommendations from which suggestions users accept."}],
}

P[11] = {
 "name": "Goal Setting & Monitoring", "metaphor": "A North Star with a progress dashboard", "icon": "target",
 "solves": "Agents wander without a clear objective — define goals and continuously check progress toward them.",
 "use_when": ["Long-running or autonomous tasks", "Success must be measurable"],
 "avoid_when": ["Trivial single actions", "No measurable success criteria"],
 "example": "Set 'reduce open tickets to <10' and monitor the count, adjusting actions until met.",
 "mistake": "Vague goals with no success metric, so the agent never knows when it's done.",
 "model_points": ["Define a concrete, measurable goal", "Monitor progress continuously", "Adjust actions toward the goal"],
 "drill": {"scenario": "An autonomous agent keeps working but never knows if it has succeeded.",
           "options": [
             {"text": "Goal Setting & Monitoring", "correct": True, "feedback": "Right — a measurable goal plus progress monitoring defines 'done'."},
             {"text": "Tool Use", "correct": False, "feedback": "Tools execute actions; they don't define success."},
             {"text": "Parallelization", "correct": False, "feedback": "Concurrency doesn't tell the agent when it's finished."}]},
 "boss": [
   {"q": "A good goal is…", "correct": "concrete and measurable",
    "wrong": ["vague and open-ended", "secret", "infinite"], "explain": "Measurable goals create a clear finish line."},
   {"q": "Monitoring lets the agent…", "correct": "track progress and adjust toward the goal",
    "wrong": ["ignore results", "loop blindly", "skip the goal"], "explain": "Continuous checks keep work on target."}],
 "review": [
   {"prompt": "What problem does Goal Setting solve?", "answer": "Giving agents a measurable objective and tracking progress toward it."},
   {"prompt": "When NOT needed?", "answer": "Trivial single actions with no measurable success."},
   {"prompt": "Goal-setting failure mode?", "answer": "Vague goals with no success metric — the agent never knows it's done."},
   {"prompt": "What makes a good goal?", "answer": "Concrete and measurable."},
   {"prompt": "Why monitor?", "answer": "To track progress and adjust actions toward the goal."},
   {"prompt": "Real-world example?", "answer": "Driving open tickets below a threshold and monitoring the count."}],
}

P[14] = {
 "name": "Knowledge Retrieval (RAG)", "metaphor": "Open-book, not from-memory", "icon": "search",
 "solves": "LLMs hallucinate facts they don't reliably know — retrieve real evidence first, then answer from it.",
 "use_when": ["Answers must be grounded in specific/up-to-date sources", "Facts change or are private"],
 "avoid_when": ["Pure reasoning with no external facts", "The model reliably knows the answer"],
 "example": "Retrieve policy snippets, then answer the question citing those snippets — refuse if unsupported.",
 "mistake": "Answering before retrieving, or citing nothing so claims can't be verified.",
 "model_points": ["Retrieve relevant evidence FIRST", "Answer grounded in that evidence", "Reject unsupported claims"],
 "drill": {"scenario": "An agent must answer questions about your company's private, frequently-changing policies.",
           "options": [
             {"text": "Knowledge Retrieval (RAG)", "correct": True, "feedback": "Right — retrieve current policy snippets, then answer grounded in them."},
             {"text": "Reasoning Techniques", "correct": False, "feedback": "Reasoning can't invent private, changing facts it was never given."},
             {"text": "Reflection", "correct": False, "feedback": "Self-review of a hallucinated answer still lacks the source facts."}]},
 "boss": [
   {"q": "RAG's core ordering is…", "correct": "retrieve evidence, THEN answer from it",
    "wrong": ["answer, then maybe search", "never retrieve", "guess confidently"], "explain": "Grounding before generation is the whole point."},
   {"q": "If retrieval finds no support, the agent should…", "correct": "decline or flag the claim as unsupported",
    "wrong": ["make it up", "answer confidently", "delete the question"], "explain": "Unsupported claims must be rejected, not fabricated."}],
 "review": [
   {"prompt": "What problem does RAG solve?", "answer": "Grounding answers in retrieved evidence to reduce hallucination."},
   {"prompt": "When NOT to use RAG?", "answer": "Pure reasoning with no external facts, or when the model reliably knows."},
   {"prompt": "RAG failure mode?", "answer": "Answering before retrieving, or citing nothing so claims can't be verified."},
   {"prompt": "RAG's required ordering?", "answer": "Retrieve evidence first, then answer grounded in it."},
   {"prompt": "What if no evidence is found?", "answer": "Decline or flag the claim as unsupported."},
   {"prompt": "Real-world RAG example?", "answer": "Answering policy questions from retrieved, cited policy snippets."}],
 "lab": {"kind": "order", "goal": "Build a grounded answer flow that won't hallucinate.",
         "prompt": "Tap the steps in the correct order.",
         "steps": [{"id": "ans", "label": "Answer using ONLY the retrieved evidence"},
                   {"id": "ret", "label": "Retrieve relevant source snippets"},
                   {"id": "chk", "label": "Reject the claim if no evidence supports it"}],
         "correct_order": ["ret", "ans", "chk"],
         "success": "Retrieve → answer from evidence → reject unsupported claims. Retrieval comes BEFORE the answer."},
 "debug": {"scenario": "An agent confidently answers private-policy questions but cites no sources and is often wrong.",
           "broken": "flow = answer_from_model_memory()",
           "options": ["Add a retrieval step before answering and ground the response in cited evidence",
                       "Increase temperature", "Add a second LLM call with no sources", "Trust the model's confidence"],
           "answer": 0, "failure_mode": "Hallucination without retrieval",
           "explain": "Retrieve first, then answer from (and cite) the evidence."},
}

P[16] = {
 "name": "Resource-Aware Optimization", "metaphor": "A budget-conscious traveler", "icon": "gauge",
 "solves": "Agents can waste tokens, money, and time — optimize for cost/latency without losing quality.",
 "use_when": ["High-volume or cost-sensitive systems", "Latency budgets matter"],
 "avoid_when": ["Quality is paramount and cost is irrelevant", "Prototypes where speed of building wins"],
 "example": "Use a cheap model for easy requests and escalate to a strong model only when needed.",
 "mistake": "Always using the most expensive path, or cutting cost so hard that quality collapses.",
 "model_points": ["Match effort to difficulty", "Cache & reuse where possible", "Escalate only with reason"],
 "drill": {"scenario": "A high-traffic agent uses a top-tier model for every trivial request, blowing the budget.",
           "options": [
             {"text": "Resource-Aware Optimization", "correct": True, "feedback": "Right — route easy requests to cheaper paths, escalate only when needed."},
             {"text": "Reflection", "correct": False, "feedback": "Self-review adds cost; it doesn't reduce it."},
             {"text": "Memory", "correct": False, "feedback": "Memory helps context, not cost control by itself."}]},
 "boss": [
   {"q": "Resource-aware agents match…", "correct": "effort/cost to task difficulty",
    "wrong": ["every task to the priciest model", "nothing", "temperature to randomness"], "explain": "Spend where it pays off."},
   {"q": "Escalating to an expensive path should…", "correct": "require a reason",
    "wrong": ["happen always", "never happen", "be random"], "explain": "Justified escalation controls cost."}],
 "review": [
   {"prompt": "What problem does Resource-Aware Optimization solve?", "answer": "Cutting cost/latency without sacrificing needed quality."},
   {"prompt": "When NOT to optimize cost?", "answer": "When quality is paramount and cost is irrelevant."},
   {"prompt": "Optimization failure mode?", "answer": "Always using the priciest path, or cutting so hard quality collapses."},
   {"prompt": "Core principle?", "answer": "Match effort/cost to task difficulty; escalate only with reason."},
   {"prompt": "A cheap win?", "answer": "Cache and reuse results where possible."},
   {"prompt": "Real-world example?", "answer": "Cheap model for easy queries, strong model only when needed."}],
}

P[20] = {
 "name": "Prioritization", "metaphor": "A triage nurse", "icon": "list-ordered",
 "solves": "Too many tasks, limited capacity — rank by impact, urgency, and confidence to work the right things first.",
 "use_when": ["Many competing tasks/goals", "Limited time or resources"],
 "avoid_when": ["A single task", "All tasks are equal and independent"],
 "example": "Rank incoming issues by severity × urgency and handle the highest-value first.",
 "mistake": "Treating all tasks as equal, so low-value work blocks critical work.",
 "model_points": ["Score tasks by impact/urgency/confidence", "Order the queue", "Re-rank as conditions change"],
 "drill": {"scenario": "An agent has 50 queued tasks and limited time before a deadline.",
           "options": [
             {"text": "Prioritization", "correct": True, "feedback": "Right — rank by impact/urgency/confidence and work the top first."},
             {"text": "Parallelization", "correct": False, "feedback": "Even in parallel you have limits — you still must choose what matters most."},
             {"text": "Routing", "correct": False, "feedback": "Routing picks a handler, not which task is most important."}]},
 "boss": [
   {"q": "Prioritization ranks tasks by…", "correct": "impact, urgency, and confidence",
    "wrong": ["alphabetical order", "random", "creation time only"], "explain": "Value-based ranking focuses effort."},
   {"q": "Priorities should be…", "correct": "re-ranked as conditions change",
    "wrong": ["fixed forever", "ignored", "secret"], "explain": "Dynamic re-ranking keeps focus on what matters now."}],
 "review": [
   {"prompt": "What problem does Prioritization solve?", "answer": "Choosing the highest-value work first under limited capacity."},
   {"prompt": "When NOT to prioritize?", "answer": "A single task, or all tasks equal and independent."},
   {"prompt": "Prioritization failure mode?", "answer": "Treating all tasks equally so low-value work blocks critical work."},
   {"prompt": "Rank tasks by what?", "answer": "Impact, urgency, and confidence."},
   {"prompt": "Keep priorities fresh how?", "answer": "Re-rank as conditions change."},
   {"prompt": "Real-world example?", "answer": "Triaging issues by severity × urgency."}],
}

P[21] = {
 "name": "Exploration & Discovery", "metaphor": "A scout mapping unknown territory", "icon": "compass",
 "solves": "Open-ended problems need active investigation — generate hypotheses, test them, keep what works.",
 "use_when": ["Open-ended research/discovery", "The path isn't known in advance"],
 "avoid_when": ["The procedure is well-defined", "Exploration cost is unjustified"],
 "example": "An agent generates several research leads, tests each, and discards weak ones.",
 "mistake": "Chasing every lead without pruning, wasting resources on dead ends.",
 "model_points": ["Generate hypotheses/leads", "Test and gather evidence", "Prune weak leads, keep discoveries"],
 "drill": {"scenario": "A research agent must investigate an open question with no fixed procedure.",
           "options": [
             {"text": "Exploration & Discovery", "correct": True, "feedback": "Right — generate hypotheses, test them, and prune weak leads."},
             {"text": "Prompt Chaining", "correct": False, "feedback": "Chaining follows fixed steps; discovery needs adaptive investigation."},
             {"text": "Routing", "correct": False, "feedback": "Routing dispatches known intents; this is open-ended search."}]},
 "boss": [
   {"q": "Exploration must include…", "correct": "pruning weak leads",
    "wrong": ["chasing every lead", "no testing", "fixed steps only"], "explain": "Pruning prevents wasting effort on dead ends."},
   {"q": "Discovery tracks…", "correct": "evidence for and against each hypothesis",
    "wrong": ["nothing", "only successes", "temperature"], "explain": "Tracking evidence guides what to keep or drop."}],
 "review": [
   {"prompt": "What problem does Exploration solve?", "answer": "Investigating open-ended problems by generating and testing hypotheses."},
   {"prompt": "When NOT to explore?", "answer": "When the procedure is well-defined or exploration cost isn't justified."},
   {"prompt": "Exploration failure mode?", "answer": "Chasing every lead without pruning, wasting resources."},
   {"prompt": "Core loop?", "answer": "Generate hypotheses → test → prune weak leads, keep discoveries."},
   {"prompt": "What to track?", "answer": "Evidence for and against each hypothesis."},
   {"prompt": "Real-world example?", "answer": "A research agent testing leads and discarding dead ends."}],
}


def shuffle_options(correct, wrong, salt):
    import hashlib, random
    opts = list(wrong) + [correct]
    h = int(hashlib.sha256((salt + correct).encode()).hexdigest(), 16)
    random.Random(h).shuffle(opts)
    return opts, opts.index(correct)


def build_chapter(num, group_id):
    p = P[num]
    cid = f"adp-{num:02d}"
    missions = []

    missions.append({
        "id": f"{cid}::briefing", "type": "briefing", "title": "Mission Brief",
        "objective": "Get the pattern in 60 seconds before you build.",
        "estimated_minutes": 2, "xp_reward": XP["briefing"],
        "payload": {"tagline": f"{p['name']} = {p['metaphor']}", "why_it_matters": p["solves"],
                    "objectives": ["Use when: " + "; ".join(p["use_when"][:2]),
                                   "Avoid when: " + "; ".join(p["avoid_when"][:2]),
                                   "Example: " + p["example"]],
                    "languages": "Agentic Design Patterns · A. Gulli"},
    })
    missions.append({
        "id": f"{cid}::mentalmodel", "type": "mentalmodel", "title": "Mental Model",
        "objective": "Lock in the visual metaphor.",
        "estimated_minutes": 2, "xp_reward": XP["mentalmodel"],
        "payload": {"metaphor": p["metaphor"], "icon": p["icon"], "pattern": p["name"],
                    "points": p["model_points"], "mistake": p["mistake"]},
    })
    # drill (pattern selection)
    d = p["drill"]
    missions.append({
        "id": f"{cid}::drill", "type": "drill", "title": "Pattern Selection Drill",
        "objective": "Pick the right pattern — and learn why the others fall short.",
        "estimated_minutes": 3, "xp_reward": XP["drill"],
        "payload": {"rounds": [{"scenario": d["scenario"], "options": d["options"]}]},
    })
    # optional lab
    if p.get("lab"):
        missions.append({
            "id": f"{cid}::lab", "type": "lab", "title": "Build Lab",
            "objective": p["lab"]["goal"], "estimated_minutes": 5, "xp_reward": XP["lab"],
            "payload": p["lab"],
        })
    # optional debug
    if p.get("debug"):
        dbg = p["debug"]
        missions.append({
            "id": f"{cid}::debug", "type": "debug", "title": "Broken Agent Fix",
            "objective": "Diagnose the failure and choose the fix.", "estimated_minutes": 3,
            "xp_reward": XP["debug"], "payload": dbg,
        })
    # boss
    boss_qs = []
    for i, q in enumerate(p["boss"]):
        opts, ans = shuffle_options(q["correct"], q["wrong"], f"{cid}-{i}")
        boss_qs.append({"q": q["q"], "options": opts, "answer": ans, "explain": q["explain"]})
    missions.append({
        "id": f"{cid}::boss", "type": "boss", "title": f"Boss: {p['name']}",
        "objective": "Combine the ideas to clear the chapter.", "estimated_minutes": 4,
        "xp_reward": XP["boss"],
        "payload": {"questions": boss_qs, "pass_threshold": max(1, int(len(boss_qs) * 0.6)),
                    "recap": p["model_points"]},
    })

    return {
        "id": cid, "is_academy": True, "path_id": "agentic-patterns",
        "world_id": -1, "number": num, "group": group_id,
        "pattern": p["name"],
        "title": f"{num}. {p['name']}", "tagline": f"{p['name']} = {p['metaphor']}",
        "type": "Pattern", "icon": p["icon"],
        "estimated_minutes": sum(m["estimated_minutes"] for m in missions),
        "objectives": [p["solves"]],
        "source_path": "Agentic Design Patterns (A. Gulli) — transformed",
        "missions": missions,
        "review_cards": p["review"],
        "badge": {"id": f"badge-{cid}", "title": f"{p['name']} Adept",
                  "description": f"Cleared the {p['name']} chapter."},
    }


def build():
    chapters = []
    group_of = {}
    for g in GROUPS:
        for n in g["patterns"]:
            group_of[n] = g["id"]
    for num in range(1, 22):
        chapters.append(build_chapter(num, group_of.get(num, "foundations")))
    chapters.sort(key=lambda c: c["number"])

    path = {
        "id": "agentic-patterns",
        "title": "Agentic Design Patterns Academy",
        "source_type": "pdf",
        "source_file_name": "Agentic Design Patterns (Antonio Gulli)",
        "attribution": "Based on 'Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems' by Antonio Gulli. Original transformed teaching content; the author donates royalties to Save the Children.",
        "description": "Master 21 agentic design patterns by building, debugging, and applying each one.",
        "tagline": "Build, debug and apply the 21 patterns that power real AI agents.",
        "groups": GROUPS,
        "chapter_count": len(chapters),
        "chapters": chapters,
    }
    out = {"version": 1, "paths": [path]}
    (BACKEND / "academy_content.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    playable_full = [c["number"] for c in chapters if any(m["type"] == "lab" for m in c["missions"])]
    print(f"Wrote academy_content.json — {len(chapters)} chapters")
    print(f"Total missions: {sum(len(c['missions']) for c in chapters)}")
    print(f"Chapters with full labs+debug: {playable_full}")


if __name__ == "__main__":
    build()
