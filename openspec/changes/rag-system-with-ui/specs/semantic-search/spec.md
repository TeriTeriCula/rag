## ADDED Requirements

### Requirement: Vector similarity search over indexed documents
The system SHALL query the vector store using a query embedding and return the top-K most semantically similar document chunks.

#### Scenario: Successful similarity search
- **WHEN** the system receives a query string
- **THEN** the system SHALL embed the query and retrieve the top 5 most similar chunks from the vector store by default

#### Scenario: Configurable result count
- **WHEN** a query is submitted with a `top_k` parameter
- **THEN** the system SHALL return exactly `top_k` chunks (or fewer if the index contains fewer chunks)

#### Scenario: No documents indexed
- **WHEN** a query is submitted and the vector store contains no chunks
- **THEN** the system SHALL return an empty results list and the query engine SHALL generate a response indicating no knowledge base is available

### Requirement: Retrieved chunks include source metadata
The system SHALL return source metadata alongside each retrieved chunk so the UI can display citations.

#### Scenario: Chunk metadata included in results
- **WHEN** the system retrieves chunks for a query
- **THEN** each result SHALL include: chunk text, source filename, document ID, chunk index, and similarity score

### Requirement: Search scoped to ready documents only
The system SHALL exclude chunks from documents whose ingestion status is not `ready` from all search results.

#### Scenario: Processing document excluded from search
- **WHEN** a document is in `processing` status and a query is run
- **THEN** no chunks from that document SHALL appear in search results

#### Scenario: Failed document excluded from search
- **WHEN** a document has `failed` ingestion status and a query is run
- **THEN** no chunks from that document SHALL appear in search results
