from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base

tracked_product_tags = Table(
    "tracked_product_tags",
    Base.metadata,
    Column(
        "tracked_product_id",
        ForeignKey("tracked_products.id"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id"),
        primary_key=True,
    ),
)
