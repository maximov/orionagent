from __future__ import annotations
import logging
import os

DEFAULT_FMT = "[%(levelname)s] %(asctime)s %(name)s: %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

def setup_logging(level: str | None = None) -> None:
    
    lvl = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    logging.basicConfig(
        level=getattr(logging, lvl, logging.INFO),
        format=DEFAULT_FMT,
        datefmt=DEFAULT_DATEFMT,
    )
    # Uvicorn логгеры
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(name).setLevel(getattr(logging, lvl, logging.INFO))

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
