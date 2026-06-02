import React from "react";

export default function CodeBlock({ code, lang = "python" }) {
  return (
    <div className="rounded-xl border border-plasma/20 bg-black/60 overflow-hidden" data-testid="code-block">
      <div className="flex items-center gap-1.5 px-3 py-2 border-b border-white/5">
        <span className="h-2.5 w-2.5 rounded-full bg-bad/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-arcane/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-ok/70" />
        <span className="ml-2 text-[10px] uppercase tracking-widest text-muted font-mono">{lang}</span>
      </div>
      <pre className="p-3 overflow-x-auto text-[12.5px] leading-relaxed font-mono text-slate-300 no-scrollbar">
        <code>{code}</code>
      </pre>
    </div>
  );
}
