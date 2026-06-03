import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Send, Check } from "lucide-react";
import { api } from "../api";

const FEEDBACK_TYPES = [
  { id: "confusing", label: "Confusing", emoji: "🤔" },
  { id: "too_easy", label: "Too easy", emoji: "😴" },
  { id: "too_hard", label: "Too hard", emoji: "😰" },
  { id: "bug", label: "Bug", emoji: "🐛" },
  { id: "boring", label: "Boring", emoji: "😐" },
  { id: "helpful", label: "Helpful", emoji: "💡" },
  { id: "fun", label: "Fun", emoji: "🎮" },
  { id: "other", label: "Other", emoji: "💬" },
];

/** Floating feedback button — visible on mission, lab, map, and quiz screens.
 *  Props: levelId, missionId, labKind (optional context) */
export default function FeedbackButton({ levelId, missionId, labKind, route }) {
  const [open, setOpen] = useState(false);
  const [kind, setKind] = useState(null);
  const [rating, setRating] = useState(0);
  const [note, setNote] = useState("");
  const [sent, setSent] = useState(false);

  const submit = async () => {
    await api.submitFeedback({
      kind: kind || "other",
      rating: rating || null,
      note: note || null,
      level_id: levelId || null,
      mission_id: missionId || null,
      lab_kind: labKind || null,
      route: route || window.location.pathname,
      user_agent: navigator.userAgent || null,
    });
    setSent(true);
    setTimeout(() => { setOpen(false); setSent(false); setKind(null); setRating(0); setNote(""); }, 2000);
  };

  return (
    <>
      {/* Floating trigger */}
      <button
        onClick={() => setOpen(true)}
        data-testid="feedback-trigger"
        className="fixed bottom-24 right-4 z-50 h-12 w-12 rounded-full bg-elevated border border-white/15 text-sub
                   flex items-center justify-center shadow-lg active:scale-95 transition-transform"
        title="Send feedback"
      >
        <MessageSquare size={18} />
      </button>

      {/* Modal */}
      <AnimatePresence>
        {open && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm px-4"
            onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
          >
            <motion.div initial={{ y: 100, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 100, opacity: 0 }}
              className="w-full max-w-md bg-surface border border-white/10 rounded-2xl p-5 pb-6 max-h-[85vh] overflow-y-auto">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-head font-bold text-lg">
                  {sent ? "Thanks!" : "Quick feedback"}
                </h3>
                <button onClick={() => setOpen(false)} className="h-8 w-8 rounded-lg bg-white/5 flex items-center justify-center">
                  <X size={16} />
                </button>
              </div>

              {sent ? (
                <div className="text-center py-6">
                  <Check size={40} className="text-ok mx-auto mb-3" />
                  <p className="text-sub text-sm">Feedback sent. You're helping make this better.</p>
                </div>
              ) : (
                <>
                  {/* Feedback type chips */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {FEEDBACK_TYPES.map((ft) => (
                      <button key={ft.id}
                        onClick={() => setKind(kind === ft.id ? null : ft.id)}
                        data-testid={`feedback-${ft.id}`}
                        className={`chip !text-sm !px-3 !py-2 ${kind === ft.id ? "!bg-plasma/20 !text-plasma !border-plasma/40" : ""}`}>
                        {ft.emoji} {ft.label}
                      </button>
                    ))}
                  </div>

                  {/* Rating */}
                  <div className="mb-4">
                    <div className="label mb-2">Rating (optional)</div>
                    <div className="flex gap-2">
                      {[1, 2, 3, 4, 5].map((v) => (
                        <button key={v}
                          onClick={() => setRating(rating === v ? 0 : v)}
                          data-testid={`rating-${v}`}
                          className={`h-10 w-10 rounded-xl text-sm font-head font-bold transition-colors ${
                            rating >= v ? "bg-arcane text-base" : "bg-white/5 text-muted"}`}>
                          {v}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Note */}
                  <div className="mb-4">
                    <div className="label mb-2">Note (optional)</div>
                    <textarea
                      value={note}
                      onChange={(e) => setNote(e.target.value)}
                      placeholder="What went well? What was confusing?"
                      data-testid="feedback-note"
                      className="w-full bg-elevated border border-white/10 rounded-xl p-3 text-sm text-ink/90 placeholder:text-muted
                                 resize-none h-20 focus:outline-none focus:border-plasma/50"
                      maxLength={500}
                    />
                  </div>

                  {/* Context */}
                  {(levelId || route) && (
                    <div className="text-xs text-muted mb-4 flex flex-wrap gap-2">
                      {levelId && <span className="chip">{levelId}</span>}
                      {missionId && <span className="chip">{missionId}</span>}
                      {labKind && <span className="chip">lab: {labKind}</span>}
                      {route && <span className="chip">{route}</span>}
                    </div>
                  )}

                  {/* Submit */}
                  <button
                    onClick={submit}
                    data-testid="feedback-submit"
                    className="btn-primary w-full"
                    disabled={!kind}
                  >
                    <Send size={16} /> Send feedback
                  </button>
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
