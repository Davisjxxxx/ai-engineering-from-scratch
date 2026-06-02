import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useApp } from "../context/AppContext";
import { Zap, Award, Trophy } from "lucide-react";

export default function RewardOverlay() {
  const { reward, clearReward } = useApp();

  useEffect(() => {
    if (reward && !reward.badges?.length) {
      const t = setTimeout(clearReward, 1600);
      return () => clearTimeout(t);
    }
  }, [reward, clearReward]);

  return (
    <AnimatePresence>
      {reward && (
        <motion.div
          className="fixed inset-0 z-[60] flex items-center justify-center p-6 bg-base/70 backdrop-blur-sm"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onClick={clearReward}
          data-testid="reward-overlay"
        >
          <motion.div
            className="card w-full max-w-sm p-7 text-center"
            initial={{ scale: 0.8, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, opacity: 0 }}
          >
            {reward.levelComplete && (
              <div className="mb-3 inline-flex items-center gap-2 text-plasma font-display text-lg">
                <Trophy size={22} /> Level Cleared
              </div>
            )}
            {reward.xp > 0 && (
              <div className="flex items-center justify-center gap-2 text-arcane">
                <Zap size={28} />
                <span className="font-display text-4xl">+{reward.xp}</span>
                <span className="font-head text-lg self-end mb-1">XP</span>
              </div>
            )}
            {reward.badges?.length > 0 && (
              <div className="mt-5 space-y-2">
                <div className="label">New Badge{reward.badges.length > 1 ? "s" : ""}</div>
                {reward.badges.map((b) => (
                  <div key={b.id} className="flex items-center gap-3 bg-elevated rounded-xl p-3 text-left">
                    <div className="h-10 w-10 rounded-lg bg-arcane/15 text-arcane flex items-center justify-center">
                      <Award size={20} />
                    </div>
                    <div>
                      <div className="font-head font-semibold text-sm">{b.title}</div>
                      <div className="text-xs text-sub">{b.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button className="btn-primary w-full mt-6" onClick={clearReward} data-testid="reward-continue">
              Continue
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
