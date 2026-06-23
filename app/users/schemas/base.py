from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BaseUser(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=12)]
    email: EmailStr

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        extra="forbid",
        json_schema_extra={"example": {"username": "samuel", "email": "samuel@gmail.com"}},
    )
