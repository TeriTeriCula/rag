## Context

There is currently no RAG system in the project. Users who want to query their document collections must use external tools or write their own scripts. This design introduces a self-contained RAG system: a backend API service, a vector store, and a web UI — all working together to let users upload documents and get grounded, cited answers via a chat interface.

## Goals / Non-Goals

**Goals:**
- Provide a REST API for document ingestion (upload, chunk, embed, index) and querying (retrieve + generate)
- Integrate a vector database for persistent embedding storage and semantic search
- Integrate an LLM (via API) for answer generation with retrieved context
- Deliver a single-page web UI for chat interaction and document management
- Display source citations alongside generated answers
- Support PDF, TXT, and DOCX document formats

**Non-Goals:**
- Multi-tenant or user authentication (out of scope for initial release)
- Fine-tuning or training custom LLMs
- Real-time collaborative editing of documents
- Mobile-native apps (responsive web is sufficient)
- Support for non-text content (images, tables within PDFs are best-effort)

## Decisions

### 1. Backend: Python + FastAPI

**Decision:** Use Python with FastAPI for the backend service.

**Rationale:** The Python ML ecosystem (LangChain, sentence-transformers, PyMuPDF, python-docx) provides first-class support for every layer of the RAG pipeline. FastAPI gives async HTTP endpoints with auto-generated OpenAPI docs with minimal boilerplate.

**Alternatives considered:**
- Node.js + Express: Better JavaScript ecosystem alignment, but LLM/embedding libraries are less mature.
- Flask: Simpler, but lacks async support needed for streaming LLM responses.

---

### 2. Vector Store: ChromaDB (local, file-persisted)

**Decision:** Use ChromaDB as the vector store, persisted to local disk.

**Rationale:** ChromaDB runs in-process (no separate service to manage), persists to disk, and has a clean Python client. It is sufficient for single-user or small-team usage with up to millions of chunks.

**Alternatives considered:**
- Qdrant (Docker): More production-ready, but adds operational complexity.
- Pinecone (cloud): Managed, but introduces external dependency and cost.
- FAISS: Fast but in-memory only; persistence requires custom serialization.

---

### 3. Embedding Model: OpenAI `text-embedding-3-small`

**Decision:** Use OpenAI's `text-embedding-3-small` for generating embeddings.

**Rationale:** High quality, cheap, widely supported, and consistent with using OpenAI for the LLM. Consistent embedding model across ingestion and query is required for correct similarity search.

**Alternatives considered:**
- `sentence-transformers/all-MiniLM-L6-v2`: Free, local, but lower quality and requires local GPU/CPU inference setup.
- `text-embedding-ada-002`: Older OpenAI model, superseded by `text-embedding-3-small`.

---

### 4. LLM: OpenAI GPT-4o (or configurable via env var)

**Decision:** Default to GPT-4o for answer generation; model configurable via `LLM_MODEL` environment variable.

**Rationale:** GPT-4o provides strong instruction-following and context utilization. Making it configurable allows switching to Claude or a local model without code changes.

---

### 5. Chunking Strategy: Recursive character text splitter, 512 tokens, 64-token overlap

**Decision:** Chunk documents using a recursive character splitter with 512-token chunks and 64-token overlap.

**Rationale:** 512 tokens balances chunk size (enough context per chunk) with retrieval precision (smaller chunks retrieve more specifically). 64-token overlap avoids losing information at chunk boundaries.

---

### 6. Frontend: React (Vite) + Tailwind CSS

**Decision:** Build the UI as a React single-page app (SPA) served by Vite in development, built to static files for production (served by FastAPI).

**Rationale:** React is the most widely supported frontend framework with mature component libraries. Tailwind CSS enables rapid UI development without a heavy component framework. FastAPI can serve the built static files directly, eliminating a separate frontend server in production.

---

### 7. API Design: REST with streaming for query responses

**Decision:** Use REST for all endpoints. The `/query` endpoint supports Server-Sent Events (SSE) for streaming LLM token output.

**Rationale:** REST is simple and universally supported. SSE enables a perceived-fast chat experience by showing tokens as they arrive without requiring WebSocket infrastructure.

## Risks / Trade-offs

- **Embedding model lock-in** → If the embedding model changes, all existing embeddings must be re-generated. Mitigation: Store embedding model name in ChromaDB collection metadata; validate on startup and error clearly if mismatch detected.
- **OpenAI API key required** → No fallback for air-gapped environments. Mitigation: Document the `LLM_MODEL` env var for switching to Ollama (local) in README.
- **No authentication** → Any user with network access can query or delete documents. Mitigation: Accept as a known limitation for v1; add auth in a follow-up.
- **Large document ingestion is slow** → PDF parsing + chunking + embedding API calls can take minutes for large files. Mitigation: Return a `202 Accepted` with a job ID from the ingestion endpoint; poll for completion via `/documents/{id}/status`.
- **ChromaDB not suitable for high concurrency** → ChromaDB's embedded mode has limited write concurrency. Mitigation: Acceptable for v1 single-user scope; document upgrade path to Qdrant for multi-user deployments.

## Migration Plan

1. Deploy backend service (`uvicorn app.main:app`) with environment variables set (`OPENAI_API_KEY`, `CHROMA_PATH`, `LLM_MODEL`)
2. Run `npm run build` in the frontend directory; backend serves `dist/` as static files
3. Access UI at `http://localhost:8000`
4. No database migrations required (ChromaDB initializes on first run)
5. **Rollback:** Stop the process; no persistent state changes to external systems

## Open Questions

- Should document ingestion be synchronous (simpler) or async with job polling (better UX for large files)?
- What is the maximum supported document file size?
- Should conversation history persist across browser sessions (localStorage vs. backend storage)?
