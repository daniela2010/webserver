# Multi-Threaded Web Server
## Submitted By
Daniela Roitman  (ID 209788272)
Shani Hasid (ID 324042431)
Yamit Barkan (ID 325106441

## Project Overview
This project implements a simple multi-threaded HTTP/1.0 web server from scratch using low-level TCP sockets in Python.
The server accepts incoming client connections, reads raw HTTP request data, parses the request line and headers, serves static files from a local `www` directory, and returns properly formatted HTTP responses.
The project was built as part of a Computer Networks programming assignment focused on socket programming, HTTP message structure, stream parsing, static file serving, security checks, and concurrency.

## Main Features
- Uses Python's low-level `socket` API.
- Binds to a local host and port.
- Listens for incoming TCP connections.
- Handles each client connection in a separate thread.
- Reads HTTP requests from a byte stream until the `\r\n\r\n` end-of-headers marker is found.
- Parses the HTTP method, requested path, HTTP version, and headers.
- Supports the `GET` method for static file access.
- Serves files from the local `www` directory.
- Detects and returns appropriate MIME types.
- Prevents directory traversal attacks using `..` path validation.
- Blocks access to unauthorized subdirectories.
- Returns valid HTTP/1.0 responses with status line, headers, blank line, and body.
- Closes each connection after sending the response.

## Supported Paths
The server allows access only to selected static paths under the `www` directory.
Allowed locations:
- `/`
- `/index.html`
- `/about/...`
- `/css/...`
- `/images/...`

Blocked locations:
- `/private/...`
- Any path containing `..`
- Any other subdirectory that is not explicitly allowed

## Project Structure
```text
webserver/
|-- server.py
|-- http_protocol.py
|-- resources.py
|-- contracts.py
`-- www/
    |-- index.html
    |-- about/
    |   |-- about.html
    |   `-- team.html
    |-- css/
    |   `-- style.css
    |-- images/
    |   |-- network.png
    |   `-- server.png
    `-- private/
        `-- data.html
```

## File Responsibilities
### `server.py`
Creates the listening socket, accepts client connections, starts a new thread for each client, reads request headers, and sends the final HTTP response.

### `http_protocol.py`
Parses raw HTTP request headers into a structured request object and builds valid HTTP/1.0 response messages.

### `resources.py`
Validates requested paths, prevents unsafe access, checks allowed subdirectories, reads static files, and determines MIME types.

### `contracts.py`
Defines shared data structures and HTTP reason phrases used by the server.

### `www/`
Contains the static files served by the web server, including HTML, CSS, and images.

## How to Run
Open a terminal inside the `webserver` directory and run:
```bash
python server.py
```

The server will start on:
```text
http://127.0.0.1:8080/
```

To stop the server, press `Ctrl+C` in the terminal.

## Browser Testing
After starting the server, open a browser and visit:
```text
http://127.0.0.1:8080/
```

or:
```text
http://127.0.0.1:8080/index.html
```

The page should load together with its CSS and images.

## cURL Testing
The following commands can be used to verify the server behavior.
On Windows PowerShell, use `curl.exe` instead of `curl`, because `curl` may run PowerShell's `Invoke-WebRequest` alias.

### Successful Request
```bash
curl.exe -v http://127.0.0.1:8080/index.html
```

Expected result:
```text
HTTP/1.0 200 OK
```

### CSS File
```bash
curl.exe -v http://127.0.0.1:8080/css/style.css
```

Expected result:
```text
HTTP/1.0 200 OK
Content-Type: text/css
```

### Missing File
```bash
curl.exe -v http://127.0.0.1:8080/missing.html
```

Expected result:
```text
HTTP/1.0 404 Not Found
```

### Forbidden Directory
```bash
curl.exe -v http://127.0.0.1:8080/private/data.html
```

Expected result:
```text
HTTP/1.0 403 Forbidden
```

### Directory Traversal Attempt
```bash
curl.exe --path-as-is -v http://127.0.0.1:8080/../server.py
```

Expected result:
```text
HTTP/1.0 403 Forbidden
```

### Unsupported Method
```bash
curl.exe -v -X POST http://127.0.0.1:8080/index.html
```

Expected result:
```text
HTTP/1.0 405 Method Not Allowed
Allow: GET
```
### Malformed Request (400)
curl cannot send a malformed HTTP request, so use this Python one-liner instead:
```powershell
python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1',8080)); s.send(b'NOT VALID\r\n\r\n'); print(s.recv(1024).decode()); s.close()"
```
Expected result:
```
HTTP/1.0 400 Bad Request
```

## HTTP Status Codes
The server supports the following status codes:
- `200 OK` - The requested static file exists and was returned successfully.
- `400 Bad Request` - The request syntax is invalid or cannot be parsed.
- `403 Forbidden` - The requested path is not allowed or contains a directory traversal attempt.
- `404 Not Found` - The requested file does not exist.
- `405 Method Not Allowed` - The request method is not supported.

## Notes
- The server is stateless and closes the connection after each response.
- The server does not use Flask, FastAPI, Django, or any other high-level web framework.
- The implementation is intended for educational purposes and local testing.
- The default host is `127.0.0.1`.
- The default port is `8080`.

## Video
- Link to the demo video: https://drive.google.com/file/d/10qffRrQMt3XZXdREMG1RixRVrI8OSze5/view?usp=sharing
