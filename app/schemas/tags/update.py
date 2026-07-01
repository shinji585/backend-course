from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class UpdateTag(BaseModel):
    name: Annotated[str | None, Field(None, description="Tag Name")]

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        from_attributes=True,
        json_schema_extra={"examples": ["Gaming", "Work", "Fashion"]},
    )
