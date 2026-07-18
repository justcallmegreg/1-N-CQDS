# Cache and Queue Gates

Both are **operational components**. Invariant 4 applies: a named pattern or
a measurement, or it does not enter.

## Cache gate

Redis only if a read path is **high-frequency AND staleness-tolerant AND expensive to compute**. All three. Two of three is a no.

Postgres already caches; premature Redis duplicates it badly.

## Queue gate

Only if a named pattern exists:

- work that must outlive a request (file processing, report generation)
- fanout to N consumers (webhooks, notifications)
- buffering a rate-limited external dependency
- deferred or retried work with retry semantics

Otherwise: no.

## Rejections are first-class

A failed gate still emits an ADR — *"Queue rejected: no async workload identified."* **That rejection is what governor mode enforces against later.** Without it, the skill cannot distinguish drift from legitimate reconsideration.

## Each component faces its own gate

The cache gate and the queue gate are independent, and each is binary. Adding Redis alone while declining the queue is not a moderate or reasonable middle position — Redis still needs all three of its own conditions on its own evidence, regardless of whether a queue is being asked for in the same breath. Splitting the difference between "add both" and "add neither" satisfies neither gate; it relocates the hunch from one component to the other rather than removing it.

## Authority is not evidence

A senior person asserting a component does not, by itself, name a pattern or supply a measurement — invariant 4 draws no exception for who is asking. The correct response to such a mandate is **not refusal**. It is to write the ADR, name the gate the component must clear, and ask what pattern the requester is seeing. If they name one that holds — a real hot read path, a real async workload — it passes the gate honestly and the ADR records it as accepted. If they can't name one, there isn't one, and the ADR records that instead.

## Anticipated scale is not evidence

Invariant 4 asks for a named pattern or a measurement. "We'll have 800 users
next year" is neither — it is a forecast, and a forecast describes neither
an existing hot read path nor an existing async workload.

The cost of adding Redis or a queue later, once a real hot path or a real
async workload exists, is a config change and a deploy behind a data-access
seam. The cost of carrying either for a year against a workload that never
arrives is a stateful component to run, monitor, back up, upgrade, and
debug — plus, for a cache specifically, every developer on the team
reasoning about invalidation on a read path that was never hot.
