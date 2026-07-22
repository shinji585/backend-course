from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from app.db.base import Base
from app.models.trackedProductsTags import tracked_product_tags
from app.schemas.enums import Currency, Status
from app.schemas.price import Price

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.user import User  # type: ignore


class TrackedProduct(Base):
    __tablename__ = "tracked_products"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(  # noqa: UP045
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP045
        DateTime(timezone=True),
        nullable=True,
    )
    owner: Mapped[Optional[User]] = relationship(back_populates="tracked_products")  # noqa: UP045
    description: Mapped[Optional[str]] = mapped_column(  # noqa: UP045
        String(1000),
        nullable=True,
    )
    target_price_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    target_price_currency: Mapped[Currency] = mapped_column(
        Enum(Currency),
        nullable=False,
    )
    current_price_amount: Mapped[Optional[Decimal]] = mapped_column(  # noqa: UP045
        Numeric(12, 2),
        nullable=True,
    )
    current_price_currency: Mapped[Optional[Currency]] = mapped_column(  # noqa: UP045
        Enum(Currency),
        nullable=True,
    )
    target_price: Mapped[Price] = composite(Price, target_price_amount, target_price_currency)
    current_price: Mapped[Optional[Price]] = composite(Price, current_price_amount, current_price_currency)  # noqa: UP045
    status: Mapped[Status] = mapped_column(Enum(Status))

    tags: Mapped[list[Tag]] = relationship(  # noqa: UP006
        secondary=tracked_product_tags,
        back_populates="tracked_products",
    )

    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
