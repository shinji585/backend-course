import uuid
from typing import Annotated

from pydantic import ConfigDict, Field

from app.enums.enum_status import EnumStatus
from app.schemas.base import BaseItem


class OutItem(BaseItem):
    id: Annotated[uuid.UUID, Field(description="Unique identifier")]
    status: Annotated[EnumStatus, Field(default=EnumStatus.PENDING)]

    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Diana Rice Bag",
                "status": "PENDING",
            }
        },
    )
