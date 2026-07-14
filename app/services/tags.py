import uuid
from pathlib import Path
from typing import Any, Literal

from app.core.logging import get_logger
from app.db.repositories.tag_repository import TagRepository
from app.schemas.tags import InternalTag, PublicTag

logger = get_logger(__name__)


class TagsServices:
    def __init__(self, config_path: Path | None = None) -> None:
        self._repo = TagRepository(config_path)

    def set_config_path(self, config_path: Path) -> bool:
        return self._repo.set_config_path(config_path)

    def _to_public(self, tag_data: dict) -> PublicTag:
        return PublicTag.model_validate({k: v for k, v in tag_data.items() if k in PublicTag.model_fields})

    def add_tag(self, tags: list[str] | None = None) -> PublicTag | list[PublicTag] | Literal[False]:
        try:
            if tags is None:
                temp = InternalTag()
                default_name = getattr(temp, "name", None)
                if default_name:
                    existing = self._repo.find_by_name(default_name)
                    if existing:
                        return self._to_public(existing)

                new_tag: dict[str, Any] = temp.model_dump(mode="json")
                if self._repo.save(new_tag):
                    logger.info(f"Tag added: {new_tag['name']}")
                    return self._to_public(new_tag)
                return False

            public_results: list[PublicTag] = []
            newly_created: list[dict] = []

            for name in tags:
                found = self._repo.find_by_name(name)
                if found:
                    public_results.append(self._to_public(found))
                    continue

                inst = InternalTag(name=name)
                dumped = inst.model_dump(mode="json")
                newly_created.append(dumped)
                public_results.append(self._to_public(dumped))

            if not newly_created:
                return public_results

            if self._repo.save_many(newly_created):
                logger.info(f"Tags added: {[t['name'] for t in newly_created]}")
                return public_results

            return False
        except Exception as e:
            logger.error(f"Failed to add tag: {e}")
            return False

    def remove_tag(self, tag_id: uuid.UUID) -> bool:
        try:
            if self._repo.delete(tag_id):
                logger.info(f"Tag removed: {tag_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove tag: {e}")
            return False

    def update_tag(self, tag_id: uuid.UUID, **kwargs) -> bool:
        try:
            if self._repo.update(tag_id, **kwargs):
                logger.info(f"Tag updated: {tag_id}")
                return True
            logger.warning(f"Tag not found: {tag_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to update tag: {e}")
            return False

    def get_tag(self, tag_id: uuid.UUID) -> PublicTag | None:
        tag_data = self._repo.find_by_id(tag_id)
        return self._to_public(tag_data) if tag_data else None

    def get_version(self) -> int:
        return self._repo.get_version()

    def get_all_tags(self) -> list[dict] | None:
        return self._repo.find_all()
