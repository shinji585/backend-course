from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.enums.enum_status import EnumStatus


class UpdateItem(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Portatil",
                "description": "Portatil Asus Vivobook 15",
                "status": "BOUGHT",
            }
        },
    )

    name: Annotated[str | None, Field(default=None)]
    description: Annotated[str | None, Field(default=None)]
    status: Annotated[EnumStatus | None, Field(default=None)]
