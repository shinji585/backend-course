from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.trackedProductsTags import tracked_product_tags

if TYPE_CHECKING:
    from app.models.trackedproduct import TrackedProduct
    from app.models.user import User  # type: ignore


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(  # noqa: UP045
        Uuid, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    owner: Mapped[Optional[User]] = relationship(back_populates="tags")  # noqa: UP045

    tracked_products: Mapped[list[TrackedProduct]] = relationship(
        secondary=tracked_product_tags,
        back_populates="tags",
    )
