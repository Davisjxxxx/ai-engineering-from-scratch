import React, { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import TopHud from "../components/TopHud";
import ProgressRing from "../components/ProgressRing";
import * as Lucide from "lucide-react";
import { Play, Swords, Stethoscope, Boxes, Brain, Check, Lock, ChevronRight, Target } from "lucide-react";

function pascal(s) { return (s || "box").split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(""); }

export default function AcademyHome() {
  const { pathId } = useParams();
  const [data, setData] = useState(null);
  const nav = useNavigate();

  useEffect(() => { api.academy(pathId).then(setData); }, [pathId]);
  if (!data) return <div className="min-h-screen flex items-center justify-center text-sub">Loading academy…</div>;

  const nba = data.next_action;

  return (
    <div className="pb-nav">
      <TopHud title="Patterns Academy" subtitle={data.title} />
      <div className="px-4 pt-4 space-y-5">

        {/* Next action + mastery */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="card p-5 bg-gradient-to-br from-elevated to-surface flex items-center gap-4">
          <ProgressRing value={data.overall_mastery} size={64} stroke={6} color="#F59E0B" label={`${data.overall_mastery}%`} />
          <div className="flex-1 min-w-0">
            <div className="label flex items-center gap-1.5"><Target size={12} /> Next move</div>
            {nba?.kind === "mission" ? (
              <>
                <div className="font-head font-bold leading-tight truncate">{nba.mission_title}</div>
                <div className="text-xs text-muted truncate">{nba.level_title} · ~{nba.estimated_minutes}m</div>
              </>
            ) : <div className="font-head font-bold">{nba?.label}</div>}
          </div>
        </motion.div>
        {nba?.kind === "mission" ? (
          <button onClick={() => nav(`/play/${encodeURIComponent(nba.level_id)}/${encodeURIComponent(nba.mission_id)}`)}
            className="btn-primary w-full" data-testid="academy-continue">
            <Play size={18} /> {data.completed_chapters ? "Continue" : "Start"} · {nba.mission_title}
          </button>
        ) : (
          <Link to={`/academy/${pathId}/dojo`} className="btn-primary w-full"><Swords size={18} /> Enter the Dojo</Link>
        )}

        {/* Game modes */}
        <div className="grid grid-cols-3 gap-3">
          <Mode to={`/academy/${pathId}/dojo`} icon={Swords} label="Dojo" sub="Pattern drills" testid="mode-dojo" />
          <Mode to={`/academy/${pathId}/clinic`} icon={Stethoscope} label="Clinic" sub="Fix agents" testid="mode-clinic" />
          <Mode to={`/academy/capstone`} icon={Boxes} label="Capstone" sub="Build systems" testid="mode-capstone" />
        </div>

        {/* Pattern map grouped */}
        <div className="label px-1">Pattern Map · {data.completed_chapters}/{data.chapter_count} cleared</div>
        {data.groups.map((g) => (
          <div key={g.id}>
            <div className="text-xs font-head font-semibold text-sub mb-2 px-1 uppercase tracking-wider">{g.name}</div>
            <div className="space-y-2">
              {g.nodes.map((n) => <PatternNode key={n.id} n={n} />)}
            </div>
          </div>
        ))}

        <p className="text-center text-[10px] text-muted pt-2">{data.attribution}</p>
      </div>
    </div>
  );
}

function Mode({ to, icon: Icon, label, sub, testid }) {
  return (
    <Link to={to} data-testid={testid} className="card p-3 text-center active:scale-[0.97] transition-transform">
      <div className="h-10 w-10 mx-auto rounded-xl bg-arcane/15 text-arcane flex items-center justify-center mb-2"><Icon size={20} /></div>
      <div className="font-head font-semibold text-sm">{label}</div>
      <div className="text-[10px] text-muted">{sub}</div>
    </Link>
  );
}

function PatternNode({ n }) {
  const Icon = Lucide[pascal(n.icon)] || Boxes;
  const locked = !n.unlocked;
  const body = (
    <div data-testid={`pattern-node-${n.id}`}
      className={`flex items-center gap-3 rounded-xl p-3 border ${
        locked ? "border-white/5 bg-base/40 opacity-60" :
        n.completed ? "border-plasma/25 bg-plasma/5" : "border-arcane/30 bg-elevated"}`}>
      <div className={`h-10 w-10 rounded-lg flex items-center justify-center shrink-0 ${
        locked ? "bg-white/5 text-muted" : n.completed ? "bg-plasma/15 text-plasma" : "bg-arcane/15 text-arcane"}`}>
        {locked ? <Lock size={16} /> : n.completed ? <Check size={18} /> : <Icon size={18} />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-head font-semibold text-sm truncate">{n.title}</div>
        <div className="text-[11px] text-muted truncate">{n.tagline}</div>
      </div>
      {!locked && (
        <div className="shrink-0">
          <ProgressRing value={n.progress} size={34} stroke={3} color={n.completed ? "#2EC4B6" : "#F59E0B"}
            label={n.completed ? "✓" : `${n.progress}%`} />
        </div>
      )}
    </div>
  );
  return locked ? body : <Link to={`/level/${encodeURIComponent(n.id)}`}>{body}</Link>;
}
