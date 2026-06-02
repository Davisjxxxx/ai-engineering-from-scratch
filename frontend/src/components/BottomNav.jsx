import React from "react";
import { NavLink } from "react-router-dom";
import { Home, Map, FlaskConical, Swords, User } from "lucide-react";

const items = [
  { to: "/", icon: Home, label: "Home", testid: "nav-home" },
  { to: "/map", icon: Map, label: "Map", testid: "nav-map" },
  { to: "/lab", icon: FlaskConical, label: "Lab", testid: "nav-lab" },
  { to: "/arena", icon: Swords, label: "Arena", testid: "nav-arena" },
  { to: "/you", icon: User, label: "You", testid: "nav-you" },
];

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 inset-x-0 z-50 glass" style={{ paddingBottom: "env(safe-area-inset-bottom)" }}>
      <div className="max-w-md mx-auto grid grid-cols-5 h-[76px]">
        {items.map(({ to, icon: Icon, label, testid }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            data-testid={testid}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center gap-1 transition-colors ${
                isActive ? "text-arcane" : "text-muted"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={22} strokeWidth={isActive ? 2.4 : 1.8} />
                <span className="text-[10px] font-head tracking-wide">{label}</span>
                {isActive && <span className="absolute top-0 h-0.5 w-8 bg-arcane rounded-full shadow-glow" />}
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
