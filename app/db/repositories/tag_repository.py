import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.db.repositories.base import requires_initialization

logger = get_logger(__name__)


class TagRepository:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path: Path | None = config_path
        self.data: dict | None = None
        if self.config_path:
            self.data = self._load_data_if_exits()

    def set_config_path(self, config_path: Path) -> bool:
        self.config_path = config_path
        try:
            self.data = self._load_data_if_exits()
            logger.info(f"Config path set to: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to set config path: {e}")
            return False

    def _load_data_if_exits(self):
        if not self.config_path or not self.config_path.exists():
            return None
        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.warning(f"Corruption at line {e.lineno}, col {e.colno}")
            self._backup_corrupted()
            return self._create_default()

    def _create_default(self) -> dict[str, Any]:
        default = {"tags": [], "last_updated": datetime.now(UTC).isoformat(), "version": 1}
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

    @requires_initialization(auto_init=True, default_return=None)
    def find_all(self) -> list[dict] | None:
        assert self.data is not None
        return self.data["tags"]

    @requires_initialization(auto_init=True, default_return=None)
    def find_by_id(self, tag_id: uuid.UUID) -> dict | None:
        assert self.data is not None
        return next((t for t in self.data["tags"] if t["id"] == tag_id), None)

    @requires_initialization(auto_init=True, default_return=None)
    def find_by_name(self, name: str) -> dict | None:
        assert self.data is not None
        return next((t for t in self.data["tags"] if t.get("name") == name), None)

    @requires_initialization(auto_init=True, default_return=False)
    def save(self, tag: dict) -> bool:
        assert self.data is not None
        self.data["tags"].append(tag)
        self.data["version"] += 1
        self.data["last_updated"] = datetime.now(UTC).isoformat()
        return self._save()

    @requires_initialization(auto_init=True, default_return=False)
    def save_many(self, tags: list[dict]) -> bool:
        assert self.data is not None
        self.data["tags"].extend(tags)
        self.data["version"] += 1
        self.data["last_updated"] = datetime.now(UTC).isoformat()
        return self._save()

    @requires_initialization(auto_init=True, default_return=False)
    def update(self, tag_id: uuid.UUID, **kwargs) -> bool:
        assert self.data is not None
        tag = self.find_by_id(tag_id)
        if tag is None:
            return False
        tag.update(kwargs)
        tag["updated_at"] = datetime.now(UTC)
        self.data["version"] += 1
        self.data["last_updated"] = datetime.now(UTC).isoformat()
        return self._save()

    @requires_initialization(auto_init=True, default_return=False)
    def delete(self, tag_id: uuid.UUID) -> bool:
        assert self.data is not None
        original_count = len(self.data["tags"])
        self.data["tags"] = [t for t in self.data["tags"] if t["id"] != tag_id]
        if len(self.data["tags"]) == original_count:
            return False
        self.data["version"] += 1
        self.data["last_updated"] = datetime.now(UTC).isoformat()
        return self._save()

    def get_version(self) -> int:
        return self.data.get("version", 1) if self.data else 1
