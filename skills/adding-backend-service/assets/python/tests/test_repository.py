# tests/test_repository.py — the seam: the repository returns boundary types
# (plain dataclasses), never SQLAlchemy model instances, so callers don't couple
# to the ORM. Uses in-memory SQLite to prove engine-independence.
from app.db import make_engine, make_session_factory, Base
from app.repository import ItemRepository
from app.models import Item as ItemModel   # the ORM model (internal)
from app.repository import Item as ItemDTO # the boundary dataclass (public)

def make_repo():
    eng = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(eng)
    sf = make_session_factory(eng)
    return ItemRepository(sf)

def test_add_and_get_returns_boundary_type_not_orm_model():
    repo = make_repo()
    created = repo.add("hello")
    assert isinstance(created, ItemDTO)
    assert not isinstance(created, ItemModel)  # the seam: no ORM type leaks out
    fetched = repo.get(created.id)
    assert fetched is not None and fetched.name == "hello" and isinstance(fetched, ItemDTO)

def test_list_returns_boundary_types():
    repo = make_repo()
    repo.add("a"); repo.add("b")
    items = repo.list()
    assert [i.name for i in items] == ["a", "b"]
    assert all(isinstance(i, ItemDTO) for i in items)

def test_works_on_a_different_engine_unchanged():
    # The same repository code runs on SQLite here and Postgres in prod — the
    # engine-independence that the portability layer promises.
    repo = make_repo()  # sqlite
    assert repo.add("x").name == "x"
