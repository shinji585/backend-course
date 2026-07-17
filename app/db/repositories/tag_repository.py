import sqlite3
import uuid
from logging import Logger
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.schemas.tags import PublicTag

logger: Logger = get_logger(__name__)


class TagRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path: Path = db_path
        self._init_db()

    def _init_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute("""
                      CREATE TABLE IF NOT EXISTS tags (
                         id         UUID PRIMARY KEY,
                         owner_id   UUID,
                         name       TEXT NOT NULL,
                         created_at TEXT NOT NULL,
                        FOREIGN KEY (owner_id) REFERENCES users (id)
                    );
               """)
        except sqlite3.OperationalError as e:
            logger.critical(f"Failed to initialize the tags table: {e}")

    def save(self, tag: dict) -> None | bool:
        sql = """
            INSERT INTO tags (
                id, owner_id, name, created_at
            ) VALUES (
                :id, :owner_id, :name, :created_at
            );
        """

        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(sql, tag)

                return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to save tag due to database integrity constraint: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while saving tag: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while saving tag: {e}")
            return None

    def find_by_id(self, tag_id: uuid.UUID) -> PublicTag | None:
        sql = """
           SELECT * FROM tags WHERE id = :tag_id
        """

        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                connection.row_factory = lambda cursor, row: sqlite3.Row(cursor, row)  # type: ignore
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(sql, {"tag_id": tag_id})
                row: Any = cursor.fetchone()

                return PublicTag.model_validate(dict(row)) if row else None

        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity error while finding tag by id: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while finding tag by id: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while finding tag by id: {e}")
            return None

    def find_by_name(self, name: str) -> PublicTag | None:
        sql = """
         SELECT * FROM tags WHERE name = :name
        """
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                connection.row_factory = lambda cursor, row: sqlite3.Row(cursor, row)  # type: ignore
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(sql, {"name": name})
                row: Any = cursor.fetchone()

                return PublicTag.model_validate(dict(row)) if row else None

        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while finding tag by name: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while finding tag by name: {e}")
            return None

    def find_all(self) -> list[PublicTag] | list[Any]:
        sql = """
           SELECT * FROM tags;
        """

        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                connection.row_factory = lambda cursor, row: sqlite3.Row(cursor, row)  # type: ignore
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(sql)
                rows: Any = cursor.fetchall()

                return [PublicTag.model_validate(dict(row)) for row in rows]

        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while finding all tags: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while finding all tags: {e}")
            return []

    def save_many(self, tags: list[dict]) -> None | bool:
        sql = """
            INSERT INTO tags (
                id, owner_id, name, created_at
            ) VALUES (
                :id, :owner_id, :name, :created_at
            );
        """
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor: sqlite3.Cursor = connection.cursor()

                for tag in tags:
                    cursor.execute(sql, tag)

                return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to save tags due to database integrity constraint: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while saving tags: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while saving tags: {e}")
            return None

    def update(self, tag_id: uuid.UUID, data: dict) -> None | bool:

        if not data:
            return None

        set_clause: str = ", ".join(f"{field} = :{field}" for field in data)
        params: dict[Any, Any] = {**data, "tag_id": tag_id}
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(f"UPDATE tags SET {set_clause} WHERE id = :tag_id", params)

                if cursor.rowcount == 0:
                    return None

            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to update tag due to database integrity constraint: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while updating tag: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while updating tag: {e}")
            return None

    def delete(self, tag_id: uuid.UUID) -> None | bool:
        sql = """
        DELETE FROM tags WHERE id = :tag_id
        """
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(sql, {"tag_id": tag_id})
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to delete tag due to database integrity constraint: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while deleting tag: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while deleting tag: {e}")
            return None
