import sqlite3
import uuid
from logging import Logger
from pathlib import Path
from typing import Any

from app.core.logging import get_logger

logger: Logger = get_logger(__name__)


class TrackedProductRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tracked_products (
                        id                      UUID PRIMARY KEY,
                        owner_id                UUID,                             
                        name                    TEXT NOT NULL,
                        description             TEXT,                             
                        quantity                INTEGER NOT NULL DEFAULT 1,
                        target_price_amount     NUMERIC(12, 2) NOT NULL,
                        target_price_currency   TEXT NOT NULL,
                        current_price_amount    NUMERIC(12, 2),                   
                        current_price_currency  TEXT,                              
                        status                  TEXT NOT NULL DEFAULT 'tracking'
                                                    CHECK (status IN ('tracking', 'paused', 'purchased', 'cancelled')),
                        created_at              TEXT NOT NULL,
                        updated_at              TEXT,                              
                        FOREIGN KEY (owner_id) REFERENCES users (id)
                    );
                """)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracked_product_tags (
                    tracked_product_id UUID NOT NULL,
                    tag_id             UUID NOT NULL,
                    PRIMARY KEY (tracked_product_id, tag_id),
                    FOREIGN KEY (tracked_product_id) REFERENCES tracked_products (id),
                    FOREIGN KEY (tag_id) REFERENCES tags (id)
                );
            """)
        except sqlite3.OperationalError as e:
            logger.critical(f"Failed to initialize database: {e}")

    def save(self, data: dict) -> None | dict[Any, Any]:
        product_sql = """
            INSERT INTO tracked_products (
                id, owner_id, name, description, quantity, 
                target_price_amount, target_price_currency, 
                current_price_amount, current_price_currency, 
                status, created_at, updated_at
            ) VALUES (
                :id, :owner_id, :name, :description, :quantity, 
                :target_price_amount, :target_price_currency, 
                :current_price_amount, :current_price_currency, 
                :status, :created_at, :updated_at
            );
        """
        tag_link_sql = """
        INSERT INTO tracked_product_tags (tracked_product_id, tag_id)
        VALUES (:tracked_product_id, :tag_id);
        """

        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(product_sql, data)

                for tag_id in data.get("tags_id", []):
                    cursor.execute(tag_link_sql, {"tracked_product_id": data["id"], "tag_id": tag_id})

                return self.find_by_id(data["id"])
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to save tracked product due to database integrity constraint: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while saving tracked product: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while saving tracked product: {e}")
            return None

    def find_all(self) -> list[dict[str, Any]]:
        sql = """
            SELECT tp.*, tpt.tag_id
            FROM tracked_products tp
            LEFT JOIN tracked_product_tags tpt ON tpt.tracked_product_id = tp.id
        """

        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                connection.row_factory = lambda cursor, row: sqlite3.Row(cursor, row)  # type: ignore
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(sql)
                rows: list[Any] = cursor.fetchall()

                products = {}
                for row in rows:
                    row_dict = dict(row)
                    product_id = row_dict["id"]
                    tag_id = row_dict.pop("tag_id")

                    if product_id not in products:
                        products[product_id] = {**row_dict, "tags_id": []}
                    if tag_id is not None:
                        products[product_id]["tags_id"].append(tag_id)

                return list(products.values())
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while finding all tracked products: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while finding all tracked products: {e}")
            return []

    def find_by_id(self, tracked_product_id: uuid.UUID) -> None | dict[Any, Any]:
        sql = """
            SELECT tp.*, tpt.tag_id
            FROM tracked_products tp
            LEFT JOIN tracked_product_tags tpt ON tpt.tracked_product_id = tp.id
            WHERE tp.id = :id
        """

        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                connection.row_factory = lambda cursor, row: sqlite3.Row(cursor, row)  # type: ignore
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(sql, {"id": tracked_product_id})
                rows: Any = cursor.fetchall()

                if not rows:
                    return None

                product = dict(rows[0])
                tag_id = product.pop("tag_id")
                product["tags_id"] = [tag_id] if tag_id else []

                for row in rows[1:]:
                    if row["tag_id"] is not None:
                        product["tags_id"].append(row["tag_id"])

                return product
        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity error while finding tracked product by id: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while finding tracked product by id: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while finding tracked product by id: {e}")
            return None

    def update(self, tracked_product_id: uuid.UUID, data: dict) -> None | bool:

        if not data:
            return None

        set_clause: str = ", ".join(f"{field} = :{field}" for field in data)
        params: dict[Any, Any] = {**data, "tracked_product_id": tracked_product_id}
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor: sqlite3.Cursor = connection.cursor()
                cursor.execute(f"UPDATE tracked_products SET {set_clause} WHERE id = :tracked_product_id", params)

                if cursor.rowcount == 0:
                    return None
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to update tracked product due to database integrity constraint: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while updating tracked product: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while updating tracked product: {e}")
            return None

    def delete(self, tracked_product_id: uuid.UUID) -> None | bool:
        sql = """
        DELETE FROM tracked_products WHERE id = :tracked_product_id
        """
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor = connection.cursor()
                cursor.execute(sql, (tracked_product_id,))
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to delete tracked product due to database integrity constraint: {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error while deleting tracked product: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while deleting tracked product: {e}")
            return None
