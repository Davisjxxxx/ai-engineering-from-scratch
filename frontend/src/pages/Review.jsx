import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import TopHud from "../components/TopHud";
import { Brain, ArrowRight, RotateCw, Check } from "lucide-react";

const GRADES = [
  { q: 1, label: "Forgot", color: "bad" },
  { q: 3, label: "Hard", color: "arcane" },
  { q: 4, label: "Good", color: "plasma" },
  { q: 5, label: "Easy", color: "ok" },
];

export default function Review() {
  const { applyResult } = useApp();
  const [data, setData] = useState(null);
  const [i, setI] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [doneCount, setDoneCount] = useState(0);

  const load = async () => { await api.seedReviews(); const d = await api.reviewDue(); setData(d); setI(0); setRevealed(false); setDoneCount(0); };
  useEffect(() => { load(); }, []);

  if (!data) return <Loading />;

  const cards = data.cards;

  if (data.total_cards === 0) {
    return (
      <div className="pb-nav">
        <TopHud title="Review Deck" subtitle="Spaced repetition" />
        <Empty title="No cards yet" body="Complete a level to unlock its review cards. Spaced repetition locks concepts into long-term memory." />
      </div>
    );
  }

  if (i >= cards.length) {
    return (
      <div className="pb-nav">
        <TopHud title="Review Deck" subtitle="Spaced repetition" />
        <div className="px-4 pt-10 text-center">
          <div className="mx-auto h-20 w-20 rounded-2xl bg-plasma/15 text-plasma flex items-center justify-center mb-4"><Check size={32} /></div>
          <h2 className="font-display text-2xl mb-1">All caught up</h2>
          <p className="text-sub text-sm mb-6">You reviewed {doneCount} card{doneCount !== 1 ? "s" : ""}. Come back when more are due.</p>
          <button className="btn-ghost w-full mb-2" onClick={load} data-testid="review-refresh"><RotateCw size={16} /> Check again</button>
          <Link to="/" className="btn-primary w-full">Back home <ArrowRight size={18} /></Link>
        </div>
      </div>
    );
  }

  const card = cards[i];
  const grade = async (q) => {
    const res = await api.gradeReview(card.card_id, q);
    applyResult(res);
    setDoneCount((c) => c + 1);
    setRevealed(false);
    setI((x) => x + 1);
  };

  return (
    <div className="pb-nav">
      <TopHud title="Review Deck" subtitle={`${data.due_count} due now`} />
      <div className="px-4 pt-4">
        <div className="flex items-center gap-2 mb-4">
          {cards.map((_, idx) => <div key={idx} className={`h-1.5 flex-1 rounded-full ${idx < i ? "bg-plasma" : idx === i ? "bg-arcane" : "bg-white/10"}`} />)}
        </div>

        <motion.div key={card.card_id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card p-6 min-h-[280px] flex flex-col">
          <div className="label flex items-center gap-1.5"><Brain size={13} /> {card.term}</div>
          <h3 className="font-head text-xl font-semibold mt-2">{card.prompt}</h3>
          {card.myth && <p className="text-xs text-muted mt-2">People often say: “{card.myth}”</p>}

          {revealed ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-5 flex-1">
              <div className="label text-plasma mb-1">Reality</div>
              <p className="text-ink/90 leading-relaxed">{card.answer}</p>
            </motion.div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <button className="btn-ghost" onClick={() => setRevealed(true)} data-testid="review-reveal">Reveal answer</button>
            </div>
          )}
        </motion.div>

        {revealed && (
          <div className="grid grid-cols-4 gap-2 mt-4">
            {GRADES.map((g) => (
              <button key={g.q} onClick={() => grade(g.q)} data-testid={`grade-${g.q}`}
                className={`rounded-xl py-3 text-sm font-head font-semibold border ${
                  g.color === "bad" ? "border-bad/40 text-bad" : g.color === "arcane" ? "border-arcane/40 text-arcane" :
                  g.color === "plasma" ? "border-plasma/40 text-plasma" : "border-ok/40 text-ok"}`}>
                {g.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Loading() { return <div className="min-h-screen flex items-center justify-center text-sub">Loading…</div>; }
function Empty({ title, body }) {
  return (
    <div className="px-4 pt-16 text-center">
      <div className="mx-auto h-20 w-20 rounded-2xl bg-white/5 text-muted flex items-center justify-center mb-4"><Brain size={30} /></div>
      <h2 className="font-head text-xl font-bold mb-1">{title}</h2>
      <p className="text-sub text-sm max-w-xs mx-auto">{body}</p>
      <Link to="/map" className="btn-primary mt-6 inline-flex">Go to Campaign</Link>
    </div>
  );
}
