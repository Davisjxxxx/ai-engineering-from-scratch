import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import TopHud from "../components/TopHud";
import { Focus, Eye, Volume2, Bell, GitBranch, Award, Brain, Download, ChevronRight, Flame, Zap, Trophy, GraduationCap } from "lucide-react";

export default function You() {
  const { profile, updateSettings } = useApp();
  const [prefs, setPrefs] = useState(null);
  const [installEvt, setInstallEvt] = useState(null);

  useEffect(() => {
    api.notifPrefs().then(setPrefs);
    const h = (e) => { e.preventDefault(); setInstallEvt(e); };
    window.addEventListener("beforeinstallprompt", h);
    return () => window.removeEventListener("beforeinstallprompt", h);
  }, []);

  if (!profile) return null;

  const savePrefs = async (patch) => {
    const next = { ...prefs, ...patch };
    setPrefs(next);
    await api.saveNotifPrefs(next);
  };

  const install = async () => { if (installEvt) { installEvt.prompt(); setInstallEvt(null); } };

  return (
    <div className="pb-nav">
      <TopHud title="You" subtitle="Profile · settings" />
      <div className="px-4 pt-4 space-y-5">

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3">
          <Stat icon={Zap} color="arcane" value={`Lv ${profile.level}`} label={`${profile.total_xp} XP`} />
          <Stat icon={Flame} color="bad" value={profile.streak_count} label="day streak" />
          <Stat icon={Trophy} color="plasma" value={profile.badges.length} label="badges" />
        </div>

        {/* Focus & accessibility */}
        <Section title="Focus & accessibility">
          <Toggle icon={Focus} label="Focus Mode" hint="Hide nav during Lab & Review for deep work"
            checked={profile.focus_mode_enabled} onChange={(v) => updateSettings({ focus_mode_enabled: v })} testid="toggle-focus" />
          <Toggle icon={Eye} label="Reduced motion" hint="Calmer transitions, less movement"
            checked={profile.reduced_motion_enabled} onChange={(v) => updateSettings({ reduced_motion_enabled: v })} testid="toggle-motion" />
          <Toggle icon={Volume2} label="Sound cues" hint="Audio feedback on wins"
            checked={profile.sound_enabled} onChange={(v) => updateSettings({ sound_enabled: v })} testid="toggle-sound" />
        </Section>

        {/* Reminders (scaffolded, coming soon) */}
        <Section title="Reminders" badge="Coming soon">
          <p className="text-xs text-muted mb-2 px-1">We're preparing gentle nudges to protect your streak. Set your preferences now — push delivery arrives in a future update.</p>
          {prefs && (
            <>
              <Toggle icon={Bell} label="Daily 5-min mission" checked={prefs.daily_mission_enabled} onChange={(v) => savePrefs({ daily_mission_enabled: v })} testid="rem-daily" />
              <Toggle icon={Flame} label="Streak rescue" checked={prefs.streak_reminder_enabled} onChange={(v) => savePrefs({ streak_reminder_enabled: v })} testid="rem-streak" />
              <Toggle icon={Brain} label="Review reminder" checked={prefs.review_reminder_enabled} onChange={(v) => savePrefs({ review_reminder_enabled: v })} testid="rem-review" />
              <Toggle icon={GitBranch} label="Daily pattern drill" checked={prefs.daily_pattern_drill_enabled} onChange={(v) => savePrefs({ daily_pattern_drill_enabled: v })} testid="rem-drill" />
              <Toggle icon={Brain} label="Resume paused lab" checked={prefs.resume_lab_enabled} onChange={(v) => savePrefs({ resume_lab_enabled: v })} testid="rem-lab" />
              <Toggle icon={Award} label="Capstone progress" checked={prefs.capstone_progress_enabled} onChange={(v) => savePrefs({ capstone_progress_enabled: v })} testid="rem-capstone" />
              <div className="flex items-center justify-between px-1 py-2">
                <span className="text-sm text-sub">Preferred time</span>
                <input type="time" value={prefs.preferred_time} onChange={(e) => savePrefs({ preferred_time: e.target.value })}
                  data-testid="rem-time" className="bg-elevated border border-white/10 rounded-lg px-2 py-1 text-sm" />
              </div>
            </>
          )}
        </Section>

        {/* Navigate */}
        <Section title="Your forge">
          <LinkRow to="/paths" icon={GraduationCap} label="Learning Paths" />
          <LinkRow to="/skills" icon={GitBranch} label="Skill Tree" />
          <LinkRow to="/badges" icon={Award} label="Badges" />
          <LinkRow to="/review" icon={Brain} label="Review Deck" />
          <LinkRow to="/braindump" icon={Brain} label="Brain Dump" />
        </Section>

        {installEvt && (
          <button onClick={install} className="btn-primary w-full" data-testid="install-pwa">
            <Download size={18} /> Install on home screen
          </button>
        )}
        <p className="text-center text-[11px] text-muted pb-2">AgentForge Quest · anonymous local profile · no account needed</p>
      </div>
    </div>
  );
}

function Stat({ icon: Icon, value, label, color }) {
  return (
    <div className="card p-3 text-center">
      <Icon size={18} className={`mx-auto mb-1 ${color === "arcane" ? "text-arcane" : color === "bad" ? "text-bad" : "text-plasma"}`} />
      <div className="font-head font-bold">{value}</div>
      <div className="text-[10px] text-muted">{label}</div>
    </div>
  );
}
function Section({ title, badge, children }) {
  return (
    <div>
      <div className="flex items-center gap-2 px-1 mb-2">
        <div className="label">{title}</div>
        {badge && <span className="chip !py-0.5 !text-arcane !border-arcane/30 !bg-arcane/10">{badge}</span>}
      </div>
      <div className="card divide-y divide-white/5">{children}</div>
    </div>
  );
}
function Toggle({ icon: Icon, label, hint, checked, onChange, testid }) {
  return (
    <label className="flex items-center gap-3 p-4 cursor-pointer">
      <Icon size={18} className="text-sub shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="text-sm font-head font-medium">{label}</div>
        {hint && <div className="text-xs text-muted">{hint}</div>}
      </div>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} data-testid={testid} className="afq-switch" />
      <style>{`.afq-switch{width:44px;height:26px;appearance:none;background:rgba(255,255,255,.12);border-radius:99px;position:relative;transition:.2s;flex-shrink:0}.afq-switch:checked{background:#F59E0B}.afq-switch::after{content:"";position:absolute;top:3px;left:3px;width:20px;height:20px;border-radius:50%;background:#fff;transition:.2s}.afq-switch:checked::after{left:21px}`}</style>
    </label>
  );
}
function LinkRow({ to, icon: Icon, label }) {
  return (
    <Link to={to} className="flex items-center gap-3 p-4" data-testid={`link-${to.slice(1)}`}>
      <Icon size={18} className="text-sub" />
      <span className="flex-1 text-sm font-head font-medium">{label}</span>
      <ChevronRight size={18} className="text-muted" />
    </Link>
  );
}
