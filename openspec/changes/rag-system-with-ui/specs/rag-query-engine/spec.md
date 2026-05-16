## ADDED Requirements

### Requirement: Generate grounded answer from retrieved context
The system SHALL combine retrieved document chunks with the user's query in a structured LLM prompt and return a generated answer that is grounded in the provided context.

#### Scenario: Answer generated with context
- **WHEN** a user submits a query and relevant chunks are retrieved
- **THEN** the system SHALL construct a prompt containing the retrieved chunks as context and the user's question, send it to the configured LLM, and return the generated answer

#### Scenario: Answer acknowledges out-of-context questions
- **WHEN** no sufficiently similar chunks are found for a query (similarity score below threshold)
- **THEN** the LLM SHALL be instructed to respond that the answer is not found in the available documents rather than hallucinating

#### Scenario: Streaming token output supported
- **WHEN** a client connects to the query endpoint with `Accept: text/event-stream`
- **THEN** the system SHALL stream LLM tokens via Server-Sent Events as they are generated

### Requirement: Source citations included in response
The system SHALL return the source document chunks used to generate each answer so the UI can display citations.

#### Scenario: Citations returned with answer
- **WHEN** a query produces a generated answer
- **THEN** the response SHALL include a `sources` array with the filename, chunk index, and relevant excerpt for each chunk used in the prompt

### Requirement: Conversation history passed to LLM
The system SHALL accept an optional conversation history in the query request and include prior turns in the LLM prompt for multi-turn coherence.

#### Scenario: Multi-turn query uses history
- **WHEN** a query request includes a `history` array of prior user/assistant turns
- **THEN** the system SHALL prepend the history to the LLM prompt so the model can resolve references like "it" or "the previous answer"

#### Scenario: First query has no history
- **WHEN** a query request omits the `history` field or passes an empty array
- **THEN** the system SHALL generate an answer using only the retrieved context and the current query

### Requirement: LLM model configurable via environment variable
The system SHALL read the LLM model identifier from the `LLM_MODEL` environment variable at startup.

#### Scenario: Custom model used when env var set
- **WHEN** `LLM_MODEL=gpt-4o-mini` is set in the environment
- **THEN** the system SHALL use `gpt-4o-mini` for all query completions

#### Scenario: Default model used when env var absent
- **WHEN** `LLM_MODEL` is not set
- **THEN** the system SHALL default to `gpt-4o`
