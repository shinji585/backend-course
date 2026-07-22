from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories.tag_repository import TagRepository
from app.db.repositories.tracked_product_repository import TrackedProductRepository
from app.services.tags import TagsServices
from app.services.trackedProduct import TrackedProductServices


def get_tag_repository(db: Session = Depends(get_db)) -> TagRepository:
    return TagRepository(db)


def get_tracked_product_repository(
    db: Session = Depends(get_db),
) -> TrackedProductRepository:
    return TrackedProductRepository(db)


def get_tag_services(repo: TagRepository = Depends(get_tag_repository)) -> TagsServices:
    return TagsServices(repo)


def get_tracked_product_services(
    repo: TrackedProductRepository = Depends(get_tracked_product_repository),
    tag_services: TagsServices = Depends(get_tag_services),
) -> TrackedProductServices:
    return TrackedProductServices(repo, tag_services)
