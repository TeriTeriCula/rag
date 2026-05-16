## ADDED Requirements

### Requirement: Upload document for indexing
The system SHALL accept document uploads in PDF, TXT, and DOCX formats and initiate an ingestion pipeline that parses, chunks, embeds, and indexes the document into the vector store.

#### Scenario: Successful PDF upload
- **WHEN** a user uploads a valid PDF file via the `/documents` endpoint
- **THEN** the system SHALL return HTTP 202 with a document ID and status `processing`

#### Scenario: Successful TXT upload
- **WHEN** a user uploads a valid TXT file
- **THEN** the system SHALL parse the raw text, chunk it, generate embeddings, and store all chunks in the vector store

#### Scenario: Successful DOCX upload
- **WHEN** a user uploads a valid DOCX file
- **THEN** the system SHALL extract paragraph text, chunk it, generate embeddings, and store all chunks in the vector store

#### Scenario: Unsupported file format rejected
- **WHEN** a user uploads a file with an extension other than .pdf, .txt, or .docx
- **THEN** the system SHALL return HTTP 400 with error message `Unsupported file type`

#### Scenario: Empty file rejected
- **WHEN** a user uploads a file with zero bytes or no extractable text content
- **THEN** the system SHALL return HTTP 422 with error message `Document contains no extractable text`

### Requirement: Chunking and embedding pipeline
The system SHALL split parsed document text into overlapping chunks and generate an embedding vector for each chunk before storing in the vector store.

#### Scenario: Chunk size and overlap applied
- **WHEN** a document is ingested
- **THEN** the system SHALL produce chunks of at most 512 tokens with 64-token overlap between consecutive chunks

#### Scenario: Chunk metadata stored
- **WHEN** chunks are stored in the vector store
- **THEN** each chunk SHALL be stored with metadata including: document ID, source filename, chunk index, and page number (where available)

### Requirement: Document ingestion status tracking
The system SHALL track the processing status of each uploaded document and expose it via a status endpoint.

#### Scenario: Status polling returns current state
- **WHEN** a client polls `GET /documents/{id}/status`
- **THEN** the system SHALL return one of: `processing`, `ready`, or `failed` with an optional error message

#### Scenario: Status becomes ready on completion
- **WHEN** all chunks for a document have been embedded and stored
- **THEN** the document status SHALL transition to `ready`

#### Scenario: Status becomes failed on pipeline error
- **WHEN** an error occurs during parsing, chunking, or embedding
- **THEN** the document status SHALL transition to `failed` and the error reason SHALL be included in the status response
