---
name: scaffolding-repository
description: Use when a project's ARCHITECTURE.md and ADRs are complete and it needs its repository structure created — directory layout, Makefile, docker-compose, README, license, and version file
---

# Scaffolding a Repository

Turns a completed architecture into a real repo skeleton. The decisions are
already made and recorded in `ARCHITECTURE.md`; this step lays out the files.

**REQUIRED BACKGROUND:** Use 1-n-cqds for the four invariants.
**Prerequisite:** `ARCHITECTURE.md` must exist. If it doesn't — **REQUIRED
SUB-SKILL:** Use deciding-architecture first. Do not scaffold undecided
architecture.

## The split: you read, the script emits

You do the fuzzy reading; `scripts/scaffold.py` does the deterministic
emission. Never hand-write the repo files — the script owns them, so a fix
lands once for every future project.

## Steps

1. **Read `ARCHITECTURE.md`.** From the Stack table, take language, database,
   portability layer, object storage, cache, and queue. From the C4 Container
   diagram, take the frontend framework. Take the system name from the title,
   and service names from the service-decomposition ADR (default: one
   service, named after the system). Version comes from `VERSION.txt` if
   present, else `0.1.0`. **A component the ADRs rejected shows as None in
   the Stack table — it must be `null` in the config, and it must not enter
   compose.** This is invariant 4 at the repo level: a rejected component in
   compose is a bug.

2. **Build the config dict** (see `scripts/scaffold.py --help`):

   ```json
   {"name": "...", "version": "...", "license": "...", "language": "...",
    "frontend": "...",
    "components": {"database": "...", "object_storage": "...|null",
                   "cache": "...|null", "queue": "...|null"},
    "services": ["..."]}
   ```

   Omit `container_engine`. The emitted Makefile always defaults to Docker
   with a runtime override (`make up CONTAINER_ENGINE=podman`); no config key
   changes that default, so don't add one expecting it to.

3. **Confirm the license with the user** if `ARCHITECTURE.md` didn't record
   one. Open source is preferred; for a commercial/BSL choice, state plainly
   that they should consult a legal advisor — you do not give legal advice.

4. **Invoke the script:**
   `python scripts/scaffold.py --config <cfg.json> --dest <repo-root>`

5. **Place `ARCHITECTURE.md`** at the repo root (it's the decision record and
   the evolve-mode switch) and confirm the generated `README.md` links it. Do
   not re-author the C4 — `deciding-architecture` already produced it; this
   skill's job is placement, not authorship.

6. **Report** what was emitted and what was deliberately omitted (the
   rejected components), pointing at the ADRs.

## What this skill does not do

Frontend code (Plan 3), backend services (Plan 4), and CI/release wiring
(Plan 5) are separate. This produces the skeleton they populate. `make up`
here boots the infra (database, object storage); app services join later.
