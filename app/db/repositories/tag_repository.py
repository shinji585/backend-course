import uuid
from collections.abc import Sequence
from logging import Logger

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError, OperationalError, PendingRollbackError, StatementError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import Tag

logger: Logger = get_logger(__name__)


class TagRepository:
    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def save(self, tag: dict) -> bool | None:
        try:
            self.session.add(Tag(**tag))
            self.session.flush()
            return True
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to save tag due to database integrity constraint: {e}")
            return None
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while saving tags: {e}")
            return None
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while saving tag: {e}")
            return None

    def save_many(self, tags: list[dict]) -> bool | None:
        try:
            self.session.add_all(Tag(**tag) for tag in tags)
            self.session.flush()
            return True
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to save tags due to database integrity constraint: {e}")
            return None
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while saving tags: {e}")
            return None
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while saving tags: {e}")
            return None

    def get_by_id(self, tag_id: uuid.UUID) -> Tag | None:
        try:
            return self.session.get(Tag, tag_id)
        except PendingRollbackError as e:
            self.session.rollback()
            logger.error(f"Session was left in an invalid state, rolled back: {e}")
            return None
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while getting tag: {e}")
            return None
        except StatementError as e:
            self.session.rollback()
            logger.error(f"Malformed statement while getting tag: {e}")
            return None
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while getting tag: {e}")
            return None

    def get_by_name(self, name: str) -> Tag | None:
        try:
            return self.session.scalars(select(Tag).where(Tag.name == name)).first()
        except PendingRollbackError as e:
            self.session.rollback()
            logger.error(f"Session was left in an invalid state, rolled back: {e}")
            return None
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while getting tag: {e}")
            return None
        except StatementError as e:
            self.session.rollback()
            logger.error(f"Malformed statement while getting tag: {e}")
            return None
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while getting tag: {e}")
            return None

    def list_all(self, offset: int, limit: int) -> Sequence[Tag]:
        try:
            stmt: Select[tuple[Tag]] = select(Tag).offset(offset).limit(limit)
            return self.session.scalars(stmt).all()
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while listing tags: {e}")
            return []
        except PendingRollbackError as e:
            self.session.rollback()
            logger.error(f"Session was left in an invalid state, rolled back: {e}")
            return []
        except StatementError as e:
            self.session.rollback()
            logger.error(f"Malformed statement while listing tags: {e}")
            return []
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while listing tags: {e}")
            return []

    def delete(self, tag_id: uuid.UUID) -> bool:
        try:
            tag: Tag | None = self.session.get(Tag, tag_id)
            if tag is None:
                return False

            self.session.delete(tag)
            self.session.flush()
            return True
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to delete tag due to database integrity constraint: {e}")
            return False
        except OperationalError as e:
            self.session.rollback()
            logger.error(f"Database operational error while deleting tag: {e}")
            return False
        except PendingRollbackError as e:
            self.session.rollback()
            logger.error(f"Session was left in an invalid state, rolled back: {e}")
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error while deleting tag: {e}")
            return False
