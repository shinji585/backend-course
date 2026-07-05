import json
import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path
from typing import Any, Literal

from app.schemas.tags import InternalTag, PublicTag

# build the logger capert
logger_file: Path = Path(__file__).resolve().parents[2] / "logger" / "logger.info"
logger_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(logger_file),
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
)

logger: logging.Logger = logging.getLogger(__name__)


def requires_initialization(default_return: Any = None, *, default_factory: Callable[[], Any] | None = None):
    """
    If not initialized, returns default_factory() if provided, else default_return.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not getattr(self, "data", None):
                logger.error("Services not initialized. Call set_config_path() first.")
                if default_factory is not None:
                    return default_factory()
                return default_return
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class TagsServices:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path: Path | None = config_path
        self.data: dict | None = None

        if self.config_path:
            self.data = self._load_or_create()

    def set_config_path(self, config_path: Path) -> bool:
        self.config_path = config_path
        try:
            self.data = self._load_or_create()
            logger.info(f"Config path set to: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to set config path: {e}")
            return False

    def _load_or_create(self) -> dict[str, Any] | Any:
        if not self.config_path:
            raise ValueError("config_path not set. Call set_config_path() first")

        if not self.config_path.exists():
            return self._create_default()

        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.warning(f"Corruption at line {e.lineno}, col {e.colno}")
            self._backup_corrupted()
            return self._create_default()

    def _create_default(self) -> dict[str, Any]:
        default = {"tags": [], "version": 1}
        self._save(default)
        return default

    def _backup_corrupted(self) -> None:
        try:
            timestap = datetime.now().strftime("Y%m%d_%H%M%S")
            backup_path = self.config_path.parent / f"{self.config_path.name}.{timestap}.corrupt"  # type: ignore
            self.config_path.rename(backup_path)  # type: ignore
            logger.info(f"Corrupted file backed up: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup: {e}")

    def _save(self, data: dict | None = None) -> bool:
        if not self.config_path:
            logger.error("config_path not set")
            return False

        if data is None:
            data = self.data

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"Failed to save: {e}")
            return False

    @requires_initialization(default_return=False)
    def add_tag(self, tags: list[str] | None = None) -> PublicTag | list[PublicTag] | Literal[False]:
        assert self.data is not None
        try:
            if tags is None:
                new_tag: dict[str, Any] = InternalTag().model_dump()
                self.data["tags"].append(new_tag)
                self.data["version"] += 1
                self.data["last_updated"] = datetime.now(UTC)

                if self._save():
                    logger.info(f"Tag added: {new_tag['name']} (v{self.data['version']})")
                    return PublicTag.model_validate(new_tag)
                return False

            instances: list[InternalTag] = [InternalTag(name=t) for t in tags]

            self.data["tags"].extend(i.model_dump() for i in instances)
            self.data["version"] += 1
            self.data["last_updated"] = datetime.now(UTC)

            if self._save():
                logger.info(f"Tags added: {[tag.name for tag in instances]} (v{self.data['version']})")
                return [PublicTag.model_validate(i.model_dump()) for i in instances]
            return False
        except Exception as e:
            logger.error(f"Failed to add tag: {e}")
            return False

    @requires_initialization(default_return=False)
    def remove_tag(self, tag_id: uuid.UUID):
        assert self.data is not None
        try:
            original_count = len(self.data["tags"])
            self.data["tags"] = [t for t in self.data["tags"] if t["id"] != tag_id]

            if len(self.data["tags"]) < original_count:
                self.data["version"] += 1
                self.data["last_updated"] = datetime.now(UTC)

                if self._save():
                    logger.info(f"Tag removed: {tag_id} (v{self.data['version']})")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove tag: {e}")
            return False

    @requires_initialization(default_return=False)
    def update_tag(self, tag_id: uuid.UUID, **kwargs) -> bool:
        assert self.data is not None

        try:
            tag: Any | None = next((t for t in self.data["tags"] if t["id"] == tag_id), None)

            if not tag:
                logger.warning(f"Tag not found: {tag_id}")
                return False

            tag.update(kwargs)
            tag["updated_at"] = datetime.now(UTC)
            self.data["version"] += 1
            self.data["last_updated"] = datetime.now(UTC)

            if self._save():
                logger.info(f"Tag updated: {tag_id} (v{self.data['version']})")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update tag: {e}")
            return False

    @requires_initialization(default_return=None)
    def get_tag(self, tag_id: uuid.UUID) -> PublicTag | None:
        assert self.data is not None
        return (
            PublicTag.model_validate(tag_data)
            if (
                tag_data := next(
                    filter(lambda tag: tag["id"] == tag_id, self.data["tags"]),
                    None,
                )
            )
            else None
        )

    def get_version(self) -> int:
        return self.data.get("version", 1) if self.data else 1

    def get_all_tags(self):
        return self.data.get("tags", []) if self.data else []
