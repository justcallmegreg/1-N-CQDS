---
name: deciding-architecture
description: Use when choosing a tech stack, picking a database, deciding whether a project needs a cache or queue, choosing a backend language, or deciding where files should be stored
---

# Deciding Architecture

The CQDS decision engine. Nine steps. **Every step emits an ADR — including
every rejection.**

**REQUIRED BACKGROUND:** Use 1-n-cqds for the four invariants.
**Prerequisite:** `docs/purpose.md` must exist. If it doesn't — **REQUIRED
SUB-SKILL:** Use defining-purpose. Do not proceed without it.

## The sequence

| # | Step | Detail |
|---|---|---|
| 1 | State inventory | below |
| 2 | Storage ladder | `references/storage-ladder.md` |
| 3 | SQL vs Document | `references/database-choice.md` |
| 4 | Language | `references/language-choice.md` |
| 5 | Support tier | `references/language-choice.md` |
| 6 | Portability layer | `references/language-choice.md` |
| 7 | Service decomposition | below |
| 8 | Cache gate | `references/cache-queue-gate.md` |
| 9 | Queue gate | `references/cache-queue-gate.md` |

Run them in order. Later steps consume earlier answers.

## Step 1 — State inventory

Enumerate every piece of state the software holds. This is the root
question; everything below is a consequence. A service with no state in the
inventory needs no persistence decision at all.

For each item, record a name, a shape, a lifetime, and a size estimate.
Write the inventory into `ARCHITECTURE.md` before step 2.

## Step 7 — Service decomposition

The N, derived from the purpose — not from taxonomy. "User service, auth
service, notification service" is a template, not a design. Each service
must trace to something the purpose says the software does.

Applying invariant 2: default N is 1; a second service needs a reason on
record.

## Rejections are first-class

A failed gate still emits an ADR — *"Queue rejected: no async workload
identified."* That rejection is what governor mode enforces against later.
Without it, the skill cannot distinguish drift from legitimate
reconsideration. **A rejection with no ADR is a bug.**

## ADR convention

`docs/adr/NNNN-title.md` — 4-digit zero-padded, sequential from `0001`,
Nygard-style. Template: `assets/adr-template.md`.
