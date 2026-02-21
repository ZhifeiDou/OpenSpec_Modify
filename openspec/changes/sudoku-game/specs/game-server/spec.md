## ADDED Requirements

### Requirement: Serve static files on localhost
The system SHALL provide an HTTP server that serves the game's static files (HTML, CSS, JavaScript) from the `testing_project/` directory on localhost.

#### Scenario: Serving the game
- **WHEN** the server is started
- **THEN** navigating to `http://localhost:<port>/` in a browser SHALL load the game's `index.html`
- **AND** all referenced CSS and JavaScript files are served correctly

### Requirement: Default port with error handling
The server SHALL listen on a default port (3000). If the default port is unavailable, the server SHALL log an error message indicating the port conflict.

#### Scenario: Successful startup on default port
- **WHEN** the server is started and port 3000 is available
- **THEN** the server listens on port 3000 and logs the URL `http://localhost:3000`

#### Scenario: Port already in use
- **WHEN** the server is started and port 3000 is already in use
- **THEN** the server logs an error message indicating the port is occupied

### Requirement: Zero external dependencies
The server MUST use only Node.js built-in modules (`http`, `fs`, `path`). No `npm install` step SHALL be required.

#### Scenario: Running without npm install
- **WHEN** a user runs `node server.js` in the `testing_project/` directory without running `npm install`
- **THEN** the server starts successfully

### Requirement: Correct MIME types
The server SHALL respond with the correct `Content-Type` header for each file type it serves.

#### Scenario: Serving HTML
- **WHEN** the server serves an `.html` file
- **THEN** the `Content-Type` header is `text/html`

#### Scenario: Serving CSS
- **WHEN** the server serves a `.css` file
- **THEN** the `Content-Type` header is `text/css`

#### Scenario: Serving JavaScript
- **WHEN** the server serves a `.js` file
- **THEN** the `Content-Type` header is `application/javascript`
