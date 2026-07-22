import uuid
from collections.abc import Sequence
from logging import Logger

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError, OperationalError, PendingRollbackError, StatementError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import Tag, TrackedProduct

logger: Logger = get_logger(__name__)


ALLOWED_UPDATE_FIELDS: set[str] = {
    "name",
    "description",
    "quantity",
    "target_price_amount",
    "target_price_currency",
    "current_price_amount",
    "current_price_currency",
    "status",
    "updated_at",
}


class TrackedProductRepository:
    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def save(self, data: dict) -> TrackedProduct | None:
        try:
            tag_ids = data.pop("tags_id", [])

            target_price = data.pop("target_price", None)
            if target_price is None:
                logger.error("Tracked product save failed: target_price is required.")
                return None

            data["target_price_amount"] = target_price["amount"]
            data["target_price_currency"] = target_price["currency"]

            current_price = data.pop("current_price", None)
            if current_price is not None:
                data["current_price_amount"] = current_price["amount"]
                data["current_price_currency"] = current_price["currency"]
            else:
                data["current_price_amount"] = None
                data["current_price_currency"] = None

            product = TrackedProduct(**data)
            if tag_ids:
                tags: Sequence[Tag] = self.session.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all()
                product.tags = list(tags)

            self.session.add(product)
            self.session.flush()
            return product
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to save tracked product due to database integrity constraint: {e}")
            return None
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while saving tracked product: {e}")
            return None
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while saving tracked product: {e}")
            return None

    def find_all(self, offset: int = 0, limit: int = 20) -> Sequence[TrackedProduct]:
        try:
            stmt: Select[tuple[TrackedProduct]] = select(TrackedProduct).offset(offset).limit(limit)
            return self.session.scalars(stmt).all()
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while finding all tracked products: {e}")
            return []
        except PendingRollbackError as e:
            self.session.rollback()
            logger.error(f"Session was left in an invalid state, rolled back: {e}")
            return []
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while finding all tracked products: {e}")
            return []

    def find_by_id(self, tracked_product_id: uuid.UUID) -> TrackedProduct | None:
        try:
            return self.session.get(TrackedProduct, tracked_product_id)
        except PendingRollbackError as e:
            self.session.rollback()
            logger.error(f"Session was left in an invalid state, rolled back: {e}")
            return None
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while finding tracked product by id: {e}")
            return None
        except StatementError as e:
            self.session.rollback()
            logger.error(f"Malformed statement while finding tracked product by id: {e}")
            return None
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while finding tracked product by id: {e}")
            return None

    def update(self, tracked_product_id: uuid.UUID, data: dict) -> bool:
        flat_data = dict(data)

        target_price = flat_data.pop("target_price", None)
        if target_price is not None:
            flat_data["target_price_amount"] = target_price["amount"]
            flat_data["target_price_currency"] = target_price["currency"]

        current_price = flat_data.pop("current_price", None)
        if current_price is not None:
            flat_data["current_price_amount"] = current_price["amount"]
            flat_data["current_price_currency"] = current_price["currency"]

        safe_data = {k: v for k, v in flat_data.items() if k in ALLOWED_UPDATE_FIELDS}
        if not safe_data:
            return False

        try:
            product: TrackedProduct | None = self.session.get(TrackedProduct, tracked_product_id)
            if product is None:
                return False

            for field, value in safe_data.items():
                setattr(product, field, value)

            self.session.flush()
            return True
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to update tracked product due to database integrity constraint: {e}")
            return False
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while updating tracked product: {e}")
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while updating tracked product: {e}")
            return False

    def delete(self, tracked_product_id: uuid.UUID) -> bool:
        try:
            product: TrackedProduct | None = self.session.get(TrackedProduct, tracked_product_id)
            if product is None:
                return False

            self.session.delete(product)
            self.session.flush()
            return True
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to delete tracked product due to database integrity constraint: {e}")
            return False
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while deleting tracked product: {e}")
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while deleting tracked product: {e}")
            return False
