import React, { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import TopHud from "../components/TopHud";
import CodeBlock from "../components/CodeBlock";
import { Play, Save, Trash2, Plus, Check, X, AlertTriangle, Bot, Zap } from "lucide-react";

const MEMORY_OPTS = ["none", "short-term", "summary", "vector"];

export default function Lab() {
  const { applyResult } = useApp();
  const [scenarios, setScenarios] = useState([]);
  const [scenarioId, setScenarioId] = useState("");
  const [build, setBuild] = useState({ name: "", role: "", prompt: "", tools: [], memory_config: "none" });
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [live, setLive] = useState(false);
  const [builds, setBuilds] = useState([]);

  useEffect(() => {
    api.labScenarios().then((s) => { setScenarios(s); setScenarioId(s[0]?.id || ""); });
    api.labBuilds().then(setBuilds);
  }, []);

  const scenario = scenarios.find((s) => s.id === scenarioId);
  const availTools = scenario?.available_tools || ["calculator", "web_search", "knowledge_base", "send_email"];

  const toggleTool = (t) =>
    setBuild((b) => ({ ...b, tools: b.tools.includes(t) ? b.tools.filter((x) => x !== t) : [...b.tools, t] }));

  const run = async () => {
    setRunning(true);
    try {
      const res = await api.labRun({ ...build, scenario_id: scenarioId, live });
      setResult(res);
    } finally { setRunning(false); }
  };

  const save = async () => {
    const saved = await api.saveBuild({ ...build, scenario_id: scenarioId });
    setBuilds((b) => [saved, ...b]);
    applyResult({ new_badges: [], profile: null }); // builds may unlock a badge; refresh handled by recompute on server
    const fresh = await api.profile(); applyResult({ profile: fresh });
  };

  const del = async (id) => { await api.deleteBuild(id); setBuilds((b) => b.filter((x) => x.id !== id)); };

  return (
    <div className="pb-nav">
      <TopHud title="AI Engineering Lab" subtitle="Sandbox · mocked AI" />
      <div className="px-4 pt-4 space-y-5">

        {/* Scenario */}
        <div className="card p-4">
          <div className="label mb-2">Mission scenario</div>
          <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
            {scenarios.map((s) => (
              <button key={s.id} onClick={() => { setScenarioId(s.id); setResult(null); }} data-testid={`scenario-${s.id}`}
                className={`shrink-0 rounded-xl px-3 py-2 text-sm border ${scenarioId === s.id ? "border-arcane bg-arcane/10 text-arcane" : "border-white/10 text-sub"}`}>
                {s.title}
              </button>
            ))}
          </div>
          {scenario && (
            <div className="mt-3 text-sm">
              <p className="text-sub">{scenario.brief}</p>
              <p className="mt-2 font-mono text-xs bg-black/40 rounded-lg p-2 text-plasma">TASK: {scenario.task}</p>
            </div>
          )}
        </div>

        {/* Builder */}
        <div className="card p-4 space-y-4">
          <div className="label flex items-center gap-1.5"><Bot size={13} /> Build your agent</div>
          <Field label="Agent name">
            <input data-testid="agent-name" value={build.name} onChange={(e) => setBuild({ ...build, name: e.target.value })}
              placeholder="e.g. Refund Resolver" className="afq-input" />
          </Field>
          <Field label="System prompt" hint="Add a role, task, constraints and an output format.">
            <textarea data-testid="agent-prompt" value={build.prompt} onChange={(e) => setBuild({ ...build, prompt: e.target.value })}
              rows={4} placeholder="You are a billing specialist. Your task is to resolve refunds. Only refund after verifying the charge. Reply as JSON with fields intent, action, message."
              className="afq-input font-mono text-[13px]" />
          </Field>
          <Field label="Tools">
            <div className="flex flex-wrap gap-2">
              {availTools.map((t) => (
                <button key={t} onClick={() => toggleTool(t)} data-testid={`tool-${t}`}
                  className={`chip ${build.tools.includes(t) ? "!bg-plasma/15 !text-plasma !border-plasma/40" : ""}`}>
                  {build.tools.includes(t) ? <Check size={12} /> : <Plus size={12} />} {t}
                </button>
              ))}
            </div>
          </Field>
          <Field label="Memory">
            <div className="flex gap-2 flex-wrap">
              {MEMORY_OPTS.map((mo) => (
                <button key={mo} onClick={() => setBuild({ ...build, memory_config: mo })} data-testid={`memory-${mo}`}
                  className={`chip ${build.memory_config === mo ? "!bg-arcane/15 !text-arcane !border-arcane/40" : ""}`}>{mo}</button>
              ))}
            </div>
          </Field>

          <label className="flex items-center justify-between bg-black/30 rounded-xl px-3 py-2.5">
            <span className="text-sm text-sub flex items-center gap-2"><Zap size={14} className="text-arcane" /> Live AI mode (DeepSeek)</span>
            <input type="checkbox" checked={live} onChange={(e) => setLive(e.target.checked)} data-testid="live-toggle" className="afq-check" />
          </label>

          <div className="flex gap-2">
            <button onClick={run} disabled={running} className="btn-primary flex-1" data-testid="run-agent">
              <Play size={18} /> {running ? "Running…" : "Run agent"}
            </button>
            <button onClick={save} disabled={!build.name} className="btn-ghost" data-testid="save-build"><Save size={18} /></button>
          </div>
        </div>

        {/* Result */}
        {result && <LabResult result={result} />}

        {/* Saved builds */}
        {builds.length > 0 && (
          <div className="space-y-2">
            <div className="label px-1">Saved agent builds</div>
            {builds.map((b) => (
              <div key={b.id} className="card p-3 flex items-center gap-3" data-testid={`build-${b.id}`}>
                <div className="h-9 w-9 rounded-lg bg-plasma/15 text-plasma flex items-center justify-center"><Bot size={16} /></div>
                <div className="flex-1 min-w-0">
                  <div className="font-head font-semibold text-sm truncate">{b.name}</div>
                  <div className="text-xs text-muted">score {b.test_results?.score ?? "—"} · {b.tools?.length || 0} tools</div>
                </div>
                <button onClick={() => del(b.id)} className="text-muted p-2" data-testid={`del-build-${b.id}`}><Trash2 size={16} /></button>
              </div>
            ))}
          </div>
        )}
      </div>
      <style>{`.afq-input{width:100%;background:#0b0c0f;border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:12px;color:#f8fafc;font-size:15px;outline:none}.afq-input:focus{border-color:rgba(245,158,11,.45)}.afq-check{width:42px;height:24px;appearance:none;background:rgba(255,255,255,.12);border-radius:99px;position:relative;transition:.2s}.afq-check:checked{background:#F59E0B}.afq-check::after{content:"";position:absolute;top:2px;left:2px;width:20px;height:20px;border-radius:50%;background:#fff;transition:.2s}.afq-check:checked::after{left:20px}`}</style>
    </div>
  );
}

function Field({ label, hint, children }) {
  return (
    <div>
      <div className="label mb-1.5">{label}</div>
      {children}
      {hint && <p className="text-[11px] text-muted mt-1">{hint}</p>}
    </div>
  );
}

function LabResult({ result }) {
  const color = result.verdict === "pass" ? "plasma" : result.verdict === "warn" ? "arcane" : "bad";
  return (
    <div className="card p-4" data-testid="lab-result">
      <div className="flex items-center justify-between">
        <div className="label">Agent run · {result.mode}</div>
        <span className={`chip ${color === "plasma" ? "!text-plasma !border-plasma/30 !bg-plasma/10" : color === "arcane" ? "!text-arcane !border-arcane/30 !bg-arcane/10" : "!text-bad !border-bad/30 !bg-bad/10"}`}>
          {result.verdict.toUpperCase()} · {result.score}%
        </span>
      </div>

      <div className="mt-3 space-y-1.5">
        {result.checks.map((c, i) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            {c.ok ? <Check size={15} className="text-ok shrink-0" /> : <X size={15} className="text-bad shrink-0" />}
            <span className={c.ok ? "text-sub" : "text-ink/80"}>{c.label}</span>
            {c.detail && <span className="text-[11px] text-muted ml-auto">{c.detail}</span>}
          </div>
        ))}
      </div>

      <div className="label mt-4 mb-1">Execution trace (mocked)</div>
      <div className="rounded-xl bg-black/50 border border-white/5 p-3 font-mono text-[12px] space-y-1">
        {result.trace.map((t, i) => (
          <div key={i}><span className={t.step === "guard" ? "text-bad" : "text-plasma"}>{t.step}</span> <span className="text-slate-400">›</span> <span className="text-slate-300">{t.text}</span></div>
        ))}
      </div>

      <div className="label mt-4 mb-1">Output</div>
      <CodeBlock code={result.output} lang="json" />

      {result.feedback?.length > 0 && (
        <div className="mt-3 rounded-xl bg-white/5 p-3">
          <div className="text-xs font-head font-semibold flex items-center gap-1.5 mb-1"><AlertTriangle size={13} className="text-arcane" /> Coach feedback</div>
          <ul className="space-y-1">
            {result.feedback.map((f, i) => <li key={i} className="text-sm text-sub">• {f}</li>)}
          </ul>
        </div>
      )}

      {result.live && (
        <div className="mt-3 rounded-xl bg-arcane/5 border border-arcane/20 p-3">
          <div className="label mb-1 text-arcane">Live AI · {result.live.mode}</div>
          <p className="text-sm text-sub whitespace-pre-wrap">{result.live.output || result.live.note || result.live.error}</p>
        </div>
      )}
    </div>
  );
}
