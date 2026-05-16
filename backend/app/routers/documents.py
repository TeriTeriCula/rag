import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.services import status_store, parser as doc_parser, chunker, embedder, vector_store

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

router = APIRouter(prefix="/documents", tags=["documents"])


async def _run_ingestion(doc_id: str, filename: str, data: bytes) -> None:
    try:
        pages = doc_parser.parse(filename, data)
        if not pages:
            status_store.set_failed(doc_id, "Document contains no extractable text")
            return

        chunks = chunker.chunk_pages(pages)
        if not chunks:
            status_store.set_failed(doc_id, "Document produced no text chunks")
            return

        texts = [c["text"] for c in chunks]
        embeddings = await embedder.embed_texts(texts)
        vector_store.upsert_chunks(doc_id, filename, chunks, embeddings)
        status_store.set_ready(doc_id)
    except Exception as exc:
        status_store.set_failed(doc_id, str(exc))


@router.post("", status_code=202)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=422, detail="Document contains no extractable text")

    doc_id = status_store.create_record(file.filename)
    background_tasks.add_task(_run_ingestion, doc_id, file.filename, data)
    return {"doc_id": doc_id, "status": "processing"}


@router.get("/{doc_id}/status")
async def get_status(doc_id: str):
    record = status_store.get_record(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"doc_id": doc_id, "status": record.status, "error": record.error}


@router.get("")
async def list_documents():
    records = status_store.all_records()
    return [
        {
            "doc_id": r.doc_id,
            "filename": r.filename,
            "status": r.status,
            "uploaded_at": r.uploaded_at,
            "error": r.error,
        }
        for r in records
    ]


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: str):
    record = status_store.get_record(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    vector_store.delete_doc_chunks(doc_id)
    status_store.delete_record(doc_id)
