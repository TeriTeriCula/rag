import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services import embedder, vector_store, status_store, llm
from app.config import TOP_K_DEFAULT

router = APIRouter(tags=["query"])

NO_DOCS_MSG = (
    "No relevant information was found in the uploaded documents. "
    "Please upload documents related to your question first, or rephrase your query."
)


class HistoryTurn(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    query: str
    history: list[HistoryTurn] = []
    top_k: int = TOP_K_DEFAULT


@router.post("/query")
async def query(request: Request, body: QueryRequest):
    ready_ids = status_store.ready_doc_ids()
    accepts_sse = "text/event-stream" in request.headers.get("accept", "")

    # No documents indexed at all — short-circuit before hitting the embedding API
    if not ready_ids:
        if accepts_sse:
            async def no_docs_stream():
                yield f"event: sources\ndata: []\n\n"
                yield f"data: {json.dumps({'token': NO_DOCS_MSG})}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(no_docs_stream(), media_type="text/event-stream")
        return {"answer": NO_DOCS_MSG, "sources": []}

    query_emb = await embedder.embed_query(body.query)
    chunks = vector_store.query_chunks(query_emb, body.top_k, ready_ids)
    history = [t.model_dump() for t in body.history]

    sources = [
        {
            "filename": c["filename"],
            "chunk_index": c["chunk_index"],
            "excerpt": c["text"][:200],
            "similarity": round(c["similarity"], 4),
        }
        for c in chunks
    ]

    # No relevant chunks found — do NOT call the LLM, return a fixed message
    if not chunks:
        no_match_msg = (
            "I could not find any relevant passages in your documents to answer this question. "
            "Try rephrasing, or upload documents that contain this information."
        )
        if accepts_sse:
            async def no_chunks_stream():
                yield f"event: sources\ndata: []\n\n"
                yield f"data: {json.dumps({'token': no_match_msg})}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(no_chunks_stream(), media_type="text/event-stream")
        return {"answer": no_match_msg, "sources": []}

    # Chunks found — call the LLM with only the retrieved context
    if accepts_sse:
        async def event_stream():
            yield f"event: sources\ndata: {json.dumps(sources)}\n\n"
            async for token in llm.generate_stream(body.query, chunks, history):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    result = await llm.generate(body.query, chunks, history)
    return {"answer": result["answer"], "sources": sources}
