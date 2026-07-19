# repository.py — THE SEAM. Public boundary type is a dataclass; the ORM model
# stays inside. Callers depend on this interface, never on SQLAlchemy.
from dataclasses import dataclass
from .models import Item as ItemModel

@dataclass(frozen=True)
class Item:            # boundary DTO — what callers see
    id: int
    name: str

def _to_dto(m: ItemModel) -> "Item":
    return Item(id=m.id, name=m.name)

class ItemRepository:
    def __init__(self, session_factory):
        self._sf = session_factory

    def add(self, name: str) -> Item:
        with self._sf() as s:
            m = ItemModel(name=name)
            s.add(m); s.commit(); s.refresh(m)
            return _to_dto(m)

    def list(self) -> list[Item]:
        with self._sf() as s:
            return [_to_dto(m) for m in s.query(ItemModel).order_by(ItemModel.id).all()]

    def get(self, item_id: int) -> Item | None:
        with self._sf() as s:
            m = s.get(ItemModel, item_id)
            return _to_dto(m) if m else None
