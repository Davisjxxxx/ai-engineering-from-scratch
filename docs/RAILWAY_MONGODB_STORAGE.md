# Railway MongoDB Storage Ops Guide

## Why the crash happened

On 2026-06-04, the AgentForge Quest app crashed at startup with:

```
pymongo.errors.OperationFailure: OutOfDiskSpace (code 14031)
available disk space of 233MB is less than required minimum of 512MB
```

The crash occurred in the startup handler (`server.py:976`) while creating the `feedback.created_at` index. MongoDB enforces a minimum free disk threshold (typically 512MB) before allowing index creation. Because index creation was in the startup path without exception handling, the entire app failed to start.

## What code fix was applied

Commit `87b9023` made the following changes to `backend/server.py`:

1. **Index classification**: Indexes are now split into critical and optional tiers.
   - Critical: `mission_progress`, `review_state`, `profiles` — app cannot function without these.
   - Optional: `test_outs`, `feedback.kind`, `feedback.created_at` — app works without these.

2. **`_safe_index()` helper**: Wraps optional index creation in try/except for `OperationFailure`. Logs a warning and continues startup instead of crashing.

3. **Feedback route degradation**: `POST /api/feedback`, `GET /api/feedback/summary`, and `GET /api/feedback/recent` now catch `OperationFailure` and return HTTP 503 with a clear JSON error instead of crashing the process.

## What still needs ops action

The code fix prevents crashes but does NOT resolve the underlying disk shortage.

**You must increase the Railway MongoDB volume storage.** The free tier includes 500MB. If your data + indexes exceed ~450MB, MongoDB will reject writes even for critical collections.

## What NOT to do

- Do NOT delete production data without explicit approval.
- Do NOT migrate to MongoDB Atlas, Supabase, or Postgres during this fix.
- Do NOT drop indexes to free space without understanding which are critical.

## Required Railway environment variables

Set these in your Railway app service dashboard (click the app tile → Variables):

| Variable | Purpose | Example |
|----------|---------|---------|
| `MONGO_URL` | MongoDB connection URI | `${{MongoDB.MONGO_URL}}` (Railway reference) or raw URI |
| `DB_NAME` | Database name | `agentforge` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |
| `UNLOCK_ALL` | Test mode — unlock all content | `true` for testing, `false` for production |
| `ADMIN_TOKEN` | Protects feedback summary/recent | Set a random string (see below) |
| `DEEPSEEK_API_KEY` | Optional live agent lab mode | Leave unset if not using |

## Setting ADMIN_TOKEN

1. Generate a random token: `python3 -c "import secrets; print(secrets.token_urlsafe(24))"`
2. In Railway → your app service → Variables → add `ADMIN_TOKEN` with that value
3. Redeploy the app
4. Verify: `curl https://your-app.up.railway.app/api/feedback/summary` should return 403
5. With correct token: `curl https://your-app.up.railway.app/api/feedback/summary -H "X-Admin-Token: your-token"` should return data

## Post-upgrade checks

After increasing the MongoDB volume, verify:

```bash
# 1. Health endpoint
curl https://your-app.up.railway.app/api/health
# → {"status":"ok","worlds":10,"levels":96,...}

# 2. Homepage loads
curl -s -o /dev/null -w "%{http_code}" https://your-app.up.railway.app/
# → 200

# 3. Submit test feedback
curl -X POST https://your-app.up.railway.app/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"kind":"fun","rating":5,"note":"Post-upgrade check"}'
# → {"ok":true}

# 4. Feedback summary (with admin token)
curl https://your-app.up.railway.app/api/feedback/summary \
  -H "X-Admin-Token: your-admin-token"
# → {"total": N, "by_kind": {...}, ...}

# 5. Tester guide
curl -s -o /dev/null -w "%{http_code}" https://your-app.up.railway.app/tester-guide
# → 200
```

## Railway MongoDB volume increase steps

1. Go to https://railway.com → your project `agentforge-quest`
2. Click the **MongoDB** service tile
3. Click **Settings** tab
4. Under **Volume**, note the current size and usage
5. Click the edit/pencil icon on the volume size
6. Increase to at least **1 GB** (or higher if usage is near 500MB)
7. Click **Save** — Railway will resize the volume (no downtime)
8. Wait for the MongoDB service to show **Online** (green)
9. The app should reconnect automatically — verify with the health check above

After the volume increase, MongoDB will have enough free space to create indexes. The optional `feedback` and `test_outs` indexes will be created on the next deploy. If you want to trigger index creation immediately, redeploy the app service.

## Local testing

```bash
# Start the full stack
docker compose up -d --build

# Health check
curl http://localhost:8000/api/health

# Test ADMIN_TOKEN behavior
# Without token set: endpoints are open
curl http://localhost:8000/api/feedback/summary

# With token set: requires X-Admin-Token header
ADMIN_TOKEN=my-secret docker compose up -d
curl http://localhost:8000/api/feedback/summary  # → 403
curl http://localhost:8000/api/feedback/summary -H "X-Admin-Token: my-secret"  # → data
```
