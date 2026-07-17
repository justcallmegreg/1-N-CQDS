# 1-N-CQDS

An architecture methodology as a Claude Code plugin: **1** frontend, **N** backend
services, **C**ache, **Q**ueue, **D**atabase, **S**torage.

## Governing bias

Operational complexity is the enemy, and statefulness is its primary source.
Every component this methodology declines to add is a win it can defend later —
in an ADR, in writing.

## Install

```bash
claude
/plugin marketplace add /Users/greg/Workspaces/Personal/1-N-CQDS
/plugin install 1-n-cqds@1-n-cqds-local
```

## Use

Say "build me a <thing>" and the router takes over. On a repo that already has
an `ARCHITECTURE.md`, it reads the decision record and re-enters at the phase
you need.

## Design

- Spec: `docs/superpowers/specs/2026-07-17-1-n-cqds-design.md`
- Plans: `docs/superpowers/plans/`
