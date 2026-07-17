import uuid
from logging import Logger
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.db.repositories.tag_repository import TagRepository
from app.schemas.tags import InternalTag, PublicTag

logger: Logger = get_logger(__name__)


class TagsServices:
    def __init__(self, config_path: Path) -> None:
        self._repo = TagRepository(config_path)

    def add_tag(self, name: str | list[str] | None = None) -> PublicTag | list[PublicTag] | None:
        try:
            if name is None:
                default_tag = InternalTag()
                existing = self._repo.find_by_name(default_tag.name)
                if existing:
                    return existing

                data: dict[str, Any] = default_tag.model_dump()
                if not self._repo.save(data):
                    return None

                logger.info(f"Tag added: {data['name']}")
                return PublicTag.model_validate(data)

            if isinstance(name, list):
                public_results: list[PublicTag] = []
                newly_created: list[dict] = []

                for n in name:
                    found: PublicTag | None = self._repo.find_by_name(n)
                    if found:
                        public_results.append(found)
                        continue

                    new_tag = InternalTag(name=n)
                    data = new_tag.model_dump()
                    newly_created.append(data)
                    public_results.append(PublicTag.model_validate(data))

                if newly_created:
                    if not self._repo.save_many(newly_created):
                        return None
                    logger.info(f"Tags added: {[t['name'] for t in newly_created]}")

                return public_results

            existing: PublicTag | None = self._repo.find_by_name(name)
            if existing:
                return existing

            new_tag = InternalTag(name=name)
            data = new_tag.model_dump()
            if not self._repo.save(data):
                return None

            logger.info(f"Tag added: {name}")
            return PublicTag.model_validate(data)

        except Exception as e:
            logger.error(f"Failed to add tag: {e}")
            return None

    def remove_tag(self, tag_id: uuid.UUID) -> bool:
        try:
            if self._repo.delete(tag_id=tag_id):
                logger.info(f"Tag removed: {tag_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove tag: {e}")
            return False

    def update_tag(self, tag_id: uuid.UUID, data: dict) -> bool:
        try:
            if self._repo.update(tag_id=tag_id, data=data):
                logger.info(f"Tag updated: {tag_id}")
                return True
            logger.warning(f"Tag not found: {tag_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to update tag: {e}")
            return False

    def get_tag(self, tag_id: uuid.UUID) -> PublicTag | None:
        return self._repo.find_by_id(tag_id=tag_id)

    def get_all_tags(self) -> list[PublicTag] | list[Any]:
        return self._repo.find_all()
