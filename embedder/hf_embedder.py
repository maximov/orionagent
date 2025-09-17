from __future__ import annotations
from typing import List, Any

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    _HUGGINGFACE_SOURCE = "langchain_huggingface"
except Exception:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    _HUGGINGFACE_SOURCE = "langchain_community"

from .base import BaseEmbedder, SupportsLangChainEmbedding


class HFEmbedder(BaseEmbedder):
    def __init__(self,
                 model_name: str = "sentence-transformers/all-mpnet-base-v2",
                 device: str = "cpu",
                 normalize_embeddings: bool = False,
                 **kwargs: Any) -> None:
        self.model_name = model_name
        self.device = device
        self.normalize = normalize_embeddings

        self._embedding: SupportsLangChainEmbedding = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": self.device},
            encode_kwargs={"normalize_embeddings": self.normalize},
            **kwargs,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedding.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embedding.embed_query(text)

    def as_langchain(self) -> SupportsLangChainEmbedding:
        return self._embedding

    def __repr__(self) -> str:
        return f"HFEmbedder(source={_HUGGINGFACE_SOURCE}, model='{self.model_name}', device='{self.device}', normalize={self.normalize})"
