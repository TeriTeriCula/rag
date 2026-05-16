## 1. Project Setup

- [x] 1.1 Initialize backend directory with Python project structure (`pyproject.toml` or `requirements.txt`)
- [x] 1.2 Add backend dependencies: `fastapi`, `uvicorn`, `chromadb`, `openai`, `langchain-text-splitters`, `PyMuPDF`, `python-docx`, `python-multipart`
- [x] 1.3 Initialize frontend directory with Vite + React + TypeScript template
- [x] 1.4 Add frontend dependencies: `tailwindcss`, `@tailwindcss/vite`, `eventsource-parser`
- [x] 1.5 Create `.env.example` with `OPENAI_API_KEY`, `CHROMA_PATH`, and `LLM_MODEL` entries
- [x] 1.6 Create top-level `docker-compose.yml` (optional) for local development convenience

## 2. Backend: Document Ingestion API

- [x] 2.1 Implement `POST /documents` endpoint accepting multipart file upload; validate file extension (pdf, txt, docx)
- [x] 2.2 Implement document parser module: PDF via PyMuPDF, TXT via plain read, DOCX via python-docx
- [x] 2.3 Implement chunking module using recursive character splitter (512 tokens, 64-token overlap)
- [x] 2.4 Implement embedding module: call OpenAI `text-embedding-3-small` for a batch of chunk texts
- [x] 2.5 Implement ChromaDB storage module: initialize collection, upsert chunks with metadata (doc_id, filename, chunk_index, page_number)
- [x] 2.6 Implement in-memory document status store (doc_id → status, error); expose `GET /documents/{id}/status`
- [x] 2.7 Wire ingestion pipeline: parse → chunk → embed → store; update status to `ready` or `failed`
- [x] 2.8 Return HTTP 400 for unsupported formats and HTTP 422 for empty/no-text documents

## 3. Backend: Document Management API

- [x] 3.1 Implement `GET /documents` endpoint returning list of all documents with filename, status, and upload timestamp
- [x] 3.2 Implement `DELETE /documents/{id}` endpoint: delete all chunks from ChromaDB by doc_id filter, remove from status store
- [x] 3.3 Ensure deleted document chunks no longer appear in any ChromaDB query results

## 4. Backend: Semantic Search and RAG Query API

- [x] 4.1 Implement `POST /query` endpoint accepting `{ query, history?, top_k? }` JSON body
- [x] 4.2 Implement semantic search: embed query text, query ChromaDB for top-K similar chunks filtered to `ready` documents
- [x] 4.3 Implement RAG prompt builder: format retrieved chunks as context + conversation history + user question
- [x] 4.4 Implement LLM call via OpenAI chat completions (model from `LLM_MODEL` env var, default `gpt-4o`)
- [x] 4.5 Implement SSE streaming: when client sends `Accept: text/event-stream`, stream tokens as `data:` events
- [x] 4.6 Include `sources` array in response (filename, chunk_index, excerpt, similarity_score)
- [x] 4.7 Handle no-results case: instruct LLM to respond that the answer is not in the available documents

## 5. Backend: Configuration and Static File Serving

- [x] 5.1 Load `OPENAI_API_KEY`, `CHROMA_PATH`, `LLM_MODEL` from environment at startup; fail fast with clear error if `OPENAI_API_KEY` is missing
- [x] 5.2 Validate ChromaDB collection embedding model matches configured embedding model on startup
- [x] 5.3 Configure FastAPI to serve React build output (`dist/`) as static files at root path

## 6. Frontend: Document Management Panel

- [x] 6.1 Build `DocumentPanel` component with file input (accept `.pdf,.txt,.docx`), upload button, and progress indicator
- [x] 6.2 Validate file extension client-side before upload; show inline error for unsupported types
- [x] 6.3 Build `DocumentList` component displaying each document's filename, status badge, and upload timestamp
- [x] 6.4 Implement polling logic: every 3 seconds re-fetch status for documents in `processing` state until terminal
- [x] 6.5 Show red error badge with failure reason tooltip for documents in `failed` state
- [x] 6.6 Implement delete button with confirmation dialog; call `DELETE /documents/{id}` and remove from list on success

## 7. Frontend: Chat Interface

- [x] 7.1 Build `ChatThread` component rendering user messages and assistant responses in chronological order
- [x] 7.2 Build `ChatInput` component with text area, send button; disable both during active response generation
- [x] 7.3 Implement SSE client: connect to `/query` with `Accept: text/event-stream`, append tokens to the current assistant message as they arrive
- [x] 7.4 Show typing indicator (animated dots) while waiting for first token from the stream
- [x] 7.5 Auto-scroll chat thread to bottom on each new message or token append
- [x] 7.6 Build `CitationList` component rendering collapsible chips (filename + excerpt) below each assistant response
- [x] 7.7 Maintain in-memory conversation history; pass `history` array with each query request

## 8. Frontend: Layout and Responsiveness

- [x] 8.1 Build main app layout: chat area + sidebar document panel for desktop (≥1024px)
- [x] 8.2 Implement toggleable drawer for document panel on tablet (640px–1023px)
- [x] 8.3 Verify no horizontal scrolling on 768px and 1280px viewport widths

## 9. Integration and Testing

- [ ] 9.1 Run end-to-end test: upload a PDF, wait for `ready` status, submit a query, verify answer and citations
- [ ] 9.2 Test deletion: delete a document, submit a query on its content, verify it no longer appears in results
- [ ] 9.3 Test error paths: upload unsupported file type, upload empty file, query with empty knowledge base
- [ ] 9.4 Test streaming: verify tokens appear progressively in the UI, not all at once

- [x] 9.5 Run frontend build (`npm run build`) and verify static files are served correctly by FastAPI
