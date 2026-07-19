---
name: adding-backend-service
description: Use when a project needs a backend service created or added — the N in 1-N-CQDS — instantiating a stateless service wired to the database, in an existing or newly scaffolded repo
---

# Adding a Backend Service

Creates one of the **N** — a stateless backend service wired to the database.
Works in a fresh repo (right after scaffolding) or an existing one (evolve mode:
"add a service").

**REQUIRED BACKGROUND:** Use 1-n-cqds for the four invariants.
**Prerequisite:** `ARCHITECTURE.md` exists (language + database decided). If not —
**REQUIRED SUB-SKILL:** Use deciding-architecture.

## 1. Read the decisions

From `ARCHITECTURE.md`: the backend **language** (all N services share it —
invariant 3), the **database**, and the **service name**. The web framework is a
per-project choice recorded in an ADR; the skeleton's defaults are FastAPI
(Python) and net/http+chi (Go) — a thin router, no heavy framework.

## 2. Instantiate the skeleton

Copy `assets/{language}/` into `backends/{name}/`, substituting the service name.
Un-comment the service's app-stub in `docker-compose.yml` (scaffolding left it
commented). The skeleton ships: a health endpoint, config from env
(`DATABASE_URL`), the ORM wiring (SQLAlchemy+Alembic for Python, GORM for Go), a
**repository layer**, and a multi-arch Dockerfile.

## 3. The repository seam — the point of the whole thing

Even with an ORM, services call **repositories, never the ORM session or driver.**
The repository is the seam that makes the storage decision reversible: within the
SQL family, Postgres↔MariaDB becomes a config change; crossing to Mongo becomes a
new repository implementation behind the same interface — not a rewrite. This is
the code-level realization of "one genuinely irreversible decision" from the
SQL-vs-Document scrutiny. Keep business logic in routes/services that depend on
the repository interface, so nothing above it imports SQLAlchemy/GORM types.

## 4. Stateless — always

The service holds no state (invariant 1): no in-process sessions, no local writes
outside `/tmp`. It can be killed and restarted at any instant. State lives in the
database and object storage.

## 5. Build the business logic

Replace the sample `Item` entity with the project's real entities (from the state
inventory in `ARCHITECTURE.md`), keeping the repository discipline. Add
migrations (Alembic for Python).

## 6. Multi-arch image

The Dockerfile builds `linux/amd64,linux/arm64`, runs as a **non-root** user, and
pins base image **digests**. Build with `docker buildx`.

## Coverage

Full skeletons ship for Python and Go (Tier 1) — the shared-language invariant
means a repo needs exactly one of these. For a **document database**, no ODM
buys cross-family portability: the repository is hand-written over the driver
instead — see `assets/mongo-repository.md`.
