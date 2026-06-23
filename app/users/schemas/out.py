import uuid
from typing import Annotated, ClassVar

from pydantic import ConfigDict, Field

from app.users.schemas.base import BaseUser


class OutUser(BaseUser):
    id: Annotated[uuid.UUID, Field(description="Unique identifier")]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {"id": "123e4567-e89b-12d3-a456-426614174000", "username": "samuel", "email": "samuel@gmail.com"}
        },
    )
