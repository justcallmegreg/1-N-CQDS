# i18n assets

**Dictionaries:** `frontend/src/locales/{locale}.yaml` — one file per locale, same
key tree. Translators edit YAML, not code. No user-facing string lives outside these.

**Runtime (Vite+React):** `i18n.ts` — `<I18nProvider locales={...} initial="en">`,
`useI18n()` gives `t(key)`, `locale`, `setLocale(l)`. Switching is in-place and reactive;
`setLocale` writes a year-long `locale` cookie so the choice survives reload with no flash.

**Loading YAML in Vite:** add `@modyfi/vite-plugin-yaml` (or equivalent) and
`import en from "./locales/en.yaml"`. Also copy `yaml.d.ts` into `src/` —
TypeScript has no ambient declaration for `*.yaml` otherwise, and the import
above fails `tsc` with `TS2307: cannot find module`.

## Loading strategy

The active locale ships eagerly; additional locales lazy-load on switch. Shipping
every locale to the client is acceptable at two or three and a bundle-size problem
at twenty. Concretely: import the initial locale's YAML statically (it's in the
first bundle regardless), and load the rest with `import()` inside `setLocale` (or
a wrapper around it) so an unused locale's dictionary never ships to a visitor who
never asks for it.

## Mapping to the other frameworks
- **Astro (content-shaped, routed locales):** use Astro's built-in i18n routing
  (`/en/`, `/de/`), read the `locale` cookie in middleware to redirect on first
  visit, and switch via client-side navigation. The YAML dictionaries are identical.
- **Next.js (app-shaped):** app-router i18n segment (`app/[locale]/`) or a client
  provider like this one; same YAML dictionaries, same cookie.
