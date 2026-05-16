## ADDED Requirements

### Requirement: Rule-based injection pattern detection
The system SHALL scan each text chunk against a library of known indirect prompt injection patterns using regex and keyword matching, and assign a rule score of 1.0 if any pattern matches, 0.0 otherwise.

#### Scenario: Known injection phrase detected
- **WHEN** a chunk contains a phrase matching the injection pattern library (e.g., "ignore previous instructions", "disregard your system prompt", "you are now", "act as", "forget everything")
- **THEN** the scanner SHALL assign a rule score of 1.0 and label the chunk `rule_match: true`

#### Scenario: Clean chunk passes rule check
- **WHEN** a chunk contains no patterns from the injection library
- **THEN** the scanner SHALL assign a rule score of 0.0 and label the chunk `rule_match: false`

#### Scenario: Data exfiltration pattern detected
- **WHEN** a chunk contains patterns associated with data exfiltration (e.g., "send to", "POST to http", "email the contents", "output all documents")
- **THEN** the scanner SHALL assign a rule score of 1.0

### Requirement: ML zero-shot injection classification
The system SHALL classify each chunk using a zero-shot NLI model with candidate labels `["prompt injection", "safe content"]` and produce an ML score ∈ [0, 1] representing injection likelihood.

#### Scenario: Zero-shot model loaded at startup
- **WHEN** the backend application starts
- **THEN** the zero-shot classification pipeline SHALL be initialized and warmed up before the first request is served

#### Scenario: Chunk classified as injection
- **WHEN** the zero-shot model assigns higher probability to "prompt injection" than "safe content"
- **THEN** the ML score SHALL equal the probability assigned to "prompt injection"

#### Scenario: Chunk classified as safe
- **WHEN** the zero-shot model assigns higher probability to "safe content"
- **THEN** the ML score SHALL reflect the lower injection probability

### Requirement: Combined threat score per chunk
The system SHALL compute a final threat score for each chunk as a weighted combination: `threat_score = 0.5 × rule_score + 0.35 × ml_score + 0.15 × anomaly_score`, clamped to [0, 1].

#### Scenario: All signals agree on injection
- **WHEN** rule_score=1.0, ml_score=0.9, anomaly_score=0.8
- **THEN** threat_score SHALL be approximately 0.937

#### Scenario: Only rule matches
- **WHEN** rule_score=1.0, ml_score=0.1, anomaly_score=0.1
- **THEN** threat_score SHALL be approximately 0.55, which may or may not exceed the threshold depending on configuration

### Requirement: Scanner exposed via standalone API
The system SHALL expose `POST /scan` accepting `{"chunks": ["text1", "text2", ...]}` and returning per-chunk threat scores without triggering a query or LLM call.

#### Scenario: Standalone scan of text chunks
- **WHEN** a client POSTs a list of text strings to `/scan`
- **THEN** the response SHALL include a list of objects with `text`, `rule_score`, `ml_score`, `anomaly_score`, and `threat_score` for each chunk

#### Scenario: Empty chunk list rejected
- **WHEN** a client POSTs an empty `chunks` array
- **THEN** the system SHALL return HTTP 422
