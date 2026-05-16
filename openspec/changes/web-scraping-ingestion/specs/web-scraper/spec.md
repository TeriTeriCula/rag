## ADDED Requirements

### Requirement: Fetch and validate URL
The system SHALL accept an HTTP or HTTPS URL, fetch its content with a 15-second timeout, and reject any URL with a non-HTTP/HTTPS scheme or that returns a non-2xx HTTP status.

#### Scenario: Valid URL fetched successfully
- **WHEN** a valid HTTP or HTTPS URL is submitted and the server returns HTTP 200 with HTML content
- **THEN** the system SHALL proceed to text extraction with the response body

#### Scenario: Non-HTTP scheme rejected
- **WHEN** a URL with scheme `ftp://`, `file://`, or any non-HTTP/HTTPS scheme is submitted
- **THEN** the system SHALL return HTTP 400 with error message `Only http:// and https:// URLs are supported`

#### Scenario: Unreachable URL
- **WHEN** the target server is unreachable or the request times out after 15 seconds
- **THEN** the document status SHALL be set to `failed` with error message `Could not reach URL: <reason>`

#### Scenario: Server returns non-2xx response
- **WHEN** the target server returns HTTP 4xx or 5xx
- **THEN** the document status SHALL be set to `failed` with error message `URL returned HTTP <status_code>`

### Requirement: Extract clean text from HTML
The system SHALL parse the fetched HTML, remove boilerplate elements (scripts, styles, navigation, headers, footers, sidebars, forms), and return the remaining visible text with collapsed whitespace.

#### Scenario: Boilerplate elements removed
- **WHEN** the HTML contains `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, or `<form>` tags
- **THEN** those elements and all their content SHALL be removed before text extraction

#### Scenario: Clean text extracted from article page
- **WHEN** a Wikipedia or documentation page URL is submitted
- **THEN** the extracted text SHALL contain the article body text without navigation menus or page chrome

#### Scenario: No extractable text
- **WHEN** the page yields an empty string after extraction (image-only page, login wall, blank page)
- **THEN** the document status SHALL be set to `failed` with error message `No extractable text found at this URL`

### Requirement: Non-HTML response rejected
The system SHALL check the `Content-Type` response header and reject URLs that do not return HTML content.

#### Scenario: PDF URL submitted
- **WHEN** a URL pointing to a `.pdf` file is submitted (Content-Type: application/pdf)
- **THEN** the document status SHALL be set to `failed` with error message `URL does not point to an HTML page. To index a PDF, please upload the file directly.`

#### Scenario: JSON or plain-text API endpoint submitted
- **WHEN** a URL returns `Content-Type: application/json` or another non-HTML type
- **THEN** the document status SHALL be set to `failed` with an appropriate content-type error message
