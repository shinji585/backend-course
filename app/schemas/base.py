from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class BaseItem(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Diana Rice Bag",
                    "description": "A 5kg bag of premium white rice, a must-have for the family kitchen.",
                },
                {
                    "name": "Boxer Motorcycle",
                    "description": "Indestructible and budget-friendly bike for daily commute.",
                },
                {
                    "name": "Toyota Car",
                    "description": "Practical everyday car with great trunk space.",
                },
            ]
        },
    )

    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=20,
            description="Name of the Item",
            title="Item Name",
            examples=["Diana Rice Bag", "Toyota Car", "Boxer Motorcycle"],
        ),
    ]
    description: Annotated[
        str,
        Field(
            min_length=10,
            max_length=100,
            description="Description of the product",
            title="Product Description",
            examples=[
                "A 5kg bag of premium white rice, a must-have for the family kitchen.",
                "Indestructible and budget-friendly bike for daily commute.",
                "Practical everyday car with great trunk space.",
            ],
        ),
    ]
