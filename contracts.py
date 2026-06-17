from dataclasses import dataclass, field

# HTTP status code -> reason phrase
REASON_PHRASES = {
    200: "OK",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
}

@dataclass
class Request:
    # HTTP method (e.g. GET)
    method: str
    # Requested URL path
    path: str
    # HTTP version (e.g. HTTP/1.0)
    version: str
    # Parsed request headers
    headers: dict = field(default_factory=dict)
    # False => malformed request => 400 Bad Request
    ok: bool = True

@dataclass
class Resource:
    # HTTP status code (200 / 403 / 404)
    status: int
    # File contents or error message
    body: bytes
    # MIME type (e.g. text/html)
    content_type: str