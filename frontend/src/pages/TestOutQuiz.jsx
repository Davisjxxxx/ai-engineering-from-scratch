import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import QuizEngine from "../components/QuizEngine";
import TopHud from "../components/TopHud";
import { ArrowLeft, Check, X, Target, BookOpen, RefreshCw } from "lucide-react";

export default function TestOutQuiz() {
  const { levelId } = useParams();
  const nav = useNavigate();
  const { refreshProfile } = useApp();
  const [quiz, setQuiz] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.testOutQuiz(levelId).then(setQuiz).catch((e) => setError(e.response?.data?.detail || "Could not load quiz"));
  }, [levelId]);

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center">
        <X size={40} className="text-bad mb-4" />
        <h2 className="font-head font-bold text-xl mb-2">Can't load test-out</h2>
        <p className="text-sub text-sm mb-6">{error}</p>
        <button onClick={() => nav(-1)} className="btn-ghost">Go back</button>
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="h-6 w-6 border-2 border-arcane border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Already passed — show success state
  if (quiz.passed && !result) {
    return (
      <div className="pb-nav">
        <TopHud title="Test Out" subtitle={quiz.level_title} />
        <div className="px-4 pt-8 text-center">
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="h-20 w-20 rounded-full bg-ok/15 flex items-center justify-center mx-auto mb-4">
            <Check size={40} className="text-ok" />
          </motion.div>
          <h2 className="font-head font-bold text-xl mb-2">Already unlocked</h2>
          <p className="text-sub text-sm mb-4">You passed this test-out with {Math.round((quiz.last_score || 0) * 100)}%.</p>
          <div className="flex gap-3 justify-center">
            <button onClick={() => nav(-1)} className="btn-ghost">Back</button>
            <button onClick={() => nav(`/level/${encodeURIComponent(levelId)}`)} className="btn-primary">Go to level</button>
          </div>
        </div>
      </div>
    );
  }

  // Show results after submission
  if (result) {
    const pct = Math.round(result.score * 100);

    return (
      <div className="pb-nav">
        <TopHud title="Test Out Result" subtitle={quiz.level_title} />
        <div className="px-4 pt-6 text-center">
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
            className={`h-20 w-20 rounded-full flex items-center justify-center mx-auto mb-4 ${
              result.passed ? "bg-ok/15" : "bg-arcane/15"}`}>
            {result.passed ? <Check size={40} className="text-ok" /> : <X size={40} className="text-arcane" />}
          </motion.div>

          <h2 className="font-head font-bold text-2xl mb-1">
            {result.passed ? "Module unlocked!" : "Not quite yet"}
          </h2>
          <p className="text-sub text-sm mb-2">
            {pct}% · {result.correct_count}/{result.total_questions} correct
          </p>
          <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden mb-4">
            <div className={`h-full rounded-full transition-all ${result.passed ? "bg-ok" : "bg-arcane"}`}
              style={{ width: `${pct}%` }} />
          </div>
          <p className="text-xs text-muted mb-6">Threshold: {Math.round(result.threshold * 100)}%</p>

          {result.passed ? (
            <div className="space-y-3">
              <p className="text-ok text-sm">Great work — you already know this material.</p>
              <div className="flex gap-3 justify-center">
                <button onClick={() => nav(-1)} className="btn-ghost">Back to map</button>
                <button onClick={() => { refreshProfile(); nav(`/level/${encodeURIComponent(levelId)}`); }}
                  className="btn-primary">Enter level</button>
              </div>
            </div>
          ) : (
            <div className="space-y-4 text-left">
              {result.missed_concepts?.length > 0 && (
                <div className="card p-4">
                  <div className="label flex items-center gap-1.5 mb-3"><Target size={13} /> Concepts to review</div>
                  <ul className="space-y-2">
                    {result.missed_concepts.map((m, i) => (
                      <li key={i} className="text-sm text-sub">
                        <span className="text-ink/90 font-medium">{m.term}</span>
                        <span className="text-muted"> — {m.explain}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.recommendations?.length > 0 && (
                <div className="card p-4">
                  <div className="label flex items-center gap-1.5 mb-3"><BookOpen size={13} /> Recommended review</div>
                  <ul className="space-y-2">
                    {result.recommendations.map((r, i) => (
                      <li key={i} className="text-sm text-sub">Return to <span className="text-arcane">{r.level_title}</span> and complete the missions.</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="text-center pt-2 space-y-3">
                <p className="text-xs text-muted">You can retry the test-out anytime from the map.</p>
                <div className="flex gap-3 justify-center">
                  <button onClick={() => { setResult(null); setQuiz(null);
                    api.testOutQuiz(levelId).then(setQuiz); }} className="btn-ghost">
                    <RefreshCw size={16} /> Retry
                  </button>
                  <button onClick={() => nav(-1)} className="btn-primary">Back to map</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Show quiz
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 glass pt-safe">
        <div className="px-4 py-3 flex items-center gap-3">
          <button onClick={() => nav(-1)} className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center">
            <ArrowLeft size={18} />
          </button>
          <div>
            <div className="label">Test Out</div>
            <h1 className="font-head font-bold text-lg truncate">{quiz.level_title}</h1>
          </div>
          <span className="chip ml-auto !text-arcane !bg-arcane/10">
            {Math.round(quiz.threshold * 100)}% to pass
          </span>
        </div>
        <div className="px-4 pb-3">
          <p className="text-xs text-sub">Answer {quiz.question_count} questions. Score {Math.round(quiz.threshold * 100)}% or higher to unlock this level.</p>
        </div>
      </header>

      <main className="flex-1 px-4 py-5 max-w-md w-full mx-auto">
        <QuizEngine
          questions={quiz.questions}
          scored={true}
          passThreshold={quiz.threshold}
          ctaLabel="Submit"
          onDone={(r) => {
            api.submitTestOut(levelId, r.answers).then(setResult);
          }}
        />
      </main>
    </div>
  );
}
