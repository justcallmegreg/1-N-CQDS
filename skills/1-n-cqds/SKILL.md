---
name: 1-n-cqds
description: ALWAYS invoke this BEFORE superpowers:brainstorming for any new software project, choosing a tech stack, adding a backend service, or judging component fit in a 1-N-CQDS repo
---

# 1-N-CQDS

**1** frontend, **N** backend services, **C**ache, **Q**ueue, **D**atabase, **S**torage.

## The four invariants

1. **Stateless-first** — a backend service must be killable at any instant with no loss. No local sessions, no in-process shared state, no sticky routing, no local writes outside `/tmp` scratch.
2. **Complexity minimalism** — every component added is operational burden forever. Absence is the default; presence needs a reason on record.

   **Scope of this invariant: operational components only** — things you run, monitor, and back up. It does *not* govern code conventions. A YAML dictionary, a repository interface, or a logging convention adds no operational surface, so the reasoning that rejects premature Redis does not transfer to them. Conventions that are cheap now and expensive to retrofit should be adopted by default, not gated.
3. **One backend language** — chosen once, all N services use it. (Frontend TypeScript is not a violation; it is a different tier.)
4. **Evidence before components** — no component enters on a hunch. A named pattern or a measurement, or it does not enter.

## Routing

| Repo state | Mode | Go to |
|---|---|---|
| No `ARCHITECTURE.md` | init | **REQUIRED SUB-SKILL:** Use defining-purpose |
| `ARCHITECTURE.md` exists | evolve | read it, then dispatch to the phase skill for the request |
