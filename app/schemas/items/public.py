import uuid
from datetime import UTC, datetime
from typing import Annotated

from pydantic import ConfigDict, Field

from app.schemas.enums import Status
from app.schemas.items.base import TrackedProductBase
from app.schemas.price import Price
from app.schemas.tags import PublicTag


class TrackedProductPublic(TrackedProductBase):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4, description="Tracked product ID.")]
    current_price: Annotated[..., Price, Field(description="Current price found.")]
    created_at: Annotated[
        datetime, Field(default_factory=lambda: datetime.now(UTC), description="When tracking started.")
    ]
    status: Annotated[Status, Field(description="Describe the status of the tracked product.")]
    updated_at: Annotated[datetime, Field(..., description="Last modification made to the tracked product.")]
    tags: Annotated[list[PublicTag], Field(description="List of tags names.")]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "8b7d5c94-2d1a-4c9f-a5d8-7e3f9b1c2d6e",
                    "name": "Lenovo Legion Pro 7",
                    "description": (
                        "16-inch gaming laptop with RTX 5080, 32 GB RAM, and 2 TB SSD. "
                        "Prefer Amazon or the official Lenovo Store. Notify me when the "
                        "price reaches my target."
                    ),
                    "quantity": 1,
                    "target_price": {"amount": 1800, "currency": "USD"},
                    "current_price": {"amount": 1949.99, "currency": "USD"},
                    "created_at": "2026-07-02T14:30:00Z",
                    "updated_at": "2026-07-04T09:15:00Z",
                    "status": "tracking",
                    "tags": [
                        {"id": "6d5af7dd-8d3b-4a7e-8b9d-f2b8e2c84b31", "name": "Gaming"},
                        {"id": "1b6e9b13-2aef-4b65-8d5f-3e8d6cbcd6d2", "name": "Work"},
                    ],
                },
                {
                    "id": "1f3b8d76-4c2e-4d98-a9f5-5e1d7c9b8a44",
                    "name": "iPhone 16 Pro Max",
                    "description": (
                        "256 GB, Natural Titanium. Prefer the Apple Store or Amazon. "
                        "Notify me when the price reaches my target."
                    ),
                    "quantity": 1,
                    "target_price": {"amount": 1100, "currency": "USD"},
                    "current_price": {"amount": 1179, "currency": "USD"},
                    "created_at": "2026-07-01T18:45:00Z",
                    "updated_at": "2026-07-03T11:20:00Z",
                    "status": "paused",
                    "tags": [
                        {"id": "4f9d2a57-bb4f-44f6-93b7-1f6c4c2ef5a1", "name": "Technology"},
                        {"id": "ab7e1d2f-5c3d-4c78-9b9a-6d3f7c9b8e11", "name": "Wishlist"},
                    ],
                },
            ]
        },
    )
