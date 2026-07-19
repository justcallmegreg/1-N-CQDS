# End-to-end backend results — Fieldnote (Python service against Postgres)

Date: 2026-07-19. Scenario: `tests/scenarios/e2e-backend.md`. Docker 27.5.1
daemon confirmed up before starting. This is a real multi-service
`docker compose up --build`, not a `compose config`-only substitute and not
a single-container smoke test.

## Config used

```json
{"name": "fieldnote", "version": "0.1.0", "license": "Apache-2.0",
 "language": "python", "frontend": "astro",
 "components": {"database": "postgres", "object_storage": "minio", "cache": null, "queue": null},
 "services": ["fieldnote"]}
```

## Setup

1. `python3 skills/scaffolding-repository/scripts/scaffold.py --config /tmp/fieldnote-cfg.json --dest /tmp/fieldnote-stack` → `scaffolded 11 paths into /tmp/fieldnote-stack`.
2. `cp -R skills/adding-backend-service/assets/python/. /tmp/fieldnote-stack/backends/fieldnote/`.
3. Resolved the current `python:3.12-slim` digest: `docker pull python:3.12-slim` → `Digest: sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de`. This **matches** the digest already pinned in the shipped Dockerfile (Task 5's work) — no re-pin was needed.
4. Replaced the commented app-stub in `docker-compose.yml` with the real service block from the brief (verbatim — `build`, `DATABASE_URL`, `SERVICE_NAME`, `depends_on: db: condition: service_healthy`, `ports: ["8000:8000"]`).
5. `docker compose config` → exit 0, valid resolved YAML (three services: `db`, `objectstore`, `fieldnote`; two volumes).

## Graded table

| # | Check | Expected | Actual | Verdict |
|---|---|---|---|---|
| 1 | Service image builds (multi-arch base, non-root, pinned digest) | builds | Built in ~20s; `USER appuser` (uid 10001) confirmed in Dockerfile; base digest matches current `python:3.12-slim` — see divergence note below for a real bug found and fixed during this build | ✅ (after shipped-asset fix) |
| 2 | `make up` boots db + service | both up, db healthy | `db` reached `(healthy)`; `fieldnote` reached `Up` running uvicorn — but only after the shipped-asset fix (see below); before the fix it exited 1 | ✅ (after fix) |
| 3 | `/health` | `{"status":"ok"}` | `{"status":"ok"}` | ✅ |
| 4 | `/health/ready` | DB reachable | `{"status":"ready"}` | ✅ |
| 5 | POST /items then GET /items | item round-trips | POST → `{"id":1,"name":"first observation"}`; GET → `[{"id":1,"name":"first observation"}]` | ✅ |
| 6 | Row present in Postgres (psql) | persisted in DB, not memory | `psql -U fieldnote -d fieldnote -c "select * from items;"` → `1 | first observation` | ✅ |
| 7 | Survives service restart | item still there (stateless) | `docker compose restart fieldnote`; re-`GET /items` → `[{"id":1,"name":"first observation"}]`, unchanged | ✅ |
| 8 | Repository seam test | 3 passed (no ORM type leaks) | `pytest -v` → `3 passed in 0.85s` (all three: boundary-type add/get, boundary-type list, cross-engine invariance) | ✅ |

**8/8 rows pass — after a real shipped-asset fix (row 1/2), applied honestly rather than worked around in the scratch copy.**

## Real bug found and fixed (shipped asset, not just scratch)

The **first** `make up` failed for real. `fieldnote` container logs:

```
Traceback (most recent call last):
  File "/usr/local/bin/alembic", line 6, in <module>
    sys.exit(main())
  ...
  File "/app/alembic/env.py", line 5, in <module>
    from app.db import Base
ModuleNotFoundError: No module named 'app'
```

`docker compose ps -a` confirmed `fieldnote-stack-fieldnote-1` had `Exited
(1)` — a genuine boot failure, not a hypothetical.

**Root cause:** the Dockerfile's `CMD` runs `alembic upgrade head &&
uvicorn app.main:app ...` from `WORKDIR /app`. `uvicorn`'s own import
machinery inserts the current working directory onto `sys.path`, so
`app.main:app` resolves fine. Alembic's console-script entry point (installed
at `/usr/local/bin/alembic`) has **no such special-case** — a Python
console-script's `sys.path[0]` is the script's own directory
(`/usr/local/bin`), not the invoking `cwd`, so `alembic/env.py`'s `from
app.db import Base` (needed to register `Base.metadata` for
autogenerate/target-metadata) could not find the `app` package at all. This
was masked in earlier tasks because Task 3/4's tests exercise the repository
and Alembic script content directly in Python, never through the installed
console-script binary from a fresh `WORKDIR`, and Task 5's Dockerfile check
was a build-only check, not a runtime boot.

**Fix, applied to the shipped asset**
(`skills/adding-backend-service/assets/python/Dockerfile`), not just the
scratch copy:

```diff
 FROM python@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS base
-ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
+# PYTHONPATH=/app: the alembic console-script entry point (unlike uvicorn,
+# which self-inserts cwd) does NOT put WORKDIR on sys.path, so `alembic
+# upgrade head` fails with `ModuleNotFoundError: No module named 'app'`
+# without this — confirmed by a real boot failure (Plan 4 Task 9).
+ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PYTHONPATH=/app
 WORKDIR /app
```

Rebuilt (`docker compose up -d --build fieldnote`) with the fixed
Dockerfile copied back into the scratch instance; the container then started
cleanly, ran `alembic upgrade head` successfully (creating `items`), and
served on `:8000`. This fix is committed **separately** from the two
scenario files per the honesty discipline — a scratch-only patch would have
hidden a broken shipped asset (the Plan 3 masking lesson this task is
explicitly warned against repeating).

## `make up` output (post-fix, full boot)

```
$ make -C /tmp/fieldnote-stack up
docker compose up -d --build
 ... [pip install layer: fastapi, uvicorn, sqlalchemy, alembic, psycopg-binary, ...]
 fieldnote  Built
 Network fieldnote-stack_default  Created
 Volume "fieldnote-stack_db_data"  Created
 Volume "fieldnote-stack_objectstore_data"  Created
 Container fieldnote-stack-objectstore-1  Created
 Container fieldnote-stack-db-1  Created
 Container fieldnote-stack-fieldnote-1  Created
 Container fieldnote-stack-db-1  Starting
 Container fieldnote-stack-objectstore-1  Starting
 Container fieldnote-stack-objectstore-1  Started
 Container fieldnote-stack-db-1  Started
 Container fieldnote-stack-db-1  Waiting
 Container fieldnote-stack-db-1  Healthy
 Container fieldnote-stack-fieldnote-1  Starting
 Container fieldnote-stack-fieldnote-1  Started
```

```
$ docker compose ps
NAME                            IMAGE                        SERVICE       STATUS                        PORTS
fieldnote-stack-db-1            postgres:16.4-alpine         db            Up (healthy)                  0.0.0.0:5432->5432/tcp
fieldnote-stack-fieldnote-1     fieldnote-stack-fieldnote     fieldnote     Up                            0.0.0.0:8000->8000/tcp
fieldnote-stack-objectstore-1   minio/minio:...               objectstore   Up                            0.0.0.0:9000-9001->9000-9001/tcp

$ docker compose logs fieldnote
fieldnote-1  | INFO:     Started server process [8]
fieldnote-1  | INFO:     Waiting for application startup.
fieldnote-1  | INFO:     Application startup complete.
fieldnote-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

(No migration-error lines in this run — `alembic upgrade head` ran silently
to completion because it had nothing to print on success, then uvicorn
started.)

## Curl round-trip (actual output)

```
$ curl -sf localhost:8000/health
{"status":"ok"}

$ curl -sf localhost:8000/health/ready
{"status":"ready"}

$ curl -sf -X POST localhost:8000/items -H 'content-type: application/json' -d '{"name":"first observation"}'
{"id":1,"name":"first observation"}

$ curl -sf localhost:8000/items
[{"id":1,"name":"first observation"}]
```

Exactly matches the brief's expected output.

## Postgres persistence proof (psql, direct — not through the API)

```
$ docker compose -f /tmp/fieldnote-stack/docker-compose.yml exec -T db psql -U fieldnote -d fieldnote -c "select * from items;"
 id |       name
----+-------------------
  1 | first observation
(1 row)
```

The row is genuinely in Postgres — this is a direct database query, not a
second HTTP call, so it rules out an in-memory or per-process cache
masquerading as persistence.

## Statelessness proof (restart-survival)

```
$ docker compose -f /tmp/fieldnote-stack/docker-compose.yml restart fieldnote
 Container fieldnote-stack-fieldnote-1  Restarting
 Container fieldnote-stack-fieldnote-1  Started

$ curl -sf localhost:8000/health   # up after ~2s
{"status":"ok"}

$ curl -sf localhost:8000/items
[{"id":1,"name":"first observation"}]
```

Only the `fieldnote` container was restarted (`db` was left running
throughout). The item survived because its state lives in Postgres, never
in the service process — invariant 1 (stateless services) holds for a real,
booted service, not just by code inspection. The service logs also show
`alembic upgrade head` ran again on restart (the migration's own idempotency
to head, per the Dockerfile's `CMD` comment) without error or duplicate
table creation, then uvicorn started cleanly a second time.

## Repository seam test (3 cases)

Run against a local venv with only the runtime dependencies installed (not
`pip install -e .`/`pip install .` on the local source tree — the flat
layout with both `app/` and `alembic/` as top-level directories is **not**
independently pip-installable outside the Dockerfile's specific COPY
ordering trick; `pip install .` in the Dockerfile only ever sees
`pyproject.toml` at that layer, before `app/`/`alembic/` are copied in, so
setuptools' auto-discovery never sees the conflict. Attempting `pip install
-e .` locally correctly reproduces `error: Multiple top-level packages
discovered in a flat-layout: ['app', 'alembic']` — a real constraint of the
shipped layout, not a bug, worth noting but out of scope to change since it
doesn't affect the Docker build or the runtime boot):

```
$ pytest -v
tests/test_repository.py::test_add_and_get_returns_boundary_type_not_orm_model PASSED
tests/test_repository.py::test_list_returns_boundary_types PASSED
tests/test_repository.py::test_works_on_a_different_engine_unchanged PASSED
3 passed in 0.85s
```

Confirms the seam: the repository never leaks the SQLAlchemy `Item` ORM
model across the boundary, and the same code runs unchanged against SQLite
(tests) and Postgres (this boot) — the portability the seam promises.

## `db.py`'s `get_session()` — confirmed still dead code

Per the task instructions, checked whether the real boot wiring uses
`app/db.py`'s `get_session()` generator. It does not: `app/routes.py`
builds its own repository via `_repo()` → `ItemRepository(make_session_factory(engine))`
directly, never through `get_session()` (no FastAPI `Depends(get_session)`
anywhere in `routes.py` or `main.py`). This matches Task 3 review's flag —
`get_session()` is currently-unused dead code. Its removal is optional per
the brief and was **not** performed here since it is not required for the
verdict and this task's mandate is proving the boot, not refactoring the
asset further than the one real bug fix above.

## Cleanup

```
$ make -C /tmp/fieldnote-stack down
docker compose down
 Container fieldnote-stack-fieldnote-1  Removed
 Container fieldnote-stack-objectstore-1  Removed
 Container fieldnote-stack-db-1  Removed
 Network fieldnote-stack_default  Removed
 Volume fieldnote-stack_db_data  Removed
 Volume fieldnote-stack_objectstore_data  Removed

$ docker compose -f /tmp/fieldnote-stack/docker-compose.yml down -v
 (no-op — already down)

$ docker compose -f /tmp/fieldnote-stack/docker-compose.yml ps -a
NAME  IMAGE  COMMAND  SERVICE  CREATED  STATUS  PORTS
(empty)

$ docker volume ls | grep fieldnote-stack
(no output)
$ docker network ls | grep fieldnote-stack
(no output)
```

Environment left clean: no containers, volumes, or networks remain from this
run. `/tmp/fieldnote-stack` was not committed (scratch only, per
instructions) and was left in place on disk for inspection but is git-ignored
territory outside this repository.

## Divergence — honest notes

1. **Real bug found and fixed** (see above): the shipped Dockerfile was
   missing `PYTHONPATH=/app`, which made `alembic upgrade head` fail with
   `ModuleNotFoundError: No module named 'app'` on a real boot. This was
   invisible in Tasks 2-5 because none of their checks actually ran the
   built image's `CMD` end to end against a real network-attached Postgres.
   Fixed in the shipped asset, committed separately from the scenario files.
2. **`pip install -e .` doesn't work locally** on the flat `app/` +
   `alembic/` layout (setuptools auto-discovery conflict) — harmless for
   the Docker build (which only ever `pip install`s before those
   directories exist) but worth flagging for anyone trying to `pip install
   -e .` for local dev; the repository seam tests still run fine via
   `pytest` with `pythonpath = ["."]` (already configured in
   `pyproject.toml`) and dependencies installed directly.
3. **`get_session()` in `db.py` remains unused dead code** — confirmed, not
   removed (optional per brief).

No other divergence found. All 8 graded rows pass, the real stack boots,
and every persistence/statelessness claim was observed directly (psql,
container restart), not asserted.

## Verdict

**Plan 4 walking-skeleton test: PASS**, with one honestly-disclosed and
honestly-fixed bug along the way. A real Python service — built from the
shipped `adding-backend-service` asset, unmodified except for the one-line
`PYTHONPATH` fix now also shipped — boots in `docker compose`, serves a real
HTTP request that reads and writes Postgres exclusively through the
repository seam (never the ORM type directly), the row is independently
confirmed present in Postgres via `psql`, and the row survives a restart of
the service container alone — proving state lives in the database, not the
process. This is Greg's call to ratify as the Plan 4 (and whole 1-N-CQDS
methodology) verdict, but nothing here contradicts a go verdict.
