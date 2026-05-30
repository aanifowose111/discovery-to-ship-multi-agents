# React Native MVP scaffold

> **Stack note:** This guide applies to projects whose MVP brief picks the workspace default of **React Native + Expo + TypeScript** (per `guides/product/mvp-scoping-methodology.md` §6.0). If a different mobile stack is chosen (Swift native, Kotlin native, Flutter, etc.), this guide does not apply — Claude will work from first principles + the agent-skills stack-agnostic skills, or you can contribute a new stack-specific scaffold guide. See `README.md` § "Stack flexibility."

The opinionated starting shape for every new React Native MVP in this workspace. Picks defaults that match the Fijara mobile app — Expo + TypeScript + a Flask-backed API — so we are not re-deciding the same questions on every new product.

Used **right after `/scope-mvp` returns `green-lit-to-build`** for any brief with `domain: mobile` or `domain: hybrid`. The scoping report has named the must-haves; this guide describes the order of work to stand up a buildable, installable shell that the must-haves will be built into.

This guide is **stack-specific**. The *how to build a feature well* questions (incremental implementation, TDD, code review) are answered by the agent-skills repo. This guide answers *what shape the RN project takes*, *what tools we default to*, and *in what order to lay down the skeleton from `create-expo-app` to a TestFlight-able build*.

---

## 1. Purpose

Every new RN MVP should reach an **installable shell** within the first 2-3 working sessions, before any feature work begins. The shell has:

- An Expo + TypeScript project scaffolded with `expo-router` file-based routing.
- One screen rendering a server response from the paired Flask backend (proves the backend pairing works end-to-end).
- A typed API client with auth-token interceptor.
- TanStack Query and Zustand wired up.
- `eas.json` configured with at least `development` and `preview` profiles.
- One passing component test.
- A successful `eas build --profile preview` that produces an installable artifact (`.ipa` for iOS, `.apk` for Android).

Feature work begins from this shell. It does not begin from `create-expo-app`. The shell exists so that "is this installable on a real device?" is answered once, early, before features mask provisioning, build, or pairing problems.

---

## 2. Operating principles

1. **Conventions over creativity at scaffold time.** The scaffold is not where to be clever. Reuse the shape below; reserve creativity for the product.
2. **Match what worked on the Fijara mobile app.** Expo, TypeScript, REST against a dockerized Flask backend, JWT-style auth stored in secure-store. Departures only when the new product genuinely needs them.
3. **The scaffold produces an installable shell, not a working product.** Working product comes from the must-haves in the MVP brief.
4. **Default to Expo (managed workflow), not bare React Native.** Bare RN buys native-module flexibility at a meaningful ops cost (Xcode + Gradle locally). Pay it only when a must-have requires a native module Expo cannot provide.
5. **Backend pairing is part of the scaffold, not a later step.** Until the shell renders one server response, "the app works on my phone" does not mean the system works.
6. **Tests exist from day one.** Even if it is one test of one component. `jest` and `@testing-library/react-native` should be live before any business logic.
7. **`.env.example` is documentation; `.env` is local-only.** Production secrets land in EAS environment variables or in the app's runtime config via the platform, never in committed `.env`.
8. **Per `CLAUDE.md`, web search/fetch is free** — look up Expo docs, library versions, EAS profiles without asking.

---

## 3. The target shape

```
<slug>/
├── .env.example
├── .env                          # gitignored
├── .gitignore
├── app.config.ts                 # dynamic Expo config (reads .env)
├── eas.json                      # EAS Build / Update profiles
├── package.json
├── tsconfig.json
├── README.md
├── MVP.md                        # the brief, from /scope-mvp
├── FUNDING.md                    # iff funding decision is made
├── SECRETS.md                    # gitignored, user-only secret-location notes
├── app/                          # expo-router — file-based routes
│   ├── _layout.tsx               # root layout: providers (QueryClient, Auth)
│   ├── index.tsx                 # home / landing screen
│   ├── (auth)/                   # auth route group
│   │   ├── _layout.tsx
│   │   └── login.tsx
│   └── (tabs)/                   # main tab navigator
│       ├── _layout.tsx
│       └── home.tsx
├── src/                          # all non-route code
│   ├── api/
│   │   ├── client.ts             # axios instance + auth interceptor
│   │   └── endpoints.ts          # typed endpoint functions
│   ├── auth/
│   │   ├── store.ts              # zustand auth store
│   │   └── secure-storage.ts     # expo-secure-store wrapper
│   ├── components/               # shared components
│   ├── hooks/
│   ├── stores/                   # other zustand stores
│   ├── theme/
│   │   ├── tokens.ts             # design tokens (colors, spacing, type scale)
│   │   └── index.ts
│   ├── types/                    # shared TS types — mirrors backend response shapes
│   └── utils/
├── assets/
│   ├── icon.png                  # 1024×1024
│   ├── splash.png
│   ├── adaptive-icon.png         # Android
│   └── favicon.png               # for web target if enabled
└── __tests__/
    ├── setup.ts                  # jest config + RN/expo polyfills
    └── home.test.tsx             # first test
```

**Do not deviate from this shape** without recording the reason in `README.md`.

---

## 4. Default conventions

### 4.1 Framework

**Expo SDK (managed workflow)** with `expo-router`. Same workflow Fijara mobile uses. Bare RN only when a must-have requires it — record that decision in the brief and `README.md`.

### 4.2 Language

**TypeScript**, strict mode in `tsconfig.json`. No incremental migration debt; the marginal cost on day one is zero.

### 4.3 Navigation

**`expo-router`** (file-based, similar to Next.js). Route groups in parentheses (`(auth)`, `(tabs)`). The root `app/_layout.tsx` mounts providers.

### 4.4 State management

| Kind of state | Tool |
|---|---|
| Server / API state (cache, refetch, mutations) | **TanStack Query** (`@tanstack/react-query`) |
| Client state, including auth (token, user, login status) | **Zustand** stores in `src/stores/` and `src/auth/store.ts` |
| Per-screen local state | `useState` / `useReducer` |

Redux only if state complexity demands it (rare at MVP scale). Context API only for theming.

### 4.5 API client

`src/api/client.ts` is an `axios` instance with two interceptors:

- **Request interceptor** — pulls the auth token from `secure-storage`, attaches `Authorization: Bearer <token>`.
- **Response interceptor** — on 401, clears the token, redirects to `/login`.

`src/api/endpoints.ts` defines one typed function per endpoint (input type → response type) so screens never reach into `client` directly. This keeps the contract explicit and makes the backend-response shapes visible in one file.

The backend base URL comes from `EXPO_PUBLIC_API_URL` in `.env` (or `app.config.ts` at build time). One URL per environment (dev, staging, prod).

### 4.6 Auth storage

**`expo-secure-store`** for the JWT (or session token). Never `AsyncStorage` for tokens. Wrapped in `src/auth/secure-storage.ts` so the choice can change later without ripping out call sites.

### 4.7 Styling

**StyleSheet + design tokens.** Define colors, spacing, and a small type scale in `src/theme/tokens.ts`; reference them from `StyleSheet.create` everywhere else.

NativeWind (Tailwind for RN) is allowed if the user is comfortable with Tailwind and the brief has multiple tightly-styled screens. It adds a build-time dependency; pay it only when it earns its place.

### 4.8 Tests

- **`jest`** + **`@testing-library/react-native`** for unit / component tests.
- **`maestro`** for e2e only when the MVP brief explicitly calls for it. Most MVPs skip e2e and rely on observation during the first-users phase.

The first test exercises one component on one route. Add more when must-haves get built.

### 4.9 Linting and formatting

**`eslint`** with the Expo preset + **`prettier`**. Optionally a `husky` + `lint-staged` pre-commit hook.

If `ruff`-style single-tool ergonomics matter, **Biome** is an emerging single-tool replacement for ESLint + Prettier — flag as an option, but don't default to it until a project specifically wants it.

### 4.10 Build pipeline

**EAS Build** for `.ipa` / `.apk` / `.aab` production artifacts. **EAS Update** for OTA JS-only updates between native releases. Builds run in the cloud; no local Xcode/Gradle setup required.

`eas.json` profiles, at minimum:

```jsonc
{
  "build": {
    "development": { "developmentClient": true, "distribution": "internal" },
    "preview":     { "distribution": "internal" },
    "production":  { "autoIncrement": true }
  },
  "submit": {
    "production": { "ios": { "ascAppId": "<...>" }, "android": { /* ... */ } }
  }
}
```

### 4.11 Backend pairing notes

- RN is **not a browser**. No CORS configuration is needed on the Flask side for the mobile client.
- The Flask backend serves the same API to both the mobile client and any web client. Endpoint design should not be mobile-specific — the same `/api/...` URLs work for both.
- Auth on the Flask side: a token endpoint (e.g., `POST /api/auth/token`) that accepts credentials and returns a JWT or opaque token. The mobile client stores it in secure-store.
- For first-user testing without a deployed backend, point `EXPO_PUBLIC_API_URL` at the local Flask dev server's network-accessible URL (your machine's LAN IP, port 5000). Real-device testing requires LAN reachability.

---

## 5. The scaffold sequence

Do these in order. Do not skip ahead to feature work until the sequence is complete.

### Step 1 — Create the project

```bash
npx create-expo-app@latest <slug> --template tabs
cd <slug>
git init && git add . && git commit -m "scaffold: create-expo-app"
```

Copy the MVP brief into the root if it isn't already there. Read it. Identify the backend URL the shell needs to call.

### Step 2 — Gitignore, env, secrets

`.gitignore` (extend the default with):

```
.env
SECRETS.md
*.tmp
.eas
```

Write `.env.example` listing every key (`EXPO_PUBLIC_API_URL=`, etc.). Copy to `.env` with local values.

`SECRETS.md` is for you — where each production secret/key lives (App Store Connect, Google Play Console, EAS secrets dashboard, backend secret manager).

### Step 3 — Restructure into `app/` (routes) + `src/` (code)

The `create-expo-app` template puts route files in `app/`. Move all non-route helpers, components, hooks, stores into `src/`. Update imports.

### Step 4 — Add core dependencies

```bash
npx expo install @tanstack/react-query zustand axios expo-secure-store
npx expo install --dev @testing-library/react-native
```

(Use `npx expo install` rather than plain `npm install` for libraries with native code — Expo will pin to versions compatible with the SDK.)

### Step 5 — API client + auth store

Create `src/api/client.ts`, `src/api/endpoints.ts`, `src/auth/store.ts`, `src/auth/secure-storage.ts`. The interceptors pull from the Zustand auth store via the secure-storage wrapper.

### Step 6 — Root layout wires providers

`app/_layout.tsx`:

```tsx
import { Stack } from "expo-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const qc = new QueryClient();

export default function RootLayout() {
  return (
    <QueryClientProvider client={qc}>
      <Stack />
    </QueryClientProvider>
  );
}
```

### Step 7 — Home screen renders one server response

`app/index.tsx` uses an `endpoints.ts` function and TanStack Query's `useQuery` to fetch one endpoint from the backend (a health check or a small data endpoint) and renders the result. This is the **end-to-end pairing proof** — until this works, the scaffold is not complete.

### Step 8 — First test

```tsx
// __tests__/home.test.tsx
import { render, screen } from "@testing-library/react-native";
import Home from "../app/index";
// mock the endpoint or wrap with a mock QueryClient
test("home screen renders", () => {
  render(<Home />);
  expect(screen.getByText(/.+/)).toBeTruthy();
});
```

```bash
npm test
```

It passes. If not, fix before proceeding.

### Step 9 — Assets

Replace the default icon, splash, and adaptive-icon with placeholders that match the product (even rough ones — 1024×1024 PNG of the slug name is fine for now). App store reviewers reject the default Expo logo.

### Step 10 — EAS config and first build

```bash
npm install -g eas-cli
eas login
eas build:configure
# edit eas.json per §4.10
eas build --profile preview --platform ios     # or android, or both
```

When the build finishes, install the artifact:

- **iOS preview build** → install via TestFlight (requires Apple Developer membership) or via the EAS-provided install link if it's an internal-distribution `.ipa`.
- **Android preview build** → install the `.apk` directly on a device.

Open the app. Confirm the home screen renders the server response from the paired Flask backend. **Until this works, the scaffold is not complete.**

### Step 11 — Commit and tag

```bash
git add . && git commit -m "scaffold: installable shell, paired with backend"
git tag scaffold-done
```

Anything from this point on is feature work.

---

## 6. First-week checklist

Once the scaffold is up, the first week's feature work follows the *first-week build checklist* from the scoping report (per `guides/product/mvp-scoping-methodology.md` §9). The scaffold guide just provides the platform on which that checklist runs.

### Skills Claude applies automatically during the build

The following skills from `.claude/skills/` (file-copied from the agent-skills repo by **Addy Osmani**, MIT-licensed) are **auto-invoked** during the build phase without the user having to ask — see `CLAUDE.md` § "Build-phase skill auto-invocation" for the full list. Most relevant for React Native mobile builds:

- **`incremental-implementation`** — every feature lands in small, testable steps.
- **`test-driven-development`** — write a failing test (`jest` + `@testing-library/react-native`), then the smallest TSX to pass it, then refactor.
- **`code-review-and-quality`** — Claude runs a 5-axis review (correctness / readability / architecture / security / performance) at every PR-ready moment.
- **`code-simplification`** — Claude proactively suggests removing cruft.
- **`frontend-ui-engineering`** — applied when writing screens, components, or styles. **React/TSX examples translate naturally** to this stack (unlike Flask, where they don't).
- **`security-and-hardening`** — auto-applied to any code touching `src/auth/`, `src/api/client.ts`, secure-store, deep-link handlers, or any input that becomes a backend request.
- **`api-and-interface-design`** — applied when designing the typed endpoint functions in `src/api/endpoints.ts`.
- **`performance-optimization`** — applied when list-rendering, navigation, or animations show user-visible latency.
- **`debugging-and-error-recovery`** — applied when behavior diverges between Expo Go, dev client, and EAS preview builds.
- **`documentation-and-adrs`** — applied when a non-trivial architecture decision deserves a record.
- **`git-workflow-and-versioning`** — applied at commit time for hygiene.
- **`ci-cd-and-automation`** — applied when setting up EAS Build / Update workflows.
- **`shipping-and-launch`** — applied at TestFlight / Play Internal Testing / production release time.

You do not need to invoke these explicitly. If you'd rather Claude *not* apply one in a specific case, just say so.

| Day | Work |
|---|---|
| 1 | Scaffold (steps 1-11 above) |
| 2 | First must-have — the smallest one, end-to-end (screen → endpoint → secure-store interaction if relevant → test) |
| 3 | Second must-have, same shape |
| 4 | Remaining must-haves; close the success-criterion measurement gap |
| 5 | Distribute to first 1-3 testers via TestFlight (iOS) / Internal Testing (Android); observe |
| weekend | Fix what broke; queue learnings |

**First-user distribution mechanics matter more than on web** — on web you send a URL. On mobile, the first 10 users need TestFlight invites (iOS) or to be added to Google Play Internal Testing (Android), and both require ~1-day platform review on the first build. Plan around this; don't promise "I'll send it tonight" the night before TestFlight first runs.

---

## 7. Handoffs

### 7.1 Outward (which workflows pick this guide up)

- `/scope-mvp` returns `green-lit-to-build` for a `domain: mobile` brief → this guide is the next thing the build follows.
- For `domain: hybrid` briefs, both this guide and `flask-mvp-scaffold.md` apply — the Flask backend is built first, then the RN app pairs to it.
- The agent-skills `code-reviewer` persona references project conventions when reviewing diffs — this guide *is* those conventions for RN MVPs.
- The agent-skills slash commands (`/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship`) operate on top of the scaffold this guide produces.

### 7.2 Inward (which guides this one defers to)

- **agent-skills repo** — `external/agent-skills/skills/incremental-implementation/`, `test-driven-development/`, `frontend-ui-engineering/` (useful for the React side), `shipping-and-launch/`. The *how to build well* lives there.
- **MVP brief** — what to build.
- `guides/product/mvp-scoping-methodology.md` §6 — `.env`, secrets, hosting (for the *backend*), and auth defaults.
- `guides/web/flask-mvp-scaffold.md` — when a hybrid brief is involved, the Flask side scaffolds with that guide first.

### 7.3 Future companion guides (write when needed, not preemptively)

- `rn-app-store-submission.md` — App Store Connect + Google Play Console setup, privacy policy requirements, content rating, review-process realities. Becomes necessary when a project is days away from first public release.
- `rn-auth-patterns.md` — JWT-with-refresh-token, OAuth via `expo-auth-session`, biometrics. Becomes necessary when the second mobile MVP picks an auth pattern different from JWT.
- `eas-build-and-update.md` — deeper than §4.10 / §5: build secret management, dynamic config, OTA cadence, channel strategy. Becomes necessary when the project starts shipping more than one build per week.
- `rn-offline-and-sync.md` — for products that need to work offline and reconcile with the backend. Becomes necessary only if a must-have requires it.

---

## 8. When to deviate from the scaffold

Deviations are allowed but must be **recorded in the project's `README.md`** with a one-paragraph reason. Acceptable reasons:

- A must-have requires a native module that Expo's managed workflow does not support → switch to bare RN. Pay the Xcode/Gradle setup cost knowingly.
- The project is a single-screen tool with no backend → drop TanStack Query, drop the API client, keep TypeScript + Expo + the test setup.
- A must-have requires real-time features (WebSockets, push notifications with rich logic) that need a different state layer.

Not acceptable reasons:

- "I want to try a new state library." Try it on a side project.
- "TypeScript feels heavy." It does not, after week one. The marginal cost is zero; the lifetime benefit is large.
- "Expo seems limiting." If it genuinely is for this product, write down what it cannot do. Usually it can.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
