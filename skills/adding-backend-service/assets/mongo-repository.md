# The MongoDB repository pattern

Document databases have no ODM that buys cross-family portability, so the
portability layer is **hand-written**: the same repository interface the SQL
skeletons expose, implemented over the Mongo driver directly. Callers can't tell
which database is behind the interface — that's the whole point.

## Same interface, different implementation

The SQL `ItemRepository` exposes `add(name) -> Item`, `list() -> [Item]`,
`get(id) -> Item | None`, returning the **boundary dataclass** `Item`, never an
ORM row. A Mongo implementation keeps that exact interface:

```python
# repository_mongo.py — same public interface as the SQLAlchemy repository.
from dataclasses import dataclass
from pymongo.database import Database

@dataclass(frozen=True)
class Item:
    id: str        # Mongo _id as string
    name: str

class ItemRepository:
    def __init__(self, db: Database):
        self._col = db["items"]

    def add(self, name: str) -> Item:
        r = self._col.insert_one({"name": name})
        return Item(id=str(r.inserted_id), name=name)

    def list(self) -> list[Item]:
        return [Item(id=str(d["_id"]), name=d["name"])
                for d in self._col.find().sort("_id")]

    def get(self, item_id: str) -> Item | None:
        from bson import ObjectId
        d = self._col.find_one({"_id": ObjectId(item_id)})
        return Item(id=str(d["_id"]), name=d["name"]) if d else None
```

## What changes, what doesn't

- **Changes:** the `id` type (int → string), the implementation, the driver
  (`pymongo`/`motor`), no Alembic (Mongo is schemaless; migrations become data
  scripts when needed).
- **Doesn't change:** the repository interface, the routes/business logic above it,
  the boundary `Item` type's shape. Swapping SQL→Mongo is re-implementing one file,
  not rewriting the service.

This is why SQL-vs-Document is "the one genuinely irreversible decision" scrutinised
hardest at architecture time — but the repository seam still contains the blast
radius to a single file.
