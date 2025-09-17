from __future__ import annotations
from typing import Sequence, Optional, Dict, Any, List, Union, TYPE_CHECKING


try:
    from langchain_qdrant import Qdrant as LCQdrant
except Exception:
    from langchain_community.vectorstores import Qdrant as LCQdrant

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams
except Exception as e:
    raise ImportError("Нужны пакеты qdrant-client и langchain-(qdrant|community)") from e

from .base import BaseVectorStore

if TYPE_CHECKING:
    from embedder.base import BaseEmbedder, SupportsLangChainEmbedding
else:
    BaseEmbedder = object               # заглушки
    SupportsLangChainEmbedding = object


class QdrantVectorStore(BaseVectorStore):
    def __init__(
        self,
        embeddings: Union[BaseEmbedder, SupportsLangChainEmbedding],
        url: str = "http://localhost:6333",
        collection_name: str = "rag_demo",
        api_key: Optional[str] = None,
        prefer_grpc: bool = False,
        distance: Distance = Distance.COSINE,
    ) -> None:
        emb = embeddings.as_langchain() if hasattr(embeddings, "as_langchain") else embeddings

        self._client = QdrantClient(url=url, api_key=api_key, prefer_grpc=prefer_grpc)
        self._ensure_collection(collection_name, emb, distance)


        self._db = LCQdrant(
            client=self._client,
            collection_name=collection_name,
            embeddings=emb,
        )

    def add_texts(
        self,
        texts: Sequence[str],
        metadatas: Optional[Sequence[Dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> int:
        self._db.add_texts(list(texts), metadatas=metadatas, ids=ids)
        return len(texts)

    def search(self, query: str, k: int = 4) -> List[str]:
        docs = self._db.similarity_search(query, k=k)
        return [d.page_content for d in docs]

    def raw(self):
        return self._db

    def _ensure_collection(self, name: str, emb_obj: Any, distance: Distance) -> None:
        """Создаёт коллекцию, если её нет. Размер вектора определяем через embed_query()."""
        try:
            self._client.get_collection(name)
            return  
        except Exception:
            pass

        if not hasattr(emb_obj, "embed_query"):
            raise RuntimeError("Embedding object must provide embed_query(text) → List[float]")

        probe = emb_obj.embed_query("dimension probe")
        if not probe or not isinstance(probe, list):
            raise RuntimeError("Failed to determine vector dimension from embedder")
        dim = len(probe)

        try:
            self._client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=dim, distance=distance),
            )
        except Exception:
            try:
                self._client.get_collection(name)
            except Exception as e:
                raise
