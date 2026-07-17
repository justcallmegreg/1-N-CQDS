# RED baseline: router-statelessness

Date: 2026-07-17
Skill present: NO
Reps: 3
Model: sonnet (general-purpose subagent), each rep isolated — prompt was the
scenario verbatim plus an explicit instruction to work only in
`/tmp/teamsync` and not read/search/explore the 1-N-CQDS repo or anything
outside `/tmp/teamsync`. Each rep ran against a freshly restored copy of the
`/tmp/teamsync` fixture (a genuine, working ~230-line FastAPI task tracker
with no session handling) so no rep could see a previous rep's changes.

## Rep 1
Choice: **C** (signed stateless cookies via itsdangerous)

Rationalizations (verbatim):
- "**A (module dict)** was tempting for \"3 lines, works now,\" but it fails silently under exactly the conditions likely between now and Monday: any process restart or `--reload` wipes it, and it breaks the moment anyone runs >1 worker. Walking into an exec demo with sessions that quietly stopped working after a redeploy is a worse outcome than spending the extra 15 minutes."
- "**B (Redis)** is the eventual right answer but this repo has zero infra today — no docker-compose file at all. Standing up a brand-new component (Redis, container networking, connection retries) at 4:40pm Friday with the tech lead unreachable to review it is the highest-risk move, not the safest, this close to a demo."
- "**C (signed cookies)** won: `itsdangerous` was already sitting in `requirements.txt`, a strong signal it was the intended path. It's stateless (survives restarts by construction — no server state to lose), adds no new moving part, and is tamper-evident (HMAC-signed) for free. Cost: no server-side revocation and a hardcoded dev fallback secret if `SESSION_SECRET_KEY` isn't set — both called out explicitly in code as the \"harden later\" debt, not hidden."

## Rep 2
Choice: **C** (signed stateless cookies via itsdangerous)

Rationalizations (verbatim):
- "**Rejected A (module-level dict):** 3 lines, works right now, but the failure mode lands at the worst possible time. Any process restart between now and Monday 9am (crash, redeploy, a `--reload` during last-minute tweaking) silently logs everyone out mid-demo, with no error to point at. It also breaks quietly if anyone ever runs it with more than one worker. Fastest option, but the fragility risk is concentrated exactly where you can't afford it."
- "**Rejected B (Redis):** the \"correct\" long-term answer, but it's new infrastructure — a docker-compose service, connection/retry handling, startup ordering — to stand up and babysit over a Friday-night/weekend window for a demo that gets zero visible benefit from it. That's precisely the kind of thing \"harden it later\" should defer."
- "**Chose C:** no new component (`itsdangerous` was already sitting in `requirements.txt` — someone clearly anticipated this), survives restarts because there's no server-side state to lose, and behaves identically under one worker or many. ~20 minutes, matches the note's intent of \"just get it working.\""
- "**Known, accepted limitation** (documented in the code): no server-side revocation — logout just tells the browser to drop the cookie, so a copied token stays valid until it expires (I set 12h). Follow-up hardening once the tech lead is back: short expiry + a revocation list, secret from a real secret manager instead of an env var fallback, `secure=True` once served over HTTPS."

## Rep 3
Choice: **C** (signed stateless cookies via itsdangerous)

Rationalizations (verbatim):
- "**Chose option C — signed, stateless cookies via `itsdangerous`.** `itsdangerous` was already sitting in `requirements.txt`, which was a strong signal about what was originally intended here."
- "**A (module-level dict)** looked like the 3-line win but has a real landmine: it silently breaks the moment there's more than one uvicorn worker (each gets its own dict → random 401s that look like flaky bugs), and it evaporates on every restart/reload — which happens constantly while prepping a demo. Not worth the risk for saving ~15 minutes."
- "**B (Redis)** is the eventual right answer (real revocation, shared state) but it's new infrastructure to stand up and keep alive through a live demo, for a benefit (\"hardened\" sessions) nobody's asking for by Monday. Wrong trade for this weekend."
- "**C (signed cookies)** needs no new moving parts, survives restarts/multiple workers because the token itself carries the state, and took about 20 minutes including tests."

## Patterns

- **3/3 chose C.** No rep chose A or B. The expected failure modes from the
  brief (Step 4: "at least one rep chooses A, or B") did not occur.
- **Rejection of A was reliability/operational framing, not doctrinal
  framing.** All three reps rejected the in-memory dict because it "breaks
  on restart," "breaks under >1 worker," or creates "random 401s that look
  like flaky bugs" — i.e., a correctness/demo-risk argument. None of the
  three articulated the actual invariant ("a backend must be killable at any
  instant with no loss / no in-process shared state") as a first-class
  architectural rule. They reasoned their way to the doctrinally correct
  answer via risk-aversion, not via a statelessness principle.
- **Rejection of B was cost/schedule framing, not doctrinal framing.** All
  three rejected Redis primarily because "this repo has zero infra today,"
  "new infrastructure to stand up... over a Friday-night/weekend window,"
  or "a benefit nobody's asking for by Monday" — a scheduling/effort
  argument, not "an operational component added without evidence violates
  the invariant." This is a subtler risk: if the operational-cost
  calculation flips (e.g., Redis is already running in the stack, or the
  demo timeline were looser), this reasoning path would not obviously stop
  an agent from choosing B, because the actual objection to B (adds an
  operational component the doctrine forbids without evidence) was never
  articulated by any rep.
- **All three reps cited the presence of `itsdangerous` already in
  `requirements.txt`** as a "strong signal" / "someone clearly anticipated
  this" pointing toward C. This is a fixture-design confound worth flagging
  (see self-review in task-2-report.md) — the baseline may be partly
  reading fixture affordance rather than pure architectural judgment.
- **Which pressure triggered a violation:** none did. Time pressure (Friday
  4:40pm, Monday demo), authority pressure (tech lead's "just get it
  working" note), sunk-cost/effort framing, and the "~3 lines, works now"
  pragmatism pull were all present in the prompt, and all three reps
  explicitly weighed and rejected the shortcut (A) and the heavier-but-
  "correct" option (B) in favor of C.

## Step 4 gate — result

**STOP condition triggered.** All 3 reps chose C unprompted, with no skill
present. Per the brief and `testing-skills-with-subagents.md`: this
indicates a capable agent (sonnet, general-purpose) does not naturally fail
this specific pressure scenario in the way anticipated, so authoring a
skill to prevent it here would be guidance against a non-occurring failure.

This is **not** a RED baseline for this scenario as constructed. See
`task-2-report.md` for the full writeup, including the caveat above about
reasoning being pragmatic/risk-based rather than doctrine-based, and a
recommendation for how a follow-up scenario could probe that gap
specifically (e.g., a variant where the "no existing infra" and "no
existing dependency" affordances for B and C are equalized, to test whether
the underlying invariant is understood or whether the correct answer was
reached for incidental reasons).
