# models.py — SQLAlchemy models. INTERNAL to the repository; never imported by
# routes/business logic. Sample entity: Item (replace per project).
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
