# EAS build and update — runbook

> **Stack note:** EAS Build / EAS Update are Expo-specific tools. This guide applies only to projects on the workspace default mobile stack (RN + Expo). For Swift native, Kotlin native, or Flutter, the equivalent tooling (Xcode Cloud, Codemagic, Bitrise, fastlane, Flutter's flutter build / Codemagic flow) replaces this — adapt the *concepts* (channels, environments, OTA-where-allowed, release ceremony) to your stack's idioms.

How an Expo + React Native MVP in this workspace **builds, distributes, and ships JS-only updates** via EAS. Picks up where `react-native-mvp-scaffold.md` §4.10 / §5 step 10 left off (`eas.json` profiles and the first preview build) and goes deep on the operational reality: secret management, dynamic config, OTA cadence, channel strategy, and what bites at submission time.

The companion guide `rn-app-store-submission.md` covers the App Store / Play Console side of release. This guide is everything *up to* but not *including* store submission.

---

## 1. Purpose

The scaffold guide gets a new RN project to its first `eas build --profile preview` successfully. From there, several real questions arrive in week one and bite hard if not pre-decided:

- Where do secrets live so they are *in* the build but *out* of git, while not duplicating across dev / staging / prod?
- How do dev / preview / production builds differ in code, and how does the JS know which environment it is in?
- When the team needs to fix a bug post-launch, do they ship an OTA (faster, JS-only) or a new native build (slower, required for some changes)?
- How do release "channels" map to git branches and to user populations?
- What is the right cadence for native builds vs. OTA updates?

This guide locks defaults for each of those questions so the engineer is not redeciding them under the pressure of a production fix.

---

## 2. Operating principles

1. **EAS Build is the production build tool. Local builds are for debugging only.** Local builds drift from EAS builds; debugging EAS-specific failures locally is its own dead end.
2. **Three profiles, three audiences.** `development` for the developer with hot reload; `preview` for internal testers (TestFlight / Play Internal Testing); `production` for the store. Skip-tier complexity is what produces a "works on preview, broken on production" surprise.
3. **EAS Update is the recovery tool for JS bugs.** Use it for JS-only fixes between native releases. Anything that touches a native module, a permission, or `app.config.ts` is a new native build, not an OTA.
4. **Secrets live in EAS, not in `.env` files that ship.** `.env` files are for local dev. EAS environment variables (account-level or project-level) are for builds. `expo-secure-store` is for runtime user data, not for build-time config.
5. **`app.config.ts` is dynamic and source-of-truth.** Static `app.json` is fine for trivial config; the moment env-based switching enters, move to `app.config.ts`. `EXPO_PUBLIC_*` envs are visible at runtime; everything else is build-time.
6. **Channel = audience.** `development` channel for active developers, `preview` for internal testers, `production` for end users. Pushing the wrong channel to the wrong audience is the OTA equivalent of force-pushing to main.
7. **Per `CLAUDE.md`, look up EAS docs freely** — the CLI and config schema change quarterly.

---

## 3. Three profiles

The scaffold guide §4.10 has a minimal example. The fully-shaped `eas.json` matching this guide:

```jsonc
{
  "cli": { "version": ">= 7.0.0", "appVersionSource": "remote" },
  "build": {
    "base": {
      "node": "20.x",
      "env": {
        "EXPO_PUBLIC_ENV": "unset"
      }
    },
    "development": {
      "extends": "base",
      "developmentClient": true,
      "distribution": "internal",
      "env": { "EXPO_PUBLIC_ENV": "development", "EXPO_PUBLIC_API_URL": "https://dev-api.<slug>.com" },
      "channel": "development"
    },
    "preview": {
      "extends": "base",
      "distribution": "internal",
      "env": { "EXPO_PUBLIC_ENV": "preview", "EXPO_PUBLIC_API_URL": "https://staging-api.<slug>.com" },
      "channel": "preview",
      "ios":     { "simulator": false },
      "android": { "buildType": "apk" }
    },
    "production": {
      "extends": "base",
      "env": { "EXPO_PUBLIC_ENV": "production", "EXPO_PUBLIC_API_URL": "https://api.<slug>.com" },
      "channel": "production",
      "autoIncrement": true,
      "ios":     { "buildConfiguration": "Release" },
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "production": {
      "ios":     { "ascAppId": "<App Store Connect app id>" },
      "android": { "serviceAccountKeyPath": "./google-play-service-account.json" }
    }
  },
  "update": {
    "fallbackToCacheTimeout": 0
  }
}
```

Key facts:

- **`appVersionSource: "remote"`** lets EAS manage the version number across builds. Forget incrementing it locally; EAS does it.
- **`autoIncrement: true`** on production bumps the build number on each production build, matching what App Store / Play Console require.
- **`developmentClient: true`** on the dev profile produces a build of Expo's *development client* (which can load a Metro bundle from a developer's machine). It is *not* the regular app shell.
- **`distribution: "internal"`** on dev and preview makes the build installable via the EAS link or via direct `.apk` / TestFlight, without store review.
- **`channel`** on each profile is what links a build to OTA updates targeted at that audience. See §6.

---

## 4. `app.config.ts` — dynamic config

```ts
// app.config.ts
import { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => {
  const env = process.env.EXPO_PUBLIC_ENV ?? "development";

  const variant = {
    development: { name: "<Slug> (Dev)",     bundleIdentifier: "com.example.<slug>.dev",     icon: "./assets/icon-dev.png" },
    preview:     { name: "<Slug> (Preview)", bundleIdentifier: "com.example.<slug>.preview", icon: "./assets/icon-preview.png" },
    production:  { name: "<Slug>",           bundleIdentifier: "com.example.<slug>",         icon: "./assets/icon.png" },
  }[env];

  return {
    ...config,
    name: variant.name,
    slug: "<slug>",
    icon: variant.icon,
    version: "1.0.0",                                    // EAS will manage if appVersionSource: remote
    runtimeVersion: { policy: "fingerprint" },           // OTA-compatibility hash
    ios: {
      bundleIdentifier: variant.bundleIdentifier,
      supportsTablet: false,
      infoPlist: {
        ITSAppUsesNonExemptEncryption: false
      }
    },
    android: {
      package: variant.bundleIdentifier,
      adaptiveIcon: { foregroundImage: variant.icon, backgroundColor: "#000000" }
    },
    extra: {
      eas: { projectId: "<eas-project-id>" }
    },
    updates: {
      url: "https://u.expo.dev/<eas-project-id>"
    }
  };
};
```

Two critical pieces:

- **Three bundle identifiers / package names** — `com.example.<slug>.dev`, `.preview`, `.production` (or `com.example.<slug>` for prod). Distinct bundles mean dev / preview / prod can coexist on the same device, which is essential for iterating without overwriting your real-user copy.
- **`runtimeVersion: { policy: "fingerprint" }`** — Expo computes a fingerprint of native dependencies. Two builds with the same fingerprint can share OTA updates; two builds with different fingerprints cannot. This prevents shipping an OTA that depends on a native module the target app does not have.

---

## 5. Secrets at build time vs. runtime

| Where the value is needed | How to store it |
|---|---|
| Visible in the JS bundle at runtime (e.g., the backend API URL, a public Sentry DSN, Stripe publishable key) | `EXPO_PUBLIC_*` env var in `eas.json` per profile, or in a local `.env` for `npx expo start`. Anything `EXPO_PUBLIC_*` is **public** — assume it ends up in the bundle. |
| At build time but **not** in the bundle (e.g., a secret used by an EAS Build script, code signing) | EAS Account / Project Environment Variables, marked **Secret**. Available to build steps via `process.env`, not embedded in the bundle. |
| At runtime, per user, sensitive (auth tokens, refresh tokens) | `expo-secure-store` per the RN scaffold guide §4.6. Never in any `.env`. |

**Failure mode:** putting a backend service-account key in `EXPO_PUBLIC_API_KEY`. It ends up in the bundle, decodable by anyone who installs the app. Use a non-public env var or, for true secrets the client should never see, broker through the Flask backend.

EAS lets you scope a secret to an account, a project, or a specific build profile. Default: project + profile (so dev secrets and prod secrets cannot collide).

---

## 6. Channels and OTA strategy

A **channel** in EAS Update terminology is a labeled stream of OTA updates. A build is bound to one channel at build time (via the `channel` key in `eas.json`). It receives OTA updates only from that channel.

| Channel | Audience | Built from | Update cadence |
|---|---|---|---|
| `development` | Active developers | `development` profile | Continuously, whenever a dev pushes to the dev branch |
| `preview` | Internal testers (TestFlight / Play Internal Testing) | `preview` profile | Whenever a new test build is ready — typically once per work cycle |
| `production` | End users | `production` profile | Carefully, after preview has been verified |

Publishing an OTA:

```bash
eas update --channel production --message "fix: incorrect total on cart screen"
```

This compiles the current JS, uploads it, and pushes it to all builds bound to the `production` channel **on the same runtime version fingerprint**. Builds on an older fingerprint do not receive it (and should not — they would crash on a missing native module).

### 6.1 When OTA is allowed

- Pure JS / TypeScript changes.
- Style changes (StyleSheet, NativeWind classes, theme tokens).
- Asset changes that ship via `require(...)` of bundled assets.
- Bug fixes that do not change native modules, permissions, or `app.config.ts`.

### 6.2 When OTA is NOT allowed (new native build required)

- Any change to `app.config.ts` that alters permissions, bundle ID, name, icon, splash, native config.
- Installing or removing a library with native code (anything `npx expo install` warns about).
- SDK upgrades (Expo SDK or React Native version).
- Anything that requires a new `runtimeVersion` fingerprint.

If you ship an OTA that includes a JS reference to a native module the build doesn't have, the app crashes on next launch for every user on that channel. The fingerprint policy prevents most of this — but only if you respect it.

### 6.3 OTA rollback

EAS Update tracks every published update. Roll back via:

```bash
eas update --channel production --republish --group <previous-update-group-id>
```

The previous update is re-published as the latest, so all users pull it on next app launch. Find the group id via `eas update:list --channel production`.

The roll-forward / roll-back loop is fast — minutes, not the hours of an App Store re-review. This is the whole point of OTA.

---

## 7. The recurring build + OTA workflow

| Trigger | Action |
|---|---|
| Dev does JS-only feature work | Hot reload via Expo dev client; no build needed |
| Internal tester needs to try a new feature | `eas build --profile preview --platform <ios|android>`; tester pulls the new build via TestFlight / Play Internal |
| Bug found post-launch, JS-only fix | `eas update --channel production --message "<concise message>"` |
| Bug found post-launch, native change required | `eas build --profile production --platform all`, submit to stores (per `rn-app-store-submission.md`); the previous version stays live until review |
| New native dependency installed | New native build required across all channels that use it |
| Expo SDK upgrade | New native build required; coordinate with users (forced-update prompt for the old version) |

### 7.1 The `runtimeVersion` discipline

Every native build records its fingerprint. Two builds with different fingerprints are different runtime versions — OTA updates are isolated by fingerprint.

A common failure: dev changes a native dependency, ships a JS-only OTA without rebuilding native, and the OTA reaches preview testers on the old native bundle. Crash on launch. The fingerprint policy prevents this if `runtimeVersion: { policy: "fingerprint" }` is set — the OTA targets only matching fingerprints.

**Never override the fingerprint policy** unless you fully understand the implications.

---

## 8. The build queue and cost

EAS Build runs builds in a cloud queue. Free tier has limited build minutes; paid tier (Production plan) gives priority.

| Plan | Build queue | Useful for |
|---|---|---|
| Free | Slower queue, limited minutes / month | Side projects, scaffolding a new MVP |
| Production | Priority queue, more minutes, concurrent builds | Active development with daily preview builds |

Estimate: an Expo SDK 50 RN app builds in ~5-15 min on the priority queue, ~15-30 on free. Plan around it during release cycles.

EAS Update has its own cost: a generous free tier (10k MAU on the most recent update generation), then paid per MAU. For first-100-users MVPs, free tier suffices.

---

## 9. Common operational gotchas

### 9.1 "But it works locally"

The Expo Go app uses a generic bundle. Your EAS preview / production builds are real bundles with your actual native deps. If something works in Expo Go but fails in a preview build, the difference is almost always a native module not auto-included in Expo Go.

### 9.2 Forgetting to set EAS Account credentials for store submission

Submission requires App Store Connect (iOS) and Google Play Console (Android) service-account credentials. EAS prompts on the first `eas submit` and remembers them. If multiple developers work on the project, see `rn-app-store-submission.md` for shared-credential patterns.

### 9.3 OTA updates not arriving

In order:

- Check the `runtimeVersion` of the installed app vs. the latest published update (`eas update:list --channel production`).
- Check the app has internet at launch — the update fetch happens at app start.
- Confirm `updates.url` in `app.config.ts` matches `https://u.expo.dev/<project-id>`.
- Confirm `eas.json` build profile sets the correct channel.

### 9.4 Build failing on iOS provisioning

EAS auto-manages provisioning profiles and certificates if you let it (the `credentials` step on first build asks). For most teams, **let EAS manage it**. Manual provisioning is for cases EAS specifically can't handle (e.g., enterprise distribution outside the App Store).

### 9.5 Multi-developer EAS access

Add team members to the Expo organization (account → team), assign roles. EAS Build / Update access flows from there.

---

## 10. The release ceremony

For every production build:

1. **Pre-build:** preview build approved by the user / tester. Manual smoke test of the success-criterion flow.
2. **Build:** `eas build --profile production --platform all --auto-submit` *(or omit auto-submit to do it manually via the runbook in `rn-app-store-submission.md`)*.
3. **Wait:** ~10-30 min for the build, then store review (1-3 days iOS, 1-7 days Android).
4. **Post-approval:** roll out gradually (TestFlight phased release / Google Play staged rollout). 1% → 10% → 100% over a few days, watching for crash spikes.
5. **Post-launch:** monitor Sentry / crash reports (when wired). First 72 hours are when issues surface.

For an OTA fix:

1. **Test the fix locally** with a dev-client connected to the change.
2. **Publish to `preview` channel first**: `eas update --channel preview --message "<message>"`. Verify on a preview-channel device.
3. **Promote to production**: `eas update --channel production --message "<message>"`. Watch for crash uplift in the next hour.
4. **Roll back if needed**: `eas update --channel production --republish --group <prior>`.

---

## 11. Handoffs

### 11.1 Outward

- `guides/mobile/react-native-mvp-scaffold.md` §4.10 / §5 step 10 produced the first `eas.json` and the first build; this guide is everything after.
- `guides/mobile/rn-app-store-submission.md` covers App Store Connect / Google Play Console once a production build is ready.
- agent-skills' `shipping-and-launch` skill complements §10 with project-agnostic release-management practices.

### 11.2 Inward (defers to)

- Expo / EAS documentation for any flag or behavior this guide doesn't cover.
- `guides/web/flask-auth-patterns.md` §11 for the server-side JWT contract the mobile client authenticates against.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
