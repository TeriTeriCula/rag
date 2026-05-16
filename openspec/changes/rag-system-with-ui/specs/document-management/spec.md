## ADDED Requirements

### Requirement: Document upload from UI
The UI SHALL provide a file picker allowing users to select and upload documents to the knowledge base.

#### Scenario: User uploads a document via UI
- **WHEN** the user selects a file and clicks Upload
- **THEN** the UI SHALL send the file to `POST /documents` and display the new document in the document list with status `Processing`

#### Scenario: Upload progress shown
- **WHEN** a file upload is in progress
- **THEN** the UI SHALL display a progress indicator for the upload

#### Scenario: Unsupported file type blocked
- **WHEN** the user selects a file that is not PDF, TXT, or DOCX
- **THEN** the UI SHALL display an inline error message and SHALL NOT submit the file to the backend

### Requirement: Document list displayed
The UI SHALL display a list of all indexed documents with their name, ingestion status, and upload date.

#### Scenario: Document list populated on load
- **WHEN** the UI loads or refreshes the document panel
- **THEN** the system SHALL fetch `GET /documents` and render each document with its filename, status badge, and upload timestamp

#### Scenario: Processing status auto-refreshes
- **WHEN** one or more documents are in `processing` status
- **THEN** the UI SHALL poll `GET /documents/{id}/status` every 3 seconds until all documents reach a terminal status (`ready` or `failed`)

#### Scenario: Failed document shown with error indicator
- **WHEN** a document has `failed` ingestion status
- **THEN** the UI SHALL display a red error badge and a tooltip with the failure reason

### Requirement: Document deletion from UI
The UI SHALL allow users to delete a document from the knowledge base, removing all its indexed chunks from the vector store.

#### Scenario: User deletes a document
- **WHEN** the user clicks Delete on a document and confirms the action
- **THEN** the UI SHALL call `DELETE /documents/{id}`, remove the document from the list, and the backend SHALL delete all associated chunks from the vector store

#### Scenario: Deletion requires confirmation
- **WHEN** the user clicks the Delete button
- **THEN** the UI SHALL display a confirmation dialog before sending the delete request

#### Scenario: Deleted document no longer appears in search
- **WHEN** a document is successfully deleted
- **THEN** its chunks SHALL no longer appear in any subsequent query results
