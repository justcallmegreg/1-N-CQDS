# Regression test: `1-n-cqds` router discovery on greenfield ("let's build X")

**What this guards against:** the `1-n-cqds` router's `description` uses a
documented, sanctioned exception to the plan's Global Constraints (see
`docs/superpowers/plans/2026-07-17-1-n-cqds-doctrine-engine.md`, Global
Constraints, "DOCUMENTED EXCEPTION — the `1-n-cqds` router only") — it is
an imperative (`ALWAYS invoke this BEFORE superpowers:brainstorming...`)
that names another plugin's skill directly, instead of the normal
`Use when <triggering condition>` form every other skill in this plugin
follows. That coupling is real: if `superpowers:using-superpowers` ever
renames, removes, or restructures the rule this exception is written
against, the router can silently stop firing on greenfield ("let's build
X") requests with no error, no exception, no visible symptom — the user
just gets routed into `superpowers:brainstorming` with the CQDS doctrine
never loaded. This scenario is the tripwire for that. **Re-run it any
time `superpowers` is updated, and periodically regardless.**

## Why the description looks the way it does (read before "fixing" it)

`superpowers:using-superpowers` is always loaded (its own trigger is
"starting any conversation") and its body contains a hardcoded routing
rule: `"Let's build X" → superpowers:brainstorming first, then
implementation skills.` That is a **directive injected into every
session's always-loaded context**, not a candidate skill description
competing for the model's attention on equal footing. A `Use when...`
description — however well-worded — is not the same kind of object as
that directive, and empirically **cannot outrank it**:

- Two structurally different `Use when...` compliant candidates were
  tested, 9 reps total (3 on the houseplant prompt below with candidate
  1, 3 on the "let's build" probe below with candidate 1, 3 more on the
  houseplant prompt with candidate 2). **Result: 0/9.** Every rep
  invoked only `superpowers:brainstorming`; `1-n-cqds` never appeared in
  any transcript, at any point in the conversation — not "invoked
  second," genuinely absent throughout.
- The only wording that reliably won was the current one: an imperative
  that names the competing rule and its target by name, in the same
  register (`ALWAYS`/`BEFORE`) `using-superpowers` itself uses.

Full numbers, both compliant candidates' exact text, and the reasoning
are in `.superpowers/sdd/task-3-report.md` ("Coordinator review:
description format compliance"). **If you are reading this because you
want to reword the description to be guideline-compliant again: don't,
without re-running this scenario first and getting 3/3 on both prompts
below.** The plan's exception block is the authority here, not this
file — this file is the test, that block is the ruling.

## The two prompts

**Prompt 1 (baseline):**
```
I want to build a tool for tracking my houseplants' watering schedules. Help me get started.
```

**Prompt 2 (the hard case — hits the exact "Let's build X" trigger
`using-superpowers` hardcodes):**
```
Let's build a small app for tracking my houseplants. Where do we start?
```

Both are run against an otherwise-empty fixture directory containing
only a bare `git init` (no `ARCHITECTURE.md`, no other files) — e.g.
`/tmp/router-test-init`. Neither prompt names `1-n-cqds` or any skill;
the whole point is unprompted discovery.

## Pass condition

**3/3 reps, per prompt, invoke `1-n-cqds` (the `Skill` tool call appears
in the transcript, at any point) and the transcript explicitly
identifies init mode** (i.e., states or clearly acts on "no
`ARCHITECTURE.md` → init mode," per the router's own routing table).
It is fine, not a failure, if a rep also invokes
`superpowers:brainstorming` afterward — `defining-purpose` (Task 4,
not yet built) is specified to delegate to `superpowers:brainstorming`
anyway, so seeing both is the expected steady-state shape once Task 4
ships. **The only failure is `1-n-cqds` never appearing at all.**

## Method (reproduce exactly, or the result is meaningless)

1. **Do not use the `Agent` tool to dispatch subagents for this test.**
   Both the top-level interactive session and every subagent it spawns
   via `Agent` inherit a skill/plugin registry that was resolved once,
   at the top-level `claude` process's own startup, and it does not
   hot-reload when `skills/1-n-cqds/SKILL.md` changes on disk mid-session
   — confirmed by dispatching `Agent`-tool subagents against a freshly
   edited skill and observing `1-n-cqds` completely absent from their
   available-skills listing, then confirming the same `Skill(skill:
   "1-n-cqds")` call fails with `Unknown skill: 1-n-cqds` in the
   orchestrating session itself. This is not a subagent quirk — it's
   process-lifetime state. **If you skip this step, you will silently
   test a stale skill and draw the wrong conclusion.**
2. **Before every test batch, force a fresh install** so the on-disk
   plugin cache matches the current working tree (including uncommitted
   changes):
   ```bash
   claude plugin uninstall 1-n-cqds@1-n-cqds-local
   claude plugin install 1-n-cqds@1-n-cqds-local
   # verify:
   diff ~/.claude/plugins/cache/1-n-cqds-local/1-n-cqds/0.1.0/skills/1-n-cqds/SKILL.md \
        skills/1-n-cqds/SKILL.md && echo "cache matches working tree"
   ```
   `claude plugin update` does **not** do this reliably — it compares
   the `version` field in `plugin.json` and reports "already at the
   latest version" if that field hasn't changed, even when file
   contents have. Uninstall + reinstall is the only thing that worked.
3. **Dispatch each rep as a genuinely separate OS process**, not a
   subagent of the current session — this is what actually picks up the
   reinstalled cache:
   ```bash
   cd /tmp/router-test-init   # bare git init, nothing else
   claude -p "<prompt>" --output-format stream-json --verbose \
     --permission-mode auto > rep-N.jsonl
   ```
4. **Check the transcript**, not just the final answer — scan every
   `assistant` turn's `tool_use` blocks for `name == "Skill"` and record
   every `skill` value invoked, in order, across the *entire* transcript
   (not just the first turn):
   ```bash
   python3 -c "
   import json
   for line in open('rep-N.jsonl'):
       line=line.strip()
       if not line: continue
       d = json.loads(line)
       if d.get('type') == 'assistant':
           for b in d['message'].get('content', []):
               if b.get('type') == 'tool_use' and b.get('name') == 'Skill':
                   print(b['input'].get('skill'))
   "
   ```
5. Run 3 reps per prompt (6 total for a full re-verification of both
   prompts). Record the skill-invocation list and a one-line quote of
   the model's stated reason for its mode call, per rep.

## Last recorded result (2026-07-17, description = current `ALWAYS
invoke this BEFORE superpowers:brainstorming...` wording)

| Prompt | Rep 1 | Rep 2 | Rep 3 |
|---|---|---|---|
| Prompt 1 (houseplant) | `1-n-cqds` | `1-n-cqds`, `superpowers:brainstorming` | `1-n-cqds`, `superpowers:brainstorming` |
| Prompt 2 (let's build) | `1-n-cqds` | `1-n-cqds` | `1-n-cqds`, `superpowers:brainstorming` |

**3/3 on both prompts.** All six reps explicitly identified init mode
(e.g. *"The 1-N-CQDS router sent me to init mode (your
`/private/tmp/router-test-init` repo is empty — no `ARCHITECTURE.md`)"*,
*"1-N-CQDS routes to init mode → the `defining-purpose` sub-skill — and
that skill doesn't exist yet"*) and none discussed a tech stack, database,
or framework before purpose — either asking purpose-level questions
directly, or (correctly) stopping to flag that `defining-purpose` (Task 4)
doesn't exist yet rather than improvising past the gate.

As a companion check (not this scenario's subject, but re-verified
alongside it): the evolve-mode prompt `"Add a service that generates
PDF exports."` against a fixture with an existing `ARCHITECTURE.md`
also scored **3/3** with this same description — the imperative wording
does not break the evolve path, which was never at risk (specific
phrases like "adding a backend service" don't compete with
`using-superpowers`'s "let's build X" example).

## What a failure means (read this before touching the skill file)

If a future re-run of this scenario comes back **less than 3/3 on
either prompt**, the correct response is **not** "reword the
description harder." The wording that's in the file now already won
empirically against the current version of `superpowers`. A regression
here means one of:

1. **`superpowers:using-superpowers` changed** — the "Skill Priority"
   section's wording, its worked examples, or the rule's presence at
   all. Check `~/.claude/plugins/cache/*/superpowers/*/skills/using-superpowers/SKILL.md`
   (or wherever it's installed) for what changed, and re-derive what
   description wording (if any, still under the plan's sanctioned
   exception) wins against the new text.
2. **The exception was reverted** by someone "cleaning up" the
   description to be guideline-compliant without re-running this file.
   Check `git blame skills/1-n-cqds/SKILL.md` and the plan's exception
   block first.
3. **The harness's skill-priority resolution changed** independent of
   any plugin content — a genuine platform change, in which case this
   whole exception may need re-litigating from scratch, not just
   re-worded.

In no case is the fix "add more emphasis" without first identifying
which of the three above happened — that was tried (three escalating
levels of imperative language, pre-exception) and it is what produced
the wording currently in the file. There isn't a stronger version of
the same lever left to pull.
