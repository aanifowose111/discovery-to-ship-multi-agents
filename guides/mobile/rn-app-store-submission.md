# RN app store submission runbook

> **Stack note:** The submission *steps* (App Store Connect / Play Console accounts, metadata, screenshots, privacy policy, reviewer notes, phased rollout, common rejections) apply to **any** mobile app regardless of stack — they're store policies, not Expo/RN specifics. The EAS Submit automation in §9 is Expo-specific; for Swift / Kotlin / Flutter, use fastlane, Xcode Cloud, Codemagic, or the equivalent submission tool your stack ships with. The rest of the runbook is reusable.

How a React Native MVP in this workspace gets from a production EAS build into the **App Store (iOS)** and **Google Play (Android)** — accounts, app records, store metadata, screenshots, review process, common rejections, and post-launch first-72-hour monitoring.

Picks up where `eas-build-and-update.md` §10 ends (a production build exists). Stops where the app is live and the first users have it.

App Store and Play Console move faster than guides do — verify any step here against the official docs before relying on it.

---

## 1. Purpose

The store submission step is where months of MVP work meets a queue of strangers reviewing the app against rules the engineer has not read. Most rejections at first-MVP scale are **structural mistakes** (missing privacy policy URL, wrong permission strings, default Expo icon, screenshots from the simulator) that take an hour to fix once known and a week to fix when discovered at review-rejection time.

This guide is the pre-flight checklist + the actual submission workflow + the first-72-hour ritual after launch.

---

## 2. Operating principles

1. **Fix everything fixable before the first submission.** Rejections cost 1-7 days of review time on a re-submission. The hour spent on a checklist before submission is cheap.
2. **Real device screenshots, never the simulator.** App Store flags fake-looking screenshots; users distrust them too.
3. **Privacy policy is mandatory.** A published URL — not a Notion page that needs login. Both stores require it.
4. **Permission strings explain *why*.** "Camera" as the explanation gets rejected; "We use the camera to attach photos to support tickets" passes.
5. **Default Expo icon and splash get rejected.** Both stores. Even Internal Testing succeeds with defaults; review does not.
6. **Per `CLAUDE.md`, look up the latest review guidelines** — Apple and Google update them quarterly.

---

## 3. Account setup (one-time, per developer identity)

Most of this only happens once per developer; record it in a `SECRETS.md` so the same data isn't re-hunted on every product.

### 3.1 Apple Developer Program

- Cost: $99/year.
- Enrolled at: https://developer.apple.com/programs/.
- Approval: ~24-48 hours typical. Sometimes longer for individual enrollment.
- What it gives you: the ability to distribute via TestFlight and the App Store, code-signing certs.

### 3.2 App Store Connect

Once the Developer Program account exists, you can access App Store Connect: https://appstoreconnect.apple.com/. This is where:

- App records are created (name, bundle ID, primary language).
- TestFlight builds are managed.
- App Store metadata (description, screenshots, keywords, support URL, privacy policy URL) is entered.
- Submissions are made.

### 3.3 Google Play Developer Account

- Cost: $25 (one-time, lifetime).
- Enrolled at: https://play.google.com/console.
- Approval: ~24-48 hours.
- What it gives you: the ability to distribute via Internal Testing, Closed Testing, Open Testing, and the Play Store.

### 3.4 Google Play Console

Once the developer account exists, you can access Play Console: https://play.google.com/console/. This is where:

- App records are created (package name, default language).
- Internal / Closed / Open testing tracks are managed.
- Store listing metadata is entered.
- Releases are pushed to tracks.

---

## 4. Privacy policy + supporting URLs

Both stores require a **public URL** for your privacy policy. Google additionally requires it before Closed Testing.

**Acceptable hosts:**

- A page on the product's marketing site.
- A GitHub Pages or Netlify free-tier page hosting a single `privacy.html`.
- iubenda or Termly (paid services that generate compliant policies).

**Unacceptable:**

- A Notion page that requires login to view.
- A Google Doc requiring a login.
- A `https://...txt` file (some Google Play reviewers reject).

The privacy policy must reflect what the app *actually* collects. Templates are fine as starting points; the substance must match.

Also publish, on the same site:

- **Support URL** (where users can email or contact you for help).
- **Marketing URL** (the product home page; for App Store).
- **Terms of Service** (recommended even if not strictly required at this scale).

---

## 5. App Store (iOS) submission

### 5.1 Create the app record in App Store Connect

In **Apps → +**:

- **Platforms:** iOS (and tvOS / macOS if applicable; almost never for this workspace's MVPs).
- **Name:** the user-facing app name. Must match what's in `app.config.ts`.
- **Primary language:** the language of the metadata.
- **Bundle ID:** the production bundle ID from `app.config.ts` (e.g., `com.example.<slug>`). Must exist in the developer portal first; EAS sets this up automatically on first build.
- **SKU:** any unique string; convention: `<slug>-ios`.

### 5.2 Prepare the metadata

In the app's **App Information** tab:

- **Subtitle** (30 chars) — secondary product positioning.
- **Category** — primary + secondary.
- **Content rights**: confirm the app doesn't use third-party content you don't have rights to.

In the **Pricing and Availability** tab:

- **Price tier** (Free or one of Apple's tiers).
- **Availability** (regions). Default: all regions where you can legally operate.

In the **Version (e.g., 1.0)** tab (this is where metadata for the build lives):

- **Promotional text** (170 chars) — updatable without resubmission.
- **Description** (4000 chars) — the App Store listing body.
- **Keywords** (100 chars) — comma-separated, no spaces after commas, no overlap with the app name (waste of space).
- **Support URL** (required).
- **Marketing URL** (optional but expected).
- **Screenshots** — see §5.3.
- **App previews** (optional 15-30s video).
- **Version notes** (what's new — required for updates, blank on first submission).

### 5.3 Screenshots (iOS)

**Required sizes:**

- 6.7" Display (1290 × 2796) — current iPhone Pro Max.
- 6.5" Display (1242 × 2688) — older iPhone Plus / Pro Max.
- 5.5" Display (1242 × 2208) — older but sometimes required.

You only need to upload one size; Apple scales the rest for older devices. Provide 6.7" as the canonical set.

**Count:** 3-10 per device size. Lead with the screen that communicates the value prop most clearly.

**Generation:** real device screenshots, optionally framed in a device mockup with overlay text. Tools: Screenshot Builder, Fastlane Snapshot, or `expo screenshot` (community plugin). Avoid the simulator — the status bar and time formatting give it away.

### 5.4 Privacy questions

In **App Privacy → Get Started**, Apple asks a structured set of questions about data collected. Be honest. Common categories:

- **Contact info:** name, email if the app collects them (most do for auth).
- **Identifiers:** user ID is "identifier"; advertising IDs are reportable.
- **Usage data:** analytics counts as usage data.
- **Diagnostics:** crash reports count.

If you say you collect none and you actually do, the review may catch it (and you've also violated user trust). If unsure, list it as collected — the review will not punish you for over-disclosure.

### 5.5 Build selection

After the build uploads via EAS to App Store Connect (this happens via `eas submit` or `eas build --auto-submit`):

- The build appears in the **TestFlight** tab and, after processing (~15-30 min), in the **Version** tab as selectable.
- Select the build in the **Build** section of the version.

### 5.6 Submit for review

- **Export Compliance:** confirm the encryption answer. For most apps using only HTTPS (no custom crypto), `ITSAppUsesNonExemptEncryption: false` in `app.config.ts` (per `eas-build-and-update.md` §4) clears this.
- **Sign in info (if the app requires login):** Apple needs a working demo account. Create one with sample data — they need to evaluate the post-login experience.
- **Notes for the reviewer:** explain anything that wouldn't be obvious. "This app requires a Pro subscription on signup. Use demo@example.com / password123 for review access; this account has Pro privileges enabled."
- **Submit.**

Review takes **1-3 days** typically. Most apps pass first review if the metadata, screenshots, privacy, and demo-account-access are correct.

### 5.7 Phased release (recommended)

Before submitting, choose **Release this version → Automatically release with phased release** (in the version settings). This rolls the app out gradually (1% → 10% → 100% over 7 days), giving you time to catch issues before they affect everyone.

---

## 6. Google Play (Android) submission

### 6.1 Create the app in Play Console

In **All apps → Create app**:

- **App name** — user-facing.
- **Default language.**
- **App or game.**
- **Free or paid.**
- **Declarations:** confirm policies, developer status.

### 6.2 Set up testing tracks

Google Play has Internal, Closed, Open, and Production tracks. For first-MVP distribution:

- **Internal Testing** (up to 100 testers, ~1-day review on first build): for the user's first 1-10 testers. Set this up before the first preview build; EAS submits to it via `eas submit --profile production --platform android --track internal`.
- **Closed Testing**: invite-list-based wider beta. Useful if scaling past 10 testers before going to production.
- **Production**: the public Play Store.

### 6.3 Required metadata (each track has requirements; production has all)

In **Store presence → Main store listing**:

- **App name, short description (80 char), full description (4000 char).**
- **Graphics:**
  - **App icon** (512 × 512, PNG, ≤1 MB) — not the default Expo icon.
  - **Feature graphic** (1024 × 500) — the banner Google shows at the top of the listing.
  - **Phone screenshots** (2-8, 16:9 or 9:16 aspect, ≥ 320 px on the shorter side, ≤ 3840).
  - **7-inch and 10-inch tablet screenshots** (optional, recommended if the app works on tablet).
- **Category, contact details, privacy policy URL.**

In **App content** (data safety section):

- Answer the structured questions about what data is collected, why, and whether it's shared. Same honesty rule as Apple.

In **App content → Target audience**:

- Set age range. Most workspace MVPs are 18+; affirmed once.

In **App content → Content rating**:

- Complete the IARC questionnaire. Free, automated.

In **App content → Privacy policy**:

- Paste the public URL.

### 6.4 Upload the build to Internal Testing

- EAS does this via `eas submit --platform android --profile production --track internal` (with the service-account JSON configured in `eas.json`).
- The build appears in Internal Testing track. Add your tester emails. They receive an invite link; once they accept, they install the build via the Play Store on their device.

### 6.5 Promote to production

- After Internal Testing validates the build, promote it: in Play Console, **Internal Testing → Releases overview → Promote release → Production**.
- Choose **staged rollout** (5% → 20% → 50% → 100% over several days).
- Production review takes **1-7 days** on first submission, often faster on subsequent updates.

---

## 7. Common rejections (and the fixes)

### iOS

| Rejection | Fix |
|---|---|
| **2.1 — Performance, app crashes.** | Test on a real device, not just the simulator. Common cause: a permission that crashes when the user denies it. |
| **2.5.1 — Software requirements.** Default app icon, splash. | Replace the Expo defaults before submitting. |
| **3.1.1 — In-App Purchase.** Trying to use Stripe / web payments for digital goods. | Use Apple's IAP for any digital content/subscription consumed inside the app. External services (physical goods, B2B SaaS subscriptions managed by the company) are exempt. |
| **5.1.1 — Data Collection and Storage.** | Privacy policy URL is missing, broken, or doesn't match disclosed data collection. |
| **5.1.5 — Privacy.** Permission strings are vague. | Use `infoPlist` in `app.config.ts` to set specific `NS*UsageDescription` strings. Example: `NSCameraUsageDescription`: "Used to attach a photo to a support ticket so our team can help diagnose the issue." |
| **Guideline 4.0 — Design.** Default Expo splash, broken layout. | Iconography + splash that matches the brand. Real device test. |

### Android

| Rejection | Fix |
|---|---|
| **Privacy policy missing or invalid.** | A public, hosted URL is required even for Internal Testing. |
| **Data safety section incomplete.** | Fill it out honestly; submit before pushing to Production. |
| **Target API level too low.** | Ensure `compileSdkVersion` and `targetSdkVersion` match Google's current requirement (often "must target API ≥ 33" or higher; updates annually). Expo handles this if you keep the SDK up to date. |
| **Sensitive permissions without justification.** | Reduce permissions to only what's used. If `SMS`, `Call Log`, or `External Storage` permissions are present, expect scrutiny. |
| **Icon doesn't match guidelines.** | 512×512, no transparent borders that look cropped, no Expo defaults. |

---

## 8. First-72-hour ritual after launch

Once the app is live on either store:

1. **Hour 0-2:** install on your own device(s) via the store (not the EAS preview link — the real store install). Confirm the user journey works end-to-end. Crashes that happen on a real store install are different from EAS-preview crashes (signing differences, store-side bundling, install-time permissions).
2. **Hour 2-24:** monitor crash reports if Sentry / Crashlytics is wired. If not wired yet, add it before scaling beyond first-10 users.
3. **Hour 24-72:** monitor reviews. The first reviews are early signal — both positive (confirms direction) and negative (the bug or UX gap you missed). Respond to negative reviews; Apple and Google both let developers reply.
4. **End of week 1:** decide whether to roll a JS-only fix via OTA (per `eas-build-and-update.md` §6.1) or queue a native build for the next pass.

---

## 9. EAS Submit (the automation)

`eas submit` automates the upload-and-credentials step on both stores. Required setup, per `eas.json`:

```jsonc
"submit": {
  "production": {
    "ios":     { "ascAppId": "<App Store Connect app id>" },
    "android": { "serviceAccountKeyPath": "./google-play-service-account.json", "track": "internal" }
  }
}
```

- **`ascAppId`:** found in App Store Connect's app URL. EAS prompts for it on first submission.
- **`serviceAccountKeyPath`:** create a service account in Google Cloud → IAM (with Android Publisher role), download the JSON, store it locally and listed in `.gitignore`. Track it in `SECRETS.md`.
- **`track`:** `internal`, `alpha` (closed), `beta` (open), or `production`. Start at `internal` and promote within Play Console.

Run `eas submit --platform <ios|android> --profile production`. EAS handles the upload, the cert/key verification, and the build-attached metadata. Final metadata (description, screenshots, privacy answers) still happens in the respective consoles.

---

## 10. Handoffs

### 10.1 Outward

- `guides/mobile/eas-build-and-update.md` §10 is the release ceremony; this guide is the store-side counterpart.
- `guides/mobile/react-native-mvp-scaffold.md` §6 mentions the first-week distribution mechanics; this guide is the deeper version for public release.

### 10.2 Inward (defers to)

- Apple's *App Store Review Guidelines* (https://developer.apple.com/app-store/review/guidelines/) — verify current version before each submission.
- Google Play's *Developer Program Policies* — same.
- Expo / EAS docs for any flag or behavior this guide doesn't cover.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
