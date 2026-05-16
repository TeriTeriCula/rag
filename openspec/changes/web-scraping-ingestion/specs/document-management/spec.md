## ADDED Requirements

### Requirement: URL-sourced documents displayed with link indicator
The UI SHALL visually distinguish URL-sourced documents from file-uploaded documents in the document list by showing a link icon and rendering the URL as a clickable external link.

#### Scenario: URL document shown with link icon
- **WHEN** a document in the list has a `source_url` field set
- **THEN** the UI SHALL display a link/globe icon instead of a file icon next to the document entry

#### Scenario: URL rendered as clickable link
- **WHEN** a URL-sourced document is displayed
- **THEN** clicking the document name SHALL open the original URL in a new browser tab

#### Scenario: File-uploaded documents unchanged
- **WHEN** a document was ingested via file upload (no `source_url`)
- **THEN** the existing filename display behavior SHALL be unchanged

### Requirement: URL input field in document panel
The UI SHALL provide a text input field and submit button in the document panel that allows users to enter a URL for scraping and indexing.

#### Scenario: User submits a URL
- **WHEN** the user types a URL into the URL input and clicks the Scrape button (or presses Enter)
- **THEN** the UI SHALL POST to `/documents/url`, add the new document to the list with status `Processing`, and clear the input field

#### Scenario: Invalid URL format blocked client-side
- **WHEN** the user submits a string that does not start with `http://` or `https://`
- **THEN** the UI SHALL display an inline error message and SHALL NOT submit the request

#### Scenario: URL input and file upload coexist
- **WHEN** the document panel is rendered
- **THEN** both the file upload button and the URL input field SHALL be visible and independently functional
