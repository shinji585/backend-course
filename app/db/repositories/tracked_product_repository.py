import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class TrackedProductRepository:
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
        if not self.config_path:
            return None

        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                logger.warning(f"Corruption at line {e.lineno}, col {e.colno}")
                self._backup_corrupted()
                return self._create_default()

        return self._create_default()

    def _create_default(self) -> dict[str, Any]:
        default = {"tracked_products": [], "last_updated": datetime.now(UTC).isoformat(), "version": 1}
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

    def find_all(self) -> list[dict]:
        assert self.data is not None
        return self.data["tracked_products"]

    def find_by_id(self, tracked_product_id: uuid.UUID) -> dict | None:
        assert self.data is not None
        return next(
            (tp for tp in self.data["tracked_products"] if uuid.UUID(tp["id"]) == tracked_product_id),
            None,
        )

    def save(self, tracked_product: dict) -> bool:
        assert self.data is not None
        self.data["tracked_products"].append(tracked_product)
        self.data["version"] += 1
        self.data["last_updated"] = datetime.now(UTC).isoformat()
        return self._save()

    def update(self, tracked_product_id: uuid.UUID, **kwargs) -> bool:
        assert self.data is not None
        tp = self.find_by_id(tracked_product_id)
        if tp is None:
            return False
        tp.update(kwargs)
        tp["updated_at"] = datetime.now(UTC).isoformat()
        self.data["version"] += 1
        self.data["last_updated"] = datetime.now(UTC).isoformat()
        return self._save()

    def delete(self, tracked_product_id: uuid.UUID) -> bool:
        assert self.data is not None
        tp = self.find_by_id(tracked_product_id)
        if tp is None:
            return False
        self.data["tracked_products"].remove(tp)
        return self._save()
