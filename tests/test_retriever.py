from typing import Sequence, Optional, Dict, Any, List
from services.retriever import Retriever
from vectorstores.base import BaseVectorStore

class FakeStore(BaseVectorStore):
    def __init__(self):
        self._texts = []

    def add_texts(
        self,
        texts: Sequence[str],
        metadatas: Optional[Sequence[Dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> int:
        self._texts.extend(list(texts))
        return len(texts)

    def search(self, query: str, k: int = 4) -> List[str]:
        q = query.lower()
        hits = [t for t in self._texts if any(w and w in t.lower() for w in q.split())]
        if not hits:
            hits = list(self._texts)
        return hits[:k]

def test_retriever_index_and_search(monkeypatch):
    import vectorstores.factory as vs_factory
    monkeypatch.setattr(vs_factory, "make_store", lambda *a, **kw: FakeStore(), raising=True)

    r = Retriever(store=None, top_k=2)
    added = r.index(
        [
            "Chroma - локальная векторная база.",
            "Qdrant - продакшен-векторстор с фильтрами.",
            "RAG - Retrieval-Augmented Generation.",
        ]
    )
    assert added == 3

    rr = r.retrieve("что такое chroma?")
    assert rr.k == 2
    assert rr.chunks
    contents = [c.content for c in rr.chunks]
    assert any("Chroma" in c or "chroma" in c for c in contents)
