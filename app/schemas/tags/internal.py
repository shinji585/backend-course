import uuid
from datetime import UTC, datetime
from typing import Annotated

from pydantic import Field

from app.schemas.tags.public import PublicTag


class InternalTag(PublicTag):
    owner_id: Annotated[uuid.UUID | None, Field(description="Owner ID")] = Field(default=None)
    created_at: Annotated[datetime, Field(description="When tag was created.")] = Field(
        default_factory=lambda: datetime.now(UTC)
    )
