# AgentForge Quest — Test Access

**No authentication.** The app uses an anonymous, device-based profile.

- The frontend generates a UUID stored in `localStorage` under key `afq_device`.
- Every API request sends header `X-Device-Id: <uuid>`.
- To simulate a player via curl/automation, send any string as `X-Device-Id` (e.g. `X-Device-Id: tester-1`). A fresh profile is auto-created on first call.

## Backend base
- Internal: `http://localhost:8001/api`
- External: `${REACT_APP_BACKEND_URL}/api`

## Optional live AI (DeepSeek)
- Set `DEEPSEEK_API_KEY` in `/app/backend/.env` to enable Agent Lab "Live AI mode".
- Without it, the lab runs fully mocked (no key required). Currently NOT set.
