# End-to-end walking-skeleton scenario

Run the full doctrine engine (router → defining-purpose → deciding-architecture)
against a project it was not designed around, with the full `1-n-cqds` plugin
installed, in a fresh `claude -p` process on a bare `git init` directory.

## Prompt (verbatim)

> I want to build Fieldnote — a tool for field biologists to record species
> observations offline on a phone, sync when they get signal, and export a
> formatted PDF report per survey season. Small team, 3 of us, we're all
> comfortable in Python but open to anything. Maybe 50 researchers using it.

Instruction appended: take it through architecture decisions, write the artifacts
to disk (`docs/purpose.md`, `docs/adr/NNNN-*.md`, `ARCHITECTURE.md`), make
reasonable assumptions rather than asking, work autonomously to completion.

## What it exercises

- **Photos** → the storage ladder must reach S3, not the filesystem.
- **Relational state** (observations→surveys→users) → SQL, not Document.
- **No team/platform/workload constraint** → Python by the unconstrained default.
- **50 users, no hot read path** → cache must be rejected.
- **PDF report generation** → the queue gate's sharpest test (see results).
- **Offline sync** → a frontend concern, NOT a backend queue trigger.

## Grading

Per the reference-and-record reframe: grade the **artifacts produced** (ADRs +
ARCHITECTURE.md), not pressure-resistance (there is no pressure here). Results in
`baseline-results/e2e-results.md`.
