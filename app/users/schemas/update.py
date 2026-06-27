from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UpdateUser(BaseModel):
    username: Annotated[str | None, Field(default=None, min_length=3, max_length=12)]
    email: Annotated[EmailStr | None, Field(default=None)]
    password: Annotated[str | None, Field(default=None, min_length=8, max_length=20)]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid", json_schema_extra={"example": {"username": "javierSamuel", "email": None, "password": None}}
    )
