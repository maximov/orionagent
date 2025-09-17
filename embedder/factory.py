from __future__ import annotations
from typing import Optional
from .hf_embedder import HFEmbedder
from .base import BaseEmbedder

try:
    # Ленивая загрузка конфигурации из core
    from core.config import settings
except Exception:
    settings = None


def make_embedder(model_name: Optional[str] = None,
                  device: Optional[str] = None,
                  normalize_embeddings: Optional[bool] = None) -> BaseEmbedder:

    if settings:
        model_name = model_name or getattr(settings, "EMB_MODEL", "sentence-transformers/all-mpnet-base-v2")
        device = device or getattr(settings, "EMB_DEVICE", "cpu")
        normalize_embeddings = normalize_embeddings if normalize_embeddings is not None else getattr(settings, "EMB_NORMALIZE", False)
    else:
        model_name = model_name or "sentence-transformers/all-mpnet-base-v2"
        device = device or "cpu"
        normalize_embeddings = normalize_embeddings if normalize_embeddings is not None else False

    return HFEmbedder(
        model_name=model_name,
        device=device,
        normalize_embeddings=normalize_embeddings,
    )
