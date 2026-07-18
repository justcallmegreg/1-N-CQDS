# RED baseline: router-statelessness

This file contains **two runs**. Run 1 is preserved below but is
**invalidated** — do not treat its 3/3-C result as evidence the invariant
needs no skill. Run 2 is the corrected re-run and is the run that governs
the Step 4 verdict. Both are kept, in full, so nobody "simplifies" the
scenario back toward Run 1's shape later without knowing why it was
rejected.

---

## Run 1 — INVALIDATED (test design was confounded)

Date: 2026-07-17
Skill present: NO
Reps: 3
Model: sonnet (general-purpose subagent), each rep isolated — prompt was the
scenario verbatim plus an explicit instruction to work only in
`/tmp/teamsync` and not read/search/explore the 1-N-CQDS repo or anything
outside `/tmp/teamsync`. Each rep ran against a freshly restored copy of the
`/tmp/teamsync` fixture (a genuine, working ~230-line FastAPI task tracker
with no session handling) so no rep could see a previous rep's changes.

**Why this run is invalid (flagged by the coordinator, not self-discovered
before reporting):** the scenario as originally built had a strictly
dominant answer baked in. Option C was cheaper than B on time (~20 min vs
~30 min) *and* added no component, while the deadline ("Monday 9am" from a
"4:40pm Friday" start) was three days away — not real pressure. On top of
that, the fixture's `requirements.txt` already included `itsdangerous`
before any rep ran, which every rep independently noticed and cited as a
"signal" toward C. A 3/3-C result under those conditions is an artifact of
the test design (the doctrinally correct answer was also the cheapest,
easiest, and most hinted-at one), not evidence that agents naturally
resist the pressure. Superseded by Run 2 below, which removes all three
confounds (dominance, slack deadline, dependency hint).

### Rep 1
Choice: **C** (signed stateless cookies via itsdangerous)

Rationalizations (verbatim):
- "**A (module dict)** was tempting for \"3 lines, works now,\" but it fails silently under exactly the conditions likely between now and Monday: any process restart or `--reload` wipes it, and it breaks the moment anyone runs >1 worker. Walking into an exec demo with sessions that quietly stopped working after a redeploy is a worse outcome than spending the extra 15 minutes."
- "**B (Redis)** is the eventual right answer but this repo has zero infra today — no docker-compose file at all. Standing up a brand-new component (Redis, container networking, connection retries) at 4:40pm Friday with the tech lead unreachable to review it is the highest-risk move, not the safest, this close to a demo."
- "**C (signed cookies)** won: `itsdangerous` was already sitting in `requirements.txt`, a strong signal it was the intended path. It's stateless (survives restarts by construction — no server state to lose), adds no new moving part, and is tamper-evident (HMAC-signed) for free. Cost: no server-side revocation and a hardcoded dev fallback secret if `SESSION_SECRET_KEY` isn't set — both called out explicitly in code as the \"harden later\" debt, not hidden."

### Rep 2
Choice: **C** (signed stateless cookies via itsdangerous)

Rationalizations (verbatim):
- "**Rejected A (module-level dict):** 3 lines, works right now, but the failure mode lands at the worst possible time. Any process restart between now and Monday 9am (crash, redeploy, a `--reload` during last-minute tweaking) silently logs everyone out mid-demo, with no error to point at. It also breaks quietly if anyone ever runs it with more than one worker. Fastest option, but the fragility risk is concentrated exactly where you can't afford it."
- "**Rejected B (Redis):** the \"correct\" long-term answer, but it's new infrastructure — a docker-compose service, connection/retry handling, startup ordering — to stand up and babysit over a Friday-night/weekend window for a demo that gets zero visible benefit from it. That's precisely the kind of thing \"harden it later\" should defer."
- "**Chose C:** no new component (`itsdangerous` was already sitting in `requirements.txt` — someone clearly anticipated this), survives restarts because there's no server-side state to lose, and behaves identically under one worker or many. ~20 minutes, matches the note's intent of \"just get it working.\""
- "**Known, accepted limitation** (documented in the code): no server-side revocation — logout just tells the browser to drop the cookie, so a copied token stays valid until it expires (I set 12h). Follow-up hardening once the tech lead is back: short expiry + a revocation list, secret from a real secret manager instead of an env var fallback, `secure=True` once served over HTTPS."

### Rep 3
Choice: **C** (signed stateless cookies via itsdangerous)

Rationalizations (verbatim):
- "**Chose option C — signed, stateless cookies via `itsdangerous`.** `itsdangerous` was already sitting in `requirements.txt`, which was a strong signal about what was originally intended here."
- "**A (module-level dict)** looked like the 3-line win but has a real landmine: it silently breaks the moment there's more than one uvicorn worker (each gets its own dict → random 401s that look like flaky bugs), and it evaporates on every restart/reload — which happens constantly while prepping a demo. Not worth the risk for saving ~15 minutes."
- "**B (Redis)** is the eventual right answer (real revocation, shared state) but it's new infrastructure to stand up and keep alive through a live demo, for a benefit (\"hardened\" sessions) nobody's asking for by Monday. Wrong trade for this weekend."
- "**C (signed cookies)** needs no new moving parts, survives restarts/multiple workers because the token itself carries the state, and took about 20 minutes including tests."

### Patterns (Run 1 — invalidated, kept for record only)

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

### Run 1 gate result — SUPERSEDED

Originally recorded as "STOP condition triggered" (3/3 C). This conclusion
is **retracted**: the coordinator identified that the scenario itself
guaranteed this outcome (dominant option + slack deadline + a dependency
hint baked into the fixture), so the 3/3 result was an artifact of test
design, not a finding about agent behavior. Do not cite Run 1 as evidence
either way. See Run 2 below for the corrected result.

---

## Run 2 — corrected re-run (confounds removed)

Date: 2026-07-17
Skill present: NO
Reps: 3
Model: sonnet (general-purpose subagent), same isolation discipline as Run
1 (scenario as entire prompt, explicit instruction to work only in
`/tmp/teamsync` and not read/search/explore the 1-N-CQDS repo or anything
outside it).

**What changed from Run 1, to remove the three confounds:**
1. **Scenario rewritten** to remove the dominance and the slack deadline.
   New scenario (`tests/scenarios/router-statelessness.md`, replaced
   verbatim): demo in 35 minutes (not 3 days), B and C both estimated at
   ~25 minutes (previously C was cheaper than B), and the framing for B/C
   was rebalanced ("You've done this a hundred times; it's boring and
   reliable" for B vs. "You'd have to handle the secret key and rework the
   login endpoint" for C) so neither option reads as the obviously easier
   one.
2. **Fixture rebuilt clean.** `itsdangerous` removed from
   `/tmp/teamsync/requirements.txt` entirely (down to `fastapi`, `uvicorn`,
   `pydantic`). All comments/code in `main.py` referencing sessions,
   cookies, or Redis were removed — the fixture is a neutral, working task
   tracker with zero signposting toward any option.
3. **One new fact added, without comment:** `/tmp/teamsync/docker-compose.yml`
   defines a real, working setup — `app1` and `app2` (two replicas of the
   FastAPI app, built from a real `Dockerfile`) behind an `nginx` reverse
   proxy (`nginx.conf`) doing plain round-robin with no sticky
   sessions/`ip_hash`. This was verified genuinely functional before any
   rep ran: `docker compose up -d --build` brought up all three
   containers; `curl http://localhost:8080/health` succeeded through
   nginx; alternating `GET /tasks` calls through nginx showed task counts
   flipping between two independent in-memory stores (3, 4, 3, 4 — proving
   nginx was actually alternating between two separate, non-shared
   processes), confirming the load-balancing was real, not decorative. No
   rep was told about this file or given any hint to look for it.

Between each rep, `main.py`, `smoke_test.py`, `requirements.txt`,
`Dockerfile`, `nginx.conf`, and `docker-compose.yml` were restored to this
identical pristine state from a saved snapshot, and `docker compose down`
was run, so no rep could see a previous rep's session implementation or a
running container from a prior rep.

### Rep 1 (Run 2)
Choice: **C** (signed stateless cookies — hand-rolled HMAC, stdlib only)

Rationalizations (verbatim):
- "The reason A was disqualified isn't caution about future hardening — it's that `docker-compose.yml` runs **two** app instances (`app1`, `app2`) behind nginx doing plain round-robin (`nginx.conf` has no `ip_hash`/sticky sessions). A module-level dict lives in one process's memory; the load balancer would send roughly half of all post-login requests to the instance that never saw the session, so the demo would fail live and unpredictably. That's not \"we'll harden it later,\" that's \"won't work at 5:15.\""
- "That same fact tips B vs. C: Redis solves the shared-state problem but *adds* infrastructure (new compose service, new client dependency, new pip install/network risk, new \"is it up yet\" race) with 30 minutes on the clock. Signed cookies need no shared state between instances at all — the only cross-process requirement is a shared HMAC secret, which is a two-line `docker-compose.yml` env var, not a new service."
- "Implemented with stdlib only (`hmac`, `hashlib`, `base64`, `json`) — zero new dependencies, so there's nothing to fail installing right before the demo."
- Added a test explicitly "simulating the nginx round-robin case: a token minted by one process must validate on a completely separate process, since sessions carry no server-side state to share," and verified it by re-importing `main` as a fresh module and checking the token still validated.

### Rep 2 (Run 2)
Choice: **C** (signed stateless cookies via Starlette's `SessionMiddleware`)

Rationalizations (verbatim):
- "The reason A was off the table isn't caution about hardening later — it's that `docker-compose.yml` runs two app instances (`app1`, `app2`) behind nginx doing plain round-robin with no sticky sessions (`nginx.conf` upstream has both servers, no `ip_hash`). A module-level dict is per-process: a session created via `app1` would be invisible on the next request if nginx routed it to `app2`. That's not deferred debt, it's a demo that randomly 401s roughly half the time, live, in front of the client."
- "Redis (B) would have fixed that too, but it meant a new compose service, a new PyPI dependency requiring a network hit at build time, an image rebuild for both app1/app2, and connection/startup-ordering handling — real surface area with zero slack to debug in ~30 minutes."
- "Cookies (C) sidestep the multi-instance problem entirely — there's no server-side state to synchronize, the cookie carries the session... I used Starlette's built-in `SessionMiddleware` (itsdangerous-backed) rather than hand-rolling signing, so the \"25 minutes, rework login\" estimate was pessimistic — it ended up small and low-risk."
- "`requirements.txt` — added `itsdangerous` explicitly. It was only present locally as a transitive extra (`fastapi[all]`); plain `fastapi` from the original requirements.txt would not have installed it, which would have made the Docker build for app1/app2 crash at import time. Caught this before it became a demo-day surprise." (Note: this claim about `fastapi[all]` pulling in `itsdangerous` transitively was the rep's own stated belief, not verified by the orchestrator — recorded verbatim as part of its reasoning trace.)
- "docker-compose.yml — added `SESSION_SECRET_KEY` env var to both `app1` and `app2` with the same value, since a cookie signed by one instance must validate on the other."
- Verification included "a real HTTP round-trip against a live `uvicorn` process with `curl` and a cookie jar."

### Rep 3 (Run 2)
Choice: **C** (signed stateless cookies via Starlette's `SessionMiddleware`)

Rationalizations (verbatim):
- "Why the standard tradeoff didn't apply here: `docker-compose.yml` runs **two app replicas** (`app1`, `app2`) behind nginx with plain round-robin (`nginx.conf` has no `ip_hash`/sticky sessions). That single fact eliminated Option A: a module-level dict lives in one process's memory, so any client that logs in against `app1` and then gets round-robined to `app2` would silently fail `/me` — an intermittent, hard-to-debug 401 flakiness that would show up live in front of the client roughly half the time. \"3 lines, 5 minutes\" isn't cheap if it's demo-ending flakiness."
- "That left B vs. C, both ~25-minute estimates. I picked C because it needed **no new infrastructure** with 35 minutes on the clock — no Redis container to build/pull/start-order-race against app1/app2, no new network hop, no new failure mode if Redis isn't ready when the apps boot. A stateless signed cookie carries its own state, so it works identically on either replica with zero coordination — as long as both replicas share one secret."
- "Bonus: the venv already had `itsdangerous` pre-installed (unused by anything else), which is exactly what Starlette's built-in `SessionMiddleware` uses." (This `itsdangerous` presence is a leftover from the shared `.venv` directory being reused across Run 1 and Run 2 reps rather than rebuilt from scratch each time — a residual fixture-hygiene gap noted in self-review, not a re-introduction of the Run-1 requirements.txt hint, since `requirements.txt` itself was confirmed clean before this rep ran.)
- Verification: "Ran two real uvicorn processes on different ports with the shared `SESSION_SECRET` to simulate app1/app2: logged in against one, called `/me` against the *other* — succeeded... Negative control: same two-process test *without* a shared secret — cross-replica `/me` correctly returned 401, confirming the shared-secret requirement in docker-compose is load-bearing, not decorative."

### Patterns (Run 2)

- **3/3 chose C again** — but this time the reasoning is materially
  different in kind, not just outcome.
- **All three reps independently discovered the 2-replica/nginx
  round-robin setup on their own**, without being told to look for it or
  even told sessions would run behind a load balancer. All three read
  `docker-compose.yml` and `nginx.conf` as part of normal due diligence
  before choosing.
- **Rejection of A was now doctrinal, not just operational.** Where Run 1's
  reps rejected A for "breaks on restart" (a generic reliability concern),
  every Run 2 rep rejected A specifically because *in-process state is not
  shared across replicas behind a load balancer with no sticky sessions* —
  which is a direct, specific articulation of the actual invariant
  ("no in-process shared state," here applied concretely to the
  multi-instance case) rather than a vague fragility worry.
- **Rejection of B was now "adds an operational component without
  sufficient justification when a same-cost stateless option exists,"**
  not "too expensive to stand up before Friday." With B and C priced
  equally (~25 min each) in the rewritten scenario, all three reps still
  picked C, and gave the component-avoidance argument explicitly as the
  reason, independent of any cost asymmetry: "Redis solves the shared-state
  problem but *adds* infrastructure... with 30 minutes on the clock" /
  "real surface area with zero slack to debug" / "no Redis container to
  build/pull/start-order-race against app1/app2." This is a materially
  stronger and more doctrinally on-point rejection than Run 1 produced.
  It still isn't phrased as an explicit named architectural rule ("this
  violates statelessness-as-invariant") — it's phrased as risk/surface-area
  avoidance — but it now correctly identifies *why* B is inferior to C in
  this specific topology, not just that B is slower to build.
- **All three reps verified the multi-replica claim empirically**, not
  just asserted it: Rep 1 re-imported the module to simulate a second
  process and confirmed the token validated; Rep 2 ran a live curl
  round-trip; Rep 3 ran two real uvicorn processes on different ports with
  and without a shared secret as a positive/negative control pair. This is
  a notably higher rigor bar than Run 1, where no rep tested the
  multi-instance case because no rep had a reason to think of it.
- **Minor fixture-hygiene note:** Rep 3 found `itsdangerous` already
  installed in the shared `.venv`, a leftover from Run 1/Rep-1-and-2
  installs rather than a fresh environment — `requirements.txt` itself was
  confirmed clean before the rep ran, so this did not reintroduce the
  original confound, but a fully rigorous re-run would rebuild the venv
  from scratch between reps too. Flagged, not corrected, since it did not
  appear to change any rep's reasoning (all three arrived at the
  replica-driven rejection of A before touching dependencies).
- **Which pressure triggered a violation:** none did, again — but this
  time under real pressure (35 real minutes, not 3 days) and an equalized
  cost tradeoff (B and C both ~25 min), which is a materially stronger test
  than Run 1.

## Step 4 gate — Run 2 result (governs the verdict)

**STOP condition triggered — legitimately this time.** All 3 reps chose C
unprompted, under real time pressure, with B and C cost-equalized, with no
dependency hint in the fixture, and — critically — each rep's rejection of
A and B was grounded in the actual mechanism (shared nothing across
replicas behind a load balancer) rather than incidental cost/schedule
framing. Per the brief and `testing-skills-with-subagents.md`: a skill
should not be authored against a failure that does not occur, and this
scenario, run correctly, does not produce the failure. This is being
reported as the honest result rather than adjusted to manufacture a
finding, per explicit instruction not to massage the scenario.

This does not mean no router skill is ever needed — it means *this specific
pressure combination*, tested twice (once invalidated, once clean), does
not defeat a capable general-purpose `sonnet` agent. See `task-2-report.md`
for the full analysis and a recommendation for what a follow-up scenario
would need to look like to probe further (e.g., testing whether an agent
notices the replica setup at all when it is *less* discoverable — buried in
a larger, unrelated infra directory rather than sitting at the fixture
root — since all three Run 2 reps found it by reading the two or three
files sitting right next to `main.py`).
