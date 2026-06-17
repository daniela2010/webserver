from contracts import Request, REASON_PHRASES

#function to parse the request
def parse_request(raw_headers: str) -> Request:
    """
    INPUT  : the header block as text
    OUTPUT : a Request object
             If the request is malformed, ok=False
   """
    # Empty request => bad request
    if raw_headers is None or raw_headers.strip() == "":
        return Request(method="", path="", version="", ok=False)
    # Split the header block into separate lines
    lines = raw_headers.split("\r\n")
    # The first line is the request line: METHOD PATH VERSION
    request_line = lines[0].strip()
    parts = request_line.split()
    # Request line must contain exactly 3 parts
    if len(parts) != 3:
        return Request(method="", path="", version="", ok=False)
    method, path, version = parts
    # Basic validation of the three required fields
    if method == "" or path == "" or version == "":
        return Request(method="", path="", version="", ok=False)
    # HTTP version should be in HTTP/... format
    if version not in ("HTTP/1.0", "HTTP/1.1"):
        return Request(method="", path="", version="", ok=False)
    # Remove query string if exists:
    # /index.html?name=test  ->  /index.html
    if "?" in path:
        path = path.split("?", 1)[0]
    # Parse the remaining header lines into a dictionary
    headers = {}
    for line in lines[1:]:
        # Skip empty lines
        if line.strip() == "":
            continue
        # Header format should be: Name: value
        if ":" not in line:
            return Request(method="", path="", version="", ok=False)

        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()
    return Request(
        method=method,
        path=path,
        version=version,
        headers=headers,
        ok=True
    )


#function to build the response
def build_response(status: int, body: bytes = b"", content_type: str = "text/plain") -> bytes:
    """
    INPUT  : a status code, the body bytes, and the content type
             (these come from Person C's Resource, or from an error case).
    OUTPUT : the complete HTTP/1.0 response as raw bytes, ready for the socket.
    """
    # Get the reason phrase for the status code
    reason = REASON_PHRASES.get(status, "OK")
    # Status line: HTTP Version + Status Code + Reason Phrase
    status_line = f"HTTP/1.0 {status} {reason}\r\n"
    # Required HTTP headers
    headers = (
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
    )
    # Blank line separates headers from body
    return status_line.encode("iso-8859-1") + headers.encode("iso-8859-1") + b"\r\n" + body



