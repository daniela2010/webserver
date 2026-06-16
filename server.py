import socket
import threading

HOST = "127.0.0.1"
PORT = 8080

def read_request_headers(conn):
    """
    Read from the socket until the end-of-headers marker (\r\n\r\n) is found,
    then return the header block as text
    """
    # Collect raw bytes here
    buffer = b""
    while True:
        # Read whatever has arrived
        data = conn.recv(4096)
        # If client disconnected, break
        if not data:
            break
        # Append what we just read
        buffer += data
        # If full header block arrived
        if b"\r\n\r\n" in buffer:
            break
        # Safety: 64 KB limit, if bigger break
        if len(buffer) > 65536:
            break
    # Return the header block as text
    return buffer.split(b"\r\n\r\n", 1)[0].decode("iso-8859-1")


def handle_client(conn, addr):
    """
    Handles ONE client connection, start to finish. Runs in its own thread,
    so a slow client here can't block the main accept() loop.
    """
    try:
        # Step 1: read the request off the socket (our robust reader above).
        request_text = read_request_headers(conn)
        # debug: see exactly what the browser sent
        print(request_text)
        # Step 2 (TEMPORARY): a hardcoded response, just to prove the networking
        # works on its own. Later this gets replaced by calls to the teammates'
        # parse request and build response functions via the shared contracts.
        body = b"<h1>Hello from my server!</h1>"
        response = (
            b"HTTP/1.0 200 OK\r\n"                                  # status line
            b"Content-Type: text/html\r\n"                         # header
            b"Content-Length: " + str(len(body)).encode() + b"\r\n"  # header (body size)
            b"\r\n"                                                # blank line = end of headers
        ) + body                                                   # the body itself
        conn.sendall(response)         # send the full response back to the client
    finally:
        # HTTP/1.0 is stateless: every request gets its own connection, then we
        # close it. The 'finally' guarantees we close even if something errors.
        conn.close()


def main():
    # Sets up the listening socket once, then loops forever accepting clients.
    # Create a TCP/IPv4 socket. AF_INET = IPv4, SOCK_STREAM = TCP (reliable, ordered).
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Let us restart the server and reuse the port immediately, instead of waiting
    # out the OS's TIME_WAIT period. Pure convenience while developing.
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_sock.bind((HOST, PORT))     # claim the port
    server_sock.listen(5)              # start listening; queue up to 5 pending clients
    print(f"Serving on http://{HOST}:{PORT}/  (press Ctrl+C to stop)")

    while True:
        # accept() BLOCKS here until a client connects, then returns a brand-new
        # socket (conn) dedicated to that client, plus their address (addr).
        conn, addr = server_sock.accept()

        # Hand this client off to its own thread, so the main loop can go straight
        # back to accept() for the next client. daemon=True lets the program exit
        # cleanly even if threads are still running.
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


# This runs main() only when the file is executed directly (python server.py),
# not when it's imported by another file.
if __name__ == "__main__":
    main()