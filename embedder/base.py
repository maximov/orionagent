from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Protocol, Any


class SupportsLangChainEmbedding(Protocol):
    def embed_documents(self, texts: List[str]) -> List[List[float]]: ...
    def embed_query(self, text: str) -> List[float]: ...


class BaseEmbedder(ABC):

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        ...

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        ...

    @abstractmethod
    def as_langchain(self) -> SupportsLangChainEmbedding:
        ...
