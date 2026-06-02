import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "../api";
import TopHud from "../components/TopHud";
import { Plus, Archive, Trash2, Brain, Tag, ArrowUpRight } from "lucide-react";

const TAGS = ["idea", "question", "todo", "project", "distraction"];

export default function BrainDump() {
  const [items, setItems] = useState([]);
  const [text, setText] = useState("");
  const [tags, setTags] = useState([]);
  const [filter, setFilter] = useState("open");

  const load = () => api.braindump().then(setItems);
  useEffect(() => { load(); }, []);

  const add = async () => {
    if (!text.trim()) return;
    const item = await api.addBrainDump({ content: text.trim(), tags });
    setItems((x) => [item, ...x]);
    setText(""); setTags([]);
  };
  const setStatus = async (id, status) => { await api.setBrainStatus(id, status); load(); };
  const del = async (id) => { await api.deleteBrain(id); setItems((x) => x.filter((i) => i.id !== id)); };

  const shown = items.filter((i) => (filter === "all" ? true : i.status === filter));

  return (
    <div className="pb-nav">
      <TopHud title="Brain Dump" subtitle="Park it · stay in flow" />
      <div className="px-4 pt-4 space-y-4">
        <div className="card p-4">
          <textarea data-testid="braindump-input" value={text} onChange={(e) => setText(e.target.value)} rows={2}
            placeholder="Quick — what's pulling your focus? Dump it here and get back to the mission."
            className="w-full bg-black/40 border border-white/10 rounded-xl p-3 text-[15px] outline-none focus:border-arcane/50 resize-none" />
          <div className="flex flex-wrap gap-2 mt-3">
            {TAGS.map((t) => (
              <button key={t} onClick={() => setTags((x) => x.includes(t) ? x.filter((y) => y !== t) : [...x, t])}
                data-testid={`tag-${t}`}
                className={`chip ${tags.includes(t) ? "!bg-plasma/15 !text-plasma !border-plasma/40" : ""}`}>
                <Tag size={11} /> {t}
              </button>
            ))}
          </div>
          <button onClick={add} className="btn-primary w-full mt-3" data-testid="braindump-add"><Plus size={18} /> Park it</button>
        </div>

        <div className="flex gap-2">
          {["open", "mission", "archived", "all"].map((f) => (
            <button key={f} onClick={() => setFilter(f)} data-testid={`filter-${f}`}
              className={`chip ${filter === f ? "!bg-arcane/15 !text-arcane !border-arcane/40" : ""}`}>{f}</button>
          ))}
        </div>

        <div className="space-y-2">
          <AnimatePresence>
            {shown.map((it) => (
              <motion.div key={it.id} layout initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -20 }}
                className="card p-4" data-testid={`brain-item-${it.id}`}>
                <p className="text-ink/90 text-[15px]">{it.content}</p>
                {it.tags?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">{it.tags.map((t) => <span key={t} className="chip !py-0.5">{t}</span>)}</div>
                )}
                <div className="flex items-center gap-2 mt-3">
                  {it.status !== "mission" && (
                    <button onClick={() => setStatus(it.id, "mission")} data-testid={`convert-${it.id}`} className="chip !text-plasma !border-plasma/30">
                      <ArrowUpRight size={12} /> To mission
                    </button>
                  )}
                  {it.status !== "archived" && (
                    <button onClick={() => setStatus(it.id, "archived")} className="chip"><Archive size={12} /> Archive</button>
                  )}
                  <button onClick={() => del(it.id)} className="chip ml-auto !text-bad/80" data-testid={`del-${it.id}`}><Trash2 size={12} /></button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {shown.length === 0 && (
            <div className="text-center py-12 text-muted">
              <Brain size={28} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">Nothing here. A clear mind makes room for the mission.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
