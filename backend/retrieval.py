import json
from pathlib import Path

import chromadb
from loguru import logger

from backend.schemas import RetrievalChunk

DATA_DIR = Path(__file__).parent.parent / "data"
CHROMA_DB_PATH = Path(__file__).parent.parent / "chroma_db"

_collection: chromadb.Collection | None = None


def init_retrieval() -> None:
    global _collection

    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    _collection = client.get_or_create_collection(
        name="astrology_knowledge",
        metadata={"hnsw:space": "cosine"},
    )

    if _collection.count() == 0:
        _ingest_knowledge()

    logger.info("ChromaDB initialized with {n} documents", n=_collection.count())


def _ingest_knowledge() -> None:
    assert _collection is not None
    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    # Planets
    planets = json.loads((DATA_DIR / "planet_meanings.json").read_text())
    for p in planets:
        doc = f"{p['name']}. {p['description']} Life domains: {', '.join(p['life_domains'])}"
        documents.append(doc)
        metadatas.append({"type": "planet", "name": p["name"], "source": "planet_meanings.json"})
        ids.append(f"planet_{p['name'].lower()}")

    # Signs
    signs = json.loads((DATA_DIR / "zodiac_sign_meanings.json").read_text())
    for s in signs:
        doc = (f"{s['name']}. {s['personality']} "
               f"Strengths: {', '.join(s['strengths'])}. "
               f"Challenges: {', '.join(s['challenges'])}")
        documents.append(doc)
        metadatas.append({"type": "sign", "name": s["name"], "source": "zodiac_sign_meanings.json"})
        ids.append(f"sign_{s['name'].lower()}")

    # Houses
    houses = json.loads((DATA_DIR / "house_meanings.json").read_text())
    for h in houses:
        doc = f"{h['name']}. {h['description']} Life domains: {', '.join(h['life_domains'])}"
        documents.append(doc)
        metadatas.append({"type": "house", "name": h["name"], "source": "house_meanings.json"})
        ids.append(f"house_{h['name'].lower().replace(' ', '_')}")

    if documents:
        _collection.add(documents=documents, metadatas=metadatas, ids=ids)
        logger.info("Ingested {n} documents into ChromaDB", n=len(documents))


def query(user_question: str, entity_type: str | None = None, entity_name: str | None = None, n_results: int = 5) -> list[RetrievalChunk]:
    if _collection is None:
        raise RuntimeError("ChromaDB not initialized — call init_retrieval() first")

    where = None
    if entity_type and entity_name:
        where = {"$and": [{"type": entity_type}, {"name": entity_name}]}
    elif entity_type:
        where = {"type": entity_type}
    results = _collection.query(query_texts=[user_question], n_results=n_results, where=where)

    chunks = []
    if results["documents"] and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        dists = results["distances"][0] if results["distances"] else [0.0] * len(docs)

        for doc, meta, dist in zip(docs, metas, dists):
            chunks.append(RetrievalChunk(
                text=doc,
                metadata=meta or {},
                score=round(1 - dist, 4),
            ))

    logger.info("Retrieved {n} chunks for query", n=len(chunks))
    return chunks
