import React, { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { ArrowLeft, Check, Play, Lock, BookOpen, Layers, HelpCircle, Hammer, Crown, Wand2, Clock, PlayCircle, GitFork, ChevronRight } from "lucide-react";

const TYPE_META = {
  briefing: { icon: BookOpen, label: "Learn", color: "plasma" },
  watch: { icon: PlayCircle, label: "Watch", color: "arcane" },
  concept: { icon: Layers, label: "Cards", color: "plasma" },
  quiz: { icon: HelpCircle, label: "Decode", color: "arcane" },
  mythbuster: { icon: Wand2, label: "Myth Buster", color: "arcane" },
  build: { icon: Hammer, label: "Build", color: "plasma" },
  boss: { icon: Crown, label: "Boss", color: "arcane" },
};

export default function LevelDetail() {
  const { id } = useParams();
  const [lv, setLv] = useState(null);
  const nav = useNavigate();

  useEffect(() => { api.level(id).then(setLv); }, [id]);
  if (!lv) return <div className="min-h-screen flex items-center justify-center text-sub">Loading…</div>;

  const nextMission = lv.missions.find((m) => m.status !== "completed");

  return (
    <div className="pb-nav">
      <header className="sticky top-0 z-40 glass pt-safe">
        <div className="px-4 py-3 flex items-center gap-3">
          <button onClick={() => nav(-1)} data-testid="back-btn" className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center">
            <ArrowLeft size={18} />
          </button>
          <div className="min-w-0">
            <div className="label">Level</div>
            <h1 className="font-head font-bold text-lg truncate">{lv.title}</h1>
          </div>
        </div>
      </header>

      <div className="px-4 pt-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-5">
          <p className="text-arcane font-head italic leading-snug">“{lv.tagline}”</p>
          <div className="flex items-center gap-2 mt-3 text-xs text-muted">
            <span className="chip"><Clock size={12} />~{lv.estimated_minutes} min</span>
            <span className="chip">{lv.type}</span>
            <span className="chip">{lv.total_xp} XP on offer</span>
          </div>
          {lv.objectives?.length > 0 && (
            <ul className="mt-4 space-y-2">
              {lv.objectives.slice(0, 3).map((o, i) => (
                <li key={i} className="flex gap-2 text-sm text-sub"><span className="text-plasma mt-0.5">▸</span>{o}</li>
              ))}
            </ul>
          )}
        </motion.div>

        {lv.forks?.length > 0 && lv.forks.map((fk) => (
          <Link key={fk.id} to={`/fork/${fk.id}`} data-testid={`fork-banner-${fk.id}`}
            className="card p-4 block active:scale-[0.99] transition-transform border-arcane/30 bg-gradient-to-br from-arcane/10 to-surface">
            <div className="flex items-center gap-3">
              <div className="h-11 w-11 rounded-xl bg-arcane/15 text-arcane flex items-center justify-center shrink-0">
                <GitFork size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="label text-arcane">Alternative path · {fk.level_count} lectures</div>
                <div className="font-head font-bold">{fk.name}</div>
              </div>
              <ChevronRight className="text-muted shrink-0" />
            </div>
            <p className="text-xs text-sub mt-2">{fk.tagline}</p>
          </Link>
        ))}

        <div className="label px-1">Missions</div>
        <div className="space-y-2.5">
          {lv.missions.map((m, i) => {
            const meta = TYPE_META[m.type] || TYPE_META.briefing;
            const Icon = meta.icon;
            const done = m.status === "completed";
            const isNext = nextMission && nextMission.id === m.id;
            return (
              <Link key={m.id} to={`/play/${encodeURIComponent(lv.id)}/${encodeURIComponent(m.id)}`}
                data-testid={`mission-${m.type}`}
                className={`card p-4 flex items-center gap-4 active:scale-[0.99] transition-transform ${isNext ? "ring-1 ring-arcane/40 shadow-glow" : ""}`}>
                <div className={`h-11 w-11 rounded-xl flex items-center justify-center shrink-0 ${
                  done ? "bg-plasma/15 text-plasma" : meta.color === "arcane" ? "bg-arcane/15 text-arcane" : "bg-white/5 text-sub"}`}>
                  {done ? <Check size={20} /> : <Icon size={20} />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="label">{meta.label} · {m.xp_reward} XP</div>
                  <div className="font-head font-semibold truncate">{m.title}</div>
                  <div className="text-xs text-muted truncate">{m.objective}</div>
                </div>
                {done ? <span className="text-[11px] text-plasma font-head">Done</span>
                  : isNext ? <Play size={18} className="text-arcane" /> : <Play size={16} className="text-muted" />}
              </Link>
            );
          })}
        </div>

        {nextMission && (
          <Link to={`/play/${encodeURIComponent(lv.id)}/${encodeURIComponent(nextMission.id)}`}
            data-testid="level-continue" className="btn-primary w-full">
            <Play size={18} /> {lv.missions.some(m=>m.status==="completed") ? "Continue" : "Start"} · {nextMission.title}
          </Link>
        )}
        {!nextMission && (
          <div className="card p-5 text-center">
            <Check className="mx-auto text-plasma mb-2" />
            <p className="font-head font-semibold">Level complete!</p>
            <Link to="/map" className="btn-plasma w-full mt-4">Back to Map</Link>
          </div>
        )}
      </div>
    </div>
  );
}
