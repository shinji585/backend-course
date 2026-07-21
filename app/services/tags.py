import uuid
from collections.abc import Sequence
from logging import Logger

from app.core.logging import get_logger
from app.db.repositories.tag_repository import TagRepository
from app.models.tag import Tag

logger: Logger = get_logger(__name__)


class TagsServices:
    def __init__(self, repo: TagRepository) -> None:
        self._repo: TagRepository = repo

    def create_tag(self, name: str) -> Tag | None:
        try:
            existing: Tag | None = self._repo.get_by_name(name)
            if existing:
                return existing

            saved: bool | None = self._repo.save({"name": name})
            if not saved:
                return None

            return self._repo.get_by_name(name)
        except Exception as e:
            logger.error(f"Failed to create tag: {e}")
            return None

    def create_tags(self, names: list[str]) -> list[Tag]:
        try:
            results: list[Tag] = []
            to_create: list[dict] = []

            for name in names:
                existing = self._repo.get_by_name(name)
                if existing:
                    results.append(existing)
                    continue
                to_create.append({"name": name})

            if to_create:
                if not self._repo.save_many(to_create):
                    return results

                for entry in to_create:
                    created = self._repo.get_by_name(entry["name"])
                    if created:
                        results.append(created)

            return results
        except Exception as e:
            logger.error(f"Failed to create tags: {e}")
            return []

    def remove_tag(self, tag_id: uuid.UUID) -> bool:
        try:
            if self._repo.delete(tag_id=tag_id):
                logger.info(f"Tag removed: {tag_id}")
                return True
            logger.warning(f"Tag not found: {tag_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to remove tag: {e}")
            return False

    def get_tag(self, tag_id: uuid.UUID) -> Tag | None:
        return self._repo.get_by_id(tag_id=tag_id)

    def get_tag_by_name(self, name: str) -> Tag | None:
        return self._repo.get_by_name(name=name)

    def list_tags(self, offset: int, limit: int) -> Sequence[Tag]:
        return self._repo.list_all(offset=offset, limit=limit)
