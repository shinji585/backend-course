import uuid
from typing import Annotated

from pydantic import Field

from app.schemas.tags.public import PublicTag


class InternalTag(PublicTag):
    owner_id: Annotated[uuid.UUID | None, Field(description="Owner ID")] = Field(default=None)
