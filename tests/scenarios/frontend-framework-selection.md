# Framework selection — three shapes

Validates that `building-frontend`'s shape→framework table is unambiguous across
**all three** app shapes, not just the offline-first one the walking-skeleton
(Task 8) actually builds. This exists because Plan 2 shipped a bug (MariaDB
silent-drop) precisely from validating only one input path — see
`[[test-the-input-space-not-the-happy-path]]`.

## Method

Three fresh subagents, each given only `skills/building-frontend/SKILL.md` and one
app description, asked which framework the skill directs and whether the table was
unambiguous. Run 2026-07-19.

## Scenarios and results

| Shape | App description | Expected | Chose | Ambiguity? |
|---|---|---|---|---|
| Content-shaped | Public marketing + docs site for an OSS library; SEO-critical; mostly static + blog + occasional embedded demo | **Astro** | **Astro** ✅ | None — direct table match |
| App-shaped | Internal auth-gated analytics dashboard; heavy client state; SSR for fast first paint; no offline need | **Next.js** | **Next.js** ✅ | None — hit all three markers, ruled out offline |
| Offline-first | Field data-collection app; must work with no signal; syncs later; installed on phones | **Vite + React PWA** | **Vite + React PWA** ✅ | None — direct table match |

## Verdict

**3/3 correct, all unambiguous.** The framework menu (added to the spec 2026-07-19
after the Fieldnote run exposed the offline-first gap) routes each shape to the
right framework with no guessing. The input-space is covered — the skill is not
merely correct for the one shape the end-to-end validation exercises.

Verbatim reasoning from each run is preserved in the controller transcript; each
subagent cited the specific shape-table row it matched.
