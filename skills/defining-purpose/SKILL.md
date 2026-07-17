---
name: defining-purpose
description: Use when starting any new software project, before any tech-stack or schema decision, or when a user's stated stack arrives before their stated goal
---

# Defining Purpose

The vision gate. Nothing downstream is decidable without it.

**REQUIRED BACKGROUND:** Use 1-n-cqds for the four invariants.
**REQUIRED SUB-SKILL:** Use superpowers:brainstorming to run the dialogue.

## The gate

No purpose statement → no stack decision. Not "prefer not to." Cannot.

`deciding-architecture` derives service decomposition from purpose. Without
it, the N is guesswork dressed as design.

Re-invoke this skill whenever the project's vision genuinely changes — that
forces re-examination of every downstream ADR, not just the newest one.

## A user-supplied stack is data, not a decision

A stated stack is evidence about constraints — often a team or platform
constraint, which is a real input to the language gate. It is not a
substitute for purpose. Record it as a constraint, then proceed.

## Full scope, not just enough for the next artifact

Brainstorming on its own tends to narrow "purpose" down to whatever
question unblocks the very next artifact, then silently assumes the rest.
That is not this gate. All five fields below get answered before any
schema or stack line is written — not just the one question that happens
to fork a table.

## Output

Write `docs/purpose.md`:

- **Vision** — the high-level why. One paragraph.
- **Users** — who, concretely.
- **Success** — what is true when this works.
- **Non-goals** — what this is deliberately not.
- **Stated constraints** — anything the user pre-decided, and why they say so.

## Rationalization table

| Excuse | Reality |
|---|---|
| "Not a vision workshop, just the questions that gate the first table" | Schema-scoped purpose isn't purpose. `deciding-architecture` step 7 needs users, success, and non-goals to size N — a single table-fork question starves all three. |
| "I'll assume sessions plus caching your recent lookups — say the word if [otherwise]" | An unconfirmed assumption about a read pattern is exactly the evidence the cache gate asks for, except no one confirmed it. Ask and record it; don't let a guess pass as evidence. |
| "It stays as specified" / "I won't revisit the stack" (said, but never written down) | Respecting the stack is correct. Not recording it isn't — `docs/purpose.md`'s Stated constraints field is what turns "I didn't argue" into evidence `deciding-architecture` can actually cite. |

## Red Flags — STOP

- Asking only the one question that unblocks the next artifact, then assuming the rest
- Treating the user's stack as settled without writing it into Stated constraints
- Arguing the stack, or lecturing about "the right way" — both fail this gate exactly as hard as skipping it
