from contracts import Request, REASON_PHRASES

def parse_request(raw_headers: str) -> Request:
    """
    Parse the HTTP header text into a Request object.
    If the request is malformed, return a Request with ok=False.
    """
    if raw_headers is None or raw_headers.strip() == "":
        return Request(method="", path="", version="", ok=False)

    lines = raw_headers.split("\r\n")
    # The request line must have the format: METHOD PATH VERSION.
    request_line = lines[0].strip()
    parts = request_line.split()

    if len(parts) != 3:
        return Request(method="", path="", version="", ok=False)
    
    method, path, version = parts
    # Validate the required request line fields.
    if method == "" or path == "" or version == "":
        return Request(method="", path="", version="", ok=False)
    if version not in ("HTTP/1.0", "HTTP/1.1"):
        return Request(method="", path="", version="", ok=False)
    # Ignore query parameters because this server only serves static files.
    if "?" in path:
        path = path.split("?", 1)[0]

    headers = {}

    for line in lines[1:]:
        if line.strip() == "":
            continue

        # Each header line must use the format: Name: value.
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

def build_response(status: int, body: bytes = b"", content_type: str = "text/plain") -> bytes:
    """
    Build a complete HTTP/1.0 response as bytes, including the status line,
    headers, blank line, and response body.
    """
    reason = REASON_PHRASES.get(status, "OK")
    # The status line starts every HTTP response.
    status_line = f"HTTP/1.0 {status} {reason}\r\n"
    # Include the required response headers.
    headers = (
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
    )

    # Add the required Allow header for 405 Method Not Allowed responses.
    if status == 405:
        headers += "Allow: GET\r\n"

    headers += "Connection: close\r\n"
    # A blank line separates headers from the response body.
    return (
        status_line.encode("iso-8859-1")
        + headers.encode("iso-8859-1")
        + b"\r\n"
        + body
    )