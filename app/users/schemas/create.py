from typing import Annotated, ClassVar

from pydantic import ConfigDict, Field

from app.users.schemas.base import BaseUser


class CreateUser(BaseUser):
    password: Annotated[str, Field(min_length=8, max_length=20)]
    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {"username": "demo_user", "email": "demo@example.com", "password": "not-a-real-password"}
        },
    )
