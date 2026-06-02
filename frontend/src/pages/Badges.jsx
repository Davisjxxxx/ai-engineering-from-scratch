import React, { useEffect, useState } from "react";
import { api } from "../api";
import TopHud from "../components/TopHud";
import * as Icons from "lucide-react";

export default function Badges() {
  const [badges, setBadges] = useState([]);
  useEffect(() => { api.badges().then(setBadges); }, []);
  const earned = badges.filter((b) => b.earned).length;

  return (
    <div className="pb-nav">
      <TopHud title="Badges" subtitle={`${earned}/${badges.length} earned`} />
      <div className="px-4 pt-4 grid grid-cols-2 gap-3">
        {badges.map((b) => {
          const Icon = Icons[pascal(b.icon)] || Icons.Award;
          return (
            <div key={b.id} data-testid={`badge-${b.id}`}
              className={`card p-4 text-center ${b.earned ? "" : "opacity-45"}`}>
              <div className={`mx-auto h-14 w-14 rounded-2xl flex items-center justify-center mb-3 ${
                b.earned ? "bg-arcane/15 text-arcane shadow-glow" : "bg-white/5 text-muted"}`}>
                <Icon size={26} />
              </div>
              <div className="font-head font-semibold text-sm">{b.title}</div>
              <div className="text-[11px] text-muted mt-1 leading-snug">{b.description}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
function pascal(s) { return (s || "").split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(""); }
