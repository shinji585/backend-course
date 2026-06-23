import uuid
from datetime import datetime
from typing import Annotated, ClassVar

from pydantic import ConfigDict, Field

from app.items.enums import EnumStatus
from app.items.schemas.base import BaseItem


class DetailItem(BaseItem):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4, description="Unique identifier")]
    status: Annotated[EnumStatus, Field(default=EnumStatus.PENDING)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid",
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Diana Rice Bag",
                "description": "A 5kg bag of premium white rice, a must-have for the family kitchen.",
                "status": "PENDING",
                "created_at": "2026-06-07T18:14:17Z",
            }
        },
    )
