import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { AppProvider, useApp } from "./context/AppContext";
import BottomNav from "./components/BottomNav";
import RewardOverlay from "./components/RewardOverlay";
import Home from "./pages/Home";
import MapPage from "./pages/Map";
import LevelDetail from "./pages/LevelDetail";
import ForkPath from "./pages/ForkPath";
import MissionPlayer from "./pages/MissionPlayer";
import Lab from "./pages/Lab";
import Arena from "./pages/Arena";
import ChallengePlayer from "./pages/ChallengePlayer";
import Review from "./pages/Review";
import Skills from "./pages/Skills";
import BrainDump from "./pages/BrainDump";
import Badges from "./pages/Badges";
import You from "./pages/You";
import Paths from "./pages/Paths";
import AcademyHome from "./pages/AcademyHome";
import Dojo from "./pages/Dojo";
import Clinic from "./pages/Clinic";
import Capstone from "./pages/Capstone";
import TestOutQuiz from "./pages/TestOutQuiz";

function Shell() {
  const { ready, profile } = useApp();
  const loc = useLocation();
  const hideNav =
    loc.pathname.startsWith("/play/") ||
    /\/dojo$|\/clinic$/.test(loc.pathname) ||
    /^\/arena\/[^/]+$/.test(loc.pathname) ||
    (profile?.focus_mode_enabled && (loc.pathname.startsWith("/lab") || loc.pathname.startsWith("/review")));

  if (!ready) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center px-8">
        <div className="h-14 w-14 rounded-2xl bg-arcane/15 text-arcane flex items-center justify-center animate-floaty">
          <div className="h-6 w-6 border-2 border-arcane border-t-transparent rounded-full animate-spin" />
        </div>
        <p className="mt-4 font-display text-xl">AgentForge Quest</p>
        <p className="text-sub text-sm mt-1">Booting your forge…</p>
      </div>
    );
  }

  return (
    <div className="relative z-10 min-h-screen max-w-md mx-auto">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/map" element={<MapPage />} />
        <Route path="/level/:id" element={<LevelDetail />} />
        <Route path="/fork/:forkId" element={<ForkPath />} />
        <Route path="/play/:levelId/:missionId" element={<MissionPlayer />} />
        <Route path="/lab" element={<Lab />} />
        <Route path="/arena" element={<Arena />} />
        <Route path="/arena/:id" element={<ChallengePlayer />} />
        <Route path="/review" element={<Review />} />
        <Route path="/skills" element={<Skills />} />
        <Route path="/braindump" element={<BrainDump />} />
        <Route path="/badges" element={<Badges />} />
        <Route path="/you" element={<You />} />
        <Route path="/paths" element={<Paths />} />
        <Route path="/academy/capstone" element={<Capstone />} />
        <Route path="/test-out/:levelId" element={<TestOutQuiz />} />
        <Route path="/academy/:pathId" element={<AcademyHome />} />
        <Route path="/academy/:pathId/dojo" element={<Dojo />} />
        <Route path="/academy/:pathId/clinic" element={<Clinic />} />
      </Routes>
      {!hideNav && <BottomNav />}
      <RewardOverlay />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <Shell />
    </AppProvider>
  );
}
