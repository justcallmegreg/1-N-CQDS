# SQL vs Document

**This is the one genuinely irreversible choice in the stack, and it gets the most scrutiny.** The "swap engines easily" goal holds only *within* a family: Postgres↔MariaDB is a configuration change; SQL↔Mongo is a rewrite that no library prevents. Its ADR is the most important document in the repository.

- **SQL** → Postgres by default; MariaDB when horizontal scale is explicitly named.
- **Document** → MongoDB, and only when the data is genuinely schema-variant or document-shaped. Not because "it's flexible."

## Why "flexible" doesn't count

"Flexible" is what a schema-variant claim sounds like before anyone has checked whether the data actually varies in shape or whether it merely hasn't been modeled yet. An ORM or a driver library papers over syntax differences within a family; it does not turn a relational rewrite into a config change, so "we can always migrate later" is not a mitigant here the way it is for other decisions in this sequence.

## The test

Read the state inventory (Step 1). Do items reference each other? Will a query ever need to span two of them? That is a relationship, and a relationship is SQL's native shape — a join. Document stores can approximate joins, but the approximation is what "genuinely" is doing in "genuinely schema-variant or document-shaped": the state item must actually vary in shape or stand alone, not merely be convenient to store as a blob.
