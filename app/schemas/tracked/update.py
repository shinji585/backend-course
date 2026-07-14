from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.enums import Status
from app.schemas.price import Price


class TrackedProductUpdate(BaseModel):
    name: Annotated[
        str | None, Field(default=None, min_length=1, max_length=100, description="Product name entered by the user.")
    ]
    description: Annotated[
        str | None,
        Field(
            default=None, min_length=1, max_length=1000, description="User notes (color, storage, preferences, etc.)."
        ),
    ]
    quantity: Annotated[int | None, Field(default=None, ge=1, le=5, description="Desired quantity.")]
    target_price: Annotated[Price | None, Field(default=None, description="Target price for notificatio.")]
    tags: Annotated[list[str] | None, Field(default=None, description="Update tags by using its antity.")]
    status: Annotated[Status | None, Field(default=None, description="Describe the status of the tracked product.")]
