import socket
import threading
import http_protocol
import resources

HOST = "127.0.0.1"
PORT = 8080

def read_request_headers(conn):
    """
    Read bytes from the client socket until the HTTP header terminator
    (\r\n\r\n) is found, then return only the header section as text.
    """
    buffer = b""
    while True:
        data = conn.recv(4096)

        # Stop reading if the client closes the connection.
        if not data:
            break
        buffer += data
        # HTTP headers end with an empty line: \r\n\r\n.
        if b"\r\n\r\n" in buffer:
            break
        # Limit the maximum header size to avoid reading unlimited data.
        if len(buffer) > 65536:
            break
    return buffer.split(b"\r\n\r\n", 1)[0].decode("iso-8859-1")


def handle_client(conn, addr):
    """
    Handle one client connection from request reading to response sending.
    This function runs in a separate thread for each connected client.
    """
    try:
        # Read the raw HTTP request and convert it into a structured Request object.
        request_text = read_request_headers(conn)
        request = http_protocol.parse_request(request_text)

        # Choose the response based on request validity, method, and requested resource.
        if not request.ok:
            # Malformed HTTP request.
            response = http_protocol.build_response(
                400, b"400 Bad Request", "text/plain"
            )
        elif request.method != "GET":
            # This server only supports GET requests.
            response = http_protocol.build_response(
                405, b"405 Method Not Allowed", "text/plain"
            )
        else:
            # Resolve the requested static file and format it as an HTTP response.
            resource = resources.resolve_resource(request.path)
            response = http_protocol.build_response(
                resource.status, resource.body, resource.content_type
            )

        conn.sendall(response)

    finally:
        # HTTP/1.0 does not require persistent connections in this project.
        # Each request is handled independently, then the socket is closed.
        conn.close()


def main():
    """
    Create the listening TCP socket and accept incoming client connections.
    Each accepted connection is handled by a new thread.
    """
    # Create a TCP/IPv4 socket.
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow the port to be reused immediately after restarting the server.
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the configured host and port, then start listening.
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"Serving on http://{HOST}:{PORT}/  (press Ctrl+C to stop)")

    while True:
        # Wait for the next client connection.
        conn, addr = server_sock.accept()
        # Use a separate thread so one slow client does not block others.
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

# Start the server only when this file is executed directly.
if __name__ == "__main__":
    main()
