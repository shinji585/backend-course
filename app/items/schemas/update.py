from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from app.items.enums import EnumStatus


class UpdateItem(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
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
