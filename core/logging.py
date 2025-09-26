# core/logging.py
from __future__ import annotations
import logging
import os

DEFAULT_FMT = "[%(levelname)s] %(asctime)s %(name)s: %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

def _coerce_level(level: str | None) -> int:
    # Приводим строковый уровень к числовому; fallback -> INFO
    lvl = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    return getattr(logging, lvl, logging.INFO)

def _ensure_formatter(logger: logging.Logger, fmt: str, datefmt: str) -> None:
    # Задаём единый формат всем хендлерам логгера
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    for h in logger.handlers:
        h.setFormatter(formatter)

def setup_logging(level: str | None = None) -> None:
    """Инициализация логирования: общий формат/уровень + приведение uvicorn-логгеров."""
    lvl = _coerce_level(level)

    root = logging.getLogger()
    # Если корневой логгер уже имеет хендлеры (uvicorn/gunicorn), не полагаемся на basicConfig
    if root.handlers:
        root.setLevel(lvl)
        _ensure_formatter(root, DEFAULT_FMT, DEFAULT_DATEFMT)
    else:
        logging.basicConfig(
            level=lvl,
            format=DEFAULT_FMT,
            datefmt=DEFAULT_DATEFMT,
        )

    # Приводим uvicorn-логгеры (уровень + формат их хендлеров)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.setLevel(lvl)
        _ensure_formatter(lg, DEFAULT_FMT, DEFAULT_DATEFMT)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
