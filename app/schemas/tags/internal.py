import uuid
from typing import Annotated

from pydantic import ConfigDict, Field

from app.schemas.tags.public import PublicTag


class InternalTag(PublicTag):
    owner_id: Annotated[uuid.UUID, Field(description="Owner ID")]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "6d5af7dd-8d3b-4a7e-8b9d-f2b8e2c84b31",
                    "owner_id": "3f1c9d87-5d3a-4f9b-a9c8-7e2d1b6f4a90",
                    "name": "Gaming",
                },
                {
                    "id": "1b6e9b13-2aef-4b65-8d5f-3e8d6cbcd6d2",
                    "owner_id": "3f1c9d87-5d3a-4f9b-a9c8-7e2d1b6f4a90",
                    "name": "Work",
                },
                {
                    "id": "4f9d2a57-bb4f-44f6-93b7-1f6c4c2ef5a1",
                    "owner_id": "8a7e2c14-91d3-4b6a-8c2f-5d1e9b7a3c42",
                    "name": "Personal",
                },
            ]
        },
    )
