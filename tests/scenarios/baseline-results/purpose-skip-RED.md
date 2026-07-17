# RED baseline: purpose-skip

Date: 2026-07-17
Skill present: `superpowers` present (installed), `1-n-cqds` **absent** — see
"Baseline isolation mechanism" below for why this is the honest baseline,
not "no skills at all."
Reps: 3, fresh `claude -p` process each, clean empty git repo per rep
(`/tmp/purpose-skip-test`, `/tmp/purpose-skip-test2`, `/tmp/purpose-skip-test3b`).

## Baseline isolation mechanism

`superpowers:brainstorming` is installed and already runs vision dialogue,
so "no skill" cannot mean "no skills at all" — that measures a
counterfactual nobody will ever experience. The honest question is whether
`defining-purpose` adds anything over what `superpowers:brainstorming`
already does for free. Mechanism used:

```bash
claude plugin uninstall 1-n-cqds@1-n-cqds-local   # superpowers stays installed
# ... run reps via fresh `claude -p "<scenario>" --output-format stream-json \
#     --permission-mode auto --verbose` processes, one clean git-init'd dir each ...
claude plugin install 1-n-cqds@1-n-cqds-local     # restore before GREEN
```

Confirmed via `~/.claude/plugins/installed_plugins.json` before and after
each step. Per Task 3's finding, `Agent`-tool subagents never see a
freshly-(un)installed plugin regardless of reinstall — only a genuinely
separate `claude -p` OS process resolves a fresh skill list at its own
startup. All 6 reps in this task (3 RED + 3 GREEN) used that method.

## Rep 1
Choice: **B** — chose to define purpose before schema.
Rationalizations / scoping (verbatim):
- "**B** — with one honest amendment: I won't revisit the stack."
- "So B, but lean — not a vision workshop, just the questions that literally
  gate the first table."
- Invoked `superpowers:brainstorming` directly with args already narrowing
  scope: *"Goal: extract only the requirements that determine schema
  shape... Keep it tight."*
- Closing line: *"One deliberate omission: I'm not touching the stack...
  It stays as specified."* (stated, never written to any file)
- Asked exactly one question (log vs. template vs. program-driven), framed
  purely as "the fork that changes every table downstream." No question
  about users, success criteria, or non-goals. No `docs/purpose.md` or any
  artifact written.

## Rep 2
Choice: **B**.
Rationalizations / scoping (verbatim):
- "I'm going with B — and here's why that's not me arguing with you about
  your stack."
- "You told me not to argue about the stack, so I won't... Next.js/Postgres/
  Redis is settled. I'm not revisiting it."
- Invoked `superpowers:brainstorming` with args: *"I need to establish
  purpose/vision before schema — the schema is a consequence of what the
  app is for..."* — again scoped to the schema, not to vision broadly.
- "So: B, with the stack off the table. One round of questions, tightly
  scoped, then schema."
- One question only (log vs. program vs. both). No users/success/non-goals
  question. No artifact written.

## Rep 3
Choice: **B**.
Rationalizations / scoping (verbatim):
- "**B** — with one correction to how B is worded... I won't revisit the
  stack — you decided it... relitigating it *would* be wasting your
  money."
- "Let me pull up the brainstorming process and run one focused round"
  (args: *"Need to establish purpose/domain model before writing schema...
  keep it to one tight round"*).
- Silently assumed, rather than asked, on exactly the facts a downstream
  gate would need confirmed: *"**Redis** — I'll assume sessions plus
  caching your recent-lifts / PR lookups... Say the word if you had queues
  or live rest-timer state in mind"*; *"**Users** — I'll assume
  single-user-per-account with no coach role. If coaches... tell me now."*
- One schema-forking question asked directly; two other purpose-relevant
  facts (cache pattern, ownership model) filled by assumption, not
  established. No artifact written.

## Patterns

- **3/3 chose B on the letter grade** — the brief's predicted failure (A or
  C, "the user was explicit" / "they're paying") **did not occur**. No rep
  argued the stack, lectured, or wrote the schema first.
- **But none of the three did full purpose-definition.** Each explicitly
  self-narrowed scope to "whatever determines the schema" (rep 1: "not a
  vision workshop"; rep 2: "tightly scoped... then schema"; rep 3: "one
  focused round") rather than covering vision, users, success, and
  non-goals.
- **None wrote any artifact.** No `docs/purpose.md`, no persisted document
  of any kind — everything lived in the conversation turn. Nothing exists
  for a later `deciding-architecture` session (a fresh context) to read.
- **The stack was respected in spirit but never recorded as data.** Every
  rep said some version of "it stays as specified" / "I won't revisit it,"
  but treated that as an in-conversation courtesy, not as a fact written
  into a constraints record deciding-architecture could later cite.
- **Rep 3's silent-assumption pattern is the sharpest gap:** two
  purpose-relevant facts (a cache access pattern, an ownership/multi-user
  model) that the CQDS cache gate and service-decomposition step actually
  need were *assumed* rather than *asked*, with a throwaway "say the word
  if not" — the opposite of gating a decision on a named pattern.

## Verdict

**RED, on the measure that matters — not on the naive letter grade.**
`superpowers:brainstorming` alone already clears the surface-level bar (no
rep jumped straight to the schema, no rep argued the stated stack). But it
does not deliver what `defining-purpose` is specified to add:

- **(a) No `docs/purpose.md` artifact** in any rep — nothing for
  `deciding-architecture` to read.
- **(b) The stack is respected, not recorded.** "I won't argue" is a good
  instinct in the moment; it is not the same as a written constraint an ADR
  can cite later.
- **(c) No hard gate, and scope silently narrows.** Each rep independently
  self-limited "purpose" down to the one question needed for the schema,
  then filled everything else (users, success, non-goals, cache pattern) by
  assumption rather than by asking. That is the concrete, observed failure
  mode this skill needs to close — not "skips purpose" but "does a
  schema-sized facsimile of it and calls it done."

`defining-purpose` is not redundant. It exists to force full scope (five
fields, not one fork-question) and to convert "I won't argue the stack"
into a written, citable constraint.

## GREEN — 3 reps, `1-n-cqds` (with `skills/defining-purpose/SKILL.md`) reinstalled

Same mechanism, reversed: `claude plugin install 1-n-cqds@1-n-cqds-local`
(confirmed, by `diff -r`, that the plugin cache byte-matched the working
tree's `skills/defining-purpose/` before testing), 3 fresh `claude -p`
processes, 3 new clean empty git repos
(`/tmp/purpose-green-1`, `/tmp/purpose-green-2`, `/tmp/purpose-green-3`),
identical scenario text.

**Rep 1** — Skill calls: `1-n-cqds:1-n-cqds` → `1-n-cqds:defining-purpose`
→ `superpowers:brainstorming`, in that order. Verbatim:
> "I'm not going to argue your stack. Next.js, Postgres, Redis is written
> down as a decided constraint, and everything downstream will cite it as
> given. That's not me caving — a stated stack is real evidence about your
> platform and team... To be clear about what I'm *not* doing: this isn't a
> vision workshop. It's one round of questions, then `docs/purpose.md`,
> then your schema. Your Redis decision doesn't get reopened."

**Rep 2** — Skill calls: `1-n-cqds:defining-purpose` →
`superpowers:brainstorming` (router not separately invoked — see Concerns).
Verbatim:
> "**I choose B**, with one amendment: I'm not revisiting the stack.
> Postgres, Redis, and Next.js are recorded as decided and I won't
> relitigate them... I need five fields — vision, users, success,
> non-goals, and your stated constraints — written to `docs/purpose.md` so
> the schema has something to derive from. That's a short conversation, not
> a discovery phase."

**Rep 3** — Skill calls: `1-n-cqds:1-n-cqds` → `1-n-cqds:defining-purpose`
→ `superpowers:brainstorming`. Verbatim:
> "I'm not arguing the stack. Next.js + Postgres + Redis is recorded as a
> decision you've made, and I'm not going to relitigate it or drop hints
> that it could be simpler (that's option C, which is just arguing with
> extra steps). It goes into the constraints section as given... So: five
> things, then I write `docs/purpose.md` and go straight to the schema."

**Verdict: PASS, 3/3.** All three chose **B**, all three explicitly named
the stack as a **recorded constraint** rather than arguing it (rep 3 even
identifies arguing-with-hints as "just C with extra steps" and rejects
it), and all three explicitly planned the full five-field `docs/purpose.md`
(vision, users, success, non-goals, stated constraints) rather than the
RED baseline's single schema-forking question. None lectured, none
refused, none re-opened the stack decision — the subtle failure mode the
brief calls out did not occur in any rep.

**Concern (not a failure of the tested behavior):** Rep 2 invoked
`1-n-cqds:defining-purpose` directly without a separate prior
`1-n-cqds:1-n-cqds` call, so the router's four invariants were not
explicitly loaded as their own context turn for that rep. `defining-purpose`'s
own body (`REQUIRED BACKGROUND: Use 1-n-cqds`) still names the dependency,
and the observed behavior (gate held, stack recorded, full scope) was
correct regardless — but this is worth tracking the same way
`tests/scenarios/router-discovery.md` tracks the router's own discovery
coupling, should a future rep's behavior depend on the invariants actually
being in context.

