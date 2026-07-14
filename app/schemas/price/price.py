from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, PlainSerializer, field_validator

from app.schemas.enums.currency import Currency


class Price(BaseModel):
    currency: Annotated[Currency, Field(default=Currency.COP)]
    amount: Annotated[
        Decimal,
        PlainSerializer(lambda x: str(x), return_type=str, when_used="json"),
        Field(description="The total monetary value."),
    ]

    @field_validator("amount", mode="after")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("amount cannot be negative")
        return v

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value) -> str:
        if isinstance(value, str):
            return value.lower()
        return value
