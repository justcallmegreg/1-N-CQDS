# 1-N-CQDS — Design Spec

**Date:** 2026-07-17
**Status:** Approved for planning

## Purpose

1-N-CQDS is a Claude skill encoding a specific software architecture methodology: **1 frontend, N backend services, Cache, Queue, Database, Storage**. It exists to make scalable software buildable in a directed way — turning architectural judgment that normally lives in one person's head into a repeatable, auditable pipeline.

The methodology's governing bias: **operational complexity is the enemy, and statefulness is its primary source.** Every component the skill declines to add is a win it must be able to defend later.

## Scope

Two modes, one pipeline.

- **Init (0→1)** — vision through scaffolded repository. Runs the pipeline from the first phase.
- **Evolve (governor)** — re-enters the pipeline at a later phase for ongoing work: adding a backend service, cutting a release, reviewing a change against the doctrine. Reads the committed decision record rather than replaying vision.

Retrofitting non-1-N-CQDS repos is **out of scope**.

## Packaging

A plugin with a router skill and seven phase skills. Chosen over a single skill with `references/` because governor mode needs real re-entry points — "add a backend service" must be directly invocable without replaying the vision phase.

```
1-n-cqds/
├── .claude-plugin/plugin.json
└── skills/
    ├── 1-n-cqds/                    # router + invariant doctrine
    ├── defining-purpose/            # → superpowers:brainstorming
    ├── deciding-architecture/       # the CQDS decision engine
    │   └── references/{storage-ladder,database-choice,cache-queue-gate,language-choice}.md
    ├── scaffolding-repository/
    │   ├── assets/{Makefile, docker-compose.yml, README.tmpl.md, CODEOWNERS, VERSION.txt, licenses/}
    │   └── scripts/scaffold.py
    ├── building-frontend/           # Astro + frontend-design + Coolify preview
    ├── adding-backend-service/      # the "N" — also the evolve entry point
    │   └── assets/{python/, go/, mongo-repository.md}   # per-language skeletons (Dockerfile lives inside each)
    ├── wiring-delivery/             # CI platform, registry, Trivy, hooks
    │   └── assets/{github/workflows/, gitlab/, hooks/}
    └── managing-releases/           # VERSION.txt, GitFlow, backport
        └── assets/{release.yml, backport.yml}
```

**Routing.** The entry skill inspects the working directory. No `ARCHITECTURE.md` → init, run from `defining-purpose`. `ARCHITECTURE.md` present → evolve: parse the decision record, dispatch to the phase skill matching the request.

**The router owns the invariants.** Phase skills own their own decision logic and templates. Doctrine lives in one place; phases stay independently invocable.

`defining-purpose` remains its own skill rather than folding into the router: it is the hard first gate, and it must be re-invocable when a project's vision genuinely changes — which should force re-examination of every downstream ADR.

## Artifact strategy

**Templates on disk + copy/fill**, not per-project LLM generation. Real files under `assets/`, variable-substituted by `scripts/scaffold.py`. Deterministic, reviewable, version-controlled. A bug fixed once in the Trivy workflow is fixed for every future project.

Claude authors only the genuinely project-specific: ADR prose, C4 diagram content, service logic.

## The four invariants

Router-owned. Every phase skill obeys them.

1. **Stateless-first** — a backend service must be killable at any instant with no loss. No local sessions, no in-process shared state, no sticky routing, no local writes outside `/tmp` scratch.
2. **Complexity minimalism** — every component added is operational burden forever. Absence is the default; presence needs a reason on record.

   **Scope of this invariant: operational components only** — things you run, monitor, and back up. It does *not* govern code conventions. A YAML dictionary, a repository interface, or a logging convention adds no operational surface, so the reasoning that rejects premature Redis does not transfer to them. Conventions that are cheap now and expensive to retrofit should be adopted by default, not gated.
3. **One backend language** — chosen once, all N services use it. (Frontend TypeScript is not a violation; it is a different tier.)
4. **Evidence before components** — no component enters on a hunch. A named pattern or a measurement, or it does not enter.

## The doctrine engine

`deciding-architecture` runs this sequence. Every step emits an ADR — including every rejection.

### 1. State inventory

Enumerate every piece of state the software holds. This is the root question; everything below is a consequence. A service with no state in the inventory needs no persistence decision at all.

### 2. Storage ladder

Applied per state item:

| State shape | Destination |
|---|---|
| Structured, queryable | **Database** |
| Opaque blob (uploads, generated artifacts) | **S3-capable API** — MinIO in compose locally, S3/R2/Spaces in prod |
| Neither, and a hard constraint forbids the above | **Filesystem — last resort** |

Filesystem **breaks invariant 1**. Choosing it requires an ADR that explicitly names it as debt and states the constraint forcing it.

### 3. SQL vs Document — the irreversible decision

**This is the one genuinely irreversible choice in the stack, and it gets the most scrutiny.** The "swap engines easily" goal holds only *within* a family: Postgres↔MariaDB is a configuration change; SQL↔Mongo is a rewrite that no library prevents. Its ADR is the most important document in the repository.

- **SQL** → Postgres by default; MariaDB when horizontal scale is explicitly named.
- **Document** → MongoDB, and only when the data is genuinely schema-variant or document-shaped. Not because "it's flexible."

### 4. Language — constraint gates, not personas

Language choice is an organizational decision, not a technical one. It is decided by **named constraints**, evaluated in order:

1. **Team constraint** — who maintains this in three years? *An existing team's language beats every preference below.* This gate fires first and hardest.
2. **Platform constraint** — a standing mandate or ecosystem investment (Microsoft shop → C#; JVM shop → Java/Kotlin). The question is "are you already committed," not "are you large."
3. **Workload constraint** — a *named* requirement demanding a systems language: hard latency floor, memory ceiling, embedded target.

**Unconstrained → Python, then Go.** Any override is recorded in an ADR.

Rejected: mapping hiring-strategy personas to languages (`enterprise → Java/C#`, `startup → Python/Go/Rust`, `scientific → C/C++`). The insight underneath it — that hiring is a real constraint — is retained and promoted to gate #1. The mechanism was rejected because it is a category-to-answer lookup with no gate, the same class of vibe-based rule the cache/queue gate exists to eliminate; because its three categories are three non-orthogonal axes collapsed into a false single-select (Red Hat is enterprise *and* open source); and because `enterprise → Java/C#` conflates "large company" with "large company founded in 2005."

### 5. Language support tiers

| Tier | Languages | What the skill provides |
|---|---|---|
| **1** | Python, Go | Full assets: skeleton, Dockerfile, hooks, CI |
| **2** | Java, C#, Rust | Doctrine and ADRs apply; **no scaffolding** — the skill says so plainly rather than faking it |
| **Out of scope** | C/C++ | 1-N-CQDS is a web service architecture. If the workload truly demands C/C++, this is the wrong methodology — say so and stop. |

### 6. Portability layer

- Python/SQL → SQLAlchemy + Alembic
- Go/SQL → GORM
- **MongoDB** → no ODM buys cross-family portability, so the portability layer is a hand-written **repository pattern**. Services talk to repositories, never to the driver.

**Tier-1 service-skeleton defaults** (added 2026-07-19; the web framework is a per-project choice the engine records in an ADR — these are the skeleton's starting points, not mandates):

- **Python** → **FastAPI** (ASGI) + SQLAlchemy + Alembic. The service exposes a health endpoint and talks to a **repository layer** over SQLAlchemy, never to sessions directly — so the SQL engine (Postgres↔MariaDB) and even the family (→ a Mongo repository) can change behind the same interface.
- **Go** → stdlib **net/http** + **chi** (a thin router, no heavy framework) + GORM, same repository discipline.

Even with an ORM, services call **repositories**, not the ORM session/driver — the repository is the seam that makes the storage decision reversible. This is the code-level realization of the "one genuinely irreversible decision" scrutiny on SQL-vs-Document: within a family the swap is a repository-implementation change, not a rewrite.

### 7. Service decomposition

The N, derived from the purpose — not from taxonomy.

### 8. Cache gate

Redis only if a read path is **high-frequency AND staleness-tolerant AND expensive to compute**. All three. Two of three is a no.

Postgres already caches; premature Redis duplicates it badly.

### 9. Queue gate

Only if a named pattern exists:

- work that must outlive a request — too large or slow to finish in-request (bulk file processing; a report too big to render within a request timeout)
- fanout to N consumers (webhooks, notifications)
- buffering a rate-limited external dependency
- deferred or retried work with retry semantics

Otherwise: no.

### Each component faces its own gate

The cache gate and the queue gate are independent, and each is binary. Adding Redis alone while declining the queue is not a moderate or reasonable middle position — Redis still needs all three of its own conditions on its own evidence, regardless of whether a queue is being asked for in the same breath. Splitting the difference between "add both" and "add neither" satisfies neither gate; it relocates the hunch from one component to the other rather than removing it.

### Authority is not evidence

A senior person asserting a component does not, by itself, name a pattern or supply a measurement — invariant 4 draws no exception for who is asking. The correct response to such a mandate is **not refusal**. It is to write the ADR, name the gate the component must clear, and ask what pattern the requester is seeing. If they name one that holds — a real hot read path, a real async workload — it passes the gate honestly and the ADR records it as accepted. If they can't name one, there isn't one, and the ADR records that instead.

This is doctrine, not armor: it was added to the spec by decision, promoted from a Task 6 ruling rather than derived from an observed baseline failure. The Task 6 cache/queue baseline came back green (6/6 refused the unjustified components under authority pressure) — capable agents already resist. This section exists to give the *words and the record*, not to instill a discipline the model lacks.

### Rejections are first-class

A failed gate still emits an ADR — *"Queue rejected: no async workload identified."* **That rejection is what governor mode enforces against later.** Without it, the skill cannot distinguish drift from legitimate reconsideration.

## Decision record

`docs/adr/NNNN-title.md`, Nygard-style:

- Context
- Decision
- **Rejected alternatives + why** ← load-bearing
- Consequences

`ARCHITECTURE.md` is the synthesis: C4 diagrams (mermaid), component table, links to ADRs. It is the file the router reads to detect evolve mode.

## Repository layout emitted

```
repo/
├── VERSION.txt                 # SSOT, MAJOR.MINOR.PATCH, uniform across all components
├── LICENSE
├── CODEOWNERS                  # or .gitlab/CODEOWNERS
├── README.md                   # structure + getting started + C4 (mermaid)
├── ARCHITECTURE.md
├── Makefile                    # help, up, down (docker default; CONTAINER_ENGINE=podman)
├── docker-compose.yml          # only components the gates approved
├── docs/adr/NNNN-*.md
├── e2e/                        # Playwright — drives the full compose stack
├── frontend/                   # Astro, Dockerfile
└── backends/{service}/         # Dockerfile, skeleton, tests
```

**Container images** — `docker buildx` multi-arch (`linux/amd64,linux/arm64`), one Dockerfile per component, non-root user, pinned base image digests.

## Frontend

- **Framework chosen by the app's shape** (revised 2026-07-19, ruling — the original Astro-default/Next-alternative menu didn't cover the offline-first case, which the deciding-architecture engine correctly picked React+Vite PWA for on Fieldnote; the menu now matches the engine):

  | App shape | Framework | Why |
  |---|---|---|
  | **Content-shaped** (marketing, docs, mostly-static, SEO-critical) | **Astro** | islands, ships minimal JS, best SEO — the default |
  | **App-shaped** (heavy client state, auth-gated dashboards, SSR wanted) | **Next.js** | SSR + app-router for stateful, server-rendered apps |
  | **Offline-first / pure-client** (PWA, works with no network, sync-on-reconnect) | **Vite + React PWA** | pure client bundle + service worker; SSR buys nothing when the app must run offline |

  Astro remains the default when the shape is ambiguous. The choice is recorded in an ADR, like every other component decision. No frameworks beyond these three.
- UI quality delegated to the `frontend-design` skill. The framework choice determines the shell; `frontend-design` determines whether the UI is any good.
- Mock is built **after** the tech stack is decided, on the chosen framework.
- **Coolify is the preview host** for the mock — a deployment target giving stakeholders a clickable URL before backends exist. Coolify is not a mock authoring tool.

`docs/purpose.md` includes a **Primary user journey** — the single most important end-to-end path a user takes (e.g. "record an observation offline → sync → generate the season PDF"). Plan 3 turns it into the mandatory Playwright e2e case.

### Playwright

**Playwright is the e2e framework, always.** It has two distinct jobs:

**1. The e2e suite** — lives at **`/e2e` in the repo root**, a peer of `frontend/` and `backends/`. A test that drives the UI through N backends to the database is testing the *system*, not the frontend. Placing it under `frontend/` would imply frontend ownership, and a suite nobody re-runs when a backend changes is a suite that tests nothing. It runs against the full compose stack.

**2. Dev-time verification** — `building-frontend` uses Playwright to load the UI it just built, screenshot it, and confirm it renders before claiming completion. This catches the "correct in the source, blank page in the browser" failure that no unit test sees. Distinct from the suite; same tool.

**Required e2e cases** (beyond project-specific flows):

- **The language switcher** — runtime locale switching is mandatory doctrine and is untestable by unit tests: it spans a click, a cookie write, a dictionary load, and a re-render. It is exactly what Playwright is for.
- **The primary user journey** named in `docs/purpose.md`.

**Cost to acknowledge:** Playwright needs browser binaries (~500MB). The pre-push hook installs them once and caches; CI uses the official Playwright image. This is a real cost and it is why e2e sits at pre-push rather than pre-commit.

### Localization

**`building-frontend` always asks whether localization is needed.** i18n is cheap to adopt at scaffold and expensive to retrofit — adding it later means touching every string in the codebase. Per invariant 2's scope clause, this is a code convention, not an operational component, so it is not gated on evidence.

**Strings live in YAML dictionaries**, one file per locale, hand-editable and translator-friendly: `frontend/src/locales/{locale}.yaml`.

**Runtime switching is mandatory.** The user can change language on the fly — no rebuild, no full page reload.

**Implementation falls out of an SEO constraint**, like every other decision in the doctrine:

| Frontend shape | Strategy |
|---|---|
| Public / indexed (content-shaped) | **Routed locales** (`/en/`, `/de/`) + client-side navigation — instant, shareable, indexable |
| Auth-gated dashboard (app-shaped) | **Client-side locale store** — true in-place swap, no navigation |

**Persistence: cookie.** SSR reads it, so first paint is already in the right language — no flash of the default locale. Chosen over `localStorage` (invisible to SSR, guarantees a flash) and URL-only (a bare visit to `/` always lands in the default language).

**Dictionary loading:** the active locale ships eagerly; additional locales lazy-load on switch. Shipping every locale to the client is acceptable at two or three and a bundle-size problem at twenty.

**RTL is asked separately from the locale list.** It is the expensive part — it changes layout, CSS logical properties, and icon direction, not just strings. Arabic or Hebrew in scope is a materially different commitment than French or German, and `frontend-design` needs to know before it designs anything.

#### The localization boundary

**Backends return stable codes. The frontend owns every human-readable string.**

This is *entailed* by the on-the-fly switching requirement, not an independent preference: if a backend returned a localized message and the user switched language, that string would be stale on screen — still in the old language, unable to re-render without re-issuing the request. Runtime switching only works if the frontend owns the strings.

Consequences: backends stay locale-free and stateless (reinforcing invariant 1), and the repository has exactly one set of dictionaries rather than one per service.

## Delivery

`wiring-delivery` branches once on **GitHub vs GitLab** and emits the matching set: build-and-push, test, Trivy.

**Registry auth is an interactive walkthrough** — authenticated vs unauthenticated. If authenticated, the skill walks the user through creating the token and setting the secret. It does not leave `TODO: set credentials` in a YAML file.

**Test gates:**

| Stage | Runs | Rationale |
|---|---|---|
| pre-commit | lint + unit + secret scan | seconds — survives daily use |
| pre-push | Playwright e2e against compose | tolerable at push frequency |
| CI | full suite + Trivy | **the authority** |

Hooks are a courtesy; the merge gate is real. E2e in pre-commit was rejected: booting compose + DB + N services per commit makes `--no-verify` muscle memory within a week, after which *no* hook runs.

## Release

- **VERSION.txt is the single source of truth.** MAJOR.MINOR.PATCH. All components share one version — no per-service versioning, to avoid confusion.
- **GitFlow**, PR/MR-only. No direct pushes to protected branches.
- **CODEOWNERS** (or the GitLab equivalent) always emitted.
- **Support window: always asked at init, no default.** It is a real commitment with real cost; the user says it out loud. The backport cherry-pick workflow is sized to the answer.

## Licensing

Open source preferred. Templates shipped:

| License | Character |
|---|---|
| MIT | Permissive, minimal |
| Apache-2.0 | Permissive + explicit patent grant — preferred for anything commercially adjacent |
| MPL-2.0 | File-level copyleft, middle ground |
| AGPL-3.0 | Network copyleft — the open-core defensive pick |
| BSL 1.1 | Source-available, time-delayed. **Not OSI-approved.** The commercial path. |

**BSL 1.1 and any commercial arrangement ship with a mandatory disclaimer directing the user to a legal advisor.** The skill does not give legal advice.

## Skill integrations

| Skill | Used for |
|---|---|
| `superpowers:brainstorming` | mandatory in `defining-purpose` — the vision gate |
| `frontend-design` | UI quality in `building-frontend` |
| `c4-architecture` | governor mode regenerates C4 from the real codebase once services exist |

On C4: `deciding-architecture` authors the initial Context and Container diagrams from the ADRs as part of its `ARCHITECTURE.md` synthesis step, because at scaffold time there is no code to analyze. `scaffolding-repository` then *places* that `ARCHITECTURE.md` into the repo and links it from the README — it does not re-author the diagrams (single producer; ruling 2026-07-18). Once services exist, C4 regeneration delegates to the existing `c4-architecture` plugin rather than duplicating its logic.

## Decisions made in this session

| Decision | Chosen | Rejected |
|---|---|---|
| Lifecycle | Scaffolder + ongoing governor | Greenfield-only; retrofit of foreign repos |
| Coolify's role | Preview host for the frontend mock | Mock authoring tool; standing deploy target for the whole stack |
| Mock timing | After the stack is decided | Mock-first as a stack-discovery tool |
| Decision state | `ARCHITECTURE.md` + ADRs | Inference from repo; `.cqds.yaml`; both |
| Artifacts | Templates + copy/fill script | Per-project LLM generation; hybrid |
| Packaging | Plugin: router + 7 phase skills | Single skill + references; init/evolve split |
| Cache/Queue trigger | Named pattern or measurement, in an ADR | Numeric thresholds; evolve-mode-only |
| Test gates | Fast pre-commit / e2e pre-push / CI authoritative | e2e in pre-commit; e2e CI-only |
| Language | Constraint gates + Python/Go default | Hiring-strategy personas |
| Template tiers | T1 Python+Go, T2 doctrine-only | Python-only; all five fully templated |
| Frontend alts | Astro default, Next.js alternative | SvelteKit; Vite SPA; Astro-only |
| Support window | Always ask | Default N-1; default N-2 |
| Localization | Always asked; YAML dictionaries; runtime switching mandatory | Gating i18n on evidence; JSON dictionaries |
| i18n strategy | Routed if indexed, client store if not | Always routed; always client store |
| Locale persistence | Cookie | localStorage; URL-only |
| i18n boundary | Backends return codes, frontend owns strings | Backend `Accept-Language` localization |
| e2e framework | Playwright, always | Cypress; Selenium |
| e2e location | `/e2e` at repo root | `frontend/e2e/`; split UI-only vs full-stack |
| Playwright's second job | Dev-time UI verification in `building-frontend` | Test-suite use only |

## Out of scope

- Retrofitting or auditing repos not born 1-N-CQDS
- C/C++ backends
- Full scaffolding for Java, C#, Rust
- Per-service independent versioning
- Backend-side localization (backends return codes; see The localization boundary)
- Legal advice on commercial licensing
