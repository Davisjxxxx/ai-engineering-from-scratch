import React from "react";
import { useApp } from "../context/AppContext";
import { Flame, Zap } from "lucide-react";

export default function TopHud({ title, subtitle }) {
  const { profile } = useApp();
  if (!profile) return null;
  const pct = Math.round((profile.xp_into_level / profile.xp_for_level) * 100);
  return (
    <header className="sticky top-0 z-40 glass pt-safe">
      <div className="max-w-md mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <div className="min-w-0">
            {subtitle && <div className="label">{subtitle}</div>}
            <h1 className="text-xl font-head font-bold truncate">{title}</h1>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="chip !text-arcane !border-arcane/30 !bg-arcane/10" data-testid="hud-streak">
              <Flame size={14} /> {profile.streak_count}
            </span>
            <span className="chip !text-plasma !border-plasma/30 !bg-plasma/10" data-testid="hud-level">
              <Zap size={14} /> Lv {profile.level}
            </span>
          </div>
        </div>
        <div className="mt-2 flex items-center gap-2" data-testid="hud-xp">
          <div className="h-1.5 flex-1 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-arcane to-yellow-300 rounded-full"
                 style={{ width: `${pct}%`, transition: "width .6s ease" }} />
          </div>
          <span className="text-[11px] text-muted font-mono">{profile.total_xp} XP</span>
        </div>
      </div>
    </header>
  );
}
