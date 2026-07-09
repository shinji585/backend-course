from decimal import Decimal
from pathlib import Path

from app.schemas.enums.currency import Currency
from app.schemas.price.price import Price
from app.schemas.tracked.create import TrackedProductCreate
from app.services.trackedProduct import TrackedProductServices

if __name__ == "__main__":
    data_path = Path(__file__).absolute().parent / "db" / "data" / "TrackedProduct.json"

    object_value = TrackedProductServices(config_path=data_path)

    tracked_product = TrackedProductCreate(
        name="iPhone 15 Pro Max",
        description="256GB, Titanium Blue, unlocked",
        target_price=Price(amount=Decimal(999.99), currency=Currency.USD),
        quantity=4,
    )

    print(object_value.create(tracked_product=tracked_product))
