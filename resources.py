import os
from contracts import Resource

# Build an absolute path to the static file directory.
# This keeps the server working even if it is started from another folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, "www")

# Only these subdirectories are available to clients.
# The empty string represents files directly inside www/.
ALLOWED_SUBDIRS = {"", "about", "css", "images"}
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
}

def detect_mime(filename: str) -> str:
    """Return the Content-Type value that matches the file extension."""
    _, ext = os.path.splitext(filename)
    return MIME_TYPES.get(ext.lower(), "application/octet-stream")

def is_safe(url_path: str) -> bool:
    """
    Validate that the requested URL path stays inside the static root
    and belongs to one of the allowed public directories.
    """
    # Reject directory traversal attempts.
    if ".." in url_path:
        return False
    # Remove the leading slash so we can inspect the first folder name.
    clean_path = url_path.lstrip("/")
    # Split the path into parts.
    parts = clean_path.split("/")
    # Files directly inside www/ have no subdirectory name.
    if len(parts) == 1:
        if os.path.isdir(os.path.join(STATIC_ROOT, parts[0])):
            first_subdir = parts[0]
        else:
            first_subdir = ""
    else:
        first_subdir = parts[0]

    if first_subdir not in ALLOWED_SUBDIRS:
        return False
    # Build the full filesystem path.
    full_path = os.path.join(STATIC_ROOT, clean_path)

    # Resolve real paths before comparing them to protect the static root.
    static_root_real = os.path.realpath(STATIC_ROOT)
    full_path_real = os.path.realpath(full_path)
    return (
        full_path_real == static_root_real
        or full_path_real.startswith(static_root_real + os.sep)
    )


def resolve_resource(url_path: str) -> Resource:
    """
    Convert a valid URL path into a Resource object containing the response
    status code, response body, and Content-Type.
    """
    if not is_safe(url_path):
        return Resource(
            status=403,
            body=b"403 Forbidden",
            content_type="text/plain"
        )
    # Map the root URL to the default homepage.
    if url_path == "/":
        url_path = "/index.html"

    # Remove the leading slash to create a relative file path.
    clean_path = url_path.lstrip("/")
    file_path = os.path.join(STATIC_ROOT, clean_path)
    # Return 404 if the requested file does not exist.
    if not os.path.isfile(file_path):
        return Resource(
            status=404,
            body=b"404 Not Found",
            content_type="text/plain"
        )

    # Read the file as raw bytes.
    with open(file_path, "rb") as file:
        body = file.read()

    # Return the file content with the correct MIME type.
    return Resource(
        status=200,
        body=body,
        content_type=detect_mime(file_path)
    )
