# Android App Build Guide

## Prerequisites

1. **Node.js 22+** with npm
2. **JDK 21** — Capacitor 8.x requires JDK 21 to compile
   - Check: `java -version` should show 21.x
   - If you have multiple JDKs, set `JAVA_HOME` before building:
     ```bash
     export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
     ```
3. **Android SDK** — installed via Android Studio or command line
   - Set `ANDROID_HOME` (typically `~/Android/Sdk`)
   - The Gradle wrapper will auto-download missing SDK components

## Environment

The Android app connects to the Railway backend. The API URL is baked in at build time:

```
REACT_APP_BACKEND_URL=https://ai-engineering-from-scratch-production.up.railway.app
```

The `mobile:build` npm script sets this automatically.

## Build Commands

```bash
cd frontend

# 1. Install dependencies (if not already done)
npm install

# 2. Build the web frontend with the Railway API URL
npm run mobile:build

# 3. Sync web assets into the Android project
npx cap sync android

# 4. Build the debug APK
cd android
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 ./gradlew assembleDebug
```

## APK Output

```
android/app/build/outputs/apk/debug/app-debug.apk  (~5.3 MB)
```

## Install on Phone

### Via adb (USB)
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

### Via direct download
Send the APK to testers (email, Drive, etc.). They must:
1. Open Settings → Security → enable "Install from unknown sources"
2. Open the APK file → tap Install

## Release Build (Play Store)

For a release-ready AAB:

```bash
# Generate a keystore (one-time)
keytool -genkey -v -keystore agentforge-release.keystore \
  -alias agentforge -keyalg RSA -keysize 2048 -validity 10000

# Build the release AAB
cd android
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 ./gradlew bundleRelease

# Output: android/app/build/outputs/bundle/release/app-release.aab
```

Then upload the AAB to Google Play Console. The keystore must be kept secure and never committed to git.

## Architecture

```
┌──────────────────────────┐
│   Android APK (5.3MB)    │
│  ┌──────────────────────┐│
│  │  Capacitor WebView   ││
│  │  (React CRA build)   ││
│  │                      ││
│  │  API calls ──────────▶  Railway Backend
│  │  (HTTPS)             ││  (FastAPI + MongoDB)
│  └──────────────────────┘│
│  Package: com.agentforge.quest
│  App Name: AgentForge Quest
│  Orientation: portrait
└──────────────────────────┘
```

The APK contains the full React app built with `REACT_APP_BACKEND_URL` pointing to Railway. All API calls go directly to the Railway backend over HTTPS. No native plugins are used — the app is a thin WebView wrapper around the existing PWA.

## npm Scripts

| Script | Purpose |
|--------|---------|
| `npm run mobile:build` | Build frontend with Railway API URL |
| `npm run mobile:sync` | Sync web assets into Android project (`npx cap sync android`) |
| `npm run mobile:open` | Open Android project in Android Studio (`npx cap open android`) |
| `npm run build` | Build frontend for web deployment (same-origin API) |

## Notes

- The debug APK is for beta testing only — not for Play Store distribution.
- The APK is unsigned (debug keystore). Play Store requires a signed release build.
- Do NOT set `ADMIN_TOKEN` in the app build. Admin endpoints remain protected server-side.
- Web deployment (Docker/Railway) is unchanged. The `npm run build` script still produces the same-origin web build.
- Generated files (`android/`, `build/`, `node_modules/`) are in `.gitignore`.
- The keystore file (`*.keystore`, `*.jks`) must NEVER be committed.
