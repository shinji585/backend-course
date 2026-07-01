import uuid
from typing import Annotated

from pydantic import ConfigDict, Field

from app.schemas.tags.base import BaseTag


class PublicTag(BaseTag):
    id: Annotated[uuid.UUID, Field(description="Tag ID")]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"id": "6d5af7dd-8d3b-4a7e-8b9d-f2b8e2c84b31", "name": "Gaming"},
                {"id": "1b6e9b13-2aef-4b65-8d5f-3e8d6cbcd6d2", "name": "Work"},
                {"id": "4f9d2a57-bb4f-44f6-93b7-1f6c4c2ef5a1", "name": "Technology"},
                {"id": "ab7e1d2f-5c3d-4c78-9b9a-6d3f7c9b8e11", "name": "Wishlist"},
            ]
        },
    )
