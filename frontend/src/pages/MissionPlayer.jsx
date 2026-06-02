import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import QuizEngine from "../components/QuizEngine";
import CodeBlock from "../components/CodeBlock";
import { X, ArrowRight, RotateCw, Check, Lightbulb, ChevronRight } from "lucide-react";

export default function MissionPlayer() {
  const { levelId, missionId } = useParams();
  const nav = useNavigate();
  const { applyResult } = useApp();
  const [level, setLevel] = useState(null);

  useEffect(() => { api.level(levelId).then(setLevel); }, [levelId]);
  if (!level) return <div className="min-h-screen flex items-center justify-center text-sub">Loading…</div>;

  const mission = level.missions.find((m) => m.id === missionId);
  if (!mission) return <div className="min-h-screen flex items-center justify-center text-sub">Mission not found</div>;

  const idx = level.missions.findIndex((m) => m.id === missionId);
  const nextMission = level.missions[idx + 1];

  const finish = async (score = 100) => {
    const res = await api.completeMission(mission.id, { score });
    applyResult(res);
    setTimeout(() => {
      if (nextMission) nav(`/play/${encodeURIComponent(levelId)}/${encodeURIComponent(nextMission.id)}`, { replace: true });
      else nav(`/level/${encodeURIComponent(levelId)}`, { replace: true });
    }, res.new_badges?.length || res.level_just_completed ? 400 : 250);
  };

  const pct = Math.round(((idx + 1) / level.missions.length) * 100);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 glass pt-safe">
        <div className="px-4 py-3 flex items-center gap-3">
          <button onClick={() => nav(`/level/${encodeURIComponent(levelId)}`)} data-testid="mission-exit"
            className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center"><X size={18} /></button>
          <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-arcane to-yellow-300 rounded-full" style={{ width: `${pct}%`, transition: "width .4s" }} />
          </div>
          <span className="chip !text-arcane !bg-arcane/10 !border-arcane/30">+{mission.xp_reward}</span>
        </div>
      </header>

      <main className="flex-1 px-4 py-5 pb-8 max-w-md w-full mx-auto">
        <AnimatePresence mode="wait">
          <motion.div key={mission.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            {mission.type === "briefing" && <Briefing m={mission} onDone={finish} />}
            {mission.type === "concept" && <ConceptCards m={mission} onDone={finish} />}
            {(mission.type === "quiz") && <QuizMission m={mission} onDone={finish} />}
            {mission.type === "mythbuster" && <MythBuster m={mission} onDone={finish} />}
            {mission.type === "build" && <BuildMission m={mission} onDone={finish} />}
            {mission.type === "boss" && <BossMission m={mission} onDone={finish} />}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

/* ---------------- Briefing ---------------- */
function Briefing({ m, onDone }) {
  const p = m.payload;
  return (
    <div data-testid="mission-briefing">
      <div className="label">Mission Briefing</div>
      <h2 className="font-display text-2xl mt-1 mb-3 leading-tight">{p.tagline || m.title}</h2>
      <div className="card p-5">
        <div className="label mb-1">Why this matters</div>
        <p className="text-ink/85 leading-relaxed">{p.why_it_matters || "Master this to level up your agent-building skills."}</p>
      </div>
      {p.objectives?.length > 0 && (
        <div className="mt-4">
          <div className="label mb-2">You'll be able to</div>
          <ul className="space-y-2">
            {p.objectives.map((o, i) => (
              <motion.li key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}
                className="flex gap-2 text-sm text-sub"><span className="text-plasma mt-0.5">▸</span>{o}</motion.li>
            ))}
          </ul>
        </div>
      )}
      <button className="btn-primary w-full mt-6" onClick={() => onDone(100)} data-testid="briefing-done">
        Got it — let's build <ArrowRight size={18} />
      </button>
    </div>
  );
}

/* ---------------- Concept flip cards ---------------- */
function ConceptCards({ m, onDone }) {
  const cards = m.payload.cards;
  const [i, setI] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const last = i === cards.length - 1;
  const c = cards[i];

  const next = () => {
    if (last) return onDone(100);
    setFlipped(false);
    setTimeout(() => setI((x) => x + 1), 120);
  };

  return (
    <div data-testid="mission-concept">
      <div className="label">Concept Cards · {i + 1}/{cards.length}</div>
      <p className="text-sub text-sm mb-4">Tap the card to reveal the reality.</p>
      <div className="[perspective:1200px]">
        <motion.button onClick={() => setFlipped((f) => !f)} data-testid="flip-card"
          className="relative w-full h-72 [transform-style:preserve-3d]"
          animate={{ rotateY: flipped ? 180 : 0 }} transition={{ duration: 0.5 }}>
          <Face className="bg-elevated border-white/10">
            <div className="label mb-2 text-arcane">People say</div>
            <p className="font-head text-xl leading-snug text-ink/90">“{c.front}”</p>
            <span className="absolute bottom-4 text-xs text-muted">tap to flip</span>
          </Face>
          <Face back className="bg-plasma/10 border-plasma/30">
            <div className="label mb-2 text-plasma">{c.term} — actually</div>
            <p className="text-[15px] leading-relaxed text-ink/90">{c.back}</p>
          </Face>
        </motion.button>
      </div>
      <button className={`w-full mt-6 ${flipped ? "btn-primary" : "btn-ghost"}`} onClick={next} data-testid="concept-next">
        {last ? "Lock it in" : "Next card"} <ChevronRight size={18} />
      </button>
    </div>
  );
}
function Face({ children, back, className }) {
  return (
    <div className={`absolute inset-0 rounded-2xl border p-6 flex flex-col items-start justify-center [backface-visibility:hidden] ${className}`}
      style={back ? { transform: "rotateY(180deg)" } : {}}>{children}</div>
  );
}

/* ---------------- Quiz ---------------- */
function QuizMission({ m, onDone }) {
  return (
    <div data-testid="mission-quiz">
      <div className="label mb-1">{m.title}</div>
      <p className="text-sub text-sm mb-5">{m.objective}</p>
      <QuizEngine questions={m.payload.questions} ctaLabel="Claim XP"
        onDone={({ correct, total }) => onDone(Math.round((correct / total) * 100))} />
    </div>
  );
}

/* ---------------- Myth Buster ---------------- */
function MythBuster({ m, onDone }) {
  const rounds = m.payload.rounds;
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState(null);
  const [score, setScore] = useState(0);
  const r = rounds[i];
  const last = i === rounds.length - 1;

  const pick = (idx) => {
    if (picked !== null) return;
    setPicked(idx);
    if (r.statements[idx].truth) setScore((s) => s + 1);
  };
  const next = () => {
    if (last) return onDone(Math.round((score / rounds.length) * 100));
    setPicked(null); setI((x) => x + 1);
  };

  return (
    <div data-testid="mission-mythbuster">
      <div className="label">Myth Buster · {i + 1}/{rounds.length}</div>
      <h3 className="font-head text-lg font-semibold mt-1 mb-1">Term: {r.term}</h3>
      <p className="text-sub text-sm mb-5">Tap the accurate statement — not the hype.</p>
      <div className="space-y-3">
        {r.statements.map((s, idx) => {
          let cls = "border-white/10 bg-elevated";
          if (picked !== null) {
            if (s.truth) cls = "border-ok/60 bg-ok/10";
            else if (idx === picked) cls = "border-bad/60 bg-bad/10";
          }
          return (
            <motion.button key={idx} whileTap={{ scale: 0.98 }} onClick={() => pick(idx)} data-testid={`myth-option-${idx}`}
              className={`w-full text-left rounded-xl border p-4 text-[15px] leading-snug ${cls}`}>
              {s.text}
            </motion.button>
          );
        })}
      </div>
      {picked !== null && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className={`mt-4 text-sm font-head ${r.statements[picked].truth ? "text-ok" : "text-sub"}`}>
          {r.statements[picked].truth ? "Accurate — myth busted." : "That's the hype. The accurate one is highlighted."}
        </motion.div>
      )}
      <button className={`w-full mt-5 ${picked !== null ? "btn-primary" : "btn-ghost opacity-50 pointer-events-none"}`}
        onClick={next} data-testid="myth-next">{last ? "Claim XP" : "Next"} <ArrowRight size={18} /></button>
    </div>
  );
}

/* ---------------- Build / Lab ---------------- */
function BuildMission({ m, onDone }) {
  const p = m.payload;
  const [showEx, setShowEx] = useState(false);
  return (
    <div data-testid="mission-build">
      <div className="label">Build It · explain-it-like-you're-building</div>
      <h3 className="font-head text-xl font-semibold mt-1 mb-3">{m.title}</h3>
      {p.concept && <p className="text-ink/85 leading-relaxed mb-4">{p.concept}</p>}
      {p.code && <CodeBlock code={p.code.code} lang={p.code.lang} />}
      {p.exercises?.length > 0 && (
        <div className="mt-4">
          <button onClick={() => setShowEx((s) => !s)} className="btn-ghost w-full" data-testid="toggle-exercises">
            <Lightbulb size={16} /> {showEx ? "Hide" : "Show"} practice tasks
          </button>
          {showEx && (
            <ul className="mt-3 space-y-2">
              {p.exercises.map((e, i) => (
                <li key={i} className="card p-3 text-sm text-sub flex gap-2"><span className="text-arcane">{i + 1}.</span>{e}</li>
              ))}
            </ul>
          )}
        </div>
      )}
      <button className="btn-primary w-full mt-6" onClick={() => onDone(100)} data-testid="build-done">
        <Check size={18} /> Locked in — claim XP
      </button>
    </div>
  );
}

/* ---------------- Boss ---------------- */
function BossMission({ m, onDone }) {
  const p = m.payload;
  const [phase, setPhase] = useState("intro"); // intro | fight | win | lose
  const [result, setResult] = useState(null);

  if (phase === "intro") {
    return (
      <div className="text-center" data-testid="boss-intro">
        <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ repeat: Infinity, duration: 2 }}
          className="mx-auto h-24 w-24 rounded-2xl bg-arcane/15 text-arcane flex items-center justify-center mb-4 shadow-glow font-display text-4xl">⚔</motion.div>
        <div className="label">Boss Battle</div>
        <h2 className="font-display text-2xl mt-1 mb-2">{m.title.replace("Boss: ", "")}</h2>
        <p className="text-sub text-sm mb-6">Clear {p.pass_threshold}/{p.questions.length} to win. Wrong answers won't hurt you — just retry.</p>
        <button className="btn-primary w-full" onClick={() => setPhase("fight")} data-testid="boss-start">Enter the arena</button>
      </div>
    );
  }
  if (phase === "fight") {
    return (
      <div data-testid="boss-fight">
        <QuizEngine questions={p.questions} ctaLabel="Finish boss"
          onDone={({ correct, total }) => {
            const passed = correct >= p.pass_threshold;
            setResult({ correct, total, passed });
            setPhase(passed ? "win" : "lose");
          }} />
      </div>
    );
  }
  if (phase === "lose") {
    return (
      <div className="text-center" data-testid="boss-lose">
        <div className="mx-auto h-20 w-20 rounded-2xl bg-bad/10 text-bad flex items-center justify-center mb-4 text-3xl">↺</div>
        <h2 className="font-head text-xl font-bold mb-2">So close — {result.correct}/{result.total}</h2>
        <p className="text-sub text-sm mb-6">No penalty. Review the concept and try again — you've got this.</p>
        <button className="btn-primary w-full" onClick={() => setPhase("fight")} data-testid="boss-retry"><RotateCw size={16} /> Retry boss</button>
      </div>
    );
  }
  return (
    <div className="text-center" data-testid="boss-win">
      <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="mx-auto h-24 w-24 rounded-2xl bg-plasma/15 text-plasma flex items-center justify-center mb-4 font-display text-4xl shadow-glowc">★</motion.div>
      <h2 className="font-display text-2xl mb-2">Boss Defeated!</h2>
      <p className="text-sub text-sm">{result.correct}/{result.total} correct</p>
      {p.recap?.length > 0 && (
        <div className="card p-4 mt-5 text-left">
          <div className="label mb-2">Level recap — what you forged</div>
          <ul className="space-y-2">
            {p.recap.map((o, i) => <li key={i} className="flex gap-2 text-sm text-sub"><Check size={14} className="text-plasma mt-0.5 shrink-0" />{o}</li>)}
          </ul>
        </div>
      )}
      <button className="btn-plasma w-full mt-6" onClick={() => onDone(Math.round((result.correct / result.total) * 100))} data-testid="boss-claim">
        Seal the skill — claim XP
      </button>
    </div>
  );
}
