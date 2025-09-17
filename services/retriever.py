from __future__ import annotations
from typing import Optional, Sequence, Dict, Any, List

from core.config import settings
from core.logging import get_logger

from vectorstores.factory import make_store
from vectorstores.base import BaseVectorStore

from domain.rag import DocumentChunk, RetrievalResult


class Retriever:
    def __init__(self, store: Optional[BaseVectorStore] = None, top_k: int = 3) -> None:
        self.log = get_logger("retriever")
        self.store = store or make_store(getattr(settings, "VS_PROVIDER", "chroma"))
        self.top_k = int(top_k)

    @property
    def available(self) -> bool:
        return self.store is not None

    def index(
        self,
        texts: Sequence[str],
        metadatas: Optional[Sequence[Dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> int:
        if not self.store:
            raise RuntimeError("VectorStore недоступен (VS_PROVIDER=none?)")
        added = self.store.add_texts(texts, metadatas=metadatas, ids=ids)
        self.log.info("indexed %d docs into store", added)
        return added

    def retrieve(self, query: str, k: Optional[int] = None) -> RetrievalResult:
        if not self.store:
            raise RuntimeError("VectorStore недоступен (VS_PROVIDER=none?)")
        kk = int(k or self.top_k)
        contents: List[str] = self.store.search(query, k=kk)

        chunks = [
            DocumentChunk(content=c, source=None, score=None) 
            for c in contents
        ]
        rr = RetrievalResult(query=query, chunks=chunks, k=kk, model_name=getattr(settings, "EMB_MODEL", None))
        return rr
