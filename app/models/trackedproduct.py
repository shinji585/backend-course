import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from app.db.base import Base
from app.models.price import PriceValueObject
from app.models.trackedProductsTags import tracked_product_tags
from app.schemas.enums import Currency, Status

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.user import User


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
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    owner: Mapped[User | None] = relationship(back_populates="tracked_products")
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    target_price_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    target_price_currency: Mapped[Currency | None] = mapped_column(
        Enum(Currency),
        nullable=True,
    )
    current_price_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    current_price_currency: Mapped[Currency | None] = mapped_column(
        Enum(Currency),
        nullable=True,
    )
    target_price: Mapped[PriceValueObject | None] = composite(
        PriceValueObject, target_price_amount, target_price_currency
    )
    current_price: Mapped[PriceValueObject | None] = composite(
        PriceValueObject, current_price_amount, current_price_currency
    )
    status: Mapped[Status] = mapped_column(Enum(Status))

    tags: Mapped[list[Tag]] = relationship(
        secondary=tracked_product_tags,
        back_populates="tracked_products",
    )

    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
