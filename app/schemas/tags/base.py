from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class BaseTag(BaseModel):
    name: Annotated[str, Field(..., ge=1, le=50)]

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        from_attributes=True,
        json_schema_extra={"example": ["Gaming", "Work", "Fashion"]},
    )
