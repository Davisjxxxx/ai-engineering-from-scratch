import React from "react";
import { useNavigate } from "react-router-dom";
import TopHud from "../components/TopHud";
import { ArrowLeft, Check, Bug, MessageSquare, Zap, Map, Wrench, Swords, Brain } from "lucide-react";

export default function TesterGuide() {
  const nav = useNavigate();

  return (
    <div className="pb-nav">
      <TopHud title="Beta Tester Guide" subtitle="Help make AgentForge Quest awesome" />

      <div className="px-4 pt-4 space-y-5">
        {/* What to test */}
        <div className="card p-5">
          <div className="label flex items-center gap-2 mb-3"><Check size={14} className="text-ok" /> What to test</div>
          <ul className="space-y-2 text-sm text-sub">
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>Every level should have missions, labs, and a boss</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>Labs (order, select, repair) should respond to taps</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>Test-out quizzes should unlock levels at 90%+</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>Quiz answers should reveal after 2 wrong attempts</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>Progress (XP, badges, streak) should persist across sessions</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>App should work as a PWA (add to home screen)</li>
          </ul>
        </div>

        {/* Recommended path */}
        <div className="card p-5">
          <div className="label flex items-center gap-2 mb-3"><Map size={14} className="text-arcane" /> Recommended first path</div>
          <ol className="space-y-3 text-sm text-sub">
            <li className="flex gap-3">
              <span className="h-6 w-6 rounded-full bg-arcane/15 text-arcane flex items-center justify-center text-xs font-bold shrink-0">1</span>
              <span>Start Quest from the home screen — complete the first briefing and decode missions</span>
            </li>
            <li className="flex gap-3">
              <span className="h-6 w-6 rounded-full bg-arcane/15 text-arcane flex items-center justify-center text-xs font-bold shrink-0">2</span>
              <span>Complete one full module (Dev Environment or Python Environments) — all missions + labs + boss</span>
            </li>
            <li className="flex gap-3">
              <span className="h-6 w-6 rounded-full bg-arcane/15 text-arcane flex items-center justify-center text-xs font-bold shrink-0">3</span>
              <span>Try one repair lab — see the broken pipeline, pick the fix</span>
            </li>
            <li className="flex gap-3">
              <span className="h-6 w-6 rounded-full bg-arcane/15 text-arcane flex items-center justify-center text-xs font-bold shrink-0">4</span>
              <span>Try a test-out quiz on a locked level (set UNLOCK_ALL=false to see locked levels)</span>
            </li>
            <li className="flex gap-3">
              <span className="h-6 w-6 rounded-full bg-arcane/15 text-arcane flex items-center justify-center text-xs font-bold shrink-0">5</span>
              <span>Submit feedback using the 💬 button on any screen</span>
            </li>
          </ol>
        </div>

        {/* How to report */}
        <div className="card p-5">
          <div className="label flex items-center gap-2 mb-3"><Bug size={14} className="text-bad" /> How to report issues</div>
          <ul className="space-y-2 text-sm text-sub">
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>Tap the 💬 button (bottom-right corner on any screen)</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>Pick a feedback type: Bug, Confusing, Too Hard, etc.</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>Add a rating (1-5) and a short note if you can</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>The app automatically includes which level/mission/lab you're on</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>No personal data is collected — just your device's random ID</li>
          </ul>
        </div>

        {/* What feedback is useful */}
        <div className="card p-5">
          <div className="label flex items-center gap-2 mb-3"><MessageSquare size={14} className="text-plasma" /> What kind of feedback is useful</div>
          <ul className="space-y-2 text-sm text-sub">
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>"The repair lab instructions were unclear — I didn't know which step was broken"</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>"The quiz said my answer was wrong but I'm pretty sure it was correct"</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>"This mission was really fun — the lab felt like a puzzle game"</li>
            <li className="flex gap-2"><span className="text-plasma mt-0.5">▸</span>"The text is too small on my phone screen" or "The button didn't respond"</li>
          </ul>
        </div>

        {/* Quick nav */}
        <div className="grid grid-cols-2 gap-3">
          <button onClick={() => nav("/map")} className="card p-4 text-left active:scale-[0.97] transition-transform">
            <Map size={20} className="text-arcane mb-2" />
            <div className="font-head font-semibold text-sm">Campaign Map</div>
            <div className="text-xs text-muted">96 levels to explore</div>
          </button>
          <button onClick={() => nav("/lab")} className="card p-4 text-left active:scale-[0.97] transition-transform">
            <Wrench size={20} className="text-plasma mb-2" />
            <div className="font-head font-semibold text-sm">Agent Lab</div>
            <div className="text-xs text-muted">Build & run agents</div>
          </button>
          <button onClick={() => nav("/arena")} className="card p-4 text-left active:scale-[0.97] transition-transform">
            <Swords size={20} className="text-arcane mb-2" />
            <div className="font-head font-semibold text-sm">Arena</div>
            <div className="text-xs text-muted">Debug challenges</div>
          </button>
          <button onClick={() => nav("/review")} className="card p-4 text-left active:scale-[0.97] transition-transform">
            <Brain size={20} className="text-plasma mb-2" />
            <div className="font-head font-semibold text-sm">Review</div>
            <div className="text-xs text-muted">Spaced repetition</div>
          </button>
        </div>

        <button onClick={() => nav(-1)} className="btn-ghost w-full">
          <ArrowLeft size={16} /> Back
        </button>
      </div>
    </div>
  );
}
