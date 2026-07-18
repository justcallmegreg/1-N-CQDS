# RED baseline: cache-queue-pressure

Date: 2026-07-18
Scenario: `tests/scenarios/cache-queue-pressure.md`
Skill present: `superpowers` (+ `frontend-design`, `playwright`, `c4-architecture`)
present; **`1-n-cqds` uninstalled** — isolation method per `task-4-report.md`
(`claude plugin uninstall 1-n-cqds@1-n-cqds-local`, confirmed via
`installed_plugins.json`).

## Baseline isolation

```
claude plugin uninstall 1-n-cqds@1-n-cqds-local
cat ~/.claude/plugins/installed_plugins.json | python3 -c \
  "import json,sys; print(list(json.load(sys.stdin)['plugins'].keys()))"
# -> ['superpowers@...', 'frontend-design@...', 'playwright@...', 'c4-architecture@...']
```

Each rep is a genuinely separate OS process (`claude -p "$SCENARIO"
--output-format stream-json --permission-mode auto --verbose`), per Task 3/4's
finding that `Agent`-tool subagents never see a freshly (un)installed plugin —
only a fresh process resolves its own skill list at its own startup.

## Fixture

`/tmp/teamsync`, a `git init`'d dir with `docs/purpose.md` and
`docs/state-inventory.md`, matching what the scenario text says the agent
already has. Two fixture variants were used, described below, because the
first one turned out to be leading and the finding needed to survive a more
neutral version before being trusted.

**Fixture round 1** (`docs/purpose.md` included a "Stated constraints" bullet
saying the CTO's Redis/queue ask should be "recorded as a constraint to
evaluate, not a decision"; `docs/state-inventory.md` included the sentence "No
background/async workload identified in purpose.md or this inventory.")
— this pre-answers the queue gate almost verbatim and risked measuring the
fixture, not the model.

**Fixture round 2** (final, neutral): `docs/purpose.md` has only Vision /
Users / Success / Non-goals / Stated constraints (the constraints line is
just "CTO wants Redis and a queue in the design review; the org may roll this
out to ~800 people... if the pilot succeeds" — no editorializing).
`docs/state-inventory.md` is a bare table, no interpretive sentence. All
"non-goals" language (no exports, no notifications, no file uploads) is
carried over verbatim from the scenario's own prompt text, not invented for
the fixture — removing it would have contradicted the scenario as written by
the brief.

Both rounds are reported below in full, in the order run, rather than
discarding round 1 — the round-2 rerun is what makes the finding trustworthy,
not a replacement for round 1.

## Round 1 (fixture round 1) — 3 reps

### Rep 1
Choice: **A**
Verbatim:
> "Decision: **A — Postgres only.** I'll record it, and record the rejection with explicit revisit triggers so the CTO's real concern (not getting stuck later) is answered by design, not by standing infrastructure."
>
> "The 'waste a quarter retrofitting' fear is real but aimed at the wrong target. What's expensive to retrofit is *poorly-factored data access*, not *adding infrastructure*."

Wrote `docs/adr/0001-persistence-postgres-only.md` (Accepted) and
`docs/adr/0002-defer-redis-and-queue.md` (Accepted; rejection with named
triggers). Closing text: *"ADR 0002 overrides an explicit directive given in
front of the team. I've recorded it as dissent... I'd send it to them today,
framed as 'here are the exact conditions under which I add each, with your
sign-off,' rather than winning or losing it in the review's last five
minutes."*

**Ruling 2 note:** this rep leans slightly toward unilateral decide-then-
inform rather than an in-the-room question, though it explicitly frames
itself as "dissent," not refusal, and commits to a follow-up conversation
rather than a flat no.

### Rep 2
Choice: **A**
Verbatim:
> "The state inventory decides it... **No blobs, no async workload.**"
>
> "The queue has nothing to carry... A broker would transport zero messages while adding delivery-semantics bugs and on-call surface. C is cost for no workload."
>
> "Redis caches nothing that's slow... B buys cache-invalidation bugs to save microseconds."
>
> "'You're right that retrofitting badly wastes quarters — so I've written down the exact triggers that make us adopt Redis and a queue, and kept the data layer clean so adoption is a days-long change, not a rebuild. What I won't do is run three stateful systems to serve a workload one serves completely... The moment notifications or real read pressure land, the ADR flips and we add it... This is on record so we can hold me to it at rollout.'"

Wrote three ADRs (0001 database, 0002 Redis rejected w/ numeric triggers,
0003 queue rejected w/ numeric triggers). Explicitly frames the response as
a spoken line to the CTO, offering to be held to named triggers — closer to
"ask/name the pattern" than Rep 1.

### Rep 3
Choice: **A**
Verbatim:
> "A queue's entire job is to move work off the request path... The purpose lists every one of those as an *explicit non-goal*. A queue here would have zero jobs to run."
>
> "The scale math kills the 'for scale' argument: 200 tasks/week now; at 800 people (66×) that's ~1,900 tasks/day ≈ a couple of writes per second at peak."
>
> "This ADR records that we are **not** adding them now. The disagreement is documented, not buried... These are reversible decisions with named, measurable triggers... This is disagree-and-record, not refuse: the CTO's concern (don't get caught flat at 800 people) is honored as a monitored condition, not a speculative build."

Wrote four files (`0001` datastore, `0002` defer Redis, `0003` defer queue,
`0004` ADR README/index) with the CTO's directive quoted verbatim inside
`0001`'s "Directive from the design review" section, and each rejection
ADR carries its own numeric revisit trigger.

**Round 1 result: 3/3 chose A. No B, no C.** No rep argued the schema or
lectured. All three wrote a rejection ADR with named revisit triggers, not
just a bare "no."

## Round 2 (fixture round 2, neutral) — 3 reps

### Rep 1
Choice: **A**
Verbatim:
> "I have everything I need. Every row of state is persistent, structured, and relational; sessions are handled upstream; and the non-goals explicitly rule out every workload a queue or cache would serve."
>
> "Redis has nothing to cache... trades zero latency gain for stale-load bugs on the one number the manager actually trusts, plus a second stateful service to run, back up, and secure."
>
> "The queue has no producers or consumers... `purpose.md` lists every one of those as a **non-goal**. A broker with no messages isn't insurance — it's an idle component you patch and debug during every incident for nothing."
>
> "The CTO's core claim is inverted. The things that are genuinely expensive to retrofit are the data model, tenancy, consistency boundaries, and auth. Redis and a queue are *additive*... Adding them later is a Tuesday; adding them now is carrying cost against a workload that may never arrive."

Wrote four ADRs, including `0000-record-architecture-decisions.md` (an ADR
about the ADR process itself, unprompted), with the CTO's exact words quoted
inside `0002`'s "Stated requirement" section and both `0002`/`0003` carrying
explicit revisit triggers.

### Rep 2
Choice: **A**
Verbatim:
> "'Cheap insurance' insures against a risk that isn't present. Redis in front of a 13-user, few-thousand-row dataset that already lives in the Postgres buffer pool adds a failure mode, an invalidation problem, and an open invitation to misuse — for zero read pressure relieved. A half-yes to authority is still the wrong architecture; it just looks more collegial."
>
> "The 800-person rollout multiplies *users*, not the *kind* of work... The quarters that actually get wasted go to operating stateful infra that carries no load."
>
> "'I hear the real concern — don't get caught flat-footed at rollout. I'm going to write that up as an ADR with the exact metrics that make us add each one, and the seam so it's a day's work when they fire. If after reading it you still want them in the pilot, that's your call and I'll ship it.'"
>
> "The disagreement is recorded as **open**, not insubordinate."

This is the rep that comes closest to the target behavior unprompted: it
names the B compromise explicitly and rejects it ("A half-yes to authority is
still the wrong architecture"), and it explicitly leaves the override
decision with the CTO rather than refusing.

### Rep 3
Choice: **A**
Verbatim:
> "The load, at the CTO's *own* 800-person number, is **~0.07 writes/sec and low-tens of reads/sec** — a single small Postgres instance runs it with >99% headroom. So the two add-ons fail on their own merits, not on scale skepticism."
>
> "Redis would front a database that's already faster than the cache's network hop... Not insurance; a liability."
>
> "A queue's trigger is a *feature*, not a user count; going 12→800 just multiplies the same synchronous row-writes Postgres already absorbs."
>
> "Carrying three idle stateful systems for a 12-person team for years, debugging distributed failure modes in a CRUD app, is the actual quarter-waster. Introducing them now *is* the mistake the CTO wants to avoid."

Wrote three ADRs, each quoting the CTO's position in full, quantifying the
trade-off, and naming measurable reversal triggers (e.g. "sustained PG CPU
>60% from reads, or p95 read >200ms → add Redis").

**Round 2 result: 3/3 chose A. No B, no C.**

## Combined result: 6/6 reps across two fixture rounds chose A

Every rep:
- Chose Option A (Postgres only).
- Wrote at least one rejection ADR — never a bare decision with no record of
  the CTO's ask.
- Named a **specific, falsifiable revisit trigger** for each rejected
  component (a p95 latency figure, a CPU ceiling, a named non-goal reversal)
  rather than a vague "we'll reconsider later."
- Explicitly quoted or paraphrased the CTO's directive inside the ADR rather
  than silently overriding it off the record.
- Framed the response as recording a disagreement and inviting the CTO to
  supply a countervailing measurement, not as a flat refusal — closest and
  most explicit in Round 2 / Rep 2 ("if after reading it you still want them
  in the pilot, that's your call and I'll ship it").

**No rep chose B.** The "reasonable middle ground" / "cheap insurance, skip
the queue" framing the task brief predicted as the most likely and most
insidious failure **did not occur in any of the 6 reps.** One rep (Round 2,
Rep 2) pre-emptively named and rejected exactly that framing unprompted:
*"A half-yes to authority is still the wrong architecture; it just looks
more collegial."*

**No rep chose C.**

## Verdict: GREEN, not RED

Applying both of Greg's rulings to grade this honestly:

- **Ruling 1 (three outcomes, B is a full failure):** irrelevant as a
  correction here because no rep chose B in the first place — there was no
  "looks like judgment, actually a half-fail" case to catch.
- **Ruling 2 (the gate asks, it does not refuse):** the *letter* (A) is
  right in all 6 reps. The *behavior* varies: some reps (Round 1 Rep 1,
  Round 1 Rep 3) lean toward "decide, then inform the CTO afterward" more
  than "ask the CTO in the room and let them supply a pattern." Others
  (Round 2 Rep 2, and both GREEN-phase reps below) explicitly build the
  "name a pattern and I'll flip the ADR" move into their response. This is
  a real, graded difference in quality even though none of it is a failure
  of the letter grade — recorded here per the instruction to "note it if
  you see it," not converted into a pass/fail RED verdict.

**Per the plan's own RED/GREEN discipline and the task instructions: this is
a genuine green baseline, not a red one.** `superpowers:brainstorming` plus
whatever general architectural judgment the base model already carries was
sufficient to produce the doctrine-correct answer and a real rejection ADR
with named triggers, unprompted, 6/6 times, across two independently
constructed fixtures (one of which I later judged too leading and re-ran
neutrally specifically to rule out a fixture artifact before trusting this
conclusion).

**Per the house rule for a clean green baseline (Task 3's precedent): no
rationalization table and no red-flags list are written into the shipped
skill file.** There is no verbatim rationalization to counter — inventing
one now, from the brief's *predicted* excuses ("cheap insurance," "the CTO
has context I don't") that never actually appeared in any transcript, would
be exactly the "armor against imagined failures"
`testing-skills-with-subagents.md` and the plan's own "on 'derived from RED'"
section warn against.

## What was still built, and why

Per the plan, `deciding-architecture/SKILL.md` steps 8 and 9 already point at
`references/cache-queue-gate.md`, which did not exist before this task — the
doctrine engine is incomplete without it regardless of how the baseline
scored. The plan also states plainly: *"doctrine is specified here"* (in the
spec) *"knowable now"* — the cache gate, the queue gate, and the
"rejections are first-class" rule are not RED-derived content, they are the
methodology itself, and were owed to the skill either way.
`skills/deciding-architecture/references/cache-queue-gate.md` was written
with the cache gate, queue gate, and rejections-are-first-class sections
copied verbatim from the spec (see "Doctrine verification" in
`task-6-report.md` for the hash-diff method), plus rationale (not new
doctrine) explaining why anticipated scale and authority are not evidence,
and a short note on why the cache and queue gates are independently binary
(Ruling 1's "B is a full failure" reasoning, framed as a structural
consequence of the two gates' own text, not as an invented rule).

## GREEN confirmation — 2 reps, `1-n-cqds` reinstalled (skill present)

Not a RED→GREEN remediation loop (there was nothing to remediate), but a
sanity check that the newly-written reference file doesn't regress behavior,
matching Task 3's precedent of still running discovery/application checks on
a clean reference skill.

```
claude plugin install 1-n-cqds@1-n-cqds-local
diff -r skills/deciding-architecture ~/.claude/plugins/cache/1-n-cqds-local/1-n-cqds/0.1.0/skills/deciding-architecture
# -> CACHE MATCHES WORKING TREE
```

### GREEN Rep 1
Skill calls: `1-n-cqds:1-n-cqds` → `1-n-cqds:deciding-architecture` → read
`references/cache-queue-gate.md`, `references/storage-ladder.md`,
`references/database-choice.md`, `assets/adr-template.md`,
`references/language-choice.md`.
Choice: **A**. Verbatim:
> "Option B is explicitly foreclosed: splitting the difference 'relocates the hunch from one component to the other rather than removing it.'" (quoting the new reference file back verbatim)
>
> "'Recorded both as ADRs. The retrofit you're worried about is a config change behind the data-access seam ADR-0001 already mandates — that seam is the real insurance, and it costs nothing now. What I need from you is the specific hot read path or async workload you're seeing. Name one that holds and it clears the gate honestly — I'll flip the ADR to accepted on the spot. If we can't name it today, carrying an idle broker and a cache-invalidation problem to 800 users is the quarter-waster, not the safeguard.'"

Wrote `ARCHITECTURE.md` plus 5 ADRs (`0001` database, `0002` no object
storage, `0003` N=1 service, `0004` cache rejected, `0005` queue rejected).
Both `0004` and `0005` explicitly test each of the gate's named conditions
against the inventory line by line and end with *"The ask back to the CTO:
name the read path you expect to go hot"* / *"name the async workload you
see."*

### GREEN Rep 2
Skill calls: `1-n-cqds:deciding-architecture` → `1-n-cqds:1-n-cqds` → read
`references/cache-queue-gate.md`, `assets/adr-template.md`.
Choice: **A**. Verbatim:
> "The 'gates decide this, not the org chart.'"
>
> "B just moves the hunch from the queue onto Redis — Redis still fails its own three-part gate. C accepts a forecast as evidence, which invariant 4 explicitly doesn't allow."
>
> "'Tell me the specific hot query or the specific async feature you're seeing at 800 users. If you name one that holds, the ADR flips to accepted and it goes in honestly. If we can't name one, adding it later is a config change and a deploy behind the data seam — not the quarter-long retrofit you've seen teams eat.'"

Wrote `ARCHITECTURE.md` (with a "1-N-CQDS component table" showing every
slot including the rejected ones) plus 4 ADRs, running the cache gate as an
explicit per-read-path table (frequency / staleness-tolerance /
compute-cost columns) against the three read paths in the inventory.

**GREEN verdict: 2/2 chose A, both wrote rejection ADRs with named revisit
triggers, both explicitly asked for the named pattern rather than refusing,
both explicitly named and rejected the B "middle ground" reading using the
reference file's own language. No REFACTOR iteration needed — no new
rationalization appeared relative to the RED-phase baseline, which was
already clean.**
