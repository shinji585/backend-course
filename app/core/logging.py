import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logger"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "application.log"

try:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
    )
except PermissionError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
