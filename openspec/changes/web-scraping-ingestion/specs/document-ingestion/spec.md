## ADDED Requirements

### Requirement: URL submission endpoint
The system SHALL expose `POST /documents/url` accepting a JSON body `{"url": "<string>"}` that initiates web scraping and indexing of the target page, returning HTTP 202 with a `doc_id` and status `processing`.

#### Scenario: Valid URL accepted
- **WHEN** a client POSTs `{"url": "https://example.com/article"}` to `/documents/url`
- **THEN** the system SHALL return HTTP 202 with `{"doc_id": "<uuid>", "status": "processing", "source_url": "https://example.com/article"}`

#### Scenario: Missing URL field rejected
- **WHEN** a client POSTs a body without a `url` field
- **THEN** the system SHALL return HTTP 422 (Pydantic validation error)

#### Scenario: URL ingestion follows same lifecycle as file upload
- **WHEN** a URL is submitted and processing begins
- **THEN** the document SHALL appear in `GET /documents` with status `processing`, transition to `ready` on success, or `failed` with an error message on any scraping or embedding error

### Requirement: Source URL stored in document record
The system SHALL store the original URL in the `DocumentRecord` so it can be returned in the document list and status responses.

#### Scenario: Source URL returned in document list
- **WHEN** `GET /documents` is called and the list includes a URL-sourced document
- **THEN** that document's entry SHALL include a `source_url` field containing the original URL and the `filename` field SHALL also contain the URL string

#### Scenario: Source URL returned in status response
- **WHEN** `GET /documents/{id}/status` is called for a URL-sourced document
- **THEN** the response SHALL include `"source_url": "<url>"` alongside `doc_id` and `status`
