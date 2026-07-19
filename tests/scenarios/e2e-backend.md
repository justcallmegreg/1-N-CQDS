# End-to-end backend validation scenario

The walking-skeleton milestone for Plan 4 (backend service skeletons) — and
the verdict for the whole 1-N-CQDS methodology. Take the real Fieldnote
architecture decisions (Postgres, MinIO, no cache, no queue), scaffold the
repo (Plan 2's `scaffold.py`), instantiate the Python service built and
tested in Tasks 2-5 (`skills/adding-backend-service/assets/python/`) into
`backends/fieldnote/`, wire it into compose, and boot the *whole* stack for
real: `make up` builds the service image and starts db + service together.
This is not a new build exercise — the skeleton is a fixed input from Tasks
2-5. This proves it actually deploys and serves against a real database
through the repository seam.

## Config under test

Same Fieldnote config as `e2e-scaffold.md` (Plan 2):

```json
{"name": "fieldnote", "version": "0.1.0", "license": "Apache-2.0",
 "language": "python", "frontend": "astro",
 "components": {"database": "postgres", "object_storage": "minio", "cache": null, "queue": null},
 "services": ["fieldnote"]}
```

## What it exercises

- The full chain: `scaffold.py` emission → asset instantiation → compose
  wiring → a real multi-service `docker compose up --build`, not a
  `compose config`-only substitute and not a single-container smoke test.
- The service's own `CMD` (`alembic upgrade head && uvicorn ...`) running
  unmodified inside the built image against a real Postgres reached over the
  compose network (`db:5432`), not SQLite and not a mocked connection.
- The repository seam end to end: an HTTP POST reaches `routes.py` →
  `ItemRepository.add()` → SQLAlchemy → Postgres, and the HTTP response body
  is the boundary DTO (`{"id":1,"name":...}`), never a leaked ORM
  representation.
- Persistence proven independently of the API: a direct `psql` query against
  the `db` container's `items` table, not just a second HTTP read.
- **Statelessness (invariant 1)**: restarting only the `fieldnote` container
  (not `db`) and confirming the row is still there — state lives in
  Postgres, not in the service process.
- The repository seam unit test (`tests/test_repository.py`, 3 cases)
  actually run, proving the SQLite-vs-Postgres engine-independence the seam
  promises.
- Clean teardown (`make down` + explicit volume/network check).

## Procedure

1. Write the config above to a scratch JSON file; run `scaffold.py --config
   ... --dest /tmp/fieldnote-stack`.
2. Copy `skills/adding-backend-service/assets/python/` into
   `/tmp/fieldnote-stack/backends/fieldnote/`.
3. Replace the commented `fieldnote` app-stub in the scaffolded
   `docker-compose.yml` with a real service block: `build: ./backends/fieldnote`,
   `DATABASE_URL: postgresql+psycopg://fieldnote:devpassword@db:5432/fieldnote`,
   `SERVICE_NAME: fieldnote`, `depends_on: db: condition: service_healthy`,
   `ports: ["8000:8000"]`.
4. Confirm the Dockerfile's pinned base digest is current
   (`docker pull python:3.12-slim` and compare `RepoDigests`).
5. `make -C /tmp/fieldnote-stack up`; wait for `db` healthy and the
   `fieldnote` container to reach a running state.
6. `curl -sf localhost:8000/health`, `/health/ready`, `POST /items`,
   `GET /items`.
7. `docker compose ... exec -T db psql -U fieldnote -d fieldnote -c "select
   * from items;"` — confirm the row exists in Postgres directly.
8. `docker compose ... restart fieldnote`; re-`curl GET /items` — confirm
   the item survives.
9. Run `pytest` against the repository seam test suite (dependencies only,
   local venv — the local source tree isn't pip-installable as a package by
   design, see results for why).
10. Grade every row in the brief's table. Record results in
    `baseline-results/e2e-backend-results.md`.
11. `make down` + `docker compose ... down -v`; verify no leftover
    containers/volumes/networks. Do not commit `/tmp/fieldnote-stack`.

## Grading

Per the reference-and-record reframe: grade the **deployed service's actual
behavior** (build success, real HTTP round-trip through the repository seam,
real persistence, real restart-survival, real test pass), not
pressure-resistance — there is no adversarial pressure in this scenario, it
is deterministic tooling either composing and running correctly or not. Any
real failure (build, migration, connection) is reported honestly, and any
fix required is applied to the shipped asset
(`skills/adding-backend-service/assets/python/...`), not just the scratch
copy — a scratch-only fix would mask a broken shipped asset (the Plan 3
masking lesson).
