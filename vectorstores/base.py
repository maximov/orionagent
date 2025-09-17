from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence, Dict, Any


class BaseVectorStore(ABC):
    @abstractmethod
    def add_texts(
        self,
        texts: Sequence[str],
        metadatas: Optional[Sequence[Dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> int:
        ...

    @abstractmethod
    def search(self, query: str, k: int = 4) -> List[str]:
        ...

    def raw(self) -> Any:
        return None
