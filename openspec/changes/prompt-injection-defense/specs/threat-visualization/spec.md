## ADDED Requirements

### Requirement: Threat score displayed on citation chips
The UI SHALL display each source chunk's threat score alongside its filename and excerpt in the citation list, using colour coding to indicate risk level.

#### Scenario: Clean chunk citation displayed
- **WHEN** a source chunk has threat_score < 0.3
- **THEN** the citation chip SHALL display a green indicator and no explicit threat label

#### Scenario: Suspicious chunk citation displayed
- **WHEN** a source chunk has threat_score >= 0.3 and < 0.6
- **THEN** the citation chip SHALL display an amber/yellow indicator with label "Suspicious"

#### Scenario: Flagged chunk citation displayed
- **WHEN** a chunk was sanitized (threat_score >= threshold) but is still shown in the sources list for transparency
- **THEN** the citation chip SHALL display a red indicator with label "Blocked" and the chunk SHALL NOT be expandable (no excerpt shown)

### Requirement: Threat warning banner on query response
The UI SHALL display a warning banner above the assistant response when any chunks were sanitized during that query.

#### Scenario: Warning banner shown after sanitization
- **WHEN** the query response includes `threat_info.sanitized: true`
- **THEN** the UI SHALL display a dismissible amber banner: "Warning: N document segment(s) were flagged as potentially malicious and excluded from this answer."

#### Scenario: No banner on clean query
- **WHEN** `threat_info.sanitized: false`
- **THEN** no warning banner SHALL be displayed

### Requirement: Document-level threat indicator in document panel
The UI SHALL show a threat badge on documents in the document management panel if any of their chunks have been flagged in the most recent scan.

#### Scenario: Threat badge shown on flagged document
- **WHEN** a document has at least one chunk with threat_score >= THREAT_THRESHOLD in the last query
- **THEN** the document panel SHALL display a red shield icon next to the document filename

#### Scenario: No badge on clean document
- **WHEN** all chunks from a document scored below the threshold
- **THEN** no threat badge SHALL appear on that document
