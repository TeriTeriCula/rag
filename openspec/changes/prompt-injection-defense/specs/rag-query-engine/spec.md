## MODIFIED Requirements

### Requirement: Generate grounded answer from retrieved context
The system SHALL combine retrieved document chunks with the user's query in a structured LLM prompt and return a generated answer that is grounded in the provided context. Before building the prompt, retrieved chunks SHALL be scanned for injection threats and sanitized by removing any chunk with threat_score >= THREAT_THRESHOLD. The response SHALL include a `threat_info` object describing any sanitization that occurred.

#### Scenario: Answer generated with context after sanitization
- **WHEN** a user submits a query, chunks are retrieved, and some chunks are flagged by the scanner
- **THEN** the system SHALL remove flagged chunks, build the LLM prompt with only clean chunks, generate a grounded answer, and include `threat_info.sanitized: true` in the response

#### Scenario: Answer acknowledges out-of-context questions
- **WHEN** no sufficiently similar chunks are found for a query (empty retrieval result)
- **THEN** the LLM SHALL be instructed to respond that the answer is not found in the available documents rather than hallucinating

#### Scenario: All chunks flagged — LLM not called
- **WHEN** every retrieved chunk is flagged by the scanner (threat_score >= THREAT_THRESHOLD)
- **THEN** the system SHALL NOT call the LLM and SHALL return a fixed warning response with `threat_info.sanitized: true` and `threat_info.flagged_count` equal to the total retrieved count

#### Scenario: Streaming token output supported
- **WHEN** a client connects to the query endpoint with `Accept: text/event-stream`
- **THEN** the system SHALL stream LLM tokens via Server-Sent Events as they are generated, preceded by a `sources` event and a `threat_info` event

#### Scenario: Citations returned with answer
- **WHEN** a query produces a generated answer
- **THEN** the response SHALL include a `sources` array with the filename, chunk index, relevant excerpt, and `threat_score` for each chunk (both clean and flagged chunks listed, flagged ones marked)

#### Scenario: Multi-turn query uses history
- **WHEN** a query request includes a `history` array of prior user/assistant turns
- **THEN** the system SHALL prepend the history to the LLM prompt so the model can resolve references like "it" or "the previous answer"

#### Scenario: First query has no history
- **WHEN** a query request omits the `history` field or passes an empty array
- **THEN** the system SHALL generate an answer using only the retrieved context and the current query

#### Scenario: LLM model configurable via environment variable
- **WHEN** `OPENAI_LLM_MODEL=gpt-4o-mini` is set in the environment
- **THEN** the system SHALL use that model for all query completions
