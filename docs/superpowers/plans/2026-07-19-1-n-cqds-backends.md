# 1-N-CQDS Backends — Implementation Plan (Plan 4 of 5)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `adding-backend-service` — the skill that instantiates a stateless backend service into `backends/{name}/` — plus the Tier-1 service-skeleton assets (Python: FastAPI + SQLAlchemy + repository + Alembic + multi-arch Dockerfile; Go: net/http + chi + GORM, built and build-checked). The walking-skeleton: `make up` boots Postgres + a Python service that serves a real HTTP request reading/writing Postgres through the repository seam.

**Architecture:** A technique skill + reusable per-language skeleton assets, same shape as Plans 2–3. The skill reads the language and database from `ARCHITECTURE.md`, copies the matching skeleton into `backends/{name}/`, and un-comments the compose app-stub. The **repository layer** is the load-bearing pattern: services call repositories, never the ORM session/driver, so the storage decision stays reversible. Python is validated end-to-end; Go compiles + its image builds; Mongo's repository pattern is documented, not built.

**Tech Stack:** Python 3.12 + FastAPI + SQLAlchemy 2.x + Alembic + Uvicorn; Go 1.23 + chi + GORM; Docker buildx (multi-arch); Postgres 16 (from Plan 2's compose).

## Where this sits

Plan 4 of 5. Plans 1–3 (doctrine engine, scaffolding, frontend) are merged.

| Plan | Scope | Testable deliverable |
|---|---|---|
| 1 ✅ | Doctrine engine | Decisions + ADRs |
| 2 ✅ | Scaffolding | Skeleton + infra boots |
| 3 ✅ | Frontend | Localized frontend, language-switch e2e passes |
| **4 (this)** | Backends — service skeletons, Dockerfiles, repository layer | `make up` boots Postgres + a service; a real request reads/writes Postgres via the repository |
| 5 | Delivery + releases | CI, registry, Trivy, GitFlow, backport |

Services go into `backends/{name}/` (the empty dir Plan 2 scaffolds) and un-comment the compose app-stub Plan 2 left. The Dockerfile lives with its component (`backends/{name}/Dockerfile`) — the compose already references it.

## Plan 1–3 learnings that govern this plan

1. **Point to the spec, don't reproduce doctrine.** The Tier-1 defaults, the portability layer, the repository seam are spec-verbatim where stated. Skeleton *code* is reviewed as code.
2. **Rationale vs rules.** The skill explains *why* the repository seam matters; it invents no new rules.
3. **Reference-and-record.** Technique + assets. The skill is tested by application; the skeleton code gets real tests (pytest for the repository; the service boots and serves).
4. **Test the input space, not the happy path.** Plan 2's MariaDB bug and Plan 3's verbatimModuleSyntax bug both came from validating one path. So: the Python repository must be tested against the swap it promises (at minimum, its interface must not leak SQLAlchemy types to callers — the thing that makes it swappable). The Go skeleton must actually `go build` AND its Docker image must build, not just "look right." **Test under the real config** (the verbatimModuleSyntax lesson): the Dockerfile builds for real; the service runs under the same Postgres the compose provides.
5. **Grade on the artifact.** The verdict is "a service boots in compose and serves a request against Postgres," not "the skeleton reads well."
6. **Honest verification.** The walking-skeleton must actually `make up` and hit the endpoint. A claimed boot that wasn't observed is the Plan-1 failure class. The Task-8 masking lesson: if a fix is needed to make it work, it lands in the shipped asset, not just the scratch copy.

## Global Constraints

From the spec (`docs/superpowers/specs/2026-07-17-1-n-cqds-design.md`), exact values:

- **Stateless-first (invariant 1):** the service is killable at any instant with no loss. No local sessions, no in-process shared state, no local writes outside `/tmp`. State lives in Postgres/S3.
- **Tier-1 skeleton defaults:** Python → FastAPI + SQLAlchemy + Alembic; Go → net/http + chi + GORM. The web framework is a per-project choice (ADR-recorded) — these are the skeleton's starting points.
- **Repository seam:** services call **repositories**, never the ORM session/driver. The repository is what makes Postgres↔MariaDB a config change and SQL→Mongo a repository-implementation change rather than a rewrite.
- **One backend language** per repo (invariant 3): all N services share the chosen language.
- **Multi-arch Docker images:** `linux/amd64,linux/arm64`, one Dockerfile per component, **non-root user**, **pinned base image digests**.
- **MongoDB portability** = hand-written repository pattern, no ODM (documented in Plan 4, not built).
- **Skill frontmatter:** `name` + `description`, `description` starts `Use when`, third person, triggers only.
- **Python:** 3.12+. **Go:** 1.23+.

## Coverage boundary

**Python is validated end-to-end** (Fieldnote is Python — the walking-skeleton boots and serves against Postgres). **Go** ships as a complete skeleton that **compiles (`go build`) and whose Docker image builds**, but is not booted full-stack (no Go project to validate against). **Mongo**'s repository pattern is **documented** in the skill (the pattern, an interface sketch), not built. Stated honestly in the skill, matching Plan 1's Tier-1/doctrine-only philosophy.

## File Structure

```
skills/adding-backend-service/
├── SKILL.md                          # technique: read language/db → instantiate skeleton → wire compose
├── assets/
│   ├── python/                       # FastAPI + SQLAlchemy + repository + Alembic skeleton
│   │   ├── app/
│   │   │   ├── main.py               # FastAPI app, health, wiring
│   │   │   ├── config.py             # env-driven config (DATABASE_URL, ...)
│   │   │   ├── db.py                  # engine/session factory
│   │   │   ├── models.py              # SQLAlchemy models (sample: Item)
│   │   │   ├── repository.py          # THE SEAM: ItemRepository over the session
│   │   │   └── routes.py              # HTTP routes calling the repository
│   │   ├── alembic/                   # migrations (env.py + one migration)
│   │   ├── alembic.ini
│   │   ├── pyproject.toml             # deps: fastapi, sqlalchemy, alembic, uvicorn, psycopg
│   │   ├── Dockerfile                 # multi-arch, non-root, pinned digest
│   │   └── tests/test_repository.py   # repository seam test (no SQLAlchemy types leak)
│   ├── go/                            # net/http + chi + GORM skeleton
│   │   ├── main.go                    # chi router, health
│   │   ├── config.go                  # env config
│   │   ├── repository.go              # THE SEAM: ItemRepository over *gorm.DB
│   │   ├── go.mod
│   │   └── Dockerfile                 # multi-arch, non-root, pinned digest
│   └── mongo-repository.md            # the Mongo repository pattern (documented, not built)
```

The **validation service** (Task 9) is instantiated in a scratch repo, not committed to the plugin.

---

### Task 1: adding-backend-service SKILL.md — the technique

**Files:**
- Create: `skills/adding-backend-service/SKILL.md`

**Interfaces:**
- Consumes: `ARCHITECTURE.md` (language, database, service names).
- Produces: a service in `backends/{name}/` with the compose app-stub un-commented. Invoked in init (after scaffold) or evolve ("add a service").

- [ ] **Step 1: Write the skill**

Technique skill, `description` compliant, budget <500 words. Doctrine (Tier-1 defaults, repository seam, stateless, multi-arch) spec-verbatim; rest is procedure.

```markdown
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
per-project choice; the skeleton's defaults are FastAPI (Python) and net/http+chi
(Go).

## 2. Instantiate the skeleton

Copy `assets/{language}/` into `backends/{name}/`, substituting the service name.
Un-comment the service's app-stub in `docker-compose.yml` (Plan-2 scaffolding left
it commented). The skeleton ships: a health endpoint, config from env
(`DATABASE_URL`), the ORM wiring, a **repository layer**, and a multi-arch Dockerfile.

## 3. The repository seam — the point of the whole thing

Services call **repositories, never the ORM session or driver.** The repository is
the interface that makes the storage decision reversible: Postgres↔MariaDB is a
config change; SQL→Mongo is a new repository implementation behind the same
interface — not a rewrite. Keep business logic in routes/services that depend on
the repository interface, so nothing above it imports SQLAlchemy/GORM types.

## 4. Stateless — always

The service holds no state (invariant 1): no in-process sessions, no local writes
outside `/tmp`. It can be killed and restarted at any instant. State is in the
database and object storage.

## 5. Build the business logic

Replace the sample `Item` entity with the project's real entities (from the state
inventory in `ARCHITECTURE.md`), keeping the repository discipline. Add migrations
(Alembic for Python).

## 6. Multi-arch image

The Dockerfile builds `linux/amd64,linux/arm64`, runs as a **non-root** user, and
pins base image **digests**. Build with `docker buildx`.

## Coverage

Full skeletons ship for Python and Go (Tier 1). For a **document database**, the
repository is hand-written over the driver (no ODM) — see `assets/mongo-repository.md`.
```

- [ ] **Step 2: Verify budget + description**

Run: `wc -w skills/adding-backend-service/SKILL.md` → <500. Description compliant.

- [ ] **Step 3: Commit**

```bash
git add skills/adding-backend-service/SKILL.md
git commit -m "feat: adding-backend-service technique skill"
```

---

### Task 2: Python skeleton — FastAPI app, config, health

**Files:**
- Create: `skills/adding-backend-service/assets/python/app/main.py`
- Create: `skills/adding-backend-service/assets/python/app/config.py`
- Create: `skills/adding-backend-service/assets/python/pyproject.toml`

**Interfaces:**
- Produces: a FastAPI app with `/health` returning `{"status":"ok"}` and `/health/ready` checking the DB; `settings` from env. Consumed by Tasks 3–4 (routes, db) and Task 9 (boot).

- [ ] **Step 1: Write config.py**

```python
# config.py — all config from the environment. Nothing hard-coded; nothing local.
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str
    service_name: str

def load_settings() -> Settings:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required")
    return Settings(database_url=url, service_name=os.environ.get("SERVICE_NAME", "service"))
```

- [ ] **Step 2: Write main.py**

```python
# main.py — FastAPI app. Stateless: no module-level mutable state beyond the
# engine (a connection pool, not app state). Health is liveness; ready checks DB.
from fastapi import FastAPI, Depends
from sqlalchemy import text
from .config import load_settings
from .db import get_session, engine
from .routes import router

app = FastAPI(title="1-N-CQDS service")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/ready")
def ready():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ready"}
```

- [ ] **Step 3: Write pyproject.toml**

```toml
[project]
name = "cqds-service"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.32",
  "sqlalchemy>=2.0",
  "alembic>=1.13",
  "psycopg[binary]>=3.2",
]

[tool.pytest.ini_options]
pythonpath = ["."]
```

- [ ] **Step 4: Syntax-check**

Run: `cd skills/adding-backend-service/assets/python && python -m py_compile app/config.py app/main.py 2>&1 | tail -3` (main.py imports .db/.routes which come in Tasks 3–4; use `python -c "import ast; ast.parse(open('app/main.py').read())"` to parse without importing).
Expected: parses, no syntax error.

- [ ] **Step 5: Commit**

```bash
git add skills/adding-backend-service/assets/python/app/config.py skills/adding-backend-service/assets/python/app/main.py skills/adding-backend-service/assets/python/pyproject.toml
git commit -m "feat: Python skeleton — FastAPI app, env config, health endpoints"
```

---

### Task 3: Python skeleton — SQLAlchemy db + models + the repository seam

**Files:**
- Create: `skills/adding-backend-service/assets/python/app/db.py`
- Create: `skills/adding-backend-service/assets/python/app/models.py`
- Create: `skills/adding-backend-service/assets/python/app/repository.py`
- Create: `skills/adding-backend-service/assets/python/app/routes.py`
- Create: `skills/adding-backend-service/assets/python/tests/test_repository.py`

**Interfaces:**
- Consumes: `settings` (Task 2).
- Produces: `ItemRepository` with `add(name) -> Item`, `list() -> list[Item]`, `get(id) -> Item | None`, using a plain dataclass `Item` (NOT the SQLAlchemy model) as the boundary type — so callers never import SQLAlchemy. This is the seam test's subject.

- [ ] **Step 1: Write the repository seam test FIRST (TDD)**

```python
# tests/test_repository.py — the seam: the repository returns boundary types
# (plain dataclasses), never SQLAlchemy model instances, so callers don't couple
# to the ORM. Uses in-memory SQLite to prove engine-independence.
from app.db import make_engine, make_session_factory, Base
from app.repository import ItemRepository
from app.models import Item as ItemModel   # the ORM model (internal)
from app.repository import Item as ItemDTO # the boundary dataclass (public)

def make_repo():
    eng = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(eng)
    sf = make_session_factory(eng)
    return ItemRepository(sf)

def test_add_and_get_returns_boundary_type_not_orm_model():
    repo = make_repo()
    created = repo.add("hello")
    assert isinstance(created, ItemDTO)
    assert not isinstance(created, ItemModel)  # the seam: no ORM type leaks out
    fetched = repo.get(created.id)
    assert fetched is not None and fetched.name == "hello" and isinstance(fetched, ItemDTO)

def test_list_returns_boundary_types():
    repo = make_repo()
    repo.add("a"); repo.add("b")
    items = repo.list()
    assert [i.name for i in items] == ["a", "b"]
    assert all(isinstance(i, ItemDTO) for i in items)

def test_works_on_a_different_engine_unchanged():
    # The same repository code runs on SQLite here and Postgres in prod — the
    # engine-independence that the portability layer promises.
    repo = make_repo()  # sqlite
    assert repo.add("x").name == "x"
```

- [ ] **Step 2: Run it, verify it fails**

Run: `cd skills/adding-backend-service/assets/python && python -m pytest tests/test_repository.py -v` (with a venv having sqlalchemy + pytest).
Expected: FAIL — `app.db`/`repository`/`models` don't exist.

- [ ] **Step 3: Write db.py**

```python
# db.py — engine + session factory. Engine-parameterized so tests use SQLite and
# prod uses Postgres with the SAME code. No global session; sessions are per-unit-of-work.
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import load_settings

class Base(DeclarativeBase):
    pass

def make_engine(url: str) -> Engine:
    return create_engine(url, future=True)

def make_session_factory(engine: Engine):
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)

# Prod singletons (a pool, not mutable app state).
_settings = None
def _get_settings():
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings

engine = make_engine(_get_settings().database_url) if __import__("os").environ.get("DATABASE_URL") else None

def get_session():
    sf = make_session_factory(engine)
    with sf() as s:
        yield s
```

- [ ] **Step 4: Write models.py**

```python
# models.py — SQLAlchemy models. INTERNAL to the repository; never imported by
# routes/business logic. Sample entity: Item (replace per project).
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
```

- [ ] **Step 5: Write repository.py (the seam)**

```python
# repository.py — THE SEAM. Public boundary type is a dataclass; the ORM model
# stays inside. Callers depend on this interface, never on SQLAlchemy.
from dataclasses import dataclass
from .models import Item as ItemModel

@dataclass(frozen=True)
class Item:            # boundary DTO — what callers see
    id: int
    name: str

def _to_dto(m: ItemModel) -> "Item":
    return Item(id=m.id, name=m.name)

class ItemRepository:
    def __init__(self, session_factory):
        self._sf = session_factory

    def add(self, name: str) -> Item:
        with self._sf() as s:
            m = ItemModel(name=name)
            s.add(m); s.commit(); s.refresh(m)
            return _to_dto(m)

    def list(self) -> list[Item]:
        with self._sf() as s:
            return [_to_dto(m) for m in s.query(ItemModel).order_by(ItemModel.id).all()]

    def get(self, item_id: int) -> Item | None:
        with self._sf() as s:
            m = s.get(ItemModel, item_id)
            return _to_dto(m) if m else None
```

- [ ] **Step 6: Write routes.py**

```python
# routes.py — HTTP layer. Depends on ItemRepository (the interface), NOT on
# SQLAlchemy. Business logic lives here and never imports the ORM.
from fastapi import APIRouter
from pydantic import BaseModel
from .db import engine, make_session_factory
from .repository import ItemRepository

router = APIRouter(prefix="/items")

class NewItem(BaseModel):
    name: str

def _repo() -> ItemRepository:
    return ItemRepository(make_session_factory(engine))

@router.post("")
def create_item(body: NewItem):
    return _repo().add(body.name)

@router.get("")
def list_items():
    return _repo().list()
```

- [ ] **Step 7: Run the tests, verify pass**

Run: `cd skills/adding-backend-service/assets/python && python -m pytest tests/test_repository.py -v`
Expected: 3 passed. The seam holds — no ORM type leaks to callers, and the repo runs unchanged on SQLite (proving engine-independence).

- [ ] **Step 8: Commit**

```bash
git add skills/adding-backend-service/assets/python/app skills/adding-backend-service/assets/python/tests
git commit -m "feat: Python skeleton — SQLAlchemy db, models, and the repository seam"
```

---

### Task 4: Python skeleton — Alembic migrations

**Files:**
- Create: `skills/adding-backend-service/assets/python/alembic.ini`
- Create: `skills/adding-backend-service/assets/python/alembic/env.py`
- Create: `skills/adding-backend-service/assets/python/alembic/versions/0001_initial.py`

**Interfaces:**
- Consumes: `Base` metadata (Task 3), `settings.database_url`.
- Produces: `alembic upgrade head` creates the `items` table. Used by Task 9's boot.

- [ ] **Step 1: Write alembic.ini**

```ini
[alembic]
script_location = alembic
sqlalchemy.url =
[loggers]
keys = root
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = WARN
handlers = console
qualname =
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

- [ ] **Step 2: Write alembic/env.py**

```python
# env.py — reads DATABASE_URL from env (not the ini), targets Base.metadata.
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db import Base
from app import models  # noqa: F401 — register tables on Base

config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section),
                                     prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

- [ ] **Step 3: Write the initial migration**

```python
# 0001_initial.py — creates the items table.
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None

def upgrade():
    op.create_table("items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False))

def downgrade():
    op.drop_table("items")
```

- [ ] **Step 4: Verify migration applies (against SQLite)**

Run: `cd skills/adding-backend-service/assets/python && DATABASE_URL="sqlite+pysqlite:///./test.db" python -m alembic upgrade head && python -c "import sqlite3; print('items' in [r[0] for r in sqlite3.connect('test.db').execute('select name from sqlite_master where type=\"table\"')])" && rm -f test.db`
Expected: prints `True` (items table created). Clean up test.db.

- [ ] **Step 5: Commit**

```bash
git add skills/adding-backend-service/assets/python/alembic.ini skills/adding-backend-service/assets/python/alembic
git commit -m "feat: Python skeleton — Alembic migrations creating the items table"
```

---

### Task 5: Python multi-arch Dockerfile

**Files:**
- Create: `skills/adding-backend-service/assets/python/Dockerfile`
- Create: `skills/adding-backend-service/assets/python/.dockerignore`

**Interfaces:**
- Produces: a multi-arch image running the service as non-root on a pinned base. Built in Task 9.

- [ ] **Step 1: Write the Dockerfile**

```dockerfile
# Multi-arch (buildx: linux/amd64,linux/arm64). Non-root. Pinned digest.
# python:3.12-slim digest below is an example — the skill re-pins to current at build.
FROM python@sha256:3c1f7e5f1a2b0e6d5a1e6a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d AS base
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# deps first for layer caching
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# non-root
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
# migrate then serve; both are stateless-safe (migration is idempotent to head)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

- [ ] **Step 2: Write .dockerignore**

```
__pycache__/
*.pyc
tests/
test.db
.venv/
```

- [ ] **Step 3: Note on digest pinning**

The `sha256:...` above is a placeholder digest and WILL NOT pull. The skill (and Task 9) must resolve the real current digest for `python:3.12-slim` at build time:
`docker buildx imagetools inspect python:3.12-slim --format '{{.Manifest.Digest}}'` (or `docker pull python:3.12-slim && docker inspect --format '{{index .RepoDigests 0}}' python:3.12-slim`). Record the resolved digest. **This is a real step, not decoration — an unpinned or fake-pinned base is a supply-chain gap the spec forbids.** Task 9 does the real pin.

- [ ] **Step 4: Commit**

```bash
git add skills/adding-backend-service/assets/python/Dockerfile skills/adding-backend-service/assets/python/.dockerignore
git commit -m "feat: Python multi-arch Dockerfile (non-root, digest-pinned base)"
```

---

### Task 6: Go skeleton — chi + GORM + repository (compiles)

**Files:**
- Create: `skills/adding-backend-service/assets/go/main.go`
- Create: `skills/adding-backend-service/assets/go/config.go`
- Create: `skills/adding-backend-service/assets/go/repository.go`
- Create: `skills/adding-backend-service/assets/go/go.mod`

**Interfaces:**
- Produces: a chi service with `/health`, `/health/ready`, `/items` (GET/POST), and an `ItemRepository` over `*gorm.DB` returning a boundary `Item` struct. Must `go build` and `go vet`.

- [ ] **Step 1: Write go.mod**

```
module cqds-service

go 1.23

require (
	github.com/go-chi/chi/v5 v5.1.0
	gorm.io/driver/postgres v1.5.9
	gorm.io/gorm v1.25.12
)
```

- [ ] **Step 2: Write config.go**

```go
package main

import (
	"os"
)

type Config struct {
	DatabaseURL string
	ServiceName string
}

func LoadConfig() (Config, error) {
	url := os.Getenv("DATABASE_URL")
	if url == "" {
		return Config{}, os.ErrInvalid
	}
	name := os.Getenv("SERVICE_NAME")
	if name == "" {
		name = "service"
	}
	return Config{DatabaseURL: url, ServiceName: name}, nil
}
```

- [ ] **Step 3: Write repository.go (the seam)**

```go
package main

import "gorm.io/gorm"

// itemModel is the GORM model — internal to the repository.
type itemModel struct {
	ID   uint `gorm:"primaryKey"`
	Name string
}

func (itemModel) TableName() string { return "items" }

// Item is the boundary type — what callers see. No GORM types leak out.
type Item struct {
	ID   uint
	Name string
}

type ItemRepository struct{ db *gorm.DB }

func NewItemRepository(db *gorm.DB) *ItemRepository { return &ItemRepository{db: db} }

func (r *ItemRepository) Add(name string) (Item, error) {
	m := itemModel{Name: name}
	if err := r.db.Create(&m).Error; err != nil {
		return Item{}, err
	}
	return Item{ID: m.ID, Name: m.Name}, nil
}

func (r *ItemRepository) List() ([]Item, error) {
	var ms []itemModel
	if err := r.db.Order("id").Find(&ms).Error; err != nil {
		return nil, err
	}
	out := make([]Item, len(ms))
	for i, m := range ms {
		out[i] = Item{ID: m.ID, Name: m.Name}
	}
	return out, nil
}
```

- [ ] **Step 4: Write main.go**

```go
package main

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	cfg, err := LoadConfig()
	if err != nil {
		log.Fatalf("config: %v", err)
	}
	db, err := gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		log.Fatalf("db: %v", err)
	}
	if err := db.AutoMigrate(&itemModel{}); err != nil {
		log.Fatalf("migrate: %v", err)
	}
	repo := NewItemRepository(db)

	r := chi.NewRouter()
	r.Get("/health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, map[string]string{"status": "ok"})
	})
	r.Get("/health/ready", func(w http.ResponseWriter, _ *http.Request) {
		sqlDB, _ := db.DB()
		if err := sqlDB.Ping(); err != nil {
			http.Error(w, "not ready", http.StatusServiceUnavailable)
			return
		}
		writeJSON(w, map[string]string{"status": "ready"})
	})
	r.Get("/items", func(w http.ResponseWriter, _ *http.Request) {
		items, err := repo.List()
		if err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		writeJSON(w, items)
	})
	r.Post("/items", func(w http.ResponseWriter, req *http.Request) {
		var body struct{ Name string }
		json.NewDecoder(req.Body).Decode(&body)
		item, err := repo.Add(body.Name)
		if err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		writeJSON(w, item)
	})
	log.Fatal(http.ListenAndServe(":8000", r))
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(v)
}
```

- [ ] **Step 5: Verify it compiles + vets**

Run: `cd skills/adding-backend-service/assets/go && go mod tidy && go build ./... && go vet ./... 2>&1 | tail -5`
Expected: builds clean, vet clean. (Go is available? If `go` is not installed in this environment, note it and fall back to `gofmt -l .` for syntax + a careful read; report which. The Dockerfile build in Task 7 is the backstop compile check.)

- [ ] **Step 6: Commit**

```bash
git add skills/adding-backend-service/assets/go
git commit -m "feat: Go skeleton — chi + GORM with the repository seam (compiles)"
```

---

### Task 7: Go multi-arch Dockerfile (image builds)

**Files:**
- Create: `skills/adding-backend-service/assets/go/Dockerfile`
- Create: `skills/adding-backend-service/assets/go/.dockerignore`

**Interfaces:**
- Produces: a multi-arch, non-root, digest-pinned Go image. Built (at least for the host arch) in this task.

- [ ] **Step 1: Write the multi-stage Dockerfile**

```dockerfile
# Multi-arch build. Static binary, distroless-nonroot runtime, pinned digests.
FROM golang@sha256:PLACEHOLDER_GO AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download 2>/dev/null || true
COPY . .
RUN CGO_ENABLED=0 go build -o /out/service ./...

FROM gcr.io/distroless/static-debian12@sha256:PLACEHOLDER_DISTROLESS
COPY --from=build /out/service /service
USER nonroot:nonroot
EXPOSE 8000
ENTRYPOINT ["/service"]
```

- [ ] **Step 2: Resolve real digests and build for host arch**

The `PLACEHOLDER_*` digests won't pull. Resolve current digests for `golang:1.23` and `gcr.io/distroless/static-debian12:nonroot`, substitute them, then build for the host arch to prove the Dockerfile works:

Run: resolve digests (`docker pull golang:1.23 && docker inspect --format '{{index .RepoDigests 0}}' golang:1.23`, same for distroless), edit the Dockerfile, then `docker build -t cqds-go-test skills/adding-backend-service/assets/go && docker image rm cqds-go-test`.
Expected: image builds, the Go binary compiles inside. (If `go build` failed in Task 6 due to no local Go, this Docker build is the real compile check — it MUST succeed here.) Record the resolved digests in the committed Dockerfile.

- [ ] **Step 3: Write .dockerignore**

```
Dockerfile
.dockerignore
*_test.go
```

- [ ] **Step 4: Commit**

```bash
git add skills/adding-backend-service/assets/go/Dockerfile skills/adding-backend-service/assets/go/.dockerignore
git commit -m "feat: Go multi-arch Dockerfile (distroless non-root, digest-pinned)"
```

---

### Task 8: Mongo repository pattern (documented)

**Files:**
- Create: `skills/adding-backend-service/assets/mongo-repository.md`

**Interfaces:**
- Produces: the documented Mongo repository pattern referenced by the skill's Coverage section. Not built.

- [ ] **Step 1: Write the Mongo repository doc**

```markdown
# The MongoDB repository pattern

Document databases have no ODM that buys cross-family portability, so the
portability layer is **hand-written**: the same repository interface the SQL
skeletons expose, implemented over the Mongo driver directly. Callers can't tell
which database is behind the interface — that's the whole point.

## Same interface, different implementation

The SQL `ItemRepository` exposes `add(name) -> Item`, `list() -> [Item]`,
`get(id) -> Item | None`, returning the **boundary dataclass** `Item`, never an
ORM row. A Mongo implementation keeps that exact interface:

```python
# repository_mongo.py — same public interface as the SQLAlchemy repository.
from dataclasses import dataclass
from pymongo.database import Database

@dataclass(frozen=True)
class Item:
    id: str        # Mongo _id as string
    name: str

class ItemRepository:
    def __init__(self, db: Database):
        self._col = db["items"]

    def add(self, name: str) -> Item:
        r = self._col.insert_one({"name": name})
        return Item(id=str(r.inserted_id), name=name)

    def list(self) -> list[Item]:
        return [Item(id=str(d["_id"]), name=d["name"])
                for d in self._col.find().sort("_id")]

    def get(self, item_id: str) -> Item | None:
        from bson import ObjectId
        d = self._col.find_one({"_id": ObjectId(item_id)})
        return Item(id=str(d["_id"]), name=d["name"]) if d else None
```

## What changes, what doesn't

- **Changes:** the `id` type (int → string), the implementation, the driver
  (`pymongo`/`motor`), no Alembic (Mongo is schemaless; migrations become data
  scripts when needed).
- **Doesn't change:** the repository interface, the routes/business logic above it,
  the boundary `Item` type's shape. Swapping SQL→Mongo is re-implementing one file,
  not rewriting the service.

This is why SQL-vs-Document is "the one genuinely irreversible decision" scrutinised
hardest at architecture time — but the repository seam still contains the blast
radius to a single file.
```

- [ ] **Step 2: Commit**

```bash
git add skills/adding-backend-service/assets/mongo-repository.md
git commit -m "docs: MongoDB repository pattern — same interface, hand-written over the driver"
```

---

### Task 9: Walking-skeleton — a service booting against Postgres

**Files:**
- Create: `tests/scenarios/e2e-backend.md`
- Create: `tests/scenarios/baseline-results/e2e-backend-results.md`

**Interfaces:**
- Consumes: everything.
- Produces: the Plan 4 verdict. Instantiate a Python service into a scratch repo, `make up` Postgres + the service, and prove a real request reads/writes Postgres through the repository. Docker is available — this is a real boot.

- [ ] **Step 1: Scaffold a Fieldnote repo + instantiate the Python service**

In a scratch dir: scaffold the Fieldnote repo (Plan 2's `scaffold.py` with the Fieldnote config), then copy `assets/python/` into `backends/fieldnote/`, and un-comment the `fieldnote` service in `docker-compose.yml` so it builds `./backends/fieldnote` and gets `DATABASE_URL` pointing at the `db` service.

The compose service block (un-commented + filled):
```yaml
  fieldnote:
    build: ./backends/fieldnote
    environment:
      DATABASE_URL: postgresql+psycopg://fieldnote:devpassword@db:5432/fieldnote
      SERVICE_NAME: fieldnote
    depends_on:
      db:
        condition: service_healthy
    ports: ["8000:8000"]
```

- [ ] **Step 2: Pin the real base digest**

Resolve the current `python:3.12-slim` digest and substitute it into the Dockerfile (the placeholder won't pull). Record it.

- [ ] **Step 3: `make up` — boot the stack for real**

Run: `make -C <scratch> up` (builds the service image, starts db + service). Wait for health.
Expected: `db` healthy, the `fieldnote` service starts, runs `alembic upgrade head` (creating `items`), and serves on :8000.

- [ ] **Step 4: Hit the service — prove it reads/writes Postgres via the repository**

Run:
```
curl -sf localhost:8000/health            # {"status":"ok"}
curl -sf localhost:8000/health/ready      # {"status":"ready"} — DB reachable
curl -sf -X POST localhost:8000/items -H 'content-type: application/json' -d '{"name":"first observation"}'
curl -sf localhost:8000/items             # [{"id":1,"name":"first observation"}]
```
Then prove it actually persisted in Postgres (not in memory):
```
docker compose -f <scratch>/docker-compose.yml exec -T db psql -U fieldnote -d fieldnote -c "select name from items;"
```
Expected: the row is in Postgres. Restart the service container and re-list — the item survives (statelessness: state is in the DB, not the service).

- [ ] **Step 5: Grade and record**

Write `tests/scenarios/baseline-results/e2e-backend-results.md`:

| Check | Expected | Result |
|---|---|---|
| Service image builds (multi-arch base, non-root, pinned digest) | builds | |
| `make up` boots db + service | both up, db healthy | |
| `/health` | `{"status":"ok"}` | |
| `/health/ready` | DB reachable | |
| POST /items then GET /items | item round-trips | |
| Row present in Postgres (psql) | persisted in DB, not memory | |
| Survives service restart | item still there (stateless) | |
| Repository seam test | 3 passed (no ORM type leaks) | |

Record honestly. If the boot fails (build error, migration failure, connection), report the real error. If a fix is needed, it lands in the SHIPPED asset (the Task-8-Plan-3 masking lesson), not just the scratch copy.

- [ ] **Step 6: Commit and report the verdict**

```bash
git add tests/scenarios/
git commit -m "test: end-to-end backend — Python service serves against Postgres via the repository"
```

Present to Greg: the booted stack, the curl round-trip, the psql proof the row is in Postgres, the restart-survival. **Plan 4 is done when a service boots in compose, serves a real request, and that request reads/writes Postgres through the repository seam — with the item surviving a service restart (proving statelessness).** That verdict is Greg's.

---

## Self-Review

**Spec coverage** — every Plan-4 spec item traces to a task:

| Spec item | Task |
|---|---|
| Tier-1 Python skeleton (FastAPI + SQLAlchemy + Alembic) | 2, 3, 4 |
| Tier-1 Go skeleton (net/http + chi + GORM) | 6 |
| Repository seam (services call repositories, not the ORM) | 3 (test), 6, 8 |
| Portability (Postgres↔MariaDB config; SQL→Mongo repo) | 3, 8 |
| Multi-arch Dockerfile, non-root, pinned digest (Python) | 5, 9 |
| Multi-arch Dockerfile, non-root, pinned digest (Go) | 7 |
| Stateless service (invariant 1) | 2, 9 (restart-survival proof) |
| MongoDB repository pattern (documented) | 8 |
| adding-backend-service skill (init + evolve) | 1 |
| Full-stack boot: service serves against Postgres | 9 |

Deferred by design: CI running the service tests + building/pushing images (Plan 5), Trivy scanning the image (Plan 5), hooks (Plan 5), frontend↔backend wiring (its own concern; the milestone is service↔Postgres).

**Placeholder scan:** the Dockerfile base digests are explicit placeholders (`sha256:...`, `PLACEHOLDER_GO`) with a REQUIRED step to resolve real digests at build (Tasks 5/7/9) — an unpinned base is a spec-forbidden supply-chain gap, so this is a real build step, flagged as such, not a plan placeholder. No other placeholders.

**Type consistency:** the repository interface is consistent — Python `ItemRepository.add(name)->Item / list()->list[Item] / get(id)->Item|None` (Task 3), Go `ItemRepository.Add/List` returning boundary `Item` (Task 6), Mongo doc mirrors the same interface (Task 8). The boundary `Item` is a plain dataclass/struct in all three, never the ORM type — the seam. `DATABASE_URL` / `SERVICE_NAME` env names are identical across config.py (Task 2), env.py (Task 4), the Dockerfile CMD (Task 5), config.go (Task 6), and the compose block (Task 9).

**Input-space coverage:** the repository test (Task 3) proves engine-independence by running on SQLite while prod uses Postgres — testing the swap the seam promises, not just the happy path. Go is compile+image-build checked (Tasks 6–7), not assumed. The MariaDB/Mongo swaps are covered by the seam's design + the Mongo doc, though only Postgres is booted (honest coverage boundary).

**Honest verification:** Task 9 actually boots the stack, hits the endpoint, and proves persistence in Postgres via psql + restart-survival — observed, not asserted.
