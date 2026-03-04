import json
from pathlib import Path

import chromadb
from loguru import logger

from backend.schemas import RetrievalChunk

DATA_DIR = Path(__file__).parent.parent / "data"

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def _get_collection() -> chromadb.Collection:
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.Client()
    _collection = _client.get_or_create_collection(
        name="astrology_knowledge",
        metadata={"hnsw:space": "cosine"},
    )

    if _collection.count() == 0:
        _ingest_knowledge()

    return _collection


def _ingest_knowledge() -> None:
    assert _collection is not None
    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    # Load JSON knowledge bases
    for filename in ["zodiac_traits.json", "planetary_impacts.json", "nakshatra_mapping.json"]:
        path = DATA_DIR / filename
        if not path.exists():
            logger.warning("Missing data file: {f}", f=filename)
            continue

        data = json.loads(path.read_text())
        source = filename.replace(".json", "")

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    text = f"{key}: " + ". ".join(f"{k}: {v}" for k, v in value.items())
                else:
                    text = f"{key}: {value}"
                doc_id = f"{source}_{key.lower().replace(' ', '_')}"
                documents.append(text)
                metadatas.append({"source": source, "key": key})
                ids.append(doc_id)

    # Load text guidance files
    for filename in ["career_guidance.txt", "love_guidance.txt", "spiritual_guidance.txt"]:
        path = DATA_DIR / filename
        if not path.exists():
            logger.warning("Missing data file: {f}", f=filename)
            continue

        source = filename.replace(".txt", "")
        lines = [l.strip() for l in path.read_text().splitlines() if l.strip()]
        for i, line in enumerate(lines):
            documents.append(line)
            metadatas.append({"source": source})
            ids.append(f"{source}_{i}")

    if documents:
        _collection.add(documents=documents, metadatas=metadatas, ids=ids)
        logger.info("Ingested {n} documents into ChromaDB", n=len(documents))


def query(features: list[str], user_question: str, n_results: int = 5) -> list[RetrievalChunk]:
    collection = _get_collection()

    # Combine features and question into query text
    query_text = f"{user_question} {' '.join(features)}"

    results = collection.query(query_texts=[query_text], n_results=n_results)

    chunks = []
    if results["documents"] and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        dists = results["distances"][0] if results["distances"] else [0.0] * len(docs)

        for doc, meta, dist in zip(docs, metas, dists):
            chunks.append(RetrievalChunk(
                text=doc,
                metadata=meta or {},
                score=round(1 - dist, 4),  # Convert distance to similarity
            ))

    logger.info("Retrieved {n} chunks for query", n=len(chunks))
    return chunks
