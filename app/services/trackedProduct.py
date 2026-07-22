import uuid
from collections.abc import Sequence
from logging import Logger
from typing import Any

from app.core.logging import get_logger
from app.db.repositories.tracked_product_repository import TrackedProductRepository
from app.models.tag import Tag
from app.models.trackedproduct import TrackedProduct
from app.schemas.tracked import TrackedProductCreate, TrackedProductPublic
from app.services.tags import TagsServices

logger: Logger = get_logger(__name__)


class TrackedProductServices:
    def __init__(self, repo: TrackedProductRepository, tag_services: TagsServices) -> None:
        self._repo: TrackedProductRepository = repo
        self._tag_services: TagsServices = tag_services

    def create(self, tracked_product: TrackedProductCreate) -> TrackedProductPublic | None:
        try:
            names: list[str] = (
                [name.strip().lower() for name in tracked_product.tags_name] if tracked_product.tags_name else []
            )
            tags: list[Tag] = self._tag_services.create_tags(names) if names else []

            data: dict[str, Any] = tracked_product.model_dump(exclude={"tags_name"})
            data["tags_id"] = [tag.id for tag in tags]

            product: TrackedProduct | None = self._repo.save(data)
            if product is None:
                return None

            logger.info(f"Tracked Product added: {product.name}")
            return TrackedProductPublic.model_validate(product)

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
            if self._repo.update(tracked_product_id, data):
                logger.info(f"Tracked product updated: {tracked_product_id}")
                return True
            logger.warning(f"Tracked product not found: {tracked_product_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to update tracked product: {e}")
            return False

    def get(self, tracked_product_id: uuid.UUID) -> TrackedProductPublic | None:
        product: TrackedProduct | None = self._repo.find_by_id(tracked_product_id)
        if product is None:
            return None
        return TrackedProductPublic.model_validate(product)

    def get_all(self, offset: int, limit: int) -> list[TrackedProductPublic]:
        products: Sequence[TrackedProduct] = self._repo.find_all(offset=offset, limit=limit)
        return [TrackedProductPublic.model_validate(p) for p in products]
