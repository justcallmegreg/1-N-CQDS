# Language — constraint gates, not personas

Language choice is an organizational decision, not a technical one. It is decided by **named constraints**, evaluated in order:

1. **Team constraint** — who maintains this in three years? *An existing team's language beats every preference below.* This gate fires first and hardest.
2. **Platform constraint** — a standing mandate or ecosystem investment (Microsoft shop → C#; JVM shop → Java/Kotlin). The question is "are you already committed," not "are you large."
3. **Workload constraint** — a *named* requirement demanding a systems language: hard latency floor, memory ceiling, embedded target.

**Unconstrained → Python, then Go.** Any override is recorded in an ADR.

Rejected: mapping hiring-strategy personas to languages (`enterprise → Java/C#`, `startup → Python/Go/Rust`, `scientific → C/C++`). The insight underneath it — that hiring is a real constraint — is retained and promoted to gate #1. The mechanism was rejected because it is a category-to-answer lookup with no gate, the same class of vibe-based rule the cache/queue gate exists to eliminate; because its three categories are three non-orthogonal axes collapsed into a false single-select (Red Hat is enterprise *and* open source); and because `enterprise → Java/C#` conflates "large company" with "large company founded in 2005."

## A gate producing the same answer as a persona is still not the persona

Gate 1 and the enterprise-persona shortcut can land on the same language — a large JVM shop is exactly the case where the team constraint fires hardest. That coincidence is not vindication for the shortcut. The persona is a lookup with no gate: it fires from the org's category alone, with nothing to check and nothing that would change the answer if the facts underneath changed. The gate fires from a named fact — headcount, a shared build, an existing template — that a reviewer can verify and that stops applying the moment it stops being true (the team is reorganized, the platform migrates). Recording "enterprise means Java" as the reason produces the right service and the wrong precedent: the next decision that cites it will be reasoning from a category, not a constraint, and won't reliably land on the right answer next time the category doesn't cleanly map.

## Language support tiers

| Tier | Languages | What the skill provides |
|---|---|---|
| **1** | Python, Go | Full assets: skeleton, Dockerfile, hooks, CI |
| **2** | Java, C#, Rust | Doctrine and ADRs apply; **no scaffolding** — the skill says so plainly rather than faking it |
| **Out of scope** | C/C++ | 1-N-CQDS is a web service architecture. If the workload truly demands C/C++, this is the wrong methodology — say so and stop. |

Tier 2 is not a soft no. The gates above still apply in full, and the resulting ADR is real — it just isn't backed by a generated skeleton. Producing a plausible-looking scaffold for a language this methodology doesn't template would be worse than admitting the gap.

## Portability layer

- Python/SQL → SQLAlchemy + Alembic
- Go/SQL → GORM
- **MongoDB** → no ODM buys cross-family portability, so the portability layer is a hand-written **repository pattern**. Services talk to repositories, never to the driver.
