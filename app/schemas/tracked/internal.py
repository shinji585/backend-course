import uuid
from datetime import UTC, datetime
from typing import Annotated

from pydantic import Field

from app.schemas.enums import Status
from app.schemas.price import Price
from app.schemas.tracked.base import TrackedProductBase


class TrackedProductInternal(TrackedProductBase):
    owner_id: Annotated[uuid.UUID | None, Field(description="User identifier.")]

    tags_id: Annotated[list[uuid.UUID], Field(description="List of tags ids.")]
    id: Annotated[..., uuid.UUID, Field(default_factory=uuid.uuid4, description="Tracked product ID.")]
    current_price: Annotated[..., Price | None, Field(description="Current price found.")]
    created_at: Annotated[
        datetime, Field(default_factory=lambda: datetime.now(UTC), description="When tracking started.")
    ]
    updated_at: Annotated[datetime | None, Field(..., description="Last modification made to the tracked product.")]
    status: Annotated[Status, Field(description="Describe the status of the tracked product.")]
