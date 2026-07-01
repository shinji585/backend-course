from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.schemas.price.enums import Currency


class Price(BaseModel):
    currency: Annotated[Currency, Field(default=Currency.COP)]
    amount: Annotated[Decimal, Field(description="The total monetary value.")]

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("amount cannot be negative")
        return v
