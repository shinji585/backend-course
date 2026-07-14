import uuid
from pathlib import Path
from typing import Literal

from app.core.logging import get_logger
from app.db.repositories.tracked_product_repository import TrackedProductRepository
from app.schemas.tags.public import PublicTag
from app.schemas.tracked import TrackedProductCreate, TrackedProductInternal, TrackedProductPublic
from app.services.tags import TagsServices

logger = get_logger(__name__)


class TrackedProductServices:
    TAG_SERVICES = TagsServices(config_path=Path(__file__).absolute().parents[1] / "db" / "data" / "tagsData.json")

    def __init__(self, config_path: Path | None = None) -> None:
        self._repo = TrackedProductRepository(config_path)

    def set_config_path(self, config_path: Path) -> bool:
        return self._repo.set_config_path(config_path)

    # in this method None means that the tracked product couldn't be added
    # literal[False] means that something internally went wrong
    def create(self, tracked_product: TrackedProductCreate) -> TrackedProductPublic | None | Literal[False]:
        try:
            names: list[str] | None = (
                [name.strip().lower() for name in tracked_product.tags_name] if tracked_product.tags_name else None
            )

            result: PublicTag | list[PublicTag] | Literal[False] = self.TAG_SERVICES.add_tag(tags=names)

            if result is False:
                return None

            if isinstance(result, list):
                ids = [tag.id for tag in result]
                data = TrackedProductInternal.model_validate(tracked_product.model_dump(exclude={"tags_name"}))
                data.tags_id = ids

                if self._repo.save(data.model_dump(mode="json")):
                    logger.info(f"Tracked Product added: {data.name}")
                    pyload = {**data.model_dump(exclude={"tags_id", "owner_id"}), "tags": result}
                    return TrackedProductPublic.model_validate(pyload)
                return None

            if isinstance(result, PublicTag):
                data = TrackedProductInternal.model_validate(tracked_product.model_dump(exclude={"tags_name"}))
                data.tags_id.append(result.id)

                if self._repo.save(data.model_dump(mode="json")):
                    logger.info(f"Tracked Product added: {data.name}")
                    pyload = {**data.model_dump(exclude={"tags_id", "owner_id"}), "tags": [result]}
                    return TrackedProductPublic.model_validate(pyload)
                return None

            return None

        except Exception as e:
            logger.error(f"Failed to create tracked product: {e}")
            return False

    def remove(self, tracked_product_id: uuid.UUID) -> bool:
        if self._repo.delete(tracked_product_id):
            logger.info(f"Tracked product removed: {tracked_product_id}")
            return True
        return False

    def update(self, tracked_product_id: uuid.UUID, **kwargs) -> bool:
        try:
            if self._repo.update(tracked_product_id, **kwargs):
                logger.info(f"Tracked product updated: {tracked_product_id}")
                return True
            logger.warning(f"Tracked product not found: {tracked_product_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to update tracked product: {e}")
            return False

    def get(self, tracked_product_id: uuid.UUID) -> TrackedProductPublic | None:
        tracked_data = self._repo.find_by_id(tracked_product_id)
        if tracked_data is None:
            return None

        return TrackedProductPublic.model_validate(
            {k: v for k, v in tracked_data.items() if k not in {"tags_id", "owner_id"}}
            | {"tags": [self.TAG_SERVICES.get_tag(tag_id=tag_id) for tag_id in tracked_data["tags_id"]]}
        )

    def get_all(self, limit: int, offset: int) -> list[TrackedProductPublic]:
        return [
            TrackedProductPublic.model_validate(
                {k: v for k, v in product.items() if k not in {"tags_id", "owner_id"}}
                | {
                    "tags": [
                        tag
                        for tag_id in product["tags_id"]
                        if (tag := self.TAG_SERVICES.get_tag(tag_id=tag_id)) is not None
                    ]
                }
            )
            for product in self._repo.find_all()[offset : offset + limit]
        ]
