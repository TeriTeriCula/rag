## Context

The existing ingestion pipeline in `backend/app/routers/documents.py` accepts multipart file uploads and passes raw bytes to `parser.py`. Everything downstream (chunking, embedding, ChromaDB upsert, status store) is already generic and works on plain text — it has no dependency on how that text arrived. Adding web scraping means adding one new path into the top of this pipeline: fetch URL → extract text → hand off to the same chunker/embedder/store flow.

The status store tracks each document as a `DocumentRecord`; URL-sourced docs will use the URL string where filename would normally go, with an optional `source_url` field added for UI display purposes.

## Goals / Non-Goals

**Goals:**
- Accept a URL via `POST /documents/url` and ingest the page text identically to a file upload
- Extract clean readable text from static HTML (remove boilerplate: nav, footer, header, scripts, styles, ads)
- Reuse the entire existing chunking → embedding → ChromaDB pipeline unchanged
- Show URL-sourced documents in the document list with their URL and a link indicator
- Provide clear error messages for unreachable URLs, non-HTML responses, and pages with no extractable text

**Non-Goals:**
- JavaScript-rendered pages (React/Vue SPAs) — requires Playwright/Selenium, adds heavy dependencies
- Crawling multiple pages / following links (single URL only per request)
- Authenticated pages (no cookie/session support)
- Rate limiting or robots.txt compliance (user's responsibility)
- PDF/file downloads from URLs (only HTML pages)

## Decisions

### 1. `requests` + `BeautifulSoup` for scraping

**Decision:** Use `requests` for HTTP fetching and `BeautifulSoup` with the `lxml` parser for HTML text extraction.

**Rationale:** Both libraries are lightweight, well-maintained, and already common in Python data pipelines. `lxml` is faster than `html.parser` for large pages. Combined, they add ~5 MB of dependencies vs. ~150 MB for Playwright.

**Alternatives considered:**
- `httpx` (async): would allow non-blocking fetch inside FastAPI; overkill for v1 since scraping runs in a background task already
- `playwright`: handles JS-rendered pages but requires a browser binary (~300 MB); not justified for static HTML scope

---

### 2. Text extraction strategy: remove boilerplate tags, join remaining text

**Decision:** After fetching HTML, remove `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, and `<form>` tags entirely. Extract text from the remaining DOM, collapse whitespace, and return the result.

**Rationale:** This heuristic correctly cleans most article and documentation pages without needing ML-based content extraction (e.g., `newspaper3k`). Simple and auditable.

**Alternatives considered:**
- `newspaper3k` / `trafilatura`: auto-detect main content; better for news articles, but adds dependencies and can aggressively remove legitimate academic/technical content
- `readability-lxml`: Mozilla's readability algorithm; good but another dependency; overkill for the target use case (academic/technical documents)

---

### 3. Reuse existing background task ingestion pattern

**Decision:** `POST /documents/url` creates a status record immediately (returns `202 Accepted`) and runs scraping + chunking + embedding in a FastAPI `BackgroundTask` — identical to file upload.

**Rationale:** Scraping + embedding can take 2–10 seconds for large pages. Returning immediately with a doc_id and polling via `/documents/{id}/status` is the same UX as file uploads and requires no new async infrastructure.

---

### 4. URL used as the display name

**Decision:** Store the full URL string as `filename` in `DocumentRecord` and add an optional `source_url` field. The document list already renders the `filename` field — URL-sourced docs will display their URL there.

**Rationale:** Minimal change to the status store and API response shape. The frontend can detect URL-sourced docs by checking if `source_url` is set and render a link icon accordingly.

## Risks / Trade-offs

- **Scraping paywalled or access-restricted pages** → Returns HTTP 4xx/5xx; document set to `failed` with the HTTP status as error message
- **Pages with no meaningful text** (image-only, login walls) → Empty text check triggers HTTP 422 equivalent — status set to `failed` with "No extractable text found"
- **Very large pages** (>500 KB text) → Chunker handles arbitrarily large text; only risk is many embedding API calls and longer processing time. Acceptable.
- **URL injection via the URL field** → `requests` fetches only the given URL; no shell execution involved. Validate URL scheme is `http` or `https` only before fetching.
- **Timeout on slow servers** → Set `requests.get` timeout to 15 seconds; document fails with timeout error if exceeded

## Migration Plan

1. Install new dependencies: `pip install requests beautifulsoup4 lxml`
2. Add to `requirements.txt`
3. No database migration — `source_url` field is optional and additive to `DocumentRecord`
4. Frontend rebuild required after UI changes: `npm run build`
5. **Rollback:** remove the `/documents/url` router registration; no data migration needed

## Open Questions

- Should there be a maximum URL count per session (rate limiting)?
- Should the scraped raw HTML be stored for audit/re-processing, or text only?
