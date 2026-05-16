## ADDED Requirements

### Requirement: Synthetic test dataset of clean and injected documents
The evaluation harness SHALL include a dataset of at least 20 text chunks: 10 clean (normal document content) and 10 injected (containing known indirect prompt injection patterns), stored as a JSON fixture file.

#### Scenario: Dataset loaded for evaluation
- **WHEN** the evaluation script is run
- **THEN** it SHALL load the fixture file and produce a list of `{text, label}` pairs where label is `"injection"` or `"clean"`

### Requirement: Detection metrics computed and reported
The harness SHALL run all chunks through the scanner and compute: accuracy, precision, recall, F1 score, false positive rate (FPR), and attack success rate (ASR).

#### Scenario: Metrics computed on test dataset
- **WHEN** the evaluation script finishes scanning all test chunks
- **THEN** it SHALL print a metrics report including accuracy, precision, recall, F1, FPR, and ASR to stdout

#### Scenario: ASR computed correctly
- **WHEN** ASR is computed
- **THEN** ASR SHALL equal the proportion of injected chunks that were NOT detected (i.e., passed through to the LLM)

### Requirement: Per-threshold sweep report
The harness SHALL run the evaluation at multiple threshold values (0.3, 0.4, 0.5, 0.6, 0.7, 0.8) and output a table showing accuracy and FPR at each threshold to help identify the optimal operating point.

#### Scenario: Threshold sweep executed
- **WHEN** the evaluation script is run with `--sweep` flag
- **THEN** it SHALL output a table with columns: threshold, accuracy, FPR, recall, F1

### Requirement: Evaluation runnable via CLI
The harness SHALL be runnable as a standalone Python script from the `backend/` directory without starting the full FastAPI server.

#### Scenario: CLI execution
- **WHEN** a user runs `python -m tests.eval.run_evaluation`
- **THEN** the script SHALL execute the full evaluation and print results without requiring a running server or API key
