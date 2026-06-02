import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import TopHud from "../components/TopHud";
import { Play, Brain, Layers, Swords, Target, ChevronRight, Sparkles } from "lucide-react";

export default function Home() {
  const { profile } = useApp();
  const [daily, setDaily] = useState(null);
  const nav = useNavigate();

  useEffect(() => { api.daily().then(setDaily).catch(() => {}); }, []);

  const nba = daily?.next_action;
  const greeting = (() => {
    const h = new Date().getHours();
    return h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
  })();

  return (
    <div className="pb-nav">
      <TopHud title="AgentForge Quest" subtitle={greeting} />
      <div className="px-4 pt-4 space-y-5">

        {/* Next best action — the single clear focal CTA */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
          className="card p-5 bg-gradient-to-br from-elevated to-surface">
          <div className="label flex items-center gap-1.5"><Target size={13} /> Your next move</div>
          {!daily ? (
            <div className="mt-3">
              <div className="h-7 w-3/4 bg-white/10 rounded-lg animate-pulse" />
              <div className="h-4 w-1/2 bg-white/5 rounded mt-2 animate-pulse" />
              <div className="h-[52px] w-full bg-white/10 rounded-xl mt-4 animate-pulse" />
            </div>
          ) : nba?.kind === "mission" ? (
            <>
              <h2 className="text-2xl font-head font-bold mt-2 leading-tight">{nba.mission_title}</h2>
              <p className="text-sub text-sm mt-1">{nba.level_title} · ~{nba.estimated_minutes} min · no penalty for retries</p>
              <button
                data-testid="continue-cta"
                onClick={() => nav(`/play/${encodeURIComponent(nba.level_id)}/${encodeURIComponent(nba.mission_id)}`)}
                className="btn-primary w-full mt-4">
                <Play size={18} /> {profile?.total_xp ? "Continue Quest" : "Start Quest"}
              </button>
            </>
          ) : (
            <>
              <h2 className="text-xl font-head font-bold mt-2">{nba?.label || "Keep your streak alive"}</h2>
              <Link to="/review" className="btn-primary w-full mt-4"><Brain size={18} /> Open Review Deck</Link>
            </>
          )}
        </motion.div>

        {/* Daily challenge */}
        {daily?.daily_challenge && (
          <Link to={`/arena/${daily.daily_challenge.id}`} data-testid="daily-challenge"
            className="card p-4 flex items-center gap-4 active:scale-[0.99] transition-transform">
            <div className="h-12 w-12 rounded-xl bg-plasma/15 text-plasma flex items-center justify-center shrink-0">
              <Sparkles size={22} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="label">Daily 5-min mission</div>
              <div className="font-head font-semibold truncate">{daily.daily_challenge.title}</div>
            </div>
            <ChevronRight className="text-muted" />
          </Link>
        )}

        {/* Quick tiles */}
        <div className="grid grid-cols-2 gap-3">
          <Tile to="/map" icon={Layers} color="arcane" title="Campaign" sub="10 worlds · 96 levels" testid="tile-map" />
          <Tile to="/lab" icon={Sparkles} color="plasma" title="Agent Lab" sub="Build & run agents" testid="tile-lab" />
          <Tile to="/arena" icon={Swords} color="arcane" title="Arena" sub="Debug challenges" testid="tile-arena" />
          <Tile to="/review" icon={Brain} color="plasma"
            title="Review" sub={daily ? `${daily.reviews_due} cards due` : "Spaced repetition"} testid="tile-review" />
        </div>

        <Link to="/braindump" data-testid="braindump-link"
          className="card p-4 flex items-center justify-between active:scale-[0.99] transition-transform">
          <div className="flex items-center gap-3">
            <Brain className="text-sub" size={20} />
            <div>
              <div className="font-head font-semibold text-sm">Brain Dump</div>
              <div className="text-xs text-muted">Park a distracting idea, stay in flow</div>
            </div>
          </div>
          <ChevronRight className="text-muted" />
        </Link>
      </div>
    </div>
  );
}

function Tile({ to, icon: Icon, title, sub, color, testid }) {
  return (
    <Link to={to} data-testid={testid}
      className="card p-4 active:scale-[0.97] transition-transform">
      <div className={`h-11 w-11 rounded-xl flex items-center justify-center mb-3 ${
        color === "arcane" ? "bg-arcane/15 text-arcane" : "bg-plasma/15 text-plasma"}`}>
        <Icon size={20} />
      </div>
      <div className="font-head font-semibold">{title}</div>
      <div className="text-xs text-muted mt-0.5">{sub}</div>
    </Link>
  );
}
