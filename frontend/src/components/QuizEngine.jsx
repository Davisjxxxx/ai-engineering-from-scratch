import React, { useState } from "react";
import { motion } from "framer-motion";
import { Check, X, ArrowRight, Lightbulb } from "lucide-react";

/** Renders rich explanations split by double-space-newline separators.
 *  Each segment is displayed as a row with appropriate text color. */
function RichExplain({ text }) {
  if (!text) return null;
  // Split on "  \n" (markdown-style soft breaks)
  const parts = text.split(/  \n/).filter(Boolean);
  if (parts.length <= 1) {
    return <div className="text-ink/80 leading-relaxed">{text}</div>;
  }
  return (
    <div className="space-y-1.5">
      {parts.map((part, i) => {
        const isMain = part.startsWith("**") && i === 0;
        return (
          <div key={i} className={`leading-relaxed ${isMain ? "text-ink font-medium" : "text-ink/80"}`}>
            {part}
          </div>
        );
      })}
    </div>
  );
}

/** Reusable quiz runner with anti-loop protection.
 *
 *  State machine per question:
 *    unanswered → incorrect_1 → incorrect_2 → revealed → completed
 *
 *  - Max 2 wrong attempts before the correct answer is revealed.
 *  - In scored mode (test-out), a revealed answer counts incorrect.
 *  - In learning mode, revealed answer still allows progression.
 *
 *  questions: [{q, options:[..], answer:idx, explain, hint1?, hint2?}]
 *  onDone({correct, total, answers}) — answers[i] is the selected option index per question */
export default function QuizEngine({ questions, onDone, passThreshold, ctaLabel = "Finish",
                                      scored = false }) {
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState(null);
  const [correct, setCorrect] = useState(0);
  const [wrongAttempts, setWrongAttempts] = useState(0); // 0, 1, or 2
  const [revealed, setRevealed] = useState(false);
  const [answers, setAnswers] = useState(() => new Array(questions.length).fill(-1));

  const q = questions[i];
  const last = i === questions.length - 1;
  const maxWrongs = 2;

  const choose = (idx) => {
    if (revealed) return;
    setPicked(idx);
    // Record the first choice as the answer
    if (answers[i] === -1) {
      const nextAnswers = [...answers];
      nextAnswers[i] = idx;
      setAnswers(nextAnswers);
    }
    if (idx === q.answer) {
      setCorrect((c) => c + 1);
      setRevealed(true);
    } else {
      const next = wrongAttempts + 1;
      setWrongAttempts(next);
      if (next >= maxWrongs) {
        setRevealed(true);
      }
    }
  };

  const next = () => {
    if (last) {
      // Record final answer if not yet recorded
      const finalAnswers = [...answers];
      if (finalAnswers[i] === -1 && picked !== null) {
        finalAnswers[i] = picked;
      }
      onDone({ correct, total: questions.length, answers: finalAnswers });
      return;
    }
    setI((x) => x + 1);
    setPicked(null);
    setRevealed(false);
    setWrongAttempts(0);
  };

  const isCorrect = revealed && picked === q.answer;
  const attemptLabel = wrongAttempts === 1 ? "First try" : "Second try";
  const hintIdx = wrongAttempts; // 1 → hint1, 2 → hint2

  return (
    <div data-testid="quiz-engine">
      <div className="flex items-center gap-2 mb-4">
        {questions.map((_, idx) => (
          <div key={idx} className={`h-1.5 flex-1 rounded-full ${
            idx < i ? "bg-plasma" : idx === i ? "bg-arcane" : "bg-white/10"}`} />
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
          else if (isPicked && !isCorrect && wrongAttempts > 0) cls = "border-bad/60 bg-bad/10";
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
                 isPicked && !isCorrect ? <X size={18} className="text-bad" /> :
                 <span className="inline-block h-4 w-4 rounded-full border border-white/25" />}
              </span>
              <span className="text-ink/90">{opt}</span>
            </motion.button>
          );
        })}
      </div>

      {/* Hints on wrong attempts */}
      {!revealed && wrongAttempts >= 1 && q[`hint${hintIdx}`] && (
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
          className="mt-4 rounded-xl p-4 bg-arcane/10 border border-arcane/25 text-sm">
          <div className="flex items-center gap-2 font-head font-semibold text-arcane mb-1">
            <Lightbulb size={16} /> {attemptLabel} hint
          </div>
          <p className="text-ink/80">{q[`hint${hintIdx}`]}</p>
        </motion.div>
      )}

      {/* Wrong attempt feedback (no hint available) */}
      {!revealed && wrongAttempts >= 1 && !q[`hint${hintIdx}`] && (
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
          className="mt-4 rounded-xl p-4 bg-white/5 border border-white/10 text-sm">
          <div className="flex items-center gap-2 font-head font-semibold text-sub mb-1">
            {wrongAttempts < maxWrongs ? "Try again — you've got one more attempt." : ""}
          </div>
        </motion.div>
      )}

      {/* Reveal: answer + rich explanation */}
      {revealed && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
          className={`mt-4 rounded-xl p-4 text-sm ${isCorrect ? "bg-ok/10" : "bg-white/5"}`}>
          <div className={`font-head font-semibold mb-2 ${isCorrect ? "text-ok" : "text-sub"}`}>
            {isCorrect ? "Correct — well done." :
              wrongAttempts >= maxWrongs ? "Here's the answer:" : "Not quite. Here's the truth:"}
          </div>
          <RichExplain text={q.explain} />
          {scored && !isCorrect && (
            <div className="mt-2 text-xs text-muted">This question is marked incorrect for scoring.</div>
          )}
        </motion.div>
      )}

      {/* Continue button: active when answered correctly OR revealed */}
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
