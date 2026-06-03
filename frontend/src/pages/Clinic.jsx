import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import { X, ArrowRight, RotateCw, Stethoscope } from "lucide-react";

export default function Clinic() {
  const { pathId } = useParams();
  const nav = useNavigate();
  const { applyResult } = useApp();
  const [cases, setCases] = useState(null);
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState(null);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);

  const load = () => api.clinic(pathId).then((d) => { setCases(d.cases); setI(0); setPicked(null); setScore(0); setDone(false); });
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [pathId]);

  if (!cases) return <div className="min-h-screen flex items-center justify-center text-sub">Loading clinic…</div>;
  const c = cases[i];
  const last = i === cases.length - 1;
  const correct = picked === c.answer;

  const pick = (idx) => { if (picked === null) { setPicked(idx); if (idx === c.answer) setScore((s) => s + 1); } };
  const next = async () => {
    if (last) { const res = await api.clinicResult(pathId, { correct: score }); applyResult(res); setDone(true); return; }
    setPicked(null); setI((x) => x + 1);
  };

  if (done) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-8 text-center">
        <div className="h-20 w-20 rounded-2xl bg-plasma/15 text-plasma flex items-center justify-center mb-4"><Stethoscope size={34} /></div>
        <h2 className="font-display text-2xl mb-1">Clinic complete</h2>
        <p className="text-sub mb-6">{score}/{cases.length} agents repaired</p>
        <button className="btn-primary w-full max-w-xs mb-2" onClick={load} data-testid="clinic-again"><RotateCw size={16} /> New cases</button>
        <button className="btn-ghost w-full max-w-xs" onClick={() => nav(`/academy/${pathId}`)}>Back to Academy</button>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 glass pt-safe">
        <div className="px-4 py-3 flex items-center gap-3">
          <button onClick={() => nav(`/academy/${pathId}`)} data-testid="clinic-exit" className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center"><X size={18} /></button>
          <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-plasma to-emerald-300" style={{ width: `${((i + 1) / cases.length) * 100}%` }} />
          </div>
          <span className="chip !text-plasma">{score}✓</span>
        </div>
      </header>
      <main className="flex-1 px-4 py-5 max-w-md w-full mx-auto" data-testid="clinic-case">
        <div className="label">Broken Agent Clinic · {i + 1}/{cases.length}</div>
        <div className="card p-4 mt-2 mb-3">
          <div className="label mb-1 text-bad">Symptom · {c.failure_mode}</div>
          <p className="text-ink/90 leading-snug">{c.scenario}</p>
          {c.broken && <pre className="mt-3 font-mono text-xs bg-black/50 rounded-lg p-3 text-bad/90 whitespace-pre-wrap">{c.broken}</pre>}
        </div>
        <p className="text-sub text-sm mb-3">Diagnose the fix:</p>
        <div className="space-y-3">
          {c.options.map((opt, idx) => {
            let cls = "border-white/10 bg-elevated";
            if (picked !== null) {
              if (idx === c.answer) cls = "border-ok/60 bg-ok/10";
              else if (idx === picked) cls = "border-bad/60 bg-bad/10";
            }
            return (
              <motion.button key={idx} whileTap={{ scale: 0.98 }} onClick={() => pick(idx)} data-testid={`clinic-option-${idx}`}
                className={`w-full text-left rounded-xl border p-4 text-[15px] ${cls}`}>{opt}</motion.button>
            );
          })}
        </div>
        {picked !== null && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className={`mt-4 rounded-xl p-4 text-sm ${correct ? "bg-ok/10 text-ok" : "bg-white/5 text-sub"}`}>
            <div className="font-head font-semibold mb-1">{correct ? "Repaired!" : "Not the root cause"}</div>
            {c.explain}
          </motion.div>
        )}
        <button className={`w-full mt-5 ${picked !== null ? "btn-primary" : "btn-ghost opacity-50 pointer-events-none"}`}
          onClick={next} data-testid="clinic-next">{last ? "Finish" : "Next"} <ArrowRight size={18} /></button>
      </main>
    </div>
  );
}
