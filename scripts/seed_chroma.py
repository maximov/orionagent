from __future__ import annotations
from core.config import settings
from vectorstores.factory import make_store

DOCS = [
    "Раздел 1. RAG используется для интеграции wiki",
    "Раздел 2. Chroma - векторная БД имеет мягкий лимит 10М",
    "Раздел 3. Pinecone - для храненя и работы с векторами в облаке",
    "Раздел 4. Qdrant - векторная БД с быстрым посиком имеет мягкий лимит 100М",
]

def main():
    print(f"[seed_chroma] CHROMA_DIR={settings.CHROMA_DIR}")
    store = make_store("chroma")
    if store is None:
        raise RuntimeError("VectorStore factory вернул None")

    added = store.add_texts(DOCS)
    print(f"[seed_chroma] Загружено документов: {added}")

    query = "Что такое Chroma?"
    results = store.search(query, k=3)
    print(f"[seed_chroma] Результаты для запроса: {query!r}")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r}")

if __name__ == "__main__":
    main()
