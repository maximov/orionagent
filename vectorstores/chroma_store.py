from __future__ import annotations
from typing import Sequence, Optional, Dict, Any, List, Union, TYPE_CHECKING
from pathlib import Path

try:
    from langchain_chroma import Chroma as LCChroma
except Exception:
    from langchain_community.vectorstores import Chroma as LCChroma  # fallback

from .base import BaseVectorStore

if TYPE_CHECKING:
    from embedder.base import BaseEmbedder, SupportsLangChainEmbedding
else:
    BaseEmbedder = object               # заглушки
    SupportsLangChainEmbedding = object


class ChromaVectorStore(BaseVectorStore):

    def __init__(
        self,
        embeddings: Union[BaseEmbedder, SupportsLangChainEmbedding],
        persist_directory: str = "./chroma_store",
        collection_name: Optional[str] = "ai_agent",
    ) -> None:
        emb = embeddings.as_langchain() if hasattr(embeddings, "as_langchain") else embeddings

        persist = Path(persist_directory)
        persist.mkdir(parents=True, exist_ok=True)

        name = collection_name or "ai_agent"
        self._db = LCChroma(
            collection_name=name,
            persist_directory=str(persist),
            embedding_function=emb,
        )

    def add_texts(
        self,
        texts: Sequence[str],
        metadatas: Optional[Sequence[Dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> int:
        self._db.add_texts(list(texts), metadatas=metadatas, ids=ids)
        try:
            self._db.persist()
        except Exception:
            pass
        return len(texts)

    def search(self, query: str, k: int = 4) -> List[str]:
        docs = self._db.similarity_search(query, k=k)
        return [d.page_content for d in docs]

    def raw(self):
        return self._db
