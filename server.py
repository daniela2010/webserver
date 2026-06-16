import socket
import threading

HOST = "127.0.0.1"
PORT = 8080

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"Serving on http://{HOST}:{PORT}/  (press Ctrl+C to stop)")

    while True:
        conn, addr = server_sock.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

def handle_client(conn, addr):
    try:
        request_text = read_request_headers(conn)
        print(request_text)            # see what the browser actually sent

        body = b"<h1>Hello from my server!</h1>"
        response = (
            b"HTTP/1.0 200 OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: " + str(len(body)).encode() + b"\r\n"
            b"\r\n"
        ) + body
        conn.sendall(response)
    finally:
        conn.close()

if __name__ == "__main__":
    main()