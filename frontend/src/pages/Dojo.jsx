import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import { X, ArrowRight, RotateCw, Swords } from "lucide-react";

export default function Dojo() {
  const { pathId } = useParams();
  const nav = useNavigate();
  const { applyResult } = useApp();
  const [rounds, setRounds] = useState(null);
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState(null);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);

  const load = () => api.dojo(pathId).then((d) => { setRounds(d.rounds); setI(0); setPicked(null); setScore(0); setDone(false); });
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [pathId]);

  if (!rounds) return <div className="min-h-screen flex items-center justify-center text-sub">Loading dojo…</div>;

  const r = rounds[i];
  const last = i === rounds.length - 1;

  const pick = (idx) => {
    if (picked !== null) return;
    setPicked(idx);
    if (r.options[idx].correct) setScore((s) => s + 1);
  };
  const next = async () => {
    if (last) {
      const res = await api.dojoResult(pathId, { correct: score });
      applyResult(res);
      setDone(true);
      return;
    }
    setPicked(null); setI((x) => x + 1);
  };

  if (done) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-8 text-center">
        <div className="h-20 w-20 rounded-2xl bg-arcane/15 text-arcane flex items-center justify-center mb-4"><Swords size={34} /></div>
        <h2 className="font-display text-2xl mb-1">Dojo cleared</h2>
        <p className="text-sub mb-6">{score}/{rounds.length} correct</p>
        <button className="btn-primary w-full max-w-xs mb-2" onClick={load} data-testid="dojo-again"><RotateCw size={16} /> New round</button>
        <button className="btn-ghost w-full max-w-xs" onClick={() => nav(`/academy/${pathId}`)}>Back to Academy</button>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 glass pt-safe">
        <div className="px-4 py-3 flex items-center gap-3">
          <button onClick={() => nav(`/academy/${pathId}`)} data-testid="dojo-exit" className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center"><X size={18} /></button>
          <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-arcane to-yellow-300" style={{ width: `${((i + 1) / rounds.length) * 100}%` }} />
          </div>
          <span className="chip !text-arcane">{score}✓</span>
        </div>
      </header>
      <main className="flex-1 px-4 py-5 max-w-md w-full mx-auto" data-testid="dojo-round">
        <div className="label">Pattern Dojo · {i + 1}/{rounds.length}</div>
        <div className="card p-4 mt-2 mb-4">
          <div className="label mb-1 text-arcane">Scenario</div>
          <p className="text-ink/90 leading-snug">{r.scenario}</p>
        </div>
        <p className="text-sub text-sm mb-3">Best pattern?</p>
        <div className="space-y-3">
          {r.options.map((opt, idx) => {
            let cls = "border-white/10 bg-elevated";
            if (picked !== null) {
              if (opt.correct) cls = "border-ok/60 bg-ok/10";
              else if (idx === picked) cls = "border-bad/60 bg-bad/10";
            }
            return (
              <motion.button key={idx} whileTap={{ scale: 0.98 }} onClick={() => pick(idx)} data-testid={`dojo-option-${idx}`}
                className={`w-full text-left rounded-xl border p-4 text-[15px] ${cls}`}>{opt.text}</motion.button>
            );
          })}
        </div>
        {picked !== null && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className={`mt-4 rounded-xl p-4 text-sm ${r.options[picked].correct ? "bg-ok/10 text-ok" : "bg-white/5 text-sub"}`}>
            {r.options[picked].feedback}
          </motion.div>
        )}
        <button className={`w-full mt-5 ${picked !== null ? "btn-primary" : "btn-ghost opacity-50 pointer-events-none"}`}
          onClick={next} data-testid="dojo-next">{last ? "Finish" : "Next"} <ArrowRight size={18} /></button>
      </main>
    </div>
  );
}
