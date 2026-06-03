# AgentForge Quest — PRD

## Original problem statement
Transform the GitHub repo `ai-engineering-from-scratch` (AI engineering curriculum: 18 phases / 96 lessons)
into **AgentForge Quest** — a mobile-first, ADHD-friendly, game-like learning PWA. Each chapter becomes a
playable level with story intro, interactive lab, mini-games/challenges, boss battles, XP, streaks, badges,
skill tree, review deck (spaced repetition) and a Brain Dump parking lot. Teach through doing; short missions;
immediate feedback; one clear next action; no shame-based feedback. Works without live AI keys.

## User
- 46, ADHD. Wants calm-focus, low-clutter, motivating (not childish), best learning psychology.
- No login. Mobile-first installable PWA. Visual: futuristic RPG / arcane-tech + clean minimal-futuristic (dark).

## Architecture
- **Backend**: FastAPI + MongoDB (Motor). Anonymous device profiles. Content is generated/static (served from
  `game_content.json`); only player progress lives in Mongo.
- **Content pipeline**: `scripts/build_content.py` parses `phases/*/*/docs/en.md` → `backend/game_content.json`
  (10 worlds with content, 96 levels, 841 key terms with myth/reality pairs).
- **Mission generation** (`content.py`): each level → Briefing, Concept flip-cards, Decode quiz, Myth-buster,
  Build/Lab, Boss gauntlet — all deterministic, derived from the lesson's key terms & sections.
- **Frontend**: React (CRA) PWA. Tailwind. framer-motion. lucide-react. Bottom nav (Home/Map/Lab/Arena/You).
  Manifest + service worker + icons (installable). Dark by default, reduced-motion + focus-mode toggles.

## Chapter → game conversion
Phases with lesson docs become Worlds: 0 Forge Outpost, 1 Vector Vale, 2 Pattern Plains, 3 Neural Nexus,
7 Attention Spire, 10 Crucible Core, 11 Prompt Bazaar, 14 Agent Sanctum, 16 Swarm Bastion, 17 Production Bulwark.
Each lesson → level with up to 6 missions + boss + review cards. Progression is global/linear (unlock next).

## Forks (alternative learning paths) — added 2026-06-02
- **MIT 18.06 — Strang's Linear Algebra** fork (`backend/fork_content.json`, built by `scripts/build_fork.py`
  from `backend/mit1806_lectures.json`). 35 lecture levels, 136 missions, anchored under World 1's
  `01-01-linear-algebra-intuition` level.
- New **watch** mission type embeds the real Strang YouTube lecture; plus Briefing, Concept Cards (curated,
  "Recall" framing), Comprehension quiz, and unit Checkpoints (boss) pulling pooled questions.
- Source assets NOT stored (only lecture metadata + YouTube IDs). MIT OCW CC BY-NC-SA 4.0.
- Endpoints: `GET /api/forks`, `GET /api/forks/{id}` (per-level progress + lock). Anchor level detail returns
  a `forks` array. Fork levels are addressable via the normal `/api/levels/{id}` + mission-complete flow;
  XP/streak/review all apply. Frontend: fork banner on anchor level → `/fork/:forkId` (ForkPath page).

## Implemented (2026-06-02)
- Campaign map (worlds/levels, lock/unlock, progress rings, mission counts).
- Mission player: briefing, concept flip-cards, quiz (decode), myth-buster, build (code trace), boss battle (pass threshold, recap).
- Challenge Arena: 9 deterministic debugging puzzles (select-one/multi/edit-json) with hints + validation.
- Agent Lab: build agent (name/prompt/tools/memory), run with deterministic validation + mocked trace/output,
  optional DeepSeek live mode (stub, key-gated), save/delete builds.
- Skill Tree (11 branches, progress by world), Badges (10), Review Deck (SM-2 spaced repetition),
  Brain Dump (add/tag/convert-to-mission/archive/delete), Daily quick mission + daily challenge.
- XP/level/streak engine, level-complete bonus, badge auto-award. Settings: focus mode, reduced motion, sound.
- Notification preferences (scaffolded, "coming soon"), PWA install prompt.

## Mocked / not live
- Agent Lab AI output is MOCKED (deterministic) unless `DEEPSEEK_API_KEY` is set (live mode optional).
- Push notifications are scaffolded only (preferences saved; no delivery yet).

## Backlog (next sprints)
- P1: Capacitor wrapper for native packaging; real push (FCM/APNs) wired to saved prefs.
- P1: Per-world boss "build a workflow" combining multiple concepts (currently boss = concept gauntlet).
- P2: Visual campaign map (node graph) art; offline content caching of level JSON.
- P2: More worlds when more phases gain `docs/en.md`; live-mode coaching using DeepSeek to grade agent builds.
- P2: Streak-rescue + weekly recap logic; optional cloud sync of the anonymous profile.
