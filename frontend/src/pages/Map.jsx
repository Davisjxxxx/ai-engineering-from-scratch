import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import TopHud from "../components/TopHud";
import ProgressRing from "../components/ProgressRing";
import { Lock, Check, ChevronDown, ChevronRight, Clock } from "lucide-react";

export default function MapPage() {
  const [data, setData] = useState(null);
  const [open, setOpen] = useState(null);

  useEffect(() => {
    api.campaign().then((d) => {
      setData(d);
      const firstActive = d.worlds.find((w) => w.unlocked && w.completed_levels < w.level_count);
      setOpen(firstActive ? firstActive.id : d.worlds[0].id);
    });
  }, []);

  if (!data) return <Loading />;

  return (
    <div className="pb-nav">
      <TopHud title="Campaign Map" subtitle="Forge your path" />
      <div className="px-4 pt-4 space-y-3">
        {data.worlds.map((w, i) => {
          const pct = Math.round((w.completed_levels / w.level_count) * 100);
          const expanded = open === w.id;
          return (
            <motion.div key={w.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}
              className="card overflow-hidden">
              <button
                data-testid={`world-${w.id}`}
                onClick={() => setOpen(expanded ? null : w.id)}
                className="w-full flex items-center gap-4 p-4 text-left">
                <ProgressRing value={pct} label={`${pct}%`} color={w.unlocked ? "#F59E0B" : "#475569"} />
                <div className="flex-1 min-w-0">
                  <div className="label">World {w.order} · {w.short}</div>
                  <div className="font-head font-bold text-lg truncate">{w.name}</div>
                  <div className="text-xs text-muted">{w.completed_levels}/{w.level_count} levels cleared</div>
                </div>
                {expanded ? <ChevronDown className="text-muted" /> : <ChevronRight className="text-muted" />}
              </button>

              {expanded && (
                <div className="px-3 pb-3 space-y-2">
                  {w.levels.map((lv) => (
                    <LevelRow key={lv.id} lv={lv} />
                  ))}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

function LevelRow({ lv }) {
  const locked = !lv.unlocked;
  const body = (
    <div data-testid={`level-row-${lv.id}`}
      className={`flex items-center gap-3 rounded-xl p-3 border ${
        locked ? "border-white/5 bg-base/40 opacity-60" :
        lv.completed ? "border-plasma/25 bg-plasma/5" : "border-arcane/30 bg-elevated"}`}>
      <div className={`h-10 w-10 rounded-lg flex items-center justify-center shrink-0 ${
        locked ? "bg-white/5 text-muted" : lv.completed ? "bg-plasma/15 text-plasma" : "bg-arcane/15 text-arcane"}`}>
        {locked ? <Lock size={16} /> : lv.completed ? <Check size={18} /> : <span className="font-head font-bold">{lv.order}</span>}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-head font-semibold text-sm truncate">{lv.title}</div>
        <div className="text-[11px] text-muted flex items-center gap-2">
          <span className="inline-flex items-center gap-1"><Clock size={11} />~{lv.estimated_minutes}m</span>
          <span>· {lv.missions_completed}/{lv.mission_count} missions</span>
        </div>
      </div>
      {!locked && lv.progress > 0 && !lv.completed && (
        <div className="w-10 h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full bg-arcane" style={{ width: `${lv.progress}%` }} />
        </div>
      )}
    </div>
  );
  return locked ? body : <Link to={`/level/${encodeURIComponent(lv.id)}`}>{body}</Link>;
}

function Loading() {
  return <div className="min-h-screen flex items-center justify-center text-sub">Loading map…</div>;
}
