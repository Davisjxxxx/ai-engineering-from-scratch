import React, { useEffect, useState } from "react";
import { api } from "../api";
import TopHud from "../components/TopHud";
import ProgressRing from "../components/ProgressRing";
import * as Icons from "lucide-react";

export default function Skills() {
  const [skills, setSkills] = useState([]);
  useEffect(() => { api.skills().then(setSkills); }, []);

  return (
    <div className="pb-nav">
      <TopHud title="Skill Tree" subtitle="Forge your mastery" />
      <div className="px-4 pt-4 grid grid-cols-2 gap-3">
        {skills.map((s) => {
          const Icon = Icons[pascal(s.icon)] || Icons.Sparkles;
          const color = s.tier >= 3 ? "#2EC4B6" : s.tier > 0 ? "#F59E0B" : "#475569";
          return (
            <div key={s.id} data-testid={`skill-${s.id}`}
              className={`card p-4 flex flex-col items-center text-center ${s.total === 0 ? "opacity-50" : ""}`}>
              <ProgressRing value={s.progress} size={56} stroke={5} color={color}
                label={<Icon size={20} style={{ color }} />} />
              <div className="font-head font-semibold text-sm mt-3 leading-tight">{s.name}</div>
              <div className="text-[11px] text-muted mt-1">
                {s.total === 0 ? "Coming soon" : `${s.done}/${s.total} levels · T${s.tier}`}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function pascal(s) { return (s || "").split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(""); }
