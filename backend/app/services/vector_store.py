import chromadb
from chromadb.config import Settings
from app.config import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def _get_collection() -> chromadb.Collection:
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"embed_model": EMBED_MODEL, "hnsw:space": "cosine"},
        )
    return _collection


def validate_embed_model() -> None:
    col = _get_collection()
    stored = col.metadata.get("embed_model")
    if stored and stored != EMBED_MODEL:
        raise RuntimeError(
            f"ChromaDB collection was created with embed model '{stored}' "
            f"but current OPENAI_EMBED_MODEL is '{EMBED_MODEL}'. "
            "Re-index all documents or point CHROMA_PATH to an empty directory."
        )


def upsert_chunks(
    doc_id: str,
    filename: str,
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:
    col = _get_collection()
    ids = [f"{doc_id}_{c['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "doc_id": doc_id,
            "filename": filename,
            "chunk_index": c["chunk_index"],
            "page_number": c["page_number"],
        }
        for c in chunks
    ]
    col.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def all_indexed_docs() -> list[dict]:
    """Return unique {doc_id, filename} pairs currently stored in the collection."""
    col = _get_collection()
    if col.count() == 0:
        return []
    results = col.get(include=["metadatas"])
    seen: set[str] = set()
    docs = []
    for meta in results["metadatas"]:
        if meta["doc_id"] not in seen:
            seen.add(meta["doc_id"])
            docs.append({"doc_id": meta["doc_id"], "filename": meta["filename"]})
    return docs


def query_chunks(
    query_embedding: list[float],
    top_k: int,
    ready_doc_ids: list[str],
) -> list[dict]:
    col = _get_collection()
    if not ready_doc_ids:
        return []
    total = col.count()
    if total == 0:
        return []

    # Use $eq for single doc to avoid ChromaDB $in quirks with one element
    if len(ready_doc_ids) == 1:
        where = {"doc_id": {"$eq": ready_doc_ids[0]}}
    else:
        where = {"doc_id": {"$in": ready_doc_ids}}

    try:
        results = col.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, total),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        return []

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text": doc,
                "filename": meta["filename"],
                "doc_id": meta["doc_id"],
                "chunk_index": meta["chunk_index"],
                "page_number": meta["page_number"],
                "similarity": 1 - dist,
            }
        )
    return chunks


def delete_doc_chunks(doc_id: str) -> None:
    col = _get_collection()
    col.delete(where={"doc_id": doc_id})
