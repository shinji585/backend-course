from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums.tags import Tags


class BaseTag(BaseModel):
    name: Annotated[str, Field(..., min_length=1, max_length=50)] = Tags.DEFAULT

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        from_attributes=True,
        json_schema_extra={"example": ["Gaming", "Work", "Fashion"]},
    )
