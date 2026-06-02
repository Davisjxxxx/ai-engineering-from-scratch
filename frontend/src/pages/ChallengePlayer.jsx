import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import { X, Check, RotateCw, Lightbulb, ArrowRight } from "lucide-react";

export default function ChallengePlayer() {
  const { id } = useParams();
  const nav = useNavigate();
  const { applyResult } = useApp();
  const [c, setC] = useState(null);
  const [sel, setSel] = useState([]);
  const [jsonText, setJsonText] = useState("");
  const [result, setResult] = useState(null);
  const [hintIdx, setHintIdx] = useState(0);

  useEffect(() => {
    api.challenges().then((list) => {
      const found = list.find((x) => x.id === id);
      setC(found);
      if (found?.kind === "edit-json") setJsonText(found.broken_state);
    });
  }, [id]);

  if (!c) return <div className="min-h-screen flex items-center justify-center text-sub">Loading…</div>;

  const toggle = (i) => {
    if (c.kind === "select-one") setSel([i]);
    else setSel((s) => (s.includes(i) ? s.filter((x) => x !== i) : [...s, i]));
  };

  const submit = async () => {
    const answer = c.kind === "edit-json" ? jsonText : c.kind === "select-one" ? sel[0] : sel;
    const res = await api.attemptChallenge(id, answer);
    setResult(res);
    if (res.passed) applyResult(res);
  };

  const retry = () => { setResult(null); setSel([]); if (c.kind === "edit-json") setJsonText(c.broken_state); };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 glass pt-safe">
        <div className="px-4 py-3 flex items-center gap-3">
          <button onClick={() => nav("/arena")} data-testid="challenge-exit" className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center"><X size={18} /></button>
          <div className="min-w-0"><div className="label">{c.skill.replace("-", " ")}</div>
            <h1 className="font-head font-bold truncate">{c.title}</h1></div>
          <span className="chip !text-arcane !bg-arcane/10 !border-arcane/30 ml-auto">+{c.xp}</span>
        </div>
      </header>

      <main className="flex-1 px-4 py-5 max-w-md w-full mx-auto">
        <div className="card p-4 mb-4">
          <p className="text-ink/90 leading-relaxed">{c.scenario}</p>
          {c.broken_state && c.kind !== "edit-json" && (
            <pre className="mt-3 font-mono text-xs bg-black/50 rounded-lg p-3 text-bad/90 whitespace-pre-wrap">{c.broken_state}</pre>
          )}
        </div>

        {c.kind === "edit-json" ? (
          <div>
            <div className="label mb-1.5">Fix the JSON (keep keys: name, tools, safe)</div>
            <textarea data-testid="json-editor" value={jsonText} onChange={(e) => setJsonText(e.target.value)} rows={5}
              className="w-full bg-black/60 border border-white/10 rounded-xl p-3 font-mono text-[13px] text-plasma outline-none focus:border-arcane/50" />
          </div>
        ) : (
          <div className="space-y-3">
            {c.options.map((opt, i) => {
              const picked = sel.includes(i);
              return (
                <motion.button key={i} whileTap={{ scale: 0.98 }} onClick={() => toggle(i)} disabled={result?.passed}
                  data-testid={`option-${i}`}
                  className={`w-full text-left rounded-xl border p-4 text-[15px] flex items-center gap-3 ${
                    picked ? "border-arcane bg-arcane/10" : "border-white/10 bg-elevated"}`}>
                  <span className={`h-5 w-5 rounded-${c.kind === "select-one" ? "full" : "md"} border flex items-center justify-center shrink-0 ${picked ? "border-arcane bg-arcane text-base" : "border-white/25"}`}>
                    {picked && <Check size={13} />}
                  </span>
                  {opt}
                </motion.button>
              );
            })}
          </div>
        )}

        {/* Hints */}
        {!result?.passed && c.hints?.length > 0 && (
          <div className="mt-4">
            <button onClick={() => setHintIdx((h) => Math.min(h + 1, c.hints.length))} data-testid="hint-btn" className="btn-ghost w-full">
              <Lightbulb size={16} /> {hintIdx === 0 ? "Need a hint?" : hintIdx < c.hints.length ? "Another hint" : "No more hints"}
            </button>
            {hintIdx > 0 && (
              <ul className="mt-2 space-y-1">
                {c.hints.slice(0, hintIdx).map((h, i) => <li key={i} className="text-sm text-arcane/90 flex gap-2"><span>💡</span>{h}</li>)}
              </ul>
            )}
          </div>
        )}

        {result && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            className={`mt-4 rounded-xl p-4 ${result.passed ? "bg-ok/10" : "bg-bad/10"}`} data-testid="challenge-result">
            <div className={`font-head font-semibold flex items-center gap-2 ${result.passed ? "text-ok" : "text-bad"}`}>
              {result.passed ? <Check size={18} /> : <RotateCw size={18} />} {result.passed ? "Solved!" : "Not yet"}
            </div>
            <p className="text-sm text-ink/80 mt-1">{result.feedback}</p>
          </motion.div>
        )}

        <div className="mt-5">
          {result?.passed ? (
            <button className="btn-plasma w-full" onClick={() => nav("/arena")} data-testid="challenge-done">Back to Arena <ArrowRight size={18} /></button>
          ) : result ? (
            <button className="btn-primary w-full" onClick={retry} data-testid="challenge-retry"><RotateCw size={16} /> Retry — no penalty</button>
          ) : (
            <button className="btn-primary w-full" onClick={submit} disabled={c.kind !== "edit-json" && sel.length === 0} data-testid="challenge-submit">Submit</button>
          )}
        </div>
      </main>
    </div>
  );
}
