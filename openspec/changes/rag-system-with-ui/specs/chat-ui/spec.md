## ADDED Requirements

### Requirement: Chat interface for submitting queries
The UI SHALL provide a text input and submit button allowing users to type natural language questions and receive answers from the RAG system.

#### Scenario: User submits a query
- **WHEN** the user types a question and presses Enter or clicks the Send button
- **THEN** the UI SHALL send the query (with conversation history) to the backend and display the response in the chat thread

#### Scenario: Streaming response displayed progressively
- **WHEN** the backend streams LLM tokens via SSE
- **THEN** the UI SHALL render tokens as they arrive, showing a typing indicator until the stream completes

#### Scenario: Input disabled during response generation
- **WHEN** the system is generating a response
- **THEN** the text input and submit button SHALL be disabled until the response is complete

### Requirement: Conversation history displayed in chat thread
The UI SHALL maintain and display the full conversation history for the current session in a scrollable chat thread.

#### Scenario: Messages displayed in order
- **WHEN** multiple query/response pairs have occurred
- **THEN** they SHALL be displayed in chronological order with clear visual distinction between user messages and assistant responses

#### Scenario: Chat thread auto-scrolls to latest message
- **WHEN** a new message (user or assistant) is added to the thread
- **THEN** the chat thread SHALL scroll to reveal the new message

#### Scenario: New session starts empty
- **WHEN** the user loads or reloads the page
- **THEN** the chat thread SHALL start empty (no cross-session persistence in v1)

### Requirement: Source citations displayed with answers
The UI SHALL display the source document references used to generate each answer, collapsible to save space.

#### Scenario: Citations shown below each answer
- **WHEN** the backend returns a `sources` array with an answer
- **THEN** the UI SHALL display each source as a collapsible chip showing filename and excerpt

#### Scenario: No citations shown for no-context answers
- **WHEN** the backend returns an empty `sources` array
- **THEN** the UI SHALL not render a citations section for that answer

### Requirement: Responsive layout
The UI SHALL be usable on desktop and tablet screen widths without horizontal scrolling.

#### Scenario: Desktop layout
- **WHEN** the viewport width is 1024px or wider
- **THEN** the document management panel SHALL appear as a sidebar alongside the chat area

#### Scenario: Tablet layout
- **WHEN** the viewport width is between 640px and 1023px
- **THEN** the document management panel SHALL collapse to a toggleable drawer
