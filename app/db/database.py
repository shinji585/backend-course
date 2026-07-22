from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

BASE_DIR: Path = Path(__file__).resolve().parent

DATABASE_PATH: Path = BASE_DIR / "data" / "trackbuy.db"

engine: Engine = create_engine(url=f"sqlite:///{DATABASE_PATH}")

SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine, autoflush=False, expire_on_commit=True)


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
