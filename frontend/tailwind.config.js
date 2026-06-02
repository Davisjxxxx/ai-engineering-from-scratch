/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}", "./public/index.html"],
  theme: {
    extend: {
      colors: {
        base: "#0A0A0C",
        surface: "#121316",
        elevated: "#1A1C23",
        ink: "#F8FAFC",
        sub: "#94A3B8",
        muted: "#64748B",
        arcane: "#F59E0B",
        plasma: "#2EC4B6",
        ok: "#10B981",
        bad: "#EF4444",
      },
      fontFamily: {
        head: ["Outfit", "sans-serif"],
        body: ["'IBM Plex Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
        display: ["Unbounded", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(245,158,11,0.35)",
        glowc: "0 0 20px rgba(46,196,182,0.30)",
      },
      keyframes: {
        floaty: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-6px)" } },
        pop: { "0%": { transform: "scale(0.6)", opacity: "0" }, "100%": { transform: "scale(1)", opacity: "1" } },
      },
      animation: { floaty: "floaty 3s ease-in-out infinite", pop: "pop .35s ease-out" },
    },
  },
  plugins: [],
};
