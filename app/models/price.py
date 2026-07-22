from dataclasses import dataclass
from decimal import Decimal

from app.schemas.enums.currency import Currency


@dataclass
class PriceValueObject:
    amount: Decimal
    currency: Currency

    def __composite_values__(self) -> tuple[Decimal, Currency]:
        return self.amount, self.currency
