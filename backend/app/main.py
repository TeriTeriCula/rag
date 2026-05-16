import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import OPENAI_API_KEY, CHROMA_PATH
from app.routers import documents, query
from app.services import vector_store, status_store

app = FastAPI(title="RAG System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(query.router)


@app.on_event("startup")
async def startup() -> None:
    if not OPENAI_API_KEY:
        sys.exit("FATAL: OPENAI_API_KEY environment variable is not set.")
    try:
        vector_store.validate_embed_model()
        # Restore any documents that were indexed in a previous server session
        for doc in vector_store.all_indexed_docs():
            status_store.restore_record(doc["doc_id"], doc["filename"])
    except RuntimeError as exc:
        sys.exit(f"FATAL: {exc}")


@app.get("/debug/info")
async def debug_info():
    """Shows what's in the status store and ChromaDB — useful for diagnosing retrieval issues."""
    col_count = vector_store._get_collection().count()
    records = status_store.all_records()
    return {
        "chroma_total_chunks": col_count,
        "status_store_docs": [
            {"doc_id": r.doc_id, "filename": r.filename, "status": r.status}
            for r in records
        ],
        "ready_doc_ids": status_store.ready_doc_ids(),
    }


# Serve built frontend if dist/ exists
_static_dir = Path(__file__).parent.parent / "static"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")
