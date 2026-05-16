## ADDED Requirements

### Requirement: Per-document centroid computation
The system SHALL compute the centroid (mean embedding vector) for all chunks belonging to the same `doc_id` and use it as the reference point for anomaly detection.

#### Scenario: Centroid computed from document chunks
- **WHEN** chunks from a single document are retrieved and their embeddings are available
- **THEN** the system SHALL compute the element-wise mean of all chunk embedding vectors for that document

#### Scenario: Single-chunk document handled
- **WHEN** a document contains only one chunk
- **THEN** the anomaly score for that chunk SHALL be 0.0 (no anomaly detectable without a reference distribution)

### Requirement: Cosine distance anomaly scoring
The system SHALL compute the cosine distance between each chunk's embedding and its document's centroid. Chunks with distance above a configurable threshold SHALL receive a high anomaly score.

#### Scenario: Chunk semantically distant from document centroid
- **WHEN** the cosine distance between a chunk embedding and its document centroid exceeds `ANOMALY_THRESHOLD` (default: 0.45)
- **THEN** the chunk's anomaly score SHALL be proportional to the excess distance, normalized to [0, 1]

#### Scenario: Chunk semantically consistent with document
- **WHEN** the cosine distance is below `ANOMALY_THRESHOLD`
- **THEN** the chunk's anomaly score SHALL be 0.0

### Requirement: Embeddings retrieved from ChromaDB
The system SHALL retrieve stored embedding vectors from ChromaDB by `doc_id` to compute centroids, without calling the embedding API again.

#### Scenario: Embeddings fetched from vector store
- **WHEN** the anomaly detector is invoked for a set of chunks
- **THEN** it SHALL query ChromaDB using `col.get(where={"doc_id": ...}, include=["embeddings"])` to retrieve stored vectors

#### Scenario: Embeddings unavailable
- **WHEN** ChromaDB returns no embeddings for a doc_id (e.g., collection does not include embeddings)
- **THEN** the anomaly score for all chunks from that document SHALL default to 0.0 and a warning SHALL be logged
