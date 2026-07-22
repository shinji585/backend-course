from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from app.db.base import Base

BASE_DIR: Path = Path(__file__).resolve().parent
BASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH: Path = BASE_DIR / "data" / "trackbuy.db"

engine: Engine = create_engine(url=f"sqlite:///{DATABASE_PATH}")

SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine, autoflush=False, expire_on_commit=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:  # noqa: UP043
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
