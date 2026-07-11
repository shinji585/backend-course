import json
from collections.abc import Callable
from functools import wraps
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


def requires_initialization(
    default_return: Any = None,
    *,
    default_factory: Callable[[], Any] | None = None,
    auto_init: bool = False,
):
    """Decorator factory to ensure repository data is initialized before use.

    - If `self.data` is None, tries to load from JSON file.
    - If the file is missing/invalid, uses `default_factory` or `default_return`.
    - When `auto_init` is True, persists initialized data back to disk.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if getattr(self, "data", None) is None:
                try:
                    if self.path.exists():
                        logger.debug("Loading data from %s", self.path)
                        with self.path.open("r", encoding="utf-8") as f:
                            self.data = json.load(f)
                    else:
                        logger.info("Data file %s does not exist", self.path)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in %s; reinitializing", self.path)
                    self.data = None

                if self.data is None:
                    if default_factory is not None:
                        self.data = default_factory()
                    else:
                        self.data = default_return

                    if auto_init:
                        logger.info("Initializing data file %s", self.path)
                        self.path.parent.mkdir(parents=True, exist_ok=True)
                        with self.path.open("w", encoding="utf-8") as f:
                            json.dump(self.data, f, indent=2)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
