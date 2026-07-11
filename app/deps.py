from functools import lru_cache
from pathlib import Path

from app.services.trackedProduct import TrackedProductServices

DATA_DIR: Path = Path(__file__).absolute().parent / "db" / "data"


@lru_cache
def get_tracked_product_services() -> TrackedProductServices:
    return TrackedProductServices(config_path=DATA_DIR / "TrackedProduct.json")
