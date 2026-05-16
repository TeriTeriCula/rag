## ADDED Requirements

### Requirement: Remove flagged chunks from LLM context
The system SHALL remove any chunk whose `threat_score` is at or above `THREAT_THRESHOLD` (default: 0.6, configurable via environment variable) from the list of chunks passed to the LLM prompt.

#### Scenario: High-threat chunk removed
- **WHEN** a retrieved chunk has threat_score >= THREAT_THRESHOLD
- **THEN** that chunk SHALL NOT appear in the LLM system prompt context and SHALL NOT contribute to the generated answer

#### Scenario: Safe chunks passed through unchanged
- **WHEN** a retrieved chunk has threat_score < THREAT_THRESHOLD
- **THEN** that chunk SHALL be included in the LLM context unchanged

#### Scenario: All chunks flagged
- **WHEN** every retrieved chunk has threat_score >= THREAT_THRESHOLD
- **THEN** the system SHALL NOT call the LLM and SHALL return a fixed response: "All retrieved document segments were flagged as potentially malicious and removed. Please upload clean documents."

### Requirement: Threat metadata included in query response
The system SHALL include a `threat_info` object in every query response containing the count of flagged chunks and the maximum threat score observed.

#### Scenario: Threat info returned with clean query
- **WHEN** no chunks are flagged
- **THEN** the response SHALL include `"threat_info": {"flagged_count": 0, "max_threat_score": 0.0, "sanitized": false}`

#### Scenario: Threat info returned when chunks removed
- **WHEN** one or more chunks are sanitized
- **THEN** the response SHALL include `"threat_info": {"flagged_count": N, "max_threat_score": X, "sanitized": true}`

### Requirement: Configurable threat threshold
The system SHALL read `THREAT_THRESHOLD` from the environment at startup and apply it consistently across all query requests.

#### Scenario: Custom threshold applied
- **WHEN** `THREAT_THRESHOLD=0.8` is set in the environment
- **THEN** only chunks with threat_score >= 0.8 SHALL be removed from the prompt

#### Scenario: Threshold 1.0 effectively disables sanitization
- **WHEN** `THREAT_THRESHOLD=1.0` is set
- **THEN** no chunks SHALL be removed regardless of their threat scores (rollback/disable mechanism)
