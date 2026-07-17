from functools import lru_cache
from pathlib import Path

from app.services import TrackedProductServices

DATA_DIR: Path = Path(__file__).absolute().parent / "db" / "data"


@lru_cache
def get_tracked_product_services() -> TrackedProductServices:
    return TrackedProductServices(db_path=DATA_DIR / "tracked_products.db", tags_db_path=DATA_DIR / "tags.db")
