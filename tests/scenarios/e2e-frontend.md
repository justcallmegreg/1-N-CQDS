# End-to-end localized frontend validation scenario

The walking-skeleton milestone for Plan 3 (frontend generation and
localization runtime): take the Plan 3 assets — `i18n.ts`, `LanguageSwitcher.tsx`,
`locales/{en,de}.yaml`, and the Playwright harness (`playwright.config.ts` +
`language-switch.spec.ts`) — and build a real, minimal, localized frontend
for Fieldnote (offline-first → Vite+React PWA, per Plan 1's ADR-0006/0007/0009
and Plan 2's `e2e-scaffold-results.md`), then run the mandatory
language-switch Playwright e2e against it. This is not a new design
exercise — the assets are fixed inputs. This proves they compose into a
working app.

## What it exercises

- `npm create vite@latest --template react-ts` + `@modyfi/vite-plugin-yaml`
  wiring so `en.yaml` / `de.yaml` import as JS objects at build time.
- The i18n runtime (`I18nProvider`/`useI18n`/cookie read-write) actually
  mounted in a real React tree, not exercised in isolation.
- `LanguageSwitcher` wired to real dictionaries with real `data-testid`
  hooks (`language-select`), consumed by a component that was not written
  by Plan 3's author.
- A minimal `App.tsx` rendering `t("app.tagline")` into
  `data-testid="app-tagline"` per the interface contract Task 4's spec
  hard-codes.
- `frontend-design` applied to real, if minimal, product surface (not a
  synthetic demo) — a distinctive field-journal aesthetic, not generic
  scaffolding chrome.
- A real `npm run build` (tsc -b + vite build) and a real `npm run dev`
  server.
- Dev-time, tool-driven browser verification (Playwright MCP): navigate,
  snapshot, screenshot, switch language, snapshot again, reload, snapshot
  again — actually observing render, not asserting it.
- The mandatory `language-switch.spec.ts` run for real with
  `@playwright/test` + a real installed Chromium against the running dev
  server.

## Procedure

1. Scaffold `npm create vite@latest fieldnote-fe -- --template react-ts` in
   `/tmp` (scratch, not the plugin repo), `npm install`,
   `npm i -D @modyfi/vite-plugin-yaml`.
2. Wire `yaml()` into `vite.config.ts`; copy `i18n.ts`, `LanguageSwitcher.tsx`,
   `locales/en.yaml`, `locales/de.yaml` into `src/`.
3. Build `App.tsx`: `<I18nProvider locales={{en, de}} initial="en">`, a
   `data-testid="app-tagline"` paragraph rendering `t("app.tagline")`, and
   `<LanguageSwitcher />`. Style with `frontend-design`.
4. `npm run build` (must succeed), then `npm run dev` (serves on :5173).
5. Drive the running dev server with the Playwright MCP browser tools:
   load `/`, snapshot + screenshot (English), switch the
   `language-select` to `de`, snapshot + screenshot again (German, in
   place — no navigation), read `document.cookie`, reload, snapshot again
   (German persists).
6. Copy `playwright.config.ts` + `language-switch.spec.ts` into
   `/tmp/fieldnote-fe/e2e/`; `npm i -D @playwright/test`;
   `npx playwright install chromium`; run the suite against the already-running
   dev server via `BASE_URL=http://localhost:5173` (the config's own
   `webServer` fallback assumes a `../frontend` sibling layout that this
   scratch dir doesn't have — `BASE_URL` is the config's documented escape
   hatch for exactly this case).
7. Grade every row in the brief's table. Record results in
   `baseline-results/e2e-frontend-results.md`.
8. Stop the dev server; do not commit `/tmp/fieldnote-fe`.

## Grading

Per the reference-and-record reframe: grade the **built app's actual
behavior** (build success, real render, real runtime switch, real cookie
persistence, real Playwright pass), not pressure-resistance — there is no
adversarial pressure in this scenario, it's deterministic tooling either
composing correctly or not.
