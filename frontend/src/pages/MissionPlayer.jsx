import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import QuizEngine from "../components/QuizEngine";
import CodeBlock from "../components/CodeBlock";
import { X, ArrowRight, RotateCw, Check, Lightbulb, ChevronRight } from "lucide-react";
import * as Lucide from "lucide-react";

function pascal(s) { return (s || "box").split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(""); }

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
            {mission.type === "watch" && <WatchMission m={mission} onDone={finish} />}
            {mission.type === "mentalmodel" && <MentalModel m={mission} onDone={finish} />}
            {mission.type === "drill" && <DrillMission m={mission} onDone={finish} />}
            {mission.type === "lab" && <LabMission m={mission} onDone={finish} />}
            {mission.type === "debug" && <DebugMission m={mission} onDone={finish} />}
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

/* ---------------- Watch (Strang video lecture) ---------------- */
function WatchMission({ m, onDone }) {
  const p = m.payload;
  const [started, setStarted] = useState(false);
  return (
    <div data-testid="mission-watch">
      <div className="label">Watch · MIT 18.06</div>
      <h3 className="font-head text-lg font-semibold mt-1 mb-3 leading-snug">{p.title}</h3>
      <div className="rounded-xl overflow-hidden border border-white/10 bg-black aspect-video">
        <iframe
          title={p.title}
          src={`https://www.youtube.com/embed/${p.youtube_id}?rel=0`}
          className="w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          onLoad={() => setStarted(true)}
          data-testid="watch-iframe"
        />
      </div>
      {p.watch_for?.length > 0 && (
        <div className="card p-4 mt-4">
          <div className="label mb-2 flex items-center gap-1.5"><Lightbulb size={13} /> Watch for</div>
          <ul className="space-y-2">
            {p.watch_for.map((w, i) => (
              <li key={i} className="flex gap-2 text-sm text-sub"><span className="text-plasma mt-0.5">▸</span>{w}</li>
            ))}
          </ul>
        </div>
      )}
      <button className="btn-primary w-full mt-6" onClick={() => onDone(100)} data-testid="watch-done">
        <Check size={18} /> I watched it — claim XP
      </button>
    </div>
  );
}

/* ---------------- Mental Model ---------------- */
function MentalModel({ m, onDone }) {
  const p = m.payload;
  const Icon = Lucide[pascal(p.icon)] || Lucide.Boxes;
  return (
    <div data-testid="mission-mentalmodel">
      <div className="label">Mental Model</div>
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        className="card p-6 mt-2 text-center bg-gradient-to-br from-plasma/10 to-surface">
        <div className="mx-auto h-20 w-20 rounded-2xl bg-plasma/15 text-plasma flex items-center justify-center mb-3 shadow-glowc">
          <Icon size={38} />
        </div>
        <div className="label text-plasma">{p.pattern}</div>
        <h2 className="font-display text-2xl mt-1">{p.metaphor}</h2>
      </motion.div>
      <ul className="mt-4 space-y-2">
        {p.points.map((pt, i) => (
          <motion.li key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
            className="card p-3 flex gap-2 text-sm text-ink/85"><span className="text-plasma mt-0.5">▸</span>{pt}</motion.li>
        ))}
      </ul>
      {p.mistake && (
        <div className="mt-4 rounded-xl bg-bad/10 border border-bad/20 p-3">
          <div className="text-xs font-head font-semibold text-bad flex items-center gap-1.5 mb-1">
            <Lucide.AlertTriangle size={13} /> Common mistake
          </div>
          <p className="text-sm text-ink/80">{p.mistake}</p>
        </div>
      )}
      {p.mini_challenge && (
        <div className="mt-4 rounded-xl bg-plasma/10 border border-plasma/25 p-3">
          <div className="text-xs font-head font-semibold text-plasma flex items-center gap-1.5 mb-1">
            <Lucide.Zap size={13} /> Try it now
          </div>
          <p className="text-sm text-ink/80">{p.mini_challenge}</p>
        </div>
      )}
      <button className="btn-primary w-full mt-6" onClick={() => onDone(100)} data-testid="mentalmodel-done">
        <Check size={18} /> Lock it in
      </button>
    </div>
  );
}

/* ---------------- Pattern Selection Drill (with hints) ---------------- */
function DrillMission({ m, onDone }) {
  const rounds = m.payload.rounds;
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState(null);
  const [score, setScore] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const r = rounds[i];
  const last = i === rounds.length - 1;
  const maxAttempts = 2;

  const pick = (idx) => {
    if (picked !== null && r.options[picked].correct) return;
    if (attempts >= maxAttempts) return;
    setPicked(idx);
    setAttempts((a) => a + 1);
    if (r.options[idx].correct) setScore((s) => s + 1);
  };
  const next = () => {
    if (last) return onDone(Math.round((score / rounds.length) * 100));
    setPicked(null); setI((x) => x + 1); setShowHint(false); setAttempts(0);
  };
  const retry = () => { setPicked(null); setShowHint(false); };

  const revealed = picked !== null && (r.options[picked]?.correct || attempts >= maxAttempts);
  const correctOpt = r.options.find((o) => o.correct);

  return (
    <div data-testid="mission-drill">
      <div className="label">Pattern Selection · {i + 1}/{rounds.length}</div>
      <div className="card p-4 mt-2 mb-4">
        <div className="label mb-1 text-arcane">Scenario</div>
        <p className="text-ink/90 leading-snug">{r.scenario}</p>
      </div>
      <p className="text-sub text-sm mb-3">Which pattern fits best?</p>
      <div className="space-y-3">
        {r.options.map((opt, idx) => {
          let cls = "border-white/10 bg-elevated";
          if (revealed && opt.correct) cls = "border-ok/60 bg-ok/10";
          else if (picked === idx && !opt.correct) cls = "border-bad/60 bg-bad/10";
          return (
            <motion.button key={idx} whileTap={{ scale: 0.98 }} onClick={() => pick(idx)}
              disabled={revealed}
              data-testid={`drill-option-${idx}`}
              className={`w-full text-left rounded-xl border p-4 text-[15px] leading-snug ${cls} ${revealed && !opt.correct ? "opacity-50" : ""}`}>
              {opt.text}
            </motion.button>
          );
        })}
      </div>

      {/* Hint system */}
      {!revealed && attempts >= 1 && (r.hint1 || r.hint2) && (
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
          className="mt-4 rounded-xl p-4 bg-arcane/10 border border-arcane/25 text-sm">
          <div className="flex items-center gap-2 font-head font-semibold text-arcane mb-1">
            <Lightbulb size={16} /> Hint {attempts}
          </div>
          <p className="text-ink/80">{attempts === 1 ? r.hint1 : r.hint2 || r.hint1}</p>
        </motion.div>
      )}

      {/* Reveal after 2 attempts */}
      {revealed && picked !== null && (
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
          className={`mt-4 rounded-xl p-4 text-sm ${r.options[picked]?.correct ? "bg-ok/10 text-ok" : "bg-white/5 text-sub"}`}>
          <div className="font-head font-semibold mb-1">
            {r.options[picked]?.correct ? "Correct — well done." : "Here's the best answer:"}
          </div>
          <div className="text-ink/80">{correctOpt?.feedback || r.explain}</div>
          {!r.options[picked]?.correct && (
            <div className="text-ok mt-2 font-head">✓ Best: {correctOpt?.text}</div>
          )}
        </motion.div>
      )}

      <div className="flex gap-2 mt-5">
        {!revealed && picked !== null && (
          <button className="btn-ghost flex-1" onClick={retry} data-testid="drill-retry">
            <RotateCw size={16} /> Try again
          </button>
        )}
        {revealed && (
          <button className="btn-primary w-full" onClick={next} data-testid="drill-next">
            {last ? "Claim XP" : "Next"} <ArrowRight size={18} />
          </button>
        )}
      </div>
    </div>
  );
}

/* ---------------- Build Lab (order / select) ---------------- */
function LabMission({ m, onDone }) {
  const p = m.payload;
  return p.kind === "order" ? <OrderLab p={p} onDone={onDone} /> : <SelectLab p={p} onDone={onDone} />;
}

function OrderLab({ p, onDone }) {
  const [pool] = useState(() => {
    const arr = [...p.steps];
    for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [arr[i], arr[j]] = [arr[j], arr[i]]; }
    return arr;
  });
  const [seq, setSeq] = useState([]);
  const [result, setResult] = useState(null);

  const add = (s) => { if (!seq.find((x) => x.id === s.id)) setSeq([...seq, s]); };
  const reset = () => { setSeq([]); setResult(null); };
  const check = () => {
    const ok = seq.length === p.correct_order.length && seq.every((s, i) => s.id === p.correct_order[i]);
    setResult(ok);
  };

  return (
    <div data-testid="mission-lab">
      <div className="label">Build Lab · order the steps</div>
      <p className="text-sub text-sm mt-1 mb-3">{p.prompt}</p>
      <div className="card p-3 min-h-[80px] mb-3">
        <div className="label mb-2">Your pipeline</div>
        {seq.length === 0 ? <p className="text-muted text-sm">Tap steps below in order…</p> : (
          <div className="space-y-2">
            {seq.map((s, i) => (
              <div key={s.id} className="flex items-center gap-2 bg-elevated rounded-lg p-2.5 text-sm">
                <span className="h-6 w-6 rounded-full bg-arcane/15 text-arcane flex items-center justify-center text-xs font-bold">{i + 1}</span>
                {s.label}
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="flex flex-wrap gap-2 mb-3">
        {pool.map((s) => {
          const used = seq.find((x) => x.id === s.id);
          return (
            <button key={s.id} onClick={() => add(s)} disabled={!!used} data-testid={`lab-step-${s.id}`}
              className={`chip ${used ? "opacity-30" : "!bg-plasma/10 !text-plasma !border-plasma/30"}`}>{s.label}</button>
          );
        })}
      </div>
      {result === null ? (
        <div className="flex gap-2">
          <button className="btn-primary flex-1" onClick={check} disabled={seq.length !== pool.length} data-testid="lab-validate">Validate</button>
          {seq.length > 0 && <button className="btn-ghost" onClick={reset}><RotateCw size={16} /></button>}
        </div>
      ) : result ? (
        <div>
          <div className="rounded-xl bg-ok/10 text-ok p-4 text-sm font-head" data-testid="lab-success">✓ {p.success}</div>
          <button className="btn-plasma w-full mt-4" onClick={() => onDone(100)} data-testid="lab-claim">Claim XP <ArrowRight size={18} /></button>
        </div>
      ) : (
        <div>
          <div className="rounded-xl bg-bad/10 text-bad p-4 text-sm">Not quite — check the order. No penalty, try again.</div>
          <button className="btn-primary w-full mt-3" onClick={reset} data-testid="lab-retry"><RotateCw size={16} /> Retry</button>
        </div>
      )}
    </div>
  );
}

function SelectLab({ p, onDone }) {
  const [sel, setSel] = useState([]);
  const [result, setResult] = useState(null);
  const toggle = (id) => setSel((s) => s.includes(id) ? s.filter((x) => x !== id) : [...s, id]);
  const check = () => setResult([...sel].sort().join() === [...p.required].sort().join());
  return (
    <div data-testid="mission-lab">
      <div className="label">Build Lab · select components</div>
      <p className="text-sub text-sm mt-1 mb-3">{p.prompt}</p>
      <div className="space-y-2 mb-3">
        {p.blocks.map((b) => {
          const picked = sel.includes(b.id);
          return (
            <motion.button key={b.id} whileTap={{ scale: 0.98 }} onClick={() => toggle(b.id)} disabled={result !== null}
              data-testid={`lab-block-${b.id}`}
              className={`w-full text-left rounded-xl border p-3.5 text-[15px] flex items-center gap-3 ${picked ? "border-plasma bg-plasma/10" : "border-white/10 bg-elevated"}`}>
              <span className={`h-5 w-5 rounded-md border flex items-center justify-center shrink-0 ${picked ? "border-plasma bg-plasma text-base" : "border-white/25"}`}>
                {picked && <Check size={13} />}
              </span>
              {b.label}
            </motion.button>
          );
        })}
      </div>
      {result === null ? (
        <button className="btn-primary w-full" onClick={check} disabled={sel.length === 0} data-testid="lab-validate">Validate build</button>
      ) : result ? (
        <div>
          <div className="rounded-xl bg-ok/10 text-ok p-4 text-sm font-head" data-testid="lab-success">✓ {p.success}</div>
          <button className="btn-plasma w-full mt-4" onClick={() => onDone(100)} data-testid="lab-claim">Claim XP <ArrowRight size={18} /></button>
        </div>
      ) : (
        <div>
          <div className="rounded-xl bg-bad/10 text-bad p-4 text-sm">Not the right set — too many or too few. Retry, no penalty.</div>
          <button className="btn-primary w-full mt-3" onClick={() => setResult(null)} data-testid="lab-retry"><RotateCw size={16} /> Retry</button>
        </div>
      )}
    </div>
  );
}

/* ---------------- Debug Challenge ---------------- */
function DebugMission({ m, onDone }) {
  const p = m.payload;
  const [picked, setPicked] = useState(null);
  const correct = picked === p.answer;
  return (
    <div data-testid="mission-debug">
      <div className="label">Broken Agent · {p.failure_mode}</div>
      <div className="card p-4 mt-2 mb-3">
        <p className="text-ink/90 leading-snug">{p.scenario}</p>
        {p.broken && <pre className="mt-3 font-mono text-xs bg-black/50 rounded-lg p-3 text-bad/90 whitespace-pre-wrap">{p.broken}</pre>}
      </div>
      <p className="text-sub text-sm mb-3">Choose the fix:</p>
      <div className="space-y-3">
        {p.options.map((opt, idx) => {
          let cls = "border-white/10 bg-elevated";
          if (picked !== null) {
            if (idx === p.answer) cls = "border-ok/60 bg-ok/10";
            else if (idx === picked) cls = "border-bad/60 bg-bad/10";
          }
          return (
            <motion.button key={idx} whileTap={{ scale: 0.98 }} onClick={() => picked === null && setPicked(idx)} data-testid={`debug-option-${idx}`}
              className={`w-full text-left rounded-xl border p-4 text-[15px] leading-snug ${cls}`}>{opt}</motion.button>
          );
        })}
      </div>
      {picked !== null && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className={`mt-4 rounded-xl p-4 text-sm ${correct ? "bg-ok/10 text-ok" : "bg-white/5 text-sub"}`}>
          <div className="font-head font-semibold mb-1">{correct ? "Fixed!" : "Not the best fix"}</div>
          <div className="text-ink/80">{p.explain}</div>
        </motion.div>
      )}
      {picked !== null && (
        correct ? (
          <button className="btn-primary w-full mt-5" onClick={() => onDone(100)} data-testid="debug-claim">Claim XP <ArrowRight size={18} /></button>
        ) : (
          <button className="btn-primary w-full mt-5" onClick={() => setPicked(null)} data-testid="debug-retry"><RotateCw size={16} /> Retry — no penalty</button>
        )
      )}
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
      {p.analogy && (
        <div className="card p-4 mt-4 bg-gradient-to-br from-plasma/10 to-surface">
          <div className="label text-plasma mb-1">Think of it like</div>
          <p className="text-ink/85 text-sm leading-relaxed">{p.analogy}</p>
        </div>
      )}
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
      {p.common_trap && (
        <div className="mt-4 rounded-xl bg-bad/10 border border-bad/20 p-3">
          <div className="text-xs font-head font-semibold text-bad flex items-center gap-1.5 mb-1">
            <Lucide.AlertTriangle size={13} /> Common trap
          </div>
          <p className="text-sm text-ink/80">{p.common_trap}</p>
        </div>
      )}
      {p.mini_challenge && (
        <div className="mt-4 rounded-xl bg-plasma/10 border border-plasma/25 p-3">
          <div className="text-xs font-head font-semibold text-plasma flex items-center gap-1.5 mb-1">
            <Lucide.Zap size={13} /> Try it now
          </div>
          <p className="text-sm text-ink/80">{p.mini_challenge}</p>
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
  const frontLabel = m.payload.front_label || "People say";
  const revealSuffix = m.payload.reveal_suffix || "— actually";
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
      <p className="text-sub text-sm mb-4">Tap the card to reveal the answer.</p>
      <div className="[perspective:1200px]">
        <motion.button onClick={() => setFlipped((f) => !f)} data-testid="flip-card"
          className="relative w-full h-72 [transform-style:preserve-3d]"
          animate={{ rotateY: flipped ? 180 : 0 }} transition={{ duration: 0.5 }}>
          <Face className="bg-elevated border-white/10">
            <div className="label mb-2 text-arcane">{frontLabel}</div>
            <p className="font-head text-xl leading-snug text-ink/90">“{c.front}”</p>
            <span className="absolute bottom-4 text-xs text-muted">tap to flip</span>
          </Face>
          <Face back className="bg-plasma/10 border-plasma/30">
            <div className="label mb-2 text-plasma">{c.term} {revealSuffix}</div>
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
