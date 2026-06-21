import os

from contracts import Resource

# The only directory the server is allowed to serve files from.
STATIC_ROOT = "www"

# Subdirectories a client is allowed to reach. for anything else, 403 Forbidden.
# "" means the root directory itself.
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
    #Map a file extension to a Content-Type. Falls back to a generic binary type.
    _, ext = os.path.splitext(filename)
    return MIME_TYPES.get(ext.lower(), "application/octet-stream")

# Return False if the request should be rejected for security reasons
def is_safe(url_path: str) -> bool:
    # Block directory traversal attempts.
    if ".." in url_path:
        return False

    # Remove the leading slash so we can inspect the first folder name.
    clean_path = url_path.lstrip("/")

    # Split the path into parts.
    parts = clean_path.split("/")

    # If the file is directly under www, there is no subfolder.
    if len(parts) == 1:
        first_subdir = ""
    else:
        first_subdir = parts[0]

    # Allow only approved subdirectories.
    if first_subdir not in ALLOWED_SUBDIRS:
        return False

    # Build the full filesystem path.
    full_path = os.path.join(STATIC_ROOT, clean_path)

    # Resolve both paths to their real absolute paths.
    static_root_real = os.path.realpath(STATIC_ROOT)
    full_path_real = os.path.realpath(full_path)

    return (
    full_path_real == static_root_real
    or
    full_path_real.startswith(
        static_root_real + os.sep
    ) )


def resolve_resource(url_path: str) -> Resource:
    # Check whether the requested URL path is allowed.
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

    # Build the full path inside the static root directory.
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


