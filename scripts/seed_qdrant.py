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
    print(f"[seed_qdrant] URL={settings.QDRANT_URL} collection={settings.QDRANT_COLLECTION}")
    if not settings.QDRANT_URL:
        raise RuntimeError("QDRANT_URL пуст — укажи URL инстанса Qdrant")

    store = make_store("qdrant")
    if store is None:
        raise RuntimeError("VectorStore factory вернул None (ожидался Qdrant)")

    added = store.add_texts(DOCS)
    print(f"[seed_qdrant] Загружено документов: {added}")

    query = "Зачем использовать Qdrant?"
    results = store.search(query, k=3)
    print(f"[seed_qdrant] Результаты для запроса: {query!r}")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r}")

if __name__ == "__main__":
    main()
