# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional

from .base import BaseVectorStore
from .chroma_store import ChromaVectorStore
from .qdrant_store import QdrantVectorStore

# используем наш слой эмбеддингов
from embedder.factory import make_embedder

# настройки приложения
try:
    from core.config import settings
except Exception:
    settings = None


def make_store(provider: Optional[str] = None) -> Optional[BaseVectorStore]:
    prov = (provider or (getattr(settings, "VS_PROVIDER", "chroma") if settings else "chroma")).lower()

    if prov in ("none", "off", "", "disabled"):
        return None

    emb = make_embedder()
    emb_lc = emb.as_langchain()

    if prov == "chroma":
        persist_dir = getattr(settings, "CHROMA_DIR", "./chroma_store") if settings else "./chroma_store"
        collection  = getattr(settings, "CHROMA_COLLECTION", "ai_agent") if settings else "ai_agent"
        return ChromaVectorStore(embeddings=emb_lc, persist_directory=persist_dir, collection_name=collection,)

    if prov == "qdrant":
        url = getattr(settings, "QDRANT_URL", "http://localhost:6333") if settings else "http://localhost:6333"
        api_key = getattr(settings, "QDRANT_API_KEY", "") if settings else ""
        collection = getattr(settings, "QDRANT_COLLECTION", "rag_demo") if settings else "rag_demo"
        return QdrantVectorStore(embeddings=emb_lc, url=url, api_key=(api_key or None), collection_name=collection)

    raise ValueError(f"Unknown VectorStore provider: {prov}")
