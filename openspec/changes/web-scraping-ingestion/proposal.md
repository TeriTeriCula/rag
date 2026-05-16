## Why

The current RAG system only accepts file uploads (PDF, DOCX, TXT), which means users must manually download web pages before indexing them. Adding URL-based ingestion lets users point the system directly at a web page and have it scraped, chunked, and indexed automatically — the same pipeline already handles everything downstream.

## What Changes

- New `POST /documents/url` endpoint accepting a URL instead of a file
- New web scraper service: fetches page HTML, extracts clean main-body text (strips nav, footer, scripts, ads), returns text for the existing chunking pipeline
- URL-sourced documents tracked in the status store identically to file-uploaded ones (same `processing → ready | failed` lifecycle)
- Document list entry shows the source URL as the "filename" with a link icon
- Frontend: new URL input field in the DocumentPanel alongside the existing file upload button
- Scraping scoped to static HTML pages (BeautifulSoup); JS-rendered pages are out of scope for v1

## Capabilities

### New Capabilities

- `web-scraper`: Fetches a URL, validates it is reachable and returns HTML, extracts clean readable text using BeautifulSoup (removes scripts, styles, nav, footer, header elements), and returns the text for downstream chunking and embedding

### Modified Capabilities

- `document-ingestion`: Now accepts both file uploads (`POST /documents`) and URL submissions (`POST /documents/url`); URL-sourced documents follow the same `processing → ready | failed` lifecycle and appear in the document list with their URL as the source label
- `document-management`: Document list entries for URL-sourced documents display the source URL and a link icon instead of a filename; delete behavior is unchanged

## Impact

- New file `backend/app/services/scraper.py`
- New endpoint in `backend/app/routers/documents.py`: `POST /documents/url`
- New dependencies: `requests`, `beautifulsoup4`, `lxml`
- `backend/app/services/status_store.py`: minor — `source_url` optional field added to `DocumentRecord`
- Frontend `DocumentPanel.tsx`: add URL input field and submission logic
- Frontend `DocumentList`: display URL with external-link icon for web-sourced docs
