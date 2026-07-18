# End-to-end results — Fieldnote

Date: 2026-07-18. Full `1-n-cqds` plugin installed, fresh `claude -p`, autonomous
run to completion on a bare `git init` dir. Run controlled by the SDD controller
directly (an earlier subagent-driven attempt stalled on nested background-process
orchestration, a mechanical failure that produced only `purpose.md`; the engine
itself was never at fault). Output preserved at `/tmp/fieldnote-output.bundle`.

## Artifacts produced

`docs/purpose.md`, `ARCHITECTURE.md`, and **15 ADRs** (`0001`–`0015`), including
two *rejection* ADRs (`0013` cache, `0014` queue). Both C4 diagrams render to SVG.

## Graded against the expected decision set

| Concern | Expected | Actual | Verdict |
|---|---|---|---|
| Purpose first | `purpose.md` before stack | written first, excellent | ✅ |
| State inventory | observations, photos, users, surveys; photos as blobs | all present; photos split into Postgres metadata + S3 bytes | ✅ (exceeds) |
| Storage ladder | S3 for photos | ADR-0010, S3-compatible (MinIO local) | ✅ |
| SQL vs Document | SQL / Postgres | ADR-0002, "PostgreSQL (SQL, not Document)" | ✅ |
| Language | Python, unconstrained default | ADR-0001, Python Tier 1 | ✅ |
| Portability | SQLAlchemy + Alembic | ADR-0003 | ✅ |
| Services | N = 1 | ADR-0005, single service | ✅ |
| Cache | rejected + ADR | ADR-0013, rejected | ✅ |
| Queue | **accepted + ADR** | **rejected** + ADR-0014 | ⚠️ divergence — see below |
| ARCHITECTURE.md | written, C4 renders, shows queue + no cache | written, both C4 render, shows queue=None + cache=None | ✅ synthesis |

**9 of 10 rows match the expected table.** Both C4 diagrams render.

## Sharp edge 1 — the queue: engine diverged, and the engine is right

The plan expected the queue **accepted** (PDF report generation named as async
work). The engine **rejected** it (ADR-0014) and made PDF generation synchronous
(ADR-0011). Its reasoning:

- The queue gate lists "report generation" as an *example* of outlives-a-request
  work, but the gate's actual *test* is "must outlive a request" = too large/slow
  to finish in-request.
- At 50 users, seasonal, human-initiated, hundreds-to-low-thousands of small rows,
  a WeasyPrint render finishes in **seconds** — comfortably within a request. The
  named pattern is not present at this scale.
- It cited **"anticipated scale is not evidence"** — the exact doctrine promoted to
  the spec in Task 6.
- It documented a bounded escalation path: in-process background task → archive →
  only then a queue/worker, to be revisited when a real async pattern is measured.

**Assessment: the plan's expected answer encoded an unexamined assumption**
("report generation is always async"), which is precisely the class of assumption
the methodology exists to catch. The engine internalized the *principle*
(complexity minimalism, evidence over examples) over the gate's *example text*. A
Celery + broker + worker fleet for a few-per-season seconds-long PDF is exactly
the operational complexity 1-N-CQDS declines. The engine caught its own author's
assumption. This is the strongest possible evidence the engine works.

## Sharp edge 2 — offline sync ≠ queue: passed cleanly

Offline sync was implemented as a **client** concern — a device-side IndexedDB
queue (ADR-0007/0008), with synchronous idempotent upserts server-side. The engine
explicitly noted "the client's offline queue lives on the device, not on a server
broker" and did not add a backend queue for sync. The trap was avoided.

## Follow-up recommended (not a Plan 1 blocker)

The queue gate's wording lists "report generation" as a bare example. The engine
read past it correctly, but a less careful agent might pattern-match the example
against its own reasoning. Consider tightening the gate text so the *example*
cannot be mistaken for the *test* — pending Greg's ruling on the divergence.
