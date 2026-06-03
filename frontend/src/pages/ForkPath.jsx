import React, { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { ArrowLeft, Check, Lock, PlayCircle, Clock, GraduationCap } from "lucide-react";

export default function ForkPath() {
  const { forkId } = useParams();
  const [fk, setFk] = useState(null);
  const nav = useNavigate();

  useEffect(() => { api.fork(forkId).then(setFk); }, [forkId]);
  if (!fk) return <div className="min-h-screen flex items-center justify-center text-sub">Loading path…</div>;

  const pct = Math.round((fk.completed_levels / fk.level_count) * 100);

  return (
    <div className="pb-nav">
      <header className="sticky top-0 z-40 glass pt-safe">
        <div className="px-4 py-3 flex items-center gap-3">
          <button onClick={() => nav(-1)} data-testid="fork-back" className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center">
            <ArrowLeft size={18} />
          </button>
          <div className="min-w-0">
            <div className="label">Alternative path</div>
            <h1 className="font-head font-bold text-lg truncate">{fk.name}</h1>
          </div>
        </div>
      </header>

      <div className="px-4 pt-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
          className="card p-5 bg-gradient-to-br from-arcane/10 to-surface">
          <div className="flex items-center gap-2 text-arcane">
            <GraduationCap size={18} />
            <span className="label !text-arcane">{fk.source}</span>
          </div>
          <p className="text-ink/90 mt-2 leading-snug">{fk.tagline}</p>
          <div className="mt-4 flex items-center gap-2">
            <div className="h-1.5 flex-1 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-arcane to-yellow-300 rounded-full" style={{ width: `${pct}%` }} />
            </div>
            <span className="text-[11px] text-muted font-mono">{fk.completed_levels}/{fk.level_count}</span>
          </div>
        </motion.div>

        <div className="label px-1">Lecture path</div>
        <div className="space-y-2">
          {fk.levels.map((lv, i) => {
            const locked = !lv.unlocked;
            const row = (
              <div data-testid={`fork-level-${lv.id}`}
                className={`flex items-center gap-3 rounded-xl p-3 border ${
                  locked ? "border-white/5 bg-base/40 opacity-60" :
                  lv.completed ? "border-plasma/25 bg-plasma/5" : "border-arcane/30 bg-elevated"}`}>
                <div className={`h-10 w-10 rounded-lg flex items-center justify-center shrink-0 ${
                  locked ? "bg-white/5 text-muted" : lv.completed ? "bg-plasma/15 text-plasma" : "bg-arcane/15 text-arcane"}`}>
                  {locked ? <Lock size={16} /> : lv.completed ? <Check size={18} /> : <PlayCircle size={18} />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-head font-semibold text-sm truncate">{lv.title}</div>
                  <div className="text-[11px] text-muted flex items-center gap-2">
                    <span className="inline-flex items-center gap-1"><Clock size={11} />~{lv.estimated_minutes}m</span>
                    <span>· {lv.missions_completed}/{lv.mission_count} steps</span>
                  </div>
                </div>
                {!locked && lv.progress > 0 && !lv.completed && (
                  <div className="w-10 h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-arcane" style={{ width: `${lv.progress}%` }} />
                  </div>
                )}
              </div>
            );
            return locked ? <div key={lv.id}>{row}</div> :
              <Link key={lv.id} to={`/level/${encodeURIComponent(lv.id)}`}>{row}</Link>;
          })}
        </div>
      </div>
    </div>
  );
}
