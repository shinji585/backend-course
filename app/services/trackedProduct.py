import uuid
from logging import Logger
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.db.repositories.tracked_product_repository import TrackedProductRepository
from app.schemas.tags.public import PublicTag
from app.schemas.tracked import TrackedProductCreate, TrackedProductInternal, TrackedProductPublic
from app.services.tags import TagsServices

logger: Logger = get_logger(__name__)


class TrackedProductServices:
    def __init__(self, db_path: Path, tags_db_path: Path) -> None:
        self._repo = TrackedProductRepository(db_path)
        self._tag_services = TagsServices(tags_db_path)

    def _flatten(self, internal: TrackedProductInternal) -> dict[str, Any]:
        data: dict[str, Any] = internal.model_dump(exclude={"target_price", "current_price"})
        data["target_price_amount"] = internal.target_price.amount if internal.target_price else None
        data["target_price_currency"] = internal.target_price.currency if internal.target_price else None
        data["current_price_amount"] = internal.current_price.amount if internal.current_price else None
        data["current_price_currency"] = internal.current_price.currency if internal.current_price else None
        return data

    def _to_public(self, data: dict) -> TrackedProductPublic:
        tags_id: Any = data.pop("tags_id", [])
        data.pop("owner_id", None)

        target_amount = data.pop("target_price_amount", None)
        target_currency = data.pop("target_price_currency", None)

        current_amount = data.pop("current_price_amount", None)
        current_currency = data.pop("current_price_currency", None)

        data["target_price"] = {"amount": target_amount, "currency": target_currency}

        data["current_price"] = (
            {
                "amount": current_amount,
                "currency": current_currency,
            }
            if current_amount is not None and current_currency is not None
            else None
        )

        tags: list[PublicTag] = [
            tag for tag_id in tags_id if (tag := self._tag_services.get_tag(tag_id=tag_id)) is not None
        ]

        data["tags"] = tags

        return TrackedProductPublic.model_validate(data)

    def create(self, tracked_product: TrackedProductCreate) -> TrackedProductPublic | None:
        try:
            names: list[str] | None = (
                [name.strip().lower() for name in tracked_product.tags_name] if tracked_product.tags_name else None
            )

            result: PublicTag | list[PublicTag] | None = self._tag_services.add_tag(name=names)
            if result is None:
                return None

            tags: list[PublicTag] = result if isinstance(result, list) else [result]

            internal: TrackedProductInternal = TrackedProductInternal.model_validate(
                tracked_product.model_dump(exclude={"tags_name"})
            )
            internal.tags_id = [tag.id for tag in tags]

            flat: dict[str, Any] = self._flatten(internal)

            if not self._repo.save(flat):
                return None

            logger.info(f"Tracked Product added: {internal.name}")
            return self._to_public(flat | {"tags_id": internal.tags_id})

        except Exception as e:
            logger.error(f"Failed to create tracked product: {e}")
            return None

    def remove(self, tracked_product_id: uuid.UUID) -> bool:
        if self._repo.delete(tracked_product_id):
            logger.info(f"Tracked product removed: {tracked_product_id}")
            return True
        return False

    def update(self, tracked_product_id: uuid.UUID, data: dict) -> bool:
        try:
            flat_data: dict[str, Any] = {k: v for k, v in data.items() if k not in {"target_price", "current_price"}}

            if "target_price" in data and data["target_price"] is not None:
                flat_data["target_price_amount"] = data["target_price"]["amount"]
                flat_data["target_price_currency"] = data["target_price"]["currency"]

            if "current_price" in data and data["current_price"] is not None:
                flat_data["current_price_amount"] = data["current_price"]["amount"]
                flat_data["current_price_currency"] = data["current_price"]["currency"]

            if self._repo.update(tracked_product_id, flat_data):
                logger.info(f"Tracked product updated: {tracked_product_id}")
                return True
            logger.warning(f"Tracked product not found: {tracked_product_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to update tracked product: {e}")
            return False

    def get(self, tracked_product_id: uuid.UUID) -> TrackedProductPublic | None:
        tracked_data: None | dict[Any, Any] = self._repo.find_by_id(tracked_product_id)
        if tracked_data is None:
            return None
        return self._to_public(tracked_data)

    def get_all(self, limit: int, offset: int) -> list[TrackedProductPublic]:
        products: list[dict[str, Any]] = self._repo.find_all()
        return [self._to_public(p) for p in products[offset : offset + limit]]
