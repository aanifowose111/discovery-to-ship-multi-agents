# mobile-apps/

Your React Native + Expo mobile applications. **This folder is gitignored** (except this README) — each individual product is its own private workspace.

## Per-product layout

When a card reaches `green-lit-to-build` for a mobile or hybrid brief and `/scope-mvp` produces a brief, the build phase starts here. Each product is a subfolder at `mobile-apps/<slug>/`:

```
mobile-apps/<slug>/
├── MVP.md                  Source-of-truth brief (from /scope-mvp)
├── FUNDING.md              Funding-path decision (if applicable)
├── README.md               Per-product overview
├── app.config.ts           Expo dynamic config
├── eas.json                EAS Build / Update profiles
├── package.json
├── tsconfig.json
├── app/                    Routes (expo-router file-based)
├── src/                    All non-route code (api, auth, components, ...)
├── __tests__/
├── assets/                 Icon, splash, adaptive icon
└── design/                 (only after the optional design phase)
    ├── DESIGN_RESEARCH.md
    ├── DESIGN_BRIEF.md
    ├── figma/
    │   └── README.md
    └── handoff/
        ├── tokens.json
        ├── assets/
        └── screenshots/
```

## Build guides

- `guides/mobile/react-native-mvp-scaffold.md` — the 11-step scaffold sequence from `npx create-expo-app` to an installable shell.
- `guides/mobile/eas-build-and-update.md` — EAS profiles, channels, OTA strategy, release ceremony.
- `guides/mobile/rn-app-store-submission.md` — Apple App Store and Google Play submission runbooks.

## Backend pairing

Most mobile apps in this workspace pair with a Flask backend (see `web-apps/`). The mobile scaffold guide §4.11 covers the contract — JWT-based auth (per `guides/web/flask-auth-patterns.md` §11), no CORS needed on the Flask side (RN is not a browser), shared endpoint design (same `/api/...` URLs serve both web and mobile clients).

## Hybrid products

When a product has both web and mobile sides (`domain: hybrid` in the MVP brief), both `web-apps/<slug>/` and `mobile-apps/<slug>/` exist. The Flask backend scaffolds first; the RN app pairs to it.
