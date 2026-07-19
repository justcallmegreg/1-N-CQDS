---
name: building-frontend
description: Use when a project's architecture is decided and it needs its frontend built — choosing the framework, building the UI, adding localization, and writing end-to-end tests
---

# Building the Frontend

Builds the "1" — the user-facing app. The architecture is decided; this makes it real and good.

**REQUIRED BACKGROUND:** Use 1-n-cqds for the four invariants.
**Prerequisite:** `docs/purpose.md` and `ARCHITECTURE.md` exist. If not — **REQUIRED SUB-SKILL:** Use deciding-architecture.
**REQUIRED SUB-SKILL:** Use frontend-design for the UI itself — it is what keeps the result from looking generic.

## 1. Framework — by app shape (from ARCHITECTURE.md's decision)

| Shape | Framework |
|---|---|
| Content-shaped (marketing, docs, mostly-static, SEO-critical) | **Astro** |
| App-shaped (heavy client state, auth-gated dashboards, SSR wanted) | **Next.js** |
| Offline-first / pure-client (PWA, works with no network, sync-on-reconnect) | **Vite + React PWA** |

Astro is the default when the shape is ambiguous. **No frameworks beyond these three.** If `ARCHITECTURE.md` already recorded the framework, use it; otherwise pick by shape and record an ADR.

## 2. Localization — always ask

Ask whether the app needs more than one language. If yes:

- Strings live in `frontend/src/locales/{locale}.yaml` — **YAML dictionaries, one per locale.** No hard-coded user-facing strings anywhere.
- **Runtime switching is mandatory** — no rebuild, no full page reload.
- **Strategy falls out of SEO:** indexed/public → routed locales (`/en/`, `/de/`) + client nav; non-indexed (auth-gated, offline-first) → client-side locale store, an in-place swap.
- **Persist the choice in a cookie** (SSR reads it → first paint is already correct, no flash of the default locale).
- **The boundary:** backends return stable codes; the frontend owns every human-readable string. This is entailed by runtime switching — a backend-localized string would go stale on screen the instant the user switches.
- **Ask about RTL separately** from the locale list — it's the expensive part. Arabic/Hebrew change layout, not just strings. If in scope, use CSS logical properties (`margin-inline-start`, not `margin-left`) and mind icon direction.

See `assets/i18n/` for the runtime and dictionary structure (shipped for Vite+React; the README maps it to Astro/Next).

## 3. Build the UI

Use frontend-design. Build the **primary user journey** from `docs/purpose.md` first — it is the spine of the app and the mandatory e2e test.

## 4. Verify — with Playwright, for real

- **Dev-time:** drive the running app with Playwright, screenshot it, confirm it actually renders. "Looks right in the code" is not verification.
- **Write the e2e suite in `/e2e`** (repo root, a peer of `frontend/` and `backends/` — it tests the system). Mandatory: the **language switcher** (switch → assert re-render + cookie) and the **primary user journey**. See `assets/playwright/`. The language-switch spec drives `data-testid="app-tagline"` — your App must render it.

## 5. Preview (Coolify)

Coolify hosts the mock at a shareable URL for stakeholders. Produce a deployable build and document the deploy; the user runs their own Coolify instance.

## Scope note

i18n + Playwright assets ship complete for Vite+React. For Astro/Next, this skill documents the mapping; the wiring is built per-project.
