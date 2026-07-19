# End-to-end localized frontend results — Fieldnote

Date: 2026-07-19. Scenario: `tests/scenarios/e2e-frontend.md`. Built in
scratch dir `/tmp/fieldnote-fe` (not committed — only this results file is
committed, per the brief). Node v26.3.0, npm 11.16.0.

## Framework

Vite 8.1.1 + React 19.2.7 + TypeScript 6.0.2, scaffolded via
`npm create vite@latest fieldnote-fe -- --template react-ts`. This matches
Fieldnote's real architecture decision (offline-first PWA, ADR-0006/0007/0009
from Plan 1, confirmed again in Plan 2's `e2e-scaffold-results.md`).
`@modyfi/vite-plugin-yaml` (^1.1.1) wired into `vite.config.ts` for direct
YAML-as-object imports:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import yaml from '@modyfi/vite-plugin-yaml'

export default defineConfig({
  plugins: [react(), yaml()],
})
```

## Assets installed, verbatim except one mechanical fix

`i18n.ts`, `LanguageSwitcher.tsx`, `locales/en.yaml`, `locales/de.yaml`
copied byte-for-byte from `skills/building-frontend/assets/i18n/` into
`src/`. Dictionary strings were **not** touched.

**One divergence, honestly noted:** `i18n.ts` as shipped imports
`ReactNode` as a value import (`import { ..., ReactNode, ... } from "react"`).
The Vite 8 / TS 6 template scaffolded here enables `verbatimModuleSyntax`,
under which a type-only import must say so explicitly. `tsc -b` failed with:

```
src/i18n.ts(3,60): error TS1484: 'ReactNode' is a type and must be imported
using a type-only import when 'verbatimModuleSyntax' is enabled.
```

Fixed by splitting the import:

```ts
import { createContext, useContext, useState, useCallback, createElement } from "react";
import type { ReactNode } from "react";
```

This is a TS-strictness compatibility fix only — no change to the i18n
contract (`useI18n()` still returns `{ t, locale, setLocale, locales }`),
cookie behavior, or any dictionary string. A newer/older Vite React template
without `verbatimModuleSyntax` would not need this.

Also added `src/yaml.d.ts` (not part of the shipped asset set, required for
any Vite+YAML setup) so TypeScript knows the shape of `*.yaml` imports:

```ts
declare module "*.yaml" {
  const data: Record<string, unknown>;
  export default data;
}
```

## App.tsx — the interface contract

```tsx
<I18nProvider locales={{ en, de }} initial="en">
  <Notebook />  {/* renders <p data-testid="app-tagline">{t("app.tagline")}</p>
                    and <LanguageSwitcher /> exactly per the brief */}
</I18nProvider>
```

Styling: a "field-journal" aesthetic (`frontend-design` skill invoked before
writing any UI code) — warm paper background with a subtle ruled-paper
texture, a dashed-stitch notebook-page border, `Fraunces` (display serif,
italic tagline) paired with `IBM Plex Mono` (labels/body — evokes typewritten
field notes), a rust/terracotta accent on the active tab and primary button,
and a small hand-drawn leaf/compass mark next to the wordmark. Kept minimal
per the brief (tagline, switcher, two nav labels, one action button — no
extra invented copy). Every user-facing string in the rendered tree comes
from `t(...)` against `en.yaml`/`de.yaml` (`app.title`, `app.tagline`,
`nav.observations`, `nav.report`, `actions.add`, `actions.switch_language`);
no hard-coded product-text strings.

## Build

```
$ npm run build
> fieldnote-fe@0.0.0 build
> tsc -b && vite build

vite v8.1.5 building client environment for production...
transforming...✓ 21 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.80 kB │ gzip:  0.44 kB
dist/assets/index-wsnQoxIF.css    3.04 kB │ gzip:  1.22 kB
dist/assets/index-CARa6VOW.js   193.58 kB │ gzip: 61.31 kB

✓ built in 341ms
```

**Build: PASS.** Typecheck (`tsc -b`) and `vite build` both succeeded, exit 0.

## Dev-time verification (Playwright MCP browser tools — observed, not assumed)

`npm run dev` served on `http://localhost:5173`. Driven with the Playwright
MCP browser tools (`browser_navigate`, `browser_snapshot`,
`browser_take_screenshot`, `browser_select_option`, `browser_evaluate`):

1. **Navigate to `/`.** Accessibility snapshot confirmed:
   `paragraph [ref=e13]: Record observations offline. Sync when you can.`
   — English tagline rendered on first paint, exactly matching `en.yaml`.
2. **Screenshot** (`fieldnote-en.png`) — visually confirms the field-journal
   layout: wordmark + leaf mark, "LANGUAGE / English" select top-right,
   italic serif tagline, "OBSERVATIONS / SEASON REPORT" tabs, a dashed entry
   well, and a rust "+ Add observation" button.
3. **Switch language**: `page.getByTestId('language-select').selectOption(['de'])`.
   Snapshot immediately after showed **no navigation** (same page object) and
   every string re-rendered in German: tagline →
   `Beobachtungen offline erfassen. Synchronisieren, wenn möglich.`, tabs →
   `Beobachtungen` / `Saisonbericht`, button →
   `Beobachtung hinzufügen`, switcher label → `Sprache`.
4. **Cookie check**: `document.cookie` evaluated to `"locale=de"`.
5. **Screenshot** (`fieldnote-de.png`) — visually confirms the German render
   in the same layout.
6. **Reload**: `browser_navigate` to `/` again (fresh navigation, cookie
   already set). Snapshot showed the page still fully in German
   (`Sprache`/`Deutsch` selected, German tagline/tabs/button) — no flash
   back to English observed.

Screenshots saved at (scratchpad, outside the repo):
`/private/tmp/claude-501/-Users-greg-Workspaces-Personal-1-N-CQDS/2eda3e58-cb76-4193-9f1c-2adcdc777476/scratchpad/fieldnote-en.png`
and `.../fieldnote-de.png`.

**Dev-time verification: PASS.** All four sub-checks (English first paint,
in-place switch, cookie write, reload persistence) directly observed via
tool-driven browser snapshots/screenshots, not asserted.

## The mandatory e2e (`language-switch.spec.ts`)

`playwright.config.ts` + `language-switch.spec.ts` copied verbatim into
`/tmp/fieldnote-fe/e2e/`. `@playwright/test` (^1.61.1) installed;
`npx playwright install chromium` — browser already present, exit 0.

The shipped config's `webServer` fallback runs
`npm --prefix ../frontend run dev`, which assumes an `e2e/` directory that
is a *sibling* of a `frontend/` directory (the real repo layout this asset
is designed for). In this scratch validation, `e2e/` lives inside
`fieldnote-fe/` itself, so that relative path doesn't resolve. The config
already anticipates this exact case: when `BASE_URL` is set, `webServer` is
`undefined` and Playwright targets the URL directly instead. Used that
documented escape hatch — dev server was already running
(`npm run dev` on :5173, confirmed via `curl` returning `200`) — rather than
editing the config or the spec.

```
$ cd /tmp/fieldnote-fe/e2e && BASE_URL=http://localhost:5173 npx playwright test --config=playwright.config.ts

Running 1 test using 1 worker

  ✓  1 language-switch.spec.ts:4:1 › switches language at runtime without reload and persists via cookie (364ms)

  1 passed (2.3s)
```

**Mandatory e2e: PASS.** 1/1 test passed — English default paint, in-place
switch to German, cookie `locale=de` written, reload persists German with
the test's own assertions (not just dev-time observation) confirming no
flash back to English.

## Graded table

| Check | Expected | Result |
|---|---|---|
| Framework | Vite+React PWA (offline-first) | ✅ Vite 8.1.1 + React 19.2.7 + TS 6.0.2, matches Plan 1/2's real architecture decision |
| i18n dicts | en.yaml + de.yaml load | ✅ loaded via `@modyfi/vite-plugin-yaml`; both dicts rendered correctly at runtime |
| Runtime switch | tagline changes EN→DE with no reload | ✅ observed via MCP snapshot (same page, no navigation) and asserted by the Playwright spec |
| Cookie persist | `locale=de` cookie; survives reload, no flash | ✅ `document.cookie` = `"locale=de"`; reload (both MCP-driven and Playwright-asserted) kept German |
| Playwright language-switch | test passes | ✅ `1 passed (2.3s)` — see command output above |
| Dev-time verification | UI observed rendering (screenshot) | ✅ `fieldnote-en.png` / `fieldnote-de.png`, both accessibility-snapshotted and screenshotted |
| No hard-coded strings | user-facing text comes from dicts | ✅ every rendered string traces to `t("...")` against `en.yaml`/`de.yaml`; no invented literal product copy |

**7/7 rows pass.**

## Divergence — honest notes

1. `i18n.ts`'s `ReactNode` import needed a mechanical `verbatimModuleSyntax`
   fix (see above) to typecheck under the Vite 8/TS 6 template scaffolded in
   this environment. No behavioral or contract change.
2. The e2e was run with `BASE_URL=http://localhost:5173` against a
   dev server started ahead of time, rather than letting the config's
   `webServer` block start it — because this scratch validation's directory
   layout (`e2e/` nested inside the frontend scratch dir) doesn't match the
   `../frontend`-sibling layout the config's `webServer` fallback assumes
   for the real repo. This is the config's own documented fallback path, not
   a modification to the config or the spec — both files are otherwise
   byte-identical to the shipped assets.

No other divergence. The test was not weakened, retried into passing, or
edited in any way to force a pass.

## Cleanup

Dev server stopped (`pkill -f "vite --port 5173"`; confirmed `curl` to
`:5173` returns no response afterward). `/tmp/fieldnote-fe` was not
committed — scratch only, per the brief.

## Verdict

**Plan 3 walking-skeleton test: PASS.** A real, minimal, localized Fieldnote
frontend builds cleanly, renders (observed via tool-driven browser snapshots
and screenshots — English on first paint, in-place switch to German, cookie
persistence across reload), and the mandatory `language-switch.spec.ts`
passes for real against a real installed Chromium. This is Greg's call to
ratify, per the brief, but nothing here contradicts a go verdict on Plan 3.
