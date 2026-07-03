from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.price import Price


class TrackedProductBase(BaseModel):
    name: Annotated[str, Field(..., min_length=1, max_length=100, description="Product name entered by the user.")]
    description: Annotated[
        str | None,
        Field(
            default=None, min_length=100, max_length=1000, description="User notes (color, storage, preferences, etc.)"
        ),
    ]
    quantity: Annotated[..., int, Field(ge=1, le=5, description="Desired quantity.")]
    target_price: Annotated[Price | None, Field(default=None, description="Target price for notification")]

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True,
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
                },
                {
                    "name": "iPhone 16 Pro Max",
                    "quantity": 1,
                },
            ]
        },
    )
