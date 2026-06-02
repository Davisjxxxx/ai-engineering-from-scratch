import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import TopHud from "../components/TopHud";
import { Check, ChevronRight, Swords } from "lucide-react";

const SKILL_COLOR = {
  "prompt-design": "arcane", "agent-routing": "plasma", "tool-use": "plasma",
  "debugging": "arcane", "safety": "bad", "evaluation": "plasma", "memory": "arcane",
};

export default function Arena() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.challenges().then(setItems); }, []);

  return (
    <div className="pb-nav">
      <TopHud title="Challenge Arena" subtitle="Short replayable puzzles" />
      <div className="px-4 pt-4 space-y-3">
        {items.map((c) => {
          const col = SKILL_COLOR[c.skill] || "arcane";
          return (
            <Link key={c.id} to={`/arena/${c.id}`} data-testid={`challenge-${c.id}`}
              className="card p-4 flex items-center gap-4 active:scale-[0.99] transition-transform">
              <div className={`h-12 w-12 rounded-xl flex items-center justify-center shrink-0 ${
                col === "arcane" ? "bg-arcane/15 text-arcane" : col === "plasma" ? "bg-plasma/15 text-plasma" : "bg-bad/10 text-bad"}`}>
                {c.solved ? <Check size={22} /> : <Swords size={20} />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="label">{c.skill.replace("-", " ")} · {c.xp} XP</div>
                <div className="font-head font-semibold truncate">{c.title}</div>
                <div className="text-xs text-muted line-clamp-1">{c.scenario}</div>
              </div>
              {c.solved && <span className="text-[11px] text-plasma font-head shrink-0">Solved</span>}
              <ChevronRight className="text-muted shrink-0" size={18} />
            </Link>
          );
        })}
      </div>
    </div>
  );
}
