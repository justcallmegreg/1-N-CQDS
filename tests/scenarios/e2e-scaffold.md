# End-to-end scaffold validation scenario

The walking-skeleton milestone for Plan 2: take the *real* architecture
decisions Plan 1 produced for Fieldnote (`tests/scenarios/baseline-results/e2e-results.md`,
preserved at `/tmp/fieldnote-output.bundle`) and run them through the
scaffolding engine (`scaffold.py` + the `scaffolding-repository` skill) to
produce a real repository, then boot its infra for real. This is not a new
architecture exercise — architecture is done. This proves emission and
runtime correctness.

## Config under test

Derived from the real Fieldnote `ARCHITECTURE.md`'s Stack table (Database:
PostgreSQL, Object storage: MinIO, Cache: None, Queue: None, single service
`fieldnote`):

```json
{"name": "fieldnote", "version": "0.1.0", "license": "Apache-2.0",
 "language": "python", "frontend": "astro",
 "components": {"database": "postgres", "object_storage": "minio", "cache": null, "queue": null},
 "services": ["fieldnote"]}
```

**Doctrine-critical expectation:** Fieldnote's architecture rejected cache
(ADR-0013) and queue (ADR-0014) after evaluating both gates against the real
state inventory and workload. The scaffolded `docker-compose.yml` **must**
contain Postgres and MinIO and **must not** contain Redis, RabbitMQ, or any
AMQP reference — a rejected component reappearing in compose is invariant 4
violated at the repo level.

## What it exercises

- `scaffold.py`'s full emission path (layout, VERSION.txt, Makefile,
  docker-compose, README, LICENSE, CODEOWNERS) against a real, not synthetic,
  config.
- The `scaffolding-repository` skill's placement step (`ARCHITECTURE.md` +
  `docs/adr/` at repo root, linked from `README.md`).
- Compose validity (`docker compose config`) with a real Docker engine, not a
  skipped/mocked check.
- **Real infra boot** (`make up`): Postgres reaching `healthy` via its
  healthcheck, MinIO reaching `Up`. This is the only step in Plan 2 that
  actually starts containers.
- Clean teardown (`make down` + explicit volume/network check) so the
  environment isn't left dirty.

## Procedure

1. Write `/tmp/fieldnote-cfg.json` with the config above.
2. `python skills/scaffolding-repository/scripts/scaffold.py --config /tmp/fieldnote-cfg.json --dest /tmp/fieldnote-repo`
3. Copy the real `ARCHITECTURE.md` and `docs/` (purpose.md + 15 ADRs) from
   `/tmp/fieldnote-output.bundle` into `/tmp/fieldnote-repo/` (the skill's
   placement step — `scaffold.py` itself does not author or place
   `ARCHITECTURE.md`, only the skill does).
4. Grade every row in the brief's table (layout, VERSION.txt, Makefile,
   compose contents, compose validity, README C4 render, LICENSE, CODEOWNERS).
5. `make -C /tmp/fieldnote-repo up`, confirm `docker compose ps` shows `db`
   healthy and `objectstore` up, then `make -C /tmp/fieldnote-repo down` and
   verify no leftover volumes/networks.

## Grading

Per the reference-and-record reframe: grade the **emitted skeleton and its
boot behavior**, not pressure-resistance (there is no adversarial pressure in
this scenario — deterministic tooling either emits the right thing or it
doesn't). Results in `baseline-results/e2e-scaffold-results.md`.
