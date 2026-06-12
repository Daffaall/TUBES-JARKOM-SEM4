import socket
import threading
import os
import datetime

HOST = "0.0.0.0"

TCP_PORT = 8000
UDP_PORT = 9000

ALLOWED_PROXY_IP = [
    "10.85.141.180"
]


def handle_tcp(client_socket, addr):

    try:

        if addr[0] not in ALLOWED_PROXY_IP:

            print(
                f"[SERVER] Ditolak: "
                f"{addr[0]}"
            )

            client_socket.close()
            return

        request = client_socket.recv(
            4096
        ).decode(
            "utf-8",
            errors="ignore"
        )

        if not request:
            return

        first_line = request.split("\n")[0]

        parts = first_line.split()

        if len(parts) < 2:
            return

        file_path = parts[1]

        if file_path == "/":
            file_path = "/index.html"

        file_path = file_path.lstrip("/")

        timestamp = (
            datetime.datetime.now()
            .strftime("%Y-%m-%d %H:%M:%S")
        )

        if os.path.exists(file_path):

            with open(
                file_path,
                "rb"
            ) as f:
                content = f.read()

            content_type = "text/html"

            if file_path.endswith(".css"):
                content_type = "text/css"

            elif file_path.endswith(".png"):
                content_type = "image/png"

            elif file_path.endswith(".mp4"):
                content_type = "video/mp4"

            header = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(content)}\r\n\r\n"
            )

            client_socket.sendall(
                header.encode() + content
            )

            print(
                f"[SERVER TCP] "
                f"{addr[0]} | "
                f"/{file_path} | "
                f"{timestamp} | 200 OK"
            )

        else:

            body = (
                b"<html><body>"
                b"<h1>404 Not Found</h1>"
                b"</body></html>"
            )

            header = (
                f"HTTP/1.1 404 Not Found\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(body)}\r\n\r\n"
            )

            client_socket.sendall(
                header.encode() + body
            )

    finally:
        client_socket.close()


def start_tcp():

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    s.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    s.bind((HOST, TCP_PORT))

    s.listen(5)

    print(
        f"[*] HTTP Server "
        f"TCP {TCP_PORT}"
    )

    while True:

        client, addr = s.accept()

        threading.Thread(
            target=handle_tcp,
            args=(client, addr),
            daemon=True
        ).start()


def start_udp():

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    s.bind((HOST, UDP_PORT))

    print(
        f"[*] UDP Echo Server "
        f"{UDP_PORT}"
    )

    while True:

        data, addr = s.recvfrom(1024)

        timestamp = (
            datetime.datetime.now()
            .strftime("%Y-%m-%d %H:%M:%S")
        )

        try:
            message = data.decode(
                "utf-8",
                errors="ignore"
            )
        except:
            message = str(data)

        print(
            f"[SERVER UDP] "
            f"{addr[0]}:{addr[1]} | "
            f"{timestamp} | "
            f"{len(data)} Bytes | "
            f"Data: {message}"
        )

        s.sendto(data, addr)

        print(
            f"[SERVER UDP] "
            f"Echo dikirim ke "
            f"{addr[0]}:{addr[1]}"
        )


if __name__ == "__main__":

    threading.Thread(
        target=start_tcp,
        daemon=True
    ).start()

    threading.Thread(
        target=start_udp,
        daemon=True
    ).start()

    while True:
        pass