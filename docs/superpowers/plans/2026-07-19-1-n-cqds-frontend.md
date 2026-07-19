# 1-N-CQDS Frontend — Implementation Plan (Plan 3 of 5)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `building-frontend` — the skill that guides construction of a project's frontend (framework chosen by app shape, UI quality via `frontend-design`, mandatory runtime i18n, Playwright verification) — plus the reusable i18n and Playwright assets it installs into a repo.

**Architecture:** A technique skill, not a deterministic emitter. Every project's UI differs, so `building-frontend` is a procedure Claude follows, and the shippable *assets* are only the framework-agnostic parts: the YAML dictionary structure, a reactive locale store with cookie persistence, and a Playwright harness whose mandatory case is the language switcher. The i18n/Playwright pattern ships fully for Vite+React PWA (what the validation uses); the skill documents its mapping to Astro (routed locales) and Next.

**Tech Stack:** Vite + React + TypeScript (validation framework), a lightweight YAML-backed i18n runtime, `js-cookie`-style cookie persistence (hand-rolled, no dep), Playwright (`@playwright/test`), `frontend-design` skill, `superpowers:brainstorming` (already the vision gate).

## Where this sits

Plan 3 of 5. Plans 1 (doctrine engine) and 2 (scaffolding) are merged.

| Plan | Scope | Testable deliverable |
|---|---|---|
| 1 ✅ | Doctrine engine | Decisions + ADRs |
| 2 ✅ | Repo scaffolding | Skeleton + infra boots |
| **3 (this)** | Frontend — building-frontend skill, i18n, Playwright | A real localized frontend that builds, renders, switches language at runtime, passes a Playwright language-switch test |
| 4 | Backends — Python/Go skeletons, multi-arch Dockerfiles, ORM | `make up` boots the full stack; a service serves against the DB |
| 5 | Delivery + releases | CI, registry, Trivy, GitFlow, backport |

**What Plan 3 produces goes into `frontend/`** (the scaffolded dir from Plan 2, currently empty) **and `e2e/`** (the Playwright suite at repo root — a peer of frontend/backends, because e2e tests the whole system, per the spec).

## Plan 1 & 2 learnings that govern this plan

1. **Point to the spec, don't reproduce doctrine.** The framework menu, the i18n boundary rule, and the Playwright placement are spec-verbatim where stated. Template/asset *code* is reviewed as code (the exception).
2. **Rationale vs. rules.** `building-frontend` explains *why* (e.g. why offline-first → client store); it introduces no new rules the spec lacks.
3. **Reference-and-record, not discipline.** This is technique + assets. `building-frontend` is tested by **application** (build a frontend with it — does it work?), not pressure baselines. The i18n runtime and Playwright test are real code with real tests.
4. **Test the input space, not the happy path.** The validation uses Vite+React (offline-first). The skill must still correctly handle content-shaped (Astro) and app-shaped (Next) — the framework-selection logic gets checked against all three shapes even though only one is built end-to-end.
5. **Grade on the artifact.** Plan 3's verdict is "a localized frontend renders and the Playwright language-switch test passes," not "the skill reads well."
6. **Honest verification.** Playwright/browser must actually run and observe the UI. A claimed render that wasn't observed is the Plan-1 failure class.

## Global Constraints

Copied from the spec (`docs/superpowers/specs/2026-07-17-1-n-cqds-design.md`), exact values:

- **Framework by app shape:** content → **Astro**; app-shaped → **Next.js**; offline-first/pure-client → **Vite + React PWA**. Astro is the default when ambiguous. No frameworks beyond these three. The choice is recorded in an ADR.
- **UI quality delegated to `frontend-design`.** The framework is the shell; `frontend-design` decides if the UI is good.
- **Localization always asked.** Strings live in **YAML dictionaries**, one file per locale, at `frontend/src/locales/{locale}.yaml`.
- **Runtime switching is mandatory** — change language with no rebuild, no full reload.
- **Strategy by SEO constraint:** public/indexed → **routed locales** (`/en/`, `/de/`) + client-side nav; auth-gated dashboard/offline → **client-side locale store** (true in-place swap).
- **Persistence: cookie** (SSR-readable → no flash of default locale). Not localStorage, not URL-only.
- **The localization boundary:** backends return **stable codes**; the frontend owns **every human-readable string**. Entailed by runtime switching — a backend-localized string goes stale on switch.
- **RTL is asked separately** from the locale list (it changes layout, not just strings — CSS logical properties, icon direction).
- **Playwright is the e2e framework.** The suite lives at **`/e2e`** (repo root, peer of frontend/backends). Two jobs: the system suite, and dev-time UI verification in `building-frontend`.
- **Mandatory e2e cases:** the **language switcher**, and the **primary user journey** named in `docs/purpose.md`.
- **Coolify** is the preview host — a **documented deploy step**, not executed during this plan (no assumed instance/credentials). Dev-time verification uses Playwright locally.
- **Skill frontmatter:** `name` + `description`, `description` starts with `Use when`, third person, triggers only.

## Coverage boundary

Full i18n + Playwright asset support ships for **Vite + React PWA** (the validation framework). For **Astro** and **Next**, `building-frontend` documents the pattern mapping (routed locales for Astro; app-router i18n for Next) but does not ship complete starter code — consistent with Plan 1's Tier-1/doctrine-only philosophy. This is stated in the skill, not hidden.

## File Structure

```
skills/building-frontend/
├── SKILL.md                              # the technique: shape→framework, frontend-design, i18n, Playwright, Coolify
├── assets/
│   ├── i18n/
│   │   ├── locales/en.yaml               # dictionary structure example
│   │   ├── locales/de.yaml
│   │   ├── i18n.ts                       # runtime: load dict, t(), reactive locale, cookie persist (Vite+React)
│   │   └── README.md                     # structure + how Astro/Next map
│   ├── playwright/
│   │   ├── playwright.config.ts          # points at /e2e, baseURL, webServer
│   │   ├── language-switch.spec.ts       # MANDATORY case — switch locale, assert re-render + cookie
│   │   └── journey.spec.ts.tmpl          # primary-user-journey template
│   └── rtl/
│       └── rtl-notes.md                  # CSS logical properties convention
└── (no tests/ — the assets are validated by the walking-skeleton build in Task 8)
```

The **validation frontend** (Task 8) is built in a scratch dir, not committed to the plugin — like the Fieldnote scaffold in Plan 2.

---

### Task 1: building-frontend SKILL.md — the technique

**Files:**
- Create: `skills/building-frontend/SKILL.md`

**Interfaces:**
- Consumes: `docs/purpose.md` (Primary user journey, users), `ARCHITECTURE.md` (frontend framework decision).
- Produces: a built, localized frontend in `frontend/` and Playwright specs in `e2e/`. Invoked after `deciding-architecture`; invokes `frontend-design`.

- [ ] **Step 1: Write the skill**

Technique skill, `description` compliant, budget <500 words. Doctrine (framework menu, i18n boundary, Playwright placement) is spec-verbatim; the rest is procedure.

```markdown
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
| Content-shaped (marketing, docs, SEO-critical) | **Astro** (default) |
| App-shaped (heavy client state, auth dashboards, SSR) | **Next.js** |
| Offline-first / pure-client (PWA, works with no network) | **Vite + React PWA** |

If `ARCHITECTURE.md` already recorded the framework, use it. Otherwise pick by shape and record an ADR.

## 2. Localization — always ask

Ask whether the app needs more than one language. If yes:

- Strings live in `frontend/src/locales/{locale}.yaml` — **YAML dictionaries, one per locale.** No hard-coded user-facing strings anywhere.
- **Runtime switching is mandatory** — no rebuild, no full reload.
- **Strategy by SEO:** indexed/public → routed locales (`/en/`,`/de/`) + client nav; auth-gated/offline → client-side locale store (in-place swap).
- **Persist the choice in a cookie** (SSR reads it → no flash of the default language).
- **The boundary:** backends return codes; the frontend owns every human string. A backend-localized message goes stale the instant the user switches — so it must not exist.
- **Ask about RTL separately** — Arabic/Hebrew change layout, not just strings. If in scope, use CSS logical properties (`margin-inline-start`, not `margin-left`) and mind icon direction.

See `assets/i18n/` for the runtime and dictionary structure (shipped for Vite+React; the README maps it to Astro/Next).

## 3. Build the UI

Use `frontend-design`. Build the **primary user journey** from `docs/purpose.md` first — it is the spine of the app and the mandatory e2e test.

## 4. Verify — with Playwright, for real

- **Dev-time:** drive the running app with Playwright, screenshot it, confirm it actually renders. "Looks right in the code" is not verification.
- **Write the e2e suite in `/e2e`** (repo root — it tests the system, not just the frontend). Two cases are mandatory: the **language switcher** (switch → assert re-render + cookie) and the **primary user journey**. See `assets/playwright/`.

## 5. Preview (Coolify)

Coolify hosts the mock at a shareable URL for stakeholders. Produce a deployable build and document the deploy; the user runs their own Coolify instance.

## Scope note

i18n + Playwright assets ship complete for Vite+React. For Astro/Next, this skill documents the mapping; the wiring is built per-project.
```

- [ ] **Step 2: Verify word budget + description compliance**

Run: `wc -w skills/building-frontend/SKILL.md`
Expected: <500. `description` starts "Use when", third person, no other-plugin skill names, no imperative.

- [ ] **Step 3: Commit**

```bash
git add skills/building-frontend/SKILL.md
git commit -m "feat: building-frontend technique skill"
```

---

### Task 2: i18n dictionary structure + runtime (Vite+React)

**Files:**
- Create: `skills/building-frontend/assets/i18n/locales/en.yaml`
- Create: `skills/building-frontend/assets/i18n/locales/de.yaml`
- Create: `skills/building-frontend/assets/i18n/i18n.ts`
- Create: `skills/building-frontend/assets/i18n/README.md`

**Interfaces:**
- Produces: `createI18n(locales: Record<string, Dict>, initial: string)` returning `{ t(key), locale, setLocale(l) }`; a React context/hook `useI18n()`; cookie read/write for `locale`. Consumed by Task 3 (switcher) and Task 8 (the app).

- [ ] **Step 1: Write the dictionary examples**

```yaml
# en.yaml — flat or nested keys; nested shown
app:
  title: "Fieldnote"
  tagline: "Record observations offline. Sync when you can."
nav:
  observations: "Observations"
  report: "Season report"
actions:
  add: "Add observation"
  switch_language: "Language"
```

```yaml
# de.yaml — same keys, translated
app:
  title: "Fieldnote"
  tagline: "Beobachtungen offline erfassen. Synchronisieren, wenn möglich."
nav:
  observations: "Beobachtungen"
  report: "Saisonbericht"
actions:
  add: "Beobachtung hinzufügen"
  switch_language: "Sprache"
```

- [ ] **Step 2: Write the runtime**

```typescript
// i18n.ts — minimal runtime i18n for Vite+React. YAML is imported as objects
// (via vite-plugin-yaml or a loader); here we type the shape.
import { createContext, useContext, useState, useCallback, ReactNode, createElement } from "react";

export type Dict = Record<string, unknown>;
const COOKIE = "locale";

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
  return m ? decodeURIComponent(m[1]) : null;
}
function writeCookie(name: string, value: string) {
  // 1 year, root path, Lax
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=31536000; SameSite=Lax`;
}

function lookup(dict: Dict, key: string): string {
  return key.split(".").reduce<unknown>((o, k) => (o && typeof o === "object" ? (o as Dict)[k] : undefined), dict) as string ?? key;
}

interface I18n { t: (key: string) => string; locale: string; setLocale: (l: string) => void; locales: string[]; }
const I18nContext = createContext<I18n | null>(null);

export function I18nProvider(props: { locales: Record<string, Dict>; initial?: string; children: ReactNode }) {
  const available = Object.keys(props.locales);
  const start = readCookie(COOKIE) ?? props.initial ?? available[0];
  const [locale, setLocaleState] = useState(available.includes(start) ? start : available[0]);
  const setLocale = useCallback((l: string) => {
    if (!available.includes(l)) return;
    writeCookie(COOKIE, l);
    setLocaleState(l);
  }, [available]);
  const t = useCallback((key: string) => lookup(props.locales[locale], key), [props.locales, locale]);
  return createElement(I18nContext.Provider, { value: { t, locale, setLocale, locales: available } }, props.children);
}

export function useI18n(): I18n {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within <I18nProvider>");
  return ctx;
}

export function initialLocaleFromCookie(fallback: string): string {
  return readCookie(COOKIE) ?? fallback;
}
```

- [ ] **Step 3: Write the README (structure + Astro/Next mapping)**

```markdown
# i18n assets

**Dictionaries:** `frontend/src/locales/{locale}.yaml` — one file per locale, same
key tree. Translators edit YAML, not code. No user-facing string lives outside these.

**Runtime (Vite+React):** `i18n.ts` — `<I18nProvider locales={...} initial="en">`,
`useI18n()` gives `t(key)`, `locale`, `setLocale(l)`. Switching is in-place and reactive;
`setLocale` writes a year-long `locale` cookie so the choice survives reload with no flash.

**Loading YAML in Vite:** add `@modyfi/vite-plugin-yaml` (or equivalent) and
`import en from "./locales/en.yaml"`.

## Mapping to the other frameworks
- **Astro (content-shaped, routed locales):** use Astro's built-in i18n routing
  (`/en/`, `/de/`), read the `locale` cookie in middleware to redirect on first
  visit, and switch via client-side navigation. The YAML dictionaries are identical.
- **Next.js (app-shaped):** app-router i18n segment (`app/[locale]/`) or a client
  provider like this one; same YAML dictionaries, same cookie.
```

- [ ] **Step 4: Type-check the runtime**

The asset must compile. In a scratch Vite+React+TS project (or with a standalone `tsc`), confirm `i18n.ts` type-checks with no errors.

Run: `cd /tmp && mkdir -p i18n-check && cp skills/building-frontend/assets/i18n/i18n.ts /tmp/i18n-check/ && cd /tmp/i18n-check && npm i -D typescript @types/react react >/dev/null 2>&1 && npx tsc --jsx react-jsx --noEmit --strict i18n.ts 2>&1 | tail -5`
Expected: no type errors. (If `tsc` reports only "cannot find module 'react'" despite install, note it — the type-check environment, not the code, is at fault; fix the env.)

- [ ] **Step 5: Commit**

```bash
git add skills/building-frontend/assets/i18n/
git commit -m "feat: i18n dictionary structure + Vite/React runtime with cookie persistence"
```

---

### Task 3: The language switcher component

**Files:**
- Create: `skills/building-frontend/assets/i18n/LanguageSwitcher.tsx`

**Interfaces:**
- Consumes: `useI18n()` from Task 2.
- Produces: `<LanguageSwitcher />` — a control that lists `locales`, shows the active one, and calls `setLocale` on change. Consumed by Task 8's app and asserted by Task 5's Playwright test (needs a stable `data-testid`).

- [ ] **Step 1: Write the component**

```tsx
// LanguageSwitcher.tsx — minimal, accessible, testable.
import { useI18n } from "./i18n";

const LABELS: Record<string, string> = { en: "English", de: "Deutsch", ar: "العربية", he: "עברית" };

export function LanguageSwitcher() {
  const { locale, setLocale, locales, t } = useI18n();
  return (
    <label data-testid="language-switcher" style={{ display: "inline-flex", gap: ".5rem", alignItems: "center" }}>
      <span>{t("actions.switch_language")}</span>
      <select
        data-testid="language-select"
        value={locale}
        onChange={(e) => setLocale(e.target.value)}
        aria-label={t("actions.switch_language")}
      >
        {locales.map((l) => (
          <option key={l} value={l}>{LABELS[l] ?? l}</option>
        ))}
      </select>
    </label>
  );
}
```

- [ ] **Step 2: Type-check it with the runtime**

Run: copy `i18n.ts` + `LanguageSwitcher.tsx` into the scratch project from Task 2 and `npx tsc --jsx react-jsx --noEmit --strict *.ts *.tsx 2>&1 | tail -5`
Expected: no type errors.

- [ ] **Step 3: Commit**

```bash
git add skills/building-frontend/assets/i18n/LanguageSwitcher.tsx
git commit -m "feat: accessible language switcher with test ids"
```

---

### Task 4: Playwright harness — config + mandatory language-switch test

**Files:**
- Create: `skills/building-frontend/assets/playwright/playwright.config.ts`
- Create: `skills/building-frontend/assets/playwright/language-switch.spec.ts`
- Create: `skills/building-frontend/assets/playwright/journey.spec.ts.tmpl`

**Interfaces:**
- Consumes: the switcher's `data-testid`s (Task 3), a running dev server.
- Produces: the e2e suite copied to `/e2e` at scaffold-into-repo time. The language-switch spec is the mandatory case that Task 8 runs green.

- [ ] **Step 1: Write the config**

```typescript
// playwright.config.ts — lives at repo /e2e; drives the frontend dev server.
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  timeout: 30_000,
  use: { baseURL: process.env.BASE_URL ?? "http://localhost:5173", trace: "on-first-retry" },
  webServer: process.env.BASE_URL
    ? undefined
    : { command: "npm --prefix ../frontend run dev", url: "http://localhost:5173", reuseExistingServer: true, timeout: 60_000 },
});
```

- [ ] **Step 2: Write the mandatory language-switch spec**

```typescript
// language-switch.spec.ts — the mandatory e2e case. Runtime switch + cookie persistence.
import { test, expect } from "@playwright/test";

test("switches language at runtime without reload and persists via cookie", async ({ page }) => {
  await page.goto("/");
  // English is the default first paint.
  await expect(page.getByTestId("app-tagline")).toContainText("Record observations offline");

  // Switch to German — in place, no navigation.
  await page.getByTestId("language-select").selectOption("de");
  await expect(page.getByTestId("app-tagline")).toContainText("Beobachtungen offline erfassen");

  // The cookie was written.
  const cookies = await page.context().cookies();
  expect(cookies.find((c) => c.name === "locale")?.value).toBe("de");

  // Reload — the choice survives, and there is no flash back to English.
  await page.reload();
  await expect(page.getByTestId("app-tagline")).toContainText("Beobachtungen offline erfassen");
});
```

- [ ] **Step 3: Write the journey template**

```typescript
// journey.spec.ts.tmpl — the primary-user-journey case. {{JOURNEY}} filled per project
// from docs/purpose.md's Primary user journey. Example fill shown in a comment.
import { test, expect } from "@playwright/test";

// Primary user journey (from docs/purpose.md): {{JOURNEY}}
// e.g. "record an observation offline → it appears in the list → survives reload"
test("primary user journey: {{JOURNEY_SHORT}}", async ({ page }) => {
  await page.goto("/");
  // TODO(per-project): drive the actual journey. This template MUST be filled,
  // not shipped as-is — an unfilled journey test is an incomplete frontend.
  // The building-frontend skill fills it from the purpose doc.
  expect(true).toBe(true);
});
```

- [ ] **Step 4: Sanity-check config parses**

Run: `cd /tmp && mkdir -p pw-check && cp skills/building-frontend/assets/playwright/*.ts /tmp/pw-check/ && cd /tmp/pw-check && npm i -D @playwright/test typescript >/dev/null 2>&1 && npx tsc --noEmit --skipLibCheck playwright.config.ts language-switch.spec.ts 2>&1 | tail -5`
Expected: no type errors (the `.tmpl` is intentionally not type-checked — it has placeholders).

- [ ] **Step 5: Commit**

```bash
git add skills/building-frontend/assets/playwright/
git commit -m "feat: Playwright harness with mandatory language-switch e2e case"
```

---

### Task 5: RTL guidance asset

**Files:**
- Create: `skills/building-frontend/assets/rtl/rtl-notes.md`

**Interfaces:**
- Produces: the RTL convention referenced by `building-frontend` Step 2. Reference material, no code.

- [ ] **Step 1: Write the RTL notes**

```markdown
# RTL support

RTL is asked **separately** from the locale list — it changes layout, not just
strings, so Arabic/Hebrew in scope is a bigger commitment than French/German.

If RTL is in scope:

- Set `dir="rtl"` on `<html>` for RTL locales (drive it from the active locale).
- Use **CSS logical properties** everywhere: `margin-inline-start` not `margin-left`,
  `padding-inline-end` not `padding-right`, `inset-inline-start` not `left`,
  `text-align: start` not `left`. These flip automatically with `dir`.
- Mind directional icons (arrows, chevrons, back/next) — mirror them for RTL.
- Keep numerals and code LTR inside RTL text where appropriate (`unicode-bidi`).
- Add an RTL locale to the Playwright language-switch matrix so layout direction
  is actually exercised, not assumed.

If RTL is NOT in scope: still prefer logical properties — they cost nothing now and
save a full layout pass later (invariant-2 scope clause: cheap conventions adopted
by default).
```

- [ ] **Step 2: Commit**

```bash
git add skills/building-frontend/assets/rtl/
git commit -m "feat: RTL guidance — logical properties, asked separately"
```

---

### Task 6: Coolify deploy documentation

**Files:**
- Create: `skills/building-frontend/assets/coolify-deploy.md`

**Interfaces:**
- Produces: the documented Coolify preview-deploy step referenced by `building-frontend` Step 5. Not executed in this plan.

- [ ] **Step 1: Write the Coolify deploy doc**

```markdown
# Preview deploy — Coolify

Coolify hosts the frontend mock at a shareable URL so stakeholders can click it
before backends exist. You run your own Coolify instance; this documents the deploy.

## One-time
1. In Coolify, create a project and add a **Static Site** (or **Nixpacks**) resource
   pointing at this repo, build path `frontend/`.
2. Build command `npm run build`, output dir `dist/` (Vite) or `.output/`/`out/`
   (Next/Astro adapter).
3. Set a domain; Coolify provisions TLS.

## Each preview
- Push the branch; Coolify auto-deploys (if you enabled it) or click **Deploy**.
- Share the URL. This is a MOCK — it need not have live backends; stub data is fine.

## Not in scope here
This plan does not push to a Coolify instance (no assumed instance/credentials).
Dev-time verification uses Playwright locally. When you have Coolify, this is the deploy path.
```

- [ ] **Step 2: Commit**

```bash
git add skills/building-frontend/assets/coolify-deploy.md
git commit -m "docs: Coolify preview-deploy step for building-frontend"
```

---

### Task 7: Framework-selection application check (the input-space test)

**Files:**
- Create: `tests/scenarios/frontend-framework-selection.md`

**Interfaces:**
- Consumes: `building-frontend` SKILL.md.
- Produces: evidence that framework selection is correct for all three app shapes — not just the offline one Task 8 builds. This exists because Plan 2 shipped a bug (MariaDB) precisely from testing only one input.

- [ ] **Step 1: Write three shape scenarios**

```markdown
# Framework selection — three shapes

Dispatch a fresh subagent with `building-frontend` available for each. Give it the
purpose/architecture snippet; ask which framework it picks and why. Grade the choice.

## A — content-shaped (expect Astro)
"A public marketing + docs site for an open-source library. SEO matters. Mostly
static pages, a blog, occasional interactive demo." → EXPECT **Astro**.

## B — app-shaped (expect Next.js)
"An internal, auth-gated analytics dashboard. Heavy client state, server-rendered
for the first paint, no offline need." → EXPECT **Next.js**.

## C — offline-first (expect Vite+React PWA)
"A field data-collection app that must work with no signal and sync later." →
EXPECT **Vite + React PWA**.
```

- [ ] **Step 2: Run the three, record results**

Dispatch three fresh subagents (one per shape), each told to read `building-frontend` and pick a framework from the app description. Record each choice + reasoning verbatim in the scenario file.

Expected: A→Astro, B→Next, C→Vite+React. A miss means the skill's shape→framework table is ambiguous — fix the skill and re-run.

- [ ] **Step 3: Commit**

```bash
git add tests/scenarios/frontend-framework-selection.md
git commit -m "test: framework selection correct across all three app shapes"
```

---

### Task 8: Walking-skeleton validation — a real localized Fieldnote frontend

**Files:**
- Create: `tests/scenarios/e2e-frontend.md`
- Create: `tests/scenarios/baseline-results/e2e-frontend-results.md`

**Interfaces:**
- Consumes: everything.
- Produces: the Plan 3 verdict. Build a minimal but real localized Fieldnote frontend in a scratch dir using the assets, run it, and pass the mandatory Playwright language-switch test. Node/npm and Playwright are available in this environment.

- [ ] **Step 1: Scaffold a Vite+React+TS app in a scratch dir**

Fieldnote is offline-first → Vite+React PWA. In `/tmp/fieldnote-fe`:

Run: `npm create vite@latest fieldnote-fe -- --template react-ts` (in /tmp), then `npm i` and add `@modyfi/vite-plugin-yaml`.

- [ ] **Step 2: Install the i18n assets and build a minimal localized UI**

- Copy `assets/i18n/i18n.ts`, `LanguageSwitcher.tsx`, and `locales/{en,de}.yaml` into `src/`.
- Wire `vite-plugin-yaml` in `vite.config.ts`.
- Build a minimal `App.tsx`: wrap in `<I18nProvider>`, render the tagline with `data-testid="app-tagline"` using `t("app.tagline")`, and mount `<LanguageSwitcher />`. Use `frontend-design` for the styling so it isn't generic.
- Confirm `npm run build` succeeds and `npm run dev` serves.

- [ ] **Step 3: Dev-time Playwright verification (drive it, screenshot it)**

Actually drive the running app with Playwright (the MCP browser tools or `@playwright/test`): load `/`, screenshot, confirm the tagline renders in English, switch to German, confirm it re-renders in place. This is the honest-verification step — observe the UI, don't assume it.

- [ ] **Step 4: Run the mandatory language-switch e2e**

- Copy `assets/playwright/playwright.config.ts` + `language-switch.spec.ts` into `/tmp/fieldnote-fe/e2e/`.
- Run: `npx playwright test` (installing browsers if needed: `npx playwright install chromium`).
- Expected: the language-switch test PASSES — English default, switch to German re-renders in place, cookie `locale=de` set, reload preserves German with no flash.

- [ ] **Step 5: Grade and record**

Write `tests/scenarios/baseline-results/e2e-frontend-results.md`:

| Check | Expected | Result |
|---|---|---|
| Framework | Vite+React PWA (offline-first) | |
| i18n dicts | en.yaml + de.yaml load | |
| Runtime switch | tagline changes EN→DE with no reload | |
| Cookie persist | `locale=de` cookie; survives reload, no flash | |
| Playwright language-switch | test passes | |
| Dev-time verification | UI observed rendering (screenshot) | |
| No hard-coded strings | user-facing text comes from dicts | |

Record honestly. If the Playwright test fails, report the real failure; do not weaken the test to pass.

- [ ] **Step 6: Commit and report the verdict**

```bash
git add tests/scenarios/
git commit -m "test: end-to-end localized Fieldnote frontend with passing language-switch e2e"
```

Present to Greg: the built frontend, the screenshot evidence, the passing language-switch test. **Plan 3 is done when a real localized frontend builds, renders (observed), switches language at runtime with cookie persistence, and the mandatory Playwright test passes.** That verdict is Greg's.

---

## Self-Review

**Spec coverage** — every Plan-3 spec item traces to a task:

| Spec item | Task |
|---|---|
| Framework by shape (Astro/Next/Vite-React) | 1, 7 |
| UI quality via frontend-design | 1, 8 |
| Localization always asked | 1 |
| YAML dictionaries, one per locale | 2 |
| Runtime switching mandatory | 2, 3, 8 |
| Strategy by SEO (routed vs store) | 1, 2 (README maps both) |
| Cookie persistence, no flash | 2, 8 |
| i18n boundary (backends return codes) | 1 |
| RTL asked separately, logical properties | 5 |
| Playwright at /e2e | 4 |
| Mandatory language-switch e2e | 4, 8 |
| Mandatory primary-user-journey e2e | 4 (template), 8 |
| Coolify documented deploy | 6 |
| Dev-time Playwright verification | 1, 8 |

Deferred by design: backend service code (Plan 4), CI running the e2e suite (Plan 5), Dockerfile for the frontend (Plan 4 — lives with the component; the compose stub already references it).

**Placeholder scan:** `journey.spec.ts.tmpl` intentionally carries `{{JOURNEY}}` placeholders — it is a template the skill fills per project, and it says so. No other placeholders.

**Type consistency:** `useI18n()` returns `{ t, locale, setLocale, locales }` in Task 2 and is consumed with exactly those names in Tasks 3 and 8. `data-testid="language-select"` / `"app-tagline"` are defined in Tasks 3/8 and asserted in Task 4's spec — consistent. Cookie name `locale` is identical across i18n.ts, the Playwright spec, and the spec's persistence rule.

**Input-space coverage:** Task 7 checks framework selection for all three shapes even though Task 8 builds only the offline one — the explicit guard against Plan 2's single-example blind spot.

**Honest-verification:** Task 8 Steps 3–4 require actually driving the app with Playwright and observing render, not asserting it.
