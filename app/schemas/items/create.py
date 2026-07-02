from typing import Annotated

from pydantic import ConfigDict, Field

from app.schemas.enums import Status
from app.schemas.items.base import TrackedProductBase
from app.schemas.tags import BaseTag


class TrackedProductCreate(TrackedProductBase):
    tags_name: Annotated[
        list[BaseTag] | None,
        Field(default=None, description="List of tag names used to organize the item.", alias="tags"),
    ]
    status: Annotated[
        Status, Field(default_factory=lambda: Status.TRACKING, description="Current tracking status of the product.")
    ]

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Lenovo Legion Pro 7",
                    "description": (
                        "16-inch gaming laptop with RTX 5080, 32 GB RAM, and 2 TB SSD. "
                        "Prefer Amazon or the official Lenovo Store. Notify me when the "
                        "price reaches my target."
                    ),
                    "quantity": 1,
                    "target_price": {"amount": 1800, "currency": "USD"},
                    "tags": ["Gaming", "Work"],
                    "status": "tracking",
                },
                {"name": "iPhone 16 Pro Max", "quantity": 1, "status": "tracking"},
            ]
        },
    )
