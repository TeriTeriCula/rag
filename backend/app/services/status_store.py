import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class DocumentRecord:
    doc_id: str
    filename: str
    status: str  # processing | ready | failed
    uploaded_at: str
    error: str | None = None


_store: dict[str, DocumentRecord] = {}


def create_record(filename: str) -> str:
    doc_id = str(uuid.uuid4())
    _store[doc_id] = DocumentRecord(
        doc_id=doc_id,
        filename=filename,
        status="processing",
        uploaded_at=datetime.now(timezone.utc).isoformat(),
    )
    return doc_id


def set_ready(doc_id: str) -> None:
    if doc_id in _store:
        _store[doc_id].status = "ready"


def set_failed(doc_id: str, error: str) -> None:
    if doc_id in _store:
        _store[doc_id].status = "failed"
        _store[doc_id].error = error


def get_record(doc_id: str) -> DocumentRecord | None:
    return _store.get(doc_id)


def all_records() -> list[DocumentRecord]:
    return list(_store.values())


def delete_record(doc_id: str) -> bool:
    return _store.pop(doc_id, None) is not None


def ready_doc_ids() -> list[str]:
    return [r.doc_id for r in _store.values() if r.status == "ready"]


def restore_record(doc_id: str, filename: str) -> None:
    """Re-add a document that is already indexed in ChromaDB but lost from the in-memory store."""
    if doc_id not in _store:
        _store[doc_id] = DocumentRecord(
            doc_id=doc_id,
            filename=filename,
            status="ready",
            uploaded_at="(restored)",
        )
