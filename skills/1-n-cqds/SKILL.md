---
name: 1-n-cqds
description: Use when starting any software project, before any tech-stack, database, cache, queue, or storage decision, or when adding a backend service or judging component fit in a 1-N-CQDS repo
---

# 1-N-CQDS

**1** frontend, **N** backends, **C**ache, **Q**ueue, **D**atabase, **S**torage.

## Invariants

1. **Stateless-first** — a backend service must be killable at any instant with
   no loss. No local sessions, no in-process shared state, no sticky routing,
   no local writes outside `/tmp` scratch.
2. **Complexity minimalism** — every component added is operational burden
   forever. Absence is the default; presence needs a reason on record.
   **Scope: operational components only** — things you run, monitor, back up.
   Not code conventions. A YAML dictionary adds no operational surface.
3. **One backend language** — chosen once, all N services use it. Frontend
   TypeScript is a different tier, not a violation.
4. **Evidence before components** — a named pattern or a measurement, or the
   component does not enter.

## Routing

| Repo state | Mode | Go to |
|---|---|---|
| No `ARCHITECTURE.md` | init | **REQUIRED SUB-SKILL:** Use defining-purpose |
| `ARCHITECTURE.md` exists | evolve | read it, then dispatch to the phase skill for the request |
