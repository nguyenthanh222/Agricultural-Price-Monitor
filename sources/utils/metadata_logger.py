import logging
import datetime
from pathlib import Path

from config import settings


def setup_logger():
    LOG_DIR = settings.ROOT_DIR / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "pipeline.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("pipeline")


def log_step(name: str, status: str, message: str = ""):
    logger = setup_logger()
    logger.info(f"{name} - {status}: {message}")
