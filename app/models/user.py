from __future__ import annotations

import uuid

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.tag import Tag
from app.models.trackedproduct import TrackedProduct


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)

    tracked_products: Mapped[list[TrackedProduct]] = relationship(
        back_populates="owner"
    )

    tags: Mapped[list[Tag]] = relationship(back_populates="owner")
