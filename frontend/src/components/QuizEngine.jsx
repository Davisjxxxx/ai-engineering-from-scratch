import React, { useState } from "react";
import { motion } from "framer-motion";
import { Check, X, ArrowRight } from "lucide-react";

/** Reusable quiz runner used by Decode and Boss missions.
 *  questions: [{q, options:[..], answer:idx, explain}]
 *  onDone({correct, total}) */
export default function QuizEngine({ questions, onDone, passThreshold, ctaLabel = "Finish" }) {
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState(null);
  const [correct, setCorrect] = useState(0);
  const [revealed, setRevealed] = useState(false);

  const q = questions[i];
  const last = i === questions.length - 1;

  const choose = (idx) => {
    if (revealed) return;
    setPicked(idx);
    setRevealed(true);
    if (idx === q.answer) setCorrect((c) => c + 1);
  };

  const next = () => {
    if (last) {
      onDone({ correct, total: questions.length });
      return;
    }
    setI((x) => x + 1);
    setPicked(null);
    setRevealed(false);
  };

  return (
    <div data-testid="quiz-engine">
      <div className="flex items-center gap-2 mb-4">
        {questions.map((_, idx) => (
          <div key={idx} className={`h-1.5 flex-1 rounded-full ${idx < i ? "bg-plasma" : idx === i ? "bg-arcane" : "bg-white/10"}`} />
        ))}
      </div>
      <div className="label mb-2">Question {i + 1} / {questions.length}</div>
      <h3 className="text-lg font-head font-semibold mb-5 leading-snug">{q.q}</h3>
      <div className="space-y-3">
        {q.options.map((opt, idx) => {
          const isAnswer = idx === q.answer;
          const isPicked = idx === picked;
          let cls = "border-white/10 bg-elevated";
          if (revealed && isAnswer) cls = "border-ok/60 bg-ok/10";
          else if (revealed && isPicked) cls = "border-bad/60 bg-bad/10";
          return (
            <motion.button
              key={idx}
              whileTap={{ scale: 0.98 }}
              onClick={() => choose(idx)}
              data-testid={`quiz-option-${idx}`}
              className={`w-full text-left rounded-xl border p-4 text-[15px] leading-snug flex items-start gap-3 ${cls}`}
            >
              <span className="mt-0.5 shrink-0">
                {revealed && isAnswer ? <Check size={18} className="text-ok" /> :
                 revealed && isPicked ? <X size={18} className="text-bad" /> :
                 <span className="inline-block h-4 w-4 rounded-full border border-white/25" />}
              </span>
              <span className="text-ink/90">{opt}</span>
            </motion.button>
          );
        })}
      </div>

      {revealed && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
          className={`mt-4 rounded-xl p-4 text-sm ${picked === q.answer ? "bg-ok/10 text-ok" : "bg-white/5 text-sub"}`}>
          <div className="font-head font-semibold mb-1">
            {picked === q.answer ? "Nice — that's it." : "Not quite. Here's the truth:"}
          </div>
          <div className="text-ink/80">{q.explain}</div>
        </motion.div>
      )}

      <button
        className={`w-full mt-5 ${revealed ? "btn-primary" : "btn-ghost opacity-50 pointer-events-none"}`}
        onClick={next}
        data-testid="quiz-next"
      >
        {last ? ctaLabel : "Next"} <ArrowRight size={18} />
      </button>
    </div>
  );
}
