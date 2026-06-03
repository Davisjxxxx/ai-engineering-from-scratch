import axios from "axios";

const BASE = process.env.REACT_APP_BACKEND_URL;

function deviceId() {
  let id = localStorage.getItem("afq_device");
  if (!id) {
    id = (crypto.randomUUID && crypto.randomUUID()) ||
      "dev-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    localStorage.setItem("afq_device", id);
  }
  return id;
}

const client = axios.create({ baseURL: `${BASE}/api` });
client.interceptors.request.use((cfg) => {
  cfg.headers["X-Device-Id"] = deviceId();
  return cfg;
});

export const api = {
  health: () => client.get("/health").then((r) => r.data),
  profile: () => client.get("/profile").then((r) => r.data),
  saveSettings: (s) => client.put("/profile/settings", s).then((r) => r.data),
  campaign: () => client.get("/campaign").then((r) => r.data),
  level: (id) => client.get(`/levels/${encodeURIComponent(id)}`).then((r) => r.data),
  completeMission: (id, body) =>
    client.post(`/missions/${encodeURIComponent(id)}/complete`, body).then((r) => r.data),
  daily: () => client.get("/daily").then((r) => r.data),
  challenges: () => client.get("/challenges").then((r) => r.data),
  attemptChallenge: (id, answer) =>
    client.post(`/challenges/${encodeURIComponent(id)}/attempt`, { answer }).then((r) => r.data),
  labScenarios: () => client.get("/lab/scenarios").then((r) => r.data),
  labRun: (build) => client.post("/lab/run", build).then((r) => r.data),
  labBuilds: () => client.get("/lab/builds").then((r) => r.data),
  saveBuild: (build) => client.post("/lab/builds", build).then((r) => r.data),
  deleteBuild: (id) => client.delete(`/lab/builds/${id}`).then((r) => r.data),
  braindump: () => client.get("/braindump").then((r) => r.data),
  addBrainDump: (b) => client.post("/braindump", b).then((r) => r.data),
  setBrainStatus: (id, status) =>
    client.put(`/braindump/${id}/status?status=${status}`).then((r) => r.data),
  deleteBrain: (id) => client.delete(`/braindump/${id}`).then((r) => r.data),
  reviewDue: () => client.get("/review/due").then((r) => r.data),
  gradeReview: (id, quality) =>
    client.post(`/review/${encodeURIComponent(id)}/grade`, { quality }).then((r) => r.data),
  seedReviews: () => client.post("/review/seed-all").then((r) => r.data),
  skills: () => client.get("/skills").then((r) => r.data),
  forks: () => client.get("/forks").then((r) => r.data),
  fork: (id) => client.get(`/forks/${encodeURIComponent(id)}`).then((r) => r.data),
  paths: () => client.get("/paths").then((r) => r.data),
  academy: (pathId) => client.get(`/academy/${pathId}`).then((r) => r.data),
  dojo: (pathId) => client.get(`/academy/${pathId}/dojo`).then((r) => r.data),
  dojoResult: (pathId, body) => client.post(`/academy/${pathId}/dojo/result`, body).then((r) => r.data),
  clinic: (pathId) => client.get(`/academy/${pathId}/clinic`).then((r) => r.data),
  clinicResult: (pathId, body) => client.post(`/academy/${pathId}/clinic/result`, body).then((r) => r.data),
  capstones: () => client.get("/academy/capstones/list").then((r) => r.data),
  validateCapstone: (id, selected) => client.post(`/academy/capstones/${id}/validate`, { selected }).then((r) => r.data),
  badges: () => client.get("/badges").then((r) => r.data),
  notifPrefs: () => client.get("/notifications/preferences").then((r) => r.data),
  saveNotifPrefs: (p) => client.put("/notifications/preferences", p).then((r) => r.data),
  testOutQuiz: (id) => client.get(`/test-out/${encodeURIComponent(id)}`).then((r) => r.data),
  submitTestOut: (id, answers) => client.post(`/test-out/${encodeURIComponent(id)}`, { answers }).then((r) => r.data),
  testOutStatus: () => client.get("/test-out/status").then((r) => r.data),
  submitFeedback: (f) => client.post("/feedback", f).then((r) => r.data),
};

export { deviceId };
