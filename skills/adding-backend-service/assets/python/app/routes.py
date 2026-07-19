# routes.py — HTTP layer. Depends on ItemRepository (the interface), NOT on
# SQLAlchemy. Business logic lives here and never imports the ORM.
from fastapi import APIRouter
from pydantic import BaseModel
from .db import engine, make_session_factory
from .repository import ItemRepository

router = APIRouter(prefix="/items")

class NewItem(BaseModel):
    name: str

def _repo() -> ItemRepository:
    return ItemRepository(make_session_factory(engine))

@router.post("")
def create_item(body: NewItem):
    return _repo().add(body.name)

@router.get("")
def list_items():
    return _repo().list()
