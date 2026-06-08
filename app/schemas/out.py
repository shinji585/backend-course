import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.enums.enum_status import EnumStatus


class OutItem(BaseModel):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4, description="ID of the Item")]
    name: Annotated[str, Field(min_length=3, max_length=20, description="Name of the Item")]
    status: Annotated[EnumStatus, Field(description="Current purchase status")]

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Diana Rice Bag",
                "status": "PENDING",
            }
        },
    )
