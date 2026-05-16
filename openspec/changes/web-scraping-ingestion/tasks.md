## 1. Backend Dependencies

- [x] 1.1 Add `requests`, `beautifulsoup4`, `lxml` to `backend/requirements.txt`
- [x] 1.2 Install dependencies: `pip install requests beautifulsoup4 lxml`

## 2. Status Store — Add source_url Field

- [x] 2.1 Add optional `source_url: str | None = None` field to `DocumentRecord` dataclass in `backend/app/services/status_store.py`
- [x] 2.2 Update `create_record(filename, source_url=None)` signature to accept and store the URL
- [x] 2.3 Update `all_records()` and `get_record()` responses to include `source_url` in serialized output

## 3. Web Scraper Service

- [x] 3.1 Create `backend/app/services/scraper.py`
- [x] 3.2 Implement `validate_url(url: str) -> None`: raise `ValueError` if scheme is not `http` or `https`
- [x] 3.3 Implement `fetch_html(url: str) -> str`: call `requests.get(url, timeout=15)`, raise on non-2xx status, raise if `Content-Type` does not contain `text/html`
- [x] 3.4 Implement `extract_text(html: str) -> str`: parse with BeautifulSoup(`lxml`), decompose `script, style, nav, header, footer, aside, form` tags, extract `.get_text()`, collapse whitespace, strip leading/trailing whitespace
- [x] 3.5 Implement `scrape(url: str) -> str`: orchestrate validate → fetch → extract; raise `ValueError("No extractable text found at this URL")` if result is empty

## 4. URL Ingestion Endpoint

- [x] 4.1 Add `POST /documents/url` route to `backend/app/routers/documents.py` with Pydantic body `class UrlRequest(BaseModel): url: str`
- [x] 4.2 Validate URL scheme in the endpoint (call `scraper.validate_url`); return HTTP 400 on invalid scheme
- [x] 4.3 Create status record with `source_url` set; return HTTP 202 with `doc_id`, `status`, and `source_url`
- [x] 4.4 Run scraping + ingestion pipeline in `BackgroundTasks`: call `scraper.scrape(url)` to get text, treat the text as a single TXT "page", pass through existing `chunker → embedder → vector_store` pipeline
- [x] 4.5 On scraping error, call `status_store.set_failed(doc_id, str(exc))`
- [x] 4.6 Update `GET /documents` and `GET /documents/{id}/status` responses to include `source_url` field

## 5. Frontend — URL Input in Document Panel

- [x] 5.1 Add URL input state (`urlInput`, `urlError`, `urlLoading`) to `DocumentPanel.tsx`
- [x] 5.2 Add a text input field with placeholder `https://example.com/page` and a "Scrape" button below the file upload button
- [x] 5.3 Client-side validation: if submitted value does not start with `http://` or `https://`, show inline error and do not submit
- [x] 5.4 On submit, POST `{"url": urlInput}` to `/documents/url`; on success add the new document to the list with status `processing` and clear the input; on error show the server error message inline
- [x] 5.5 Show a loading spinner on the Scrape button while the request is in flight

## 6. Frontend — URL Document Display

- [x] 6.1 Update `DocumentRecord` type in `frontend/src/api/client.ts` to include `source_url?: string | null`
- [x] 6.2 Update `listDocuments` and `getDocumentStatus` API calls to pass through `source_url`
- [x] 6.3 In the document list item, if `source_url` is set: render a globe/link icon instead of a file icon, and make the document name a `<a href={source_url} target="_blank" rel="noopener noreferrer">` link
- [x] 6.4 Ensure existing file-uploaded documents (no `source_url`) display unchanged

## 7. Verification

- [ ] 7.1 Submit a Wikipedia article URL → verify document reaches `ready` status and querying its content returns grounded answers
- [ ] 7.2 Submit an `ftp://` URL → verify HTTP 400 is returned and no record is created
- [ ] 7.3 Submit a URL to a non-existent page (404) → verify document reaches `failed` with `URL returned HTTP 404`
- [ ] 7.4 Submit a URL pointing to a PDF file → verify document reaches `failed` with content-type error
- [ ] 7.5 Submit a URL to a page with no text content → verify document reaches `failed` with "No extractable text" message
- [ ] 7.6 Verify file upload still works alongside URL submission (no regression)
- [x] 7.7 Rebuild frontend (`npm run build`) and verify production serving works
