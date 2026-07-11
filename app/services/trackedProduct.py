import json
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path
from typing import Any, Literal

from app.core.logging import get_logger
from app.schemas.tags.public import PublicTag
from app.schemas.tracked import TrackedProductCreate, TrackedProductInternal, TrackedProductPublic
from app.services.tags import TagsServices

logger = get_logger(__name__)


def requires_initialization(
    default_return: Any = None,
    *,
    default_factory: Callable[[], Any] | None = None,
    auto_init: bool = False,
):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if getattr(self, "data", None) is None:
                # Load existing data; let _load_data_if_exits manage JSON / backup logic.
                try:
                    if hasattr(self, "_load_data_if_exits"):
                        self.data = self._load_data_if_exits()
                except (OSError, ValueError) as exc:
                    # Only swallow expected environment/config issues.
                    logger.exception(
                        "Error while loading data via %s._load_data_if_exits: %s",
                        type(self).__name__,
                        exc,
                    )
                    self.data = getattr(self, "data", None)

                if self.data is None and auto_init:
                    if hasattr(self, "_create_default"):
                        try:
                            # Keep original semantics: call _create_default and swallow expected errors.
                            self.data = self._create_default()
                        except (OSError, ValueError) as exc:
                            logger.exception(
                                "Error while creating default data via %s._create_default: %s",
                                type(self).__name__,
                                exc,
                            )
                            # Preserve your existing fallback
                            self.data = getattr(self, "data", None)

                if getattr(self, "data", None) is None:
                    logger.error("Services not initialized. Call set_config_path() first.")
                    if default_factory is not None:
                        return default_factory()
                    return default_return

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class TrackedProductServices:
    TAG_SERVICES = TagsServices(config_path=Path(__file__).absolute().parents[1] / "db" / "data" / "tagsData.json")

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

    def _create_json_field(self):
        if not self.config_path:
            raise ValueError("config_path not set. Call set_config_path() first")

        if not self.config_path.exists():
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

    # in this method None means that the tracked product couldn't be added
    # literal[False] means that something internally went wrong
    @requires_initialization(auto_init=True, default_return=False)
    def create(self, tracked_product: TrackedProductCreate) -> TrackedProductPublic | None | Literal[False]:
        assert self.data is not None
        try:
            names: list[str] | None = (
                [tag.name for tag in tracked_product.tags_name] if tracked_product.tags_name else None
            )

            # pass the names to the add_tag
            result: PublicTag | list[PublicTag] | Literal[False] = self.TAG_SERVICES.add_tag(tags=names)

            if result is not False:
                # validate that it is a list
                if isinstance(result, list):
                    ids = [tag.id for tag in result]
                    data = TrackedProductInternal.model_validate(tracked_product.model_dump(exclude={"tags_name"}))
                    data.tags_id = ids
                    self.data["tracked_products"].append(data.model_dump(mode="json"))
                    self.data["version"] += 1
                    self.data["last_updated"] = datetime.now(UTC).isoformat()

                    if self._save():
                        logger.info(f"Tracked Product added: {data.name} (v{self.data['version']})")
                        pyload = {**data.model_dump(exclude={"tags_id", "owner_id"}), "tags": result}
                        return TrackedProductPublic.model_validate(pyload)
                    return None

                if isinstance(result, PublicTag):
                    data: TrackedProductInternal = TrackedProductInternal.model_validate(
                        tracked_product.model_dump(exclude={"tags_name"})
                    )
                    data.tags_id.append(result.id)
                    self.data["tracked_products"].append(data.model_dump(mode="json"))
                    self.data["version"] += 1
                    self.data["last_updated"] = datetime.now(UTC).isoformat()

                    if self._save():
                        logger.info(f"Tracked Product added: {data.name} (v{self.data['version']})")
                        pyload = {**data.model_dump(exclude={"tags_id", "owner_id"}), "tags": [result]}
                        return TrackedProductPublic.model_validate(pyload)
                return None
            return None

        except Exception as e:
            logger.error(f"Failed to create tracked product: {e}")
            return False

    @requires_initialization(default_return=False)
    def remove(self, tracked_product_id: uuid.UUID) -> bool:
        assert self.data is not None
        if matched := next((tp for tp in self.data["tracked_products"] if tp["id"] == tracked_product_id), None):
            self.data["tracked_products"].remove(matched)

            if self._save():
                logger.info(f"Tracked product removed: {tracked_product_id} (v{self.data['version']})")
                return True

        return False

    @requires_initialization(default_return=False)
    def update(self, tracked_product_id: uuid.UUID, **kwargs):
        assert self.data is not None

        try:
            tracked_product: Any | None = next(
                (tp for tp in self.data["tracked_products"] if tp["id"] == tracked_product_id), None
            )

            if not tracked_product:
                logger.warning(f"Tracked product not found: {tracked_product_id}")
                return False

            tracked_product.update(kwargs)
            tracked_product["updated_at"] = datetime.now(UTC)
            self.data["version"] += 1
            self.data["last_updated"] = datetime.now(UTC).isoformat()

            if self._save():
                logger.info(f"Tracked product updated: {tracked_product_id} (v{self.data['version']})")
                return True
        except Exception as e:
            logger.error(f"Failed to update tracked product: {e}")
            return False

    @requires_initialization(default_return=None)
    def get(self, tracked_product_id: uuid.UUID) -> TrackedProductPublic | None:
        assert self.data is not None
        return (
            TrackedProductPublic.model_validate(
                {k: v for k, v in tracked_data.items() if k not in ("tags_id", "owner_id")}
                | {"tags": [self.TAG_SERVICES.get_tag(tag_id=tag_id) for tag_id in tracked_data["tags_id"]]}
            )
            if (
                tracked_data := next(
                    filter(lambda tracked: tracked["id"] == tracked_product_id, self.data["tracked_products"]),
                    None,
                )
            )
            else None
        )

    # this method needs to chang because the data returned is not allowed, data here has fields that are private
    # this data needs to live in the server
    def get_all(self) -> list[TrackedProductPublic]:
        assert self.data is not None
        return [
            TrackedProductPublic.model_validate(
                {k: v for k, v in product.items() if k not in ("tags_id", "owner_id")}
                | {"tags": [self.TAG_SERVICES.get_tag(tag_id=tag_id) for tag_id in product["tags_id"]]}
            )
            for product in self.data["tracked_products"]
        ]
