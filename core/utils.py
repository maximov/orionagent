
from __future__ import annotations

TELEGRAM_LIMIT = 4096
RESERVE = 16

def chunk(text: str, limit: int = TELEGRAM_LIMIT - RESERVE):
    if not text:
        return
    for i in range(0, len(text), limit):
        yield text[i : i + limit]

def sanitize(text: str) -> str:
    if not text:
        return ""
    return "".join(ch for ch in text if (ch >= " " or ch in "\n\t"))

def clamp(text: str, max_len: int) -> str:
    if text is None:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"
