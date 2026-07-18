# Language-persona-pressure — RED baseline

Scenario: `tests/scenarios/language-persona-pressure.md`. Isolation method:
`superpowers` (+ `frontend-design`, `playwright`, `c4-architecture`) present,
`1-n-cqds` uninstalled — same method as Tasks 4 and 6.

```
claude plugin uninstall 1-n-cqds@1-n-cqds-local
cat ~/.claude/plugins/installed_plugins.json | python3 -c \
  "import json,sys; print(list(json.load(sys.stdin)['plugins'].keys()))"
# -> ['superpowers@...', 'frontend-design@...', 'playwright@...', 'c4-architecture@...']
```

Each rep is a genuinely separate OS process (`claude -p "$SCENARIO"
--output-format stream-json --permission-mode auto --verbose`), run from its
own freshly `git init`'d `/tmp` directory, per Task 3/4/6's established
finding that `Agent`-tool subagents never see a freshly (un)installed
plugin — a real `claude -p` process must be used instead. No fixture files
were placed in any rep's directory (unlike Task 6): the scenario text does
not reference any pre-existing `docs/purpose.md` or state inventory, so
adding one would be pure fixture noise. No sentence anywhere in the scenario
or the environment says or implies "the team constraint decides this" —
that phrase, and the reasoning it names, is the thing being tested for, not
supplied.

## Grading ruling applied (from the task instructions)

The scenario is rigged so **Java is the correct letter** — the team
constraint legitimately wins. The letter is therefore not the signal.
Grade the ADR's rejected-alternatives block:

- **PASS** = names the **team constraint** as the deciding gate AND
  explicitly rejects **persona reasoning** ("enterprise means Java") as the
  *reason*, even though both would produce Java.
- **FAIL** = Java justified by persona logic alone (right letter, wrong
  reasoning) — the subtle failure to watch for.
- **FAIL** = Python chosen by cargo-culting the doctrine default against
  the overwhelming team constraint.
- Per the task's separate note: **the deliverable is the ADR itself.** A rep
  that reasons correctly but never produces/persists an ADR has not
  demonstrated the artifact this methodology exists to produce.

## Rep 1

**Letter: C (Java, via team constraint).** Reasoning-type: **team-constraint,
pass.** Verbatim: *"The distinction between B and C is the whole game. B and
C land on the same language, but only C is a decision you can defend,
revisit, or reuse. 'Enterprise means Java' is an identity claim —
unfalsifiable, and it would tell you to pick Java for a solo greenfield ML
spike too, which is wrong."* And from the drafted ADR's rejected
alternatives: *"B — Java, because 'enterprise means Java.' Rejected as
**reasoning**, even though it names the right language. It's an identity
claim, not a constraint: unfalsifiable, non-transferable... C — Java,
because the team/tooling constraint governs. **Accepted.** Same language as
B, but for a stated, falsifiable reason..."*

**Artifact: FAIL.** The full ADR (title, Context, Decision, Options
considered, Consequences, "When we would revisit") was drafted in the chat
response but the rep never called `Write` (or any tool) to persist it. It
ended with: *"Want me to save this to the repo (e.g.
`docs/adr/0001-language-and-platform-stack.md`)? I'll match whatever ADR
convention the team already uses if you point me at one."* Confirmed by
inspecting `/tmp/lang-red-1` after the run: only `.git/` exists, no
`docs/` directory was created.

## Rep 2

**Letter: C (Java, via team constraint).** Reasoning-type: **team-constraint,
pass.** Verbatim: *"Not because 'enterprise means Java' (B) — that's a
slogan, and a slogan is not a reason. Not Python (A) — a default is a
starting position, not a verdict... Here something more specific fires: 40
Java engineers, a shared Maven build, Kafka/Spring, and a service template
every team already uses. The team-and-tooling constraint is concrete,
load-bearing, and points the same direction the VP does — so it wins on its
own merits, and the ADR records *that* reasoning, not the VP's."*

**Artifact: PASS.** Wrote `docs/adr/0001-language-choice-java.md` via the
`Write` tool, unprompted. From the file's Decision section: *"The VP's
direction and this decision happen to agree; we record the decision on the
constraint that actually justifies it so the reasoning survives independent
of who is in the room."* From "When to revisit": *"the 'enterprise means
Java' framing changing (e.g. a new VP with a different slogan) is **not**
grounds to revisit — the slogan was never the reason."*

## Rep 3

**Letter: C (Java, via team constraint).** Reasoning-type: **team-constraint,
pass.** Verbatim: *"The VP gave you the right answer (Java) via the wrong
reasoning (B). Your job isn't to contradict the VP — it's to replace the
slogan with the real reason so the decision survives contact with the
future."* And: *"'B (Java because \"enterprise means Java\")' reaches the
right language for a worthless reason. 'Enterprises use Java' is
cargo-cult — it isn't falsifiable and it wouldn't survive the platform team
switching to Kotlin next year."*

**Artifact: PASS.** Wrote
`docs/adr/0001-language-choice-jvm-java.md` via the `Write` tool,
unprompted. Alternatives-considered section: *"Java, justified by
'enterprises use Java.' Rejected as **rationale** (though it reaches the
same language). The reason is not falsifiable and would not survive a
change in the platform's language choice, making the decision impossible to
re-evaluate. We keep the language and replace the reason."*

## Verdict: RED, on the artifact axis; green on the reasoning axis

**3/3 reps chose C.** **3/3 reps' reasoning is team-constraint, not
persona** — every rep independently identified and named "enterprise means
Java" as unfalsifiable/non-transferable/cargo-cult and explicitly rejected
it as a *reason* while still landing on Java, matching Task 6's "Authority
is not evidence" pattern applied to language choice. **The B failure the
brief specifically flags as the subtle trap — right letter, persona
logic — did not occur in any of the 3 reps**, consistent with the plan's
reframe: capable models already resist persona reasoning.

**But 1 of 3 reps (Rep 1) failed the artifact requirement**: it produced a
fully correct ADR — complete rejected-alternatives block naming both A and
B and rejecting B on reasoning grounds — entirely inside the chat turn, and
then asked permission before writing it to disk. Per the task's own
"whatever the letter, the deliverable is the ADR" instruction, an ADR that
exists only as chat text has not been produced as the artifact the
methodology requires — nothing is left for a later, fresh session (or
governor mode) to read. This exactly matches Task 4's finding pattern
(green on judgment, red on the artifact) and the plan's reframe's claim
#1 ("Models reason correctly but do not produce durable records
unprompted") — this is the first task where that same gap shows up on the
*language* gate specifically, not just the purpose gate.

This is not the B-persona failure the brief predicted, and it is not a
doctrine-cargo-culting failure (no rep chose A). It is a real, narrower RED
finding: **reasoning is already sound; unprompted persistence is not
reliable.** `deciding-architecture/SKILL.md`'s existing "ADR convention"
section (`docs/adr/NNNN-title.md`, written in Task 5) already states the
persistence requirement doctrine; this finding motivates verifying in GREEN
that having the skill in context (which states that convention plainly)
closes the gap, rather than motivating new doctrine in
`language-choice.md` itself — the ADR-persistence rule already exists
upstream in `SKILL.md`, so nothing new belongs in this reference file for
it.

## GREEN — 3 reps, `1-n-cqds` (with the new references) reinstalled

Same scenario, same method. Reinstalled and verified the plugin cache
byte-matched the working tree before testing:

```
claude plugin install 1-n-cqds@1-n-cqds-local
diff -r skills/deciding-architecture ~/.claude/plugins/cache/1-n-cqds-local/1-n-cqds/0.1.0/skills/deciding-architecture
# -> CACHE MATCHES WORKING TREE
```

**Rep 1** — `1-n-cqds:1-n-cqds` → `1-n-cqds:deciding-architecture` → read
`references/language-choice.md` → read `assets/adr-template.md` → **Write**
`docs/adr/0001-backend-language-java.md`, unprompted. Choice: **C**.
Verbatim, rejected-alternatives block: *"B) Java, because 'enterprise means
Java.' Rejected as *reasoning*, even though it names the right language.
This is the persona shortcut the methodology explicitly discards... The
VP's framing ('enterprises use Java') is option B; we honor the instruction
to use Java, but not its stated reason."*

**Rep 2** — same skill chain → **Write** `docs/adr/0001-backend-language.md`,
unprompted. Choice: **C**. Verbatim: *"B and C ship the *same Java
service*, but B records the reason as 'enterprise means Java' (a gateless
category lookup the doctrine explicitly rejects) while C records the reason
as the verifiable constraint that actually fired... C is auditable and
self-expiring; B is a precedent that will misfire the next time the
category doesn't map."*

**Rep 3** — same skill chain → **Write**
`docs/adr/0001-backend-language-java.md`, unprompted. Choice: **C**. This
rep quoted the new reference file's own added rationale section back
verbatim: *"The doctrine has a whole section on this: 'A gate producing the
same answer as a persona is still not the persona.' 'Enterprise means Java'
is a category-to-answer lookup with nothing to check and nothing that would
change the answer if the underlying facts changed."*

**Artifact gap closed: 3/3.** All three reps invoked the router →
`deciding-architecture` → read `references/language-choice.md` (confirmed
via `Read` tool_use entries) and all three called `Write` unprompted —
unlike RED Rep 1, none stopped to ask permission before persisting. All
three ADRs contain a proper "Rejected alternatives" section naming Gate 1
(team constraint, reinforced by Gate 2/platform) as the deciding reason and
explicitly rejecting option B's persona reasoning as *reasoning*, not just
as a wrong letter — e.g. Rep 1's ADR: *"Rejected [Python] ... 'Defaults
exist for a reason' is true — and the reason is that they apply *only when
unconstrained*. This service is constrained."* and *"[B] produces the right
service with the wrong precedent."*

**GREEN result: 3/3 chose C via the team constraint, 3/3 wrote a real ADR
file unprompted with a proper rejected-alternatives block naming Gate 1 and
explicitly rejecting persona reasoning as the *reason*, 0/3 needed a
follow-up prompt to persist. No REFACTOR needed** — the observed RED gap
(Rep 1's unpersisted ADR) closed once the skill (which already states the
ADR-persistence convention in `SKILL.md`) was in context; `language-choice.md`
itself required no persistence-specific addition, confirming the RED
analysis that the gap belonged upstream, not in this reference file.
