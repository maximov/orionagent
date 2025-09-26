# embedder/factory.py
from __future__ import annotations
from typing import Optional

from .base import BaseEmbedder
from .hf_embedder import HFEmbedder  # предполагаем, что доступен

try:
    # Ленивая загрузка конфигурации из core
    from core.config import settings  # type: ignore
except ImportError:
    settings = None  # type: ignore


def _to_bool(v: object, default: bool = False) -> bool:
    # Приведение "1/true/yes/on" → True; иное → False; None → default
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "on"}


def make_embedder(
    model_name: Optional[str] = None,
    device: Optional[str] = None,
    normalize_embeddings: Optional[bool] = None,
) -> BaseEmbedder:
    if settings is not None:
        model_name = model_name or getattr(settings, "EMB_MODEL", "sentence-transformers/all-mpnet-base-v2")
        device = device or getattr(settings, "EMB_DEVICE", "cpu")
        norm_default = getattr(settings, "EMB_NORMALIZE", False)
        normalize_embeddings = _to_bool(
            normalize_embeddings if normalize_embeddings is not None else norm_default, False
        )
    else:
        model_name = model_name or "sentence-transformers/all-mpnet-base-v2"
        device = device or "cpu"
        normalize_embeddings = _to_bool(normalize_embeddings, False)

    if not isinstance(model_name, str) or not model_name:
        raise ValueError("Некорректный EMB_MODEL: ожидается непустая строка")
    if not isinstance(device, str) or not device:
        raise ValueError("Некорректный EMB_DEVICE: ожидается непустая строка")

    return HFEmbedder(
        model_name=model_name,
        device=device,
        normalize_embeddings=bool(normalize_embeddings),
    )
