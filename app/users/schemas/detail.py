import uuid
from typing import Annotated, ClassVar

from pydantic import ConfigDict, Field

from app.users.schemas.out import OutUser


class DetailUser(OutUser):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4, description="Unique identifier")]
    hashed_password: Annotated[str, Field(min_length=8, max_length=20)]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "samuel",
                "emai": "samuel@gmail.com",
                "hashed_password": "samuel124",
            }
        },
    )
