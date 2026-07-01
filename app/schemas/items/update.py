from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.price import Price
from app.schemas.tags import UpdateTag


class TrackedProductUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, ge=1, le=100, description="Product name entered by the user.")]
    description: Annotated[
        str | None, Field(default=None, ge=100, le=100, description="User notes (color, storage, preferences, etc.)")
    ]
    quantity: Annotated[int | None, Field(default=None, ge=1, le=5, description="Desired quantity")]
    target_price: Annotated[Price | None, Field(default=None, description="Target price for notificatio")]
    tags: Annotated[list[UpdateTag] | None, Field(default=None, description="Update Tags by using its antity")]
    status: None

    # in this section tomorrow I will start by this
