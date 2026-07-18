# Storage Ladder

Applied per state item.

| State shape | Destination |
|---|---|
| Structured, queryable | **Database** |
| Opaque blob (uploads, generated artifacts) | **S3-capable API** — MinIO in compose locally, S3/R2/Spaces in prod |
| Neither, and a hard constraint forbids the above | **Filesystem — last resort** |

Filesystem **breaks invariant 1**. Choosing it requires an ADR that explicitly
names it as debt and states the constraint forcing it.

Scratch under `/tmp`, discarded within one request, is not state — invariant 1
already permits it (`No local writes outside /tmp scratch`) — and does not
enter this ladder.

## Why blobs never go in the database

Blobs in a database inflate backups, slow replication, and blow out row
sizes for data nobody queries. The DB stores the metadata and the key; the
object store holds the bytes.
