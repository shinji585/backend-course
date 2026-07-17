import sqlite3
from logging import Logger
from pathlib import Path

from app.core.logging import get_logger
from app.schemas.tracked.public import TrackedProductPublic

logger: Logger = get_logger(__name__)


class TrackedProductRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor = connection.cursor()
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
        except sqlite3.OperationalError as e:
            logger.critical(f"Failed to initialize database: {e}")

    def create(self, data: dict) -> TrackedProductPublic | None:
        sql = """
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

        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
                cursor = connection.cursor()

                cursor.execute(sql, data)

                return TrackedProductPublic.model_validate(data)
        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity violatin (e.g., duplicate ID or foreign key fail): {e}")
            return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error during insertion: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during insertion: {e}")
            return None
