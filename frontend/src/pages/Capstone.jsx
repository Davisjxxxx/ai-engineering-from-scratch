import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import TopHud from "../components/TopHud";
import * as Lucide from "lucide-react";
import { Boxes, Check, X, RotateCw, Sparkles, ArrowLeft } from "lucide-react";

function pascal(s) { return (s || "box").split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(""); }

export default function Capstone() {
  const nav = useNavigate();
  const { applyResult } = useApp();
  const [data, setData] = useState(null);
  const [capstone, setCapstone] = useState(null);
  const [sel, setSel] = useState([]);
  const [result, setResult] = useState(null);

  useEffect(() => { api.capstones().then(setData); }, []);
  if (!data) return <div className="min-h-screen flex items-center justify-center text-sub">Loading…</div>;

  const toggle = (id) => { setResult(null); setSel((s) => s.includes(id) ? s.filter((x) => x !== id) : [...s, id]); };
  const validate = async () => {
    const res = await api.validateCapstone(capstone.id, sel);
    setResult(res);
    if (res.passed) applyResult(res);
  };

  if (!capstone) {
    return (
      <div className="pb-nav">
        <TopHud title="Capstone Simulator" subtitle="Build a full agentic system" />
        <div className="px-4 pt-4 space-y-3">
          <p className="text-sub text-sm px-1">Pick a system to architect. Assemble the right pattern blocks and validate your design.</p>
          {data.capstones.map((c, i) => (
            <motion.button key={c.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
              onClick={() => { setCapstone(c); setSel([]); setResult(null); }} data-testid={`capstone-${c.id}`}
              className="card p-4 w-full text-left flex items-center gap-4 active:scale-[0.99] transition-transform">
              <div className="h-12 w-12 rounded-xl bg-arcane/15 text-arcane flex items-center justify-center shrink-0"><Boxes size={22} /></div>
              <div className="flex-1 min-w-0">
                <div className="font-head font-semibold">{c.title}</div>
                <div className="text-xs text-muted">{c.brief}</div>
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="pb-nav">
      <header className="sticky top-0 z-40 glass pt-safe">
        <div className="px-4 py-3 flex items-center gap-3">
          <button onClick={() => { setCapstone(null); setResult(null); }} data-testid="capstone-back" className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center"><ArrowLeft size={18} /></button>
          <div className="min-w-0"><div className="label">Capstone</div><h1 className="font-head font-bold truncate">{capstone.title}</h1></div>
        </div>
      </header>
      <div className="px-4 pt-4 space-y-4">
        <div className="card p-4"><p className="text-sub text-sm">{capstone.brief}</p></div>
        <div className="label px-1">Drag in your pattern blocks</div>
        <div className="grid grid-cols-2 gap-2">
          {data.blocks.map((b) => {
            const Icon = Lucide[pascal(b.icon)] || Boxes;
            const picked = sel.includes(b.id);
            return (
              <button key={b.id} onClick={() => toggle(b.id)} data-testid={`block-${b.id}`}
                className={`rounded-xl border p-3 flex items-center gap-2 text-sm text-left ${picked ? "border-plasma bg-plasma/10 text-plasma" : "border-white/10 bg-elevated text-sub"}`}>
                <Icon size={16} className="shrink-0" /> <span className="truncate">{b.label}</span>
                {picked && <Check size={14} className="ml-auto shrink-0" />}
              </button>
            );
          })}
        </div>

        {result && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            className={`card p-4 ${result.passed ? "border-ok/30" : "border-arcane/30"}`} data-testid="capstone-result">
            <div className={`font-head font-semibold flex items-center gap-2 ${result.passed ? "text-ok" : "text-arcane"}`}>
              {result.passed ? <Sparkles size={18} /> : <X size={18} />} {result.passed ? "Production-shaped!" : `Design score ${result.score}%`}
            </div>
            <ul className="mt-2 space-y-1">
              {result.feedback.map((f, idx) => <li key={idx} className="text-sm text-sub">• {f}</li>)}
            </ul>
          </motion.div>
        )}

        {result?.passed ? (
          <button className="btn-plasma w-full" onClick={() => { setCapstone(null); setResult(null); }} data-testid="capstone-done">Build another system</button>
        ) : (
          <button className="btn-primary w-full" onClick={validate} disabled={sel.length === 0} data-testid="capstone-validate">
            {result ? <><RotateCw size={16} /> Re-validate</> : "Validate architecture"}
          </button>
        )}
      </div>
    </div>
  );
}
