# End-to-end scaffold results — Fieldnote

Date: 2026-07-18. Scenario: `tests/scenarios/e2e-scaffold.md`. Docker 27.5.1
daemon confirmed up before starting; this is a real boot, not a
`compose config`-only substitute.

## Config used

```json
{"name": "fieldnote", "version": "0.1.0", "license": "Apache-2.0",
 "language": "python", "frontend": "astro",
 "components": {"database": "postgres", "object_storage": "minio", "cache": null, "queue": null},
 "services": ["fieldnote"]}
```

Written to `/tmp/fieldnote-cfg.json`, exactly matching the brief's Step 1
config.

## Command run

```
python3 skills/scaffolding-repository/scripts/scaffold.py \
  --config /tmp/fieldnote-cfg.json --dest /tmp/fieldnote-repo
```

Output: `scaffolded 11 paths into /tmp/fieldnote-repo`. Exit 0.

Per the `scaffolding-repository` skill's Step 5 (placement, not authorship),
the real Fieldnote `ARCHITECTURE.md` and `docs/` (purpose.md + 15 ADRs,
`0001`-`0015`, including the two rejection ADRs `0013` cache and `0014`
queue) were recovered from the preserved `/tmp/fieldnote-output.bundle` (a
git bundle from Plan 1's actual end-to-end run) and copied into
`/tmp/fieldnote-repo/` — this is the real decision record, not a
reconstruction.

## Graded table

| # | Check | Expected | Actual | Verdict |
|---|---|---|---|---|
| 1 | Layout | `frontend/`, `backends/fieldnote/`, `e2e/`, `docs/adr/` | all four present (`ls` confirmed), plus `docs/purpose.md` and 15 ADRs placed | ✅ |
| 2 | VERSION.txt | `0.1.0` | `0.1.0` | ✅ |
| 3 | Makefile | help/up/down present, `make help` runs | `make -C /tmp/fieldnote-repo help` exit 0, printed `help`, `up`, `down` with descriptions | ✅ |
| 4 | compose — approved present | postgres + minio | `image: postgres:16.4-alpine` (service `db`) and `image: minio/minio:RELEASE.2024-08-17T01-24-54Z` (service `objectstore`) both present | ✅ |
| 5 | compose — rejected absent | no redis, no rabbitmq, no amqp | `grep -in "redis\|rabbitmq\|amqp" docker-compose.yml` → **no matches** | ✅ |
| 6 | compose validity | `docker compose config` exits 0 | exit 0, valid resolved YAML | ✅ |
| 7 | README | C4 renders, links ARCHITECTURE.md | ```mermaid C4Context``` block present; rendered via `npx -y @mermaid-js/mermaid-cli` → `fieldnote-c4.svg` produced, no errors; `ARCHITECTURE.md` linked twice (structure list + closing pointer) | ✅ |
| 8 | LICENSE | Apache-2.0 text | Head: `Apache License` / `Version 2.0, January 2004`; body contains full "TERMS AND CONDITIONS" + "APPENDIX: How to apply the Apache License" | ✅ |
| 9 | CODEOWNERS | present | present: `* @fieldnote-maintainers`, `/frontend/ @fieldnote-frontend`, `/backends/ @fieldnote-backend` | ✅ |
| 10 | **Infra boot (real)** | `db` reaches healthy, `objectstore` up | `make up` → both containers created and started; after 8s, `db` = `Up ... (healthy)`, `objectstore` = `Up` (no healthcheck defined for MinIO in the template, so "Up" is its terminal state) | ✅ |

**10/10 rows pass.**

## Emitted docker-compose.yml (full contents)

```yaml
# fieldnote local stack. Managed by 1-N-CQDS scaffolding.
# App services (frontend, backends) are added in Plans 3-4; stubbed below.
services:
  db:
    image: postgres:16.4-alpine
    environment:
      POSTGRES_USER: fieldnote
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: fieldnote
    ports: ["5432:5432"]
    volumes: ["db_data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fieldnote"]
      interval: 5s
      timeout: 5s
      retries: 5
  objectstore:
    image: minio/minio:RELEASE.2024-08-17T01-24-54Z
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: fieldnote
      MINIO_ROOT_PASSWORD: devpassword
    ports: ["9000:9000", "9001:9001"]
    volumes: ["objectstore_data:/data"]
# Added in Plan 3 (frontend) and Plan 4 (backends):
#   frontend:
#     build: ./frontend
#   fieldnote:
#     build: ./backends/fieldnote
volumes:
  db_data:
  objectstore_data:
```

Exactly two services (`db`, `objectstore`), exactly two volumes. No `cache`
or `queue` service block — the template's own `# --- CACHE:redis ---` and
`# --- QUEUE:rabbitmq ---` fragments were correctly skipped by
`render_compose()` because `components.cache` and `components.queue` are
both `null` in the config.

`grep -in "redis\|rabbitmq\|amqp" docker-compose.yml` → **zero matches.**
`docker compose -f docker-compose.yml config` → **exit 0.**

## Real boot output

```
$ make up
docker compose up -d --build
 [images pulled: postgres:16.4-alpine, minio/minio:RELEASE.2024-08-17T01-24-54Z]
 Network fieldnote-repo_default  Created
 Volume "fieldnote-repo_objectstore_data"  Created
 Volume "fieldnote-repo_db_data"  Created
 Container fieldnote-repo-db-1  Started
 Container fieldnote-repo-objectstore-1  Started
```

After an 8-second settle (Postgres healthcheck interval 5s):

```
$ docker compose -f docker-compose.yml ps
NAME                           IMAGE                                      COMMAND                  SERVICE       STATUS                    PORTS
fieldnote-repo-db-1            postgres:16.4-alpine                       "docker-entrypoint.s…"   db            Up 14 seconds (healthy)   0.0.0.0:5432->5432/tcp
fieldnote-repo-objectstore-1   minio/minio:RELEASE.2024-08-17T01-24-54Z   "/usr/bin/docker-ent…"   objectstore   Up 14 seconds             0.0.0.0:9000-9001->9000-9001/tcp

$ docker inspect --format='{{.Name}}: {{.State.Status}} health={{.State.Health.Status}}' fieldnote-repo-db-1
/fieldnote-repo-db-1: running health=healthy

$ docker inspect --format='{{.Name}}: {{.State.Status}}' fieldnote-repo-objectstore-1
/fieldnote-repo-objectstore-1: running
```

**`db` (Postgres) reached `healthy`. `objectstore` (MinIO) reached `Up`/`running`.**
No cache or queue container exists to check — none was ever created, matching
the compose file.

## Cleanup

```
$ make down
docker compose down
 Container fieldnote-repo-db-1  Removed
 Container fieldnote-repo-objectstore-1  Removed
 Network fieldnote-repo_default  Removed

$ docker compose -f docker-compose.yml ps -a
NAME  IMAGE  COMMAND  SERVICE  CREATED  STATUS  PORTS
(empty)

$ docker volume ls | grep fieldnote-repo
local     fieldnote-repo_db_data
local     fieldnote-repo_objectstore_data
```

`make down` (plain `docker compose down`) does not remove named volumes by
design — ran `docker compose -f docker-compose.yml down -v` explicitly to
also drop them, then re-checked:

```
$ docker volume ls | grep fieldnote-repo
(no output — confirmed clean)
$ docker network ls | grep fieldnote-repo
(no output — confirmed clean)
```

Environment left clean: no containers, volumes, or networks remain from this
run.

## Divergence — honest note

The task's given config sets `"frontend": "astro"`. The real, recovered
Fieldnote `ARCHITECTURE.md` (from `/tmp/fieldnote-output.bundle`, Plan 1's
actual end-to-end run) records the frontend decision as **React + Vite PWA
(TypeScript)** (ADR-0006/0007/0009), not Astro — Fieldnote is an
installable offline-first PWA with a Service Worker and IndexedDB (Dexie) for
the on-device sync queue, a fit React+Vite/Workbox was chosen for over Astro.

This divergence has **zero effect on the graded rows above**: `scaffold.py`
never reads `config["frontend"]` today (confirmed in
`skills/scaffolding-repository/scripts/scaffold.py` — grep for `frontend`
matches only the config dict shape and the `frontend/` directory `mkdir`,
never `config["frontend"]`). It only affects what a human or a later Plan
3/4 step would read out of the config when scaffolding actual frontend code,
which is explicitly out of scope for Plan 2. Recorded here rather than
silently reconciled, per the honesty discipline — the task brief's example
config was illustrative of the *shape*, not a byte-exact transcription of the
real Stack table's frontend row, and this run did not correct it.

No other divergence found. All 10 graded rows pass against the config as
given, and the real infra boots successfully.

## Verdict

**Plan 2 walking-skeleton test: PASS.** Scaffolding the real Fieldnote
architecture decisions yields a valid skeleton whose compose contains exactly
the two approved components (Postgres, MinIO) and excludes both rejected
components (Redis, RabbitMQ/AMQP), and whose infra boots for real — Postgres
reaches `healthy`, MinIO reaches `Up`. This is Greg's call to ratify, per the
brief, but nothing here contradicts a go verdict on Plan 2.
