# core/utils.py
from __future__ import annotations
from typing import Iterator

TELEGRAM_LIMIT = 4096
RESERVE = 16
ELLIPSIS = "…"  # единый суффикс для обрезки


def chunk(text: str, limit: int = TELEGRAM_LIMIT - RESERVE) -> Iterator[str]:
    if not text:
        return
    step = max(1, int(limit))
    for i in range(0, len(text), step):
        yield text[i : i + step]


def sanitize(text: str) -> str:
    """
    Удаляем управляющие символы < ' ' (кроме \n, \t).
    """
    if not text:
        return ""
    # text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "".join(ch for ch in text if (ch >= " " or ch in "\n\t"))


def clamp(text: str | None, max_len: int, suffix: str = ELLIPSIS) -> str:
    """
    Обрезаем строку до max_len символов с суффиксом (по умолчанию …).
    """
    if not text:
        return ""
    if max_len <= 0:
        return ""
    if len(text) <= max_len:
        return text
    if not suffix:
        return text[:max_len]
    if max_len <= len(suffix):
        return suffix[:max_len]
    return text[: max_len - len(suffix)] + suffix
