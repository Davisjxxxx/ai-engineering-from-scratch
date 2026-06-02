import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "../api";

const Ctx = createContext(null);
export const useApp = () => useContext(Ctx);

export function AppProvider({ children }) {
  const [profile, setProfile] = useState(null);
  const [reward, setReward] = useState(null); // {xp, badges, levelComplete}
  const [ready, setReady] = useState(false);

  const refreshProfile = useCallback(async () => {
    const p = await api.profile();
    setProfile(p);
    document.body.classList.toggle("reduce-motion", !!p.reduced_motion_enabled);
    return p;
  }, []);

  useEffect(() => {
    refreshProfile().finally(() => setReady(true));
  }, [refreshProfile]);

  const applyResult = useCallback((res) => {
    if (!res) return;
    if (res.profile) {
      setProfile(res.profile);
      document.body.classList.toggle("reduce-motion", !!res.profile.reduced_motion_enabled);
    }
    const xp = res.xp_gained ?? res.xp ?? 0;
    const badges = res.new_badges || [];
    if (xp > 0 || badges.length || res.level_just_completed) {
      setReward({ xp, badges, levelComplete: !!res.level_just_completed });
    }
  }, []);

  const clearReward = () => setReward(null);

  const updateSettings = useCallback(async (patch) => {
    const next = {
      focus_mode_enabled: profile?.focus_mode_enabled || false,
      reduced_motion_enabled: profile?.reduced_motion_enabled || false,
      sound_enabled: profile?.sound_enabled ?? true,
      ...patch,
    };
    const p = await api.saveSettings(next);
    setProfile(p);
    document.body.classList.toggle("reduce-motion", !!p.reduced_motion_enabled);
    return p;
  }, [profile]);

  return (
    <Ctx.Provider value={{ profile, ready, refreshProfile, applyResult, reward, clearReward, updateSettings, setProfile }}>
      {children}
    </Ctx.Provider>
  );
}
