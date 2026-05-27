import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from backend.config import settings


def setup_logger():
    project_root = Path(__file__).resolve().parents[1]
    log_dir = project_root / settings.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "server.log"

    logger = logging.getLogger("llm-serving-platform")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
