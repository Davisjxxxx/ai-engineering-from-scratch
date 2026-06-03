import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import TopHud from "../components/TopHud";
import { Compass, Layers, ChevronRight, GraduationCap } from "lucide-react";

export default function Paths() {
  const [paths, setPaths] = useState([]);
  useEffect(() => { api.paths().then(setPaths); }, []);

  return (
    <div className="pb-nav">
      <TopHud title="Learning Paths" subtitle="Choose your journey" />
      <div className="px-4 pt-4 space-y-3">
        {paths.map((p, i) => {
          const to = p.kind === "campaign" ? "/map" : `/academy/${p.id}`;
          const Icon = p.kind === "campaign" ? Layers : GraduationCap;
          const accent = p.kind === "campaign" ? "plasma" : "arcane";
          return (
            <motion.div key={p.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <Link to={to} data-testid={`path-${p.id}`}
                className="card p-5 block active:scale-[0.99] transition-transform">
                <div className="flex items-center gap-4">
                  <div className={`h-14 w-14 rounded-2xl flex items-center justify-center shrink-0 ${
                    accent === "plasma" ? "bg-plasma/15 text-plasma" : "bg-arcane/15 text-arcane"}`}>
                    <Icon size={26} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="label">{p.unit_count} {p.unit_label} · {p.completed || 0} done</div>
                    <div className="font-head font-bold text-lg leading-tight">{p.title}</div>
                  </div>
                  <ChevronRight className="text-muted shrink-0" />
                </div>
                <p className="text-sm text-sub mt-3">{p.tagline}</p>
                {p.attribution && <p className="text-[10px] text-muted mt-2">{p.attribution}</p>}
                <div className="mt-3 h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div className={`h-full ${accent === "plasma" ? "bg-plasma" : "bg-arcane"}`}
                    style={{ width: `${Math.round(100 * (p.completed || 0) / p.unit_count)}%` }} />
                </div>
              </Link>
            </motion.div>
          );
        })}
        <p className="text-center text-[11px] text-muted pt-2 flex items-center justify-center gap-1">
          <Compass size={12} /> More paths can be added from PDFs & courses
        </p>
      </div>
    </div>
  );
}
