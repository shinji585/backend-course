import uuid
from datetime import datetime
from typing import Annotated

from pydantic import ConfigDict, Field

from app.enums.enum_status import EnumStatus
from app.schemas.base import BaseItem


class DetailItem(BaseItem):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4, description="ID of the Item")]
    status: Annotated[EnumStatus, Field(default=EnumStatus.PENDING)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]

    model_config = ConfigDict(
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
