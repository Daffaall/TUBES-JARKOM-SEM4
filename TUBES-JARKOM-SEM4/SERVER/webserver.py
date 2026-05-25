import socket
import threading
import os
import datetime

TCP_PORT = 8000
UDP_PORT = 9000
HOST = '0.0.0.0'

def handle_tcp(client_socket, addr):
    try:
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')
        if not request: return
        
        first_line = request.split('\n')[0]
        if len(first_line.split()) > 1 and first_line.split()[0] == 'GET':
            file_path = first_line.split()[1]
            if file_path == '/': file_path = '/index.html'
            file_path = file_path.lstrip('/')
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Menambahkan ekstensi MIME agar web dari asprak tampil rapi di browser
                content_type = "text/html"
                if file_path.endswith(".css"): content_type = "text/css"
                elif file_path.endswith(".png"): content_type = "image/png"
                elif file_path.endswith(".mp4"): content_type = "video/mp4"

                # Mengirim response dengan format HTTP/1.1 yang valid (200 OK)
                response_header = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}; charset=utf-8\r\nContent-Length: {len(content)}\r\n\r\n"
                client_socket.sendall(response_header.encode() + content)
                # Mencatat log sesuai pedoman: IP client, jalur berkas, timestamp, dan status code
                print(f"[SERVER TCP] {addr[0]} | /{file_path} | {timestamp} | 200 OK")
            else:
                # Menangani error umum seperti 404 Not Found
                error_msg = b"<html><body><h1>404 Not Found</h1></body></html>"
                response_header = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {len(error_msg)}\r\n\r\n"
                client_socket.sendall(response_header.encode() + error_msg)
                print(f"[SERVER TCP] {addr[0]} | /{file_path} | {timestamp} | 404 Not Found")
    except Exception as e:
        print(f"[SERVER TCP] Error: {e}")
    finally:
        client_socket.close()

def start_tcp():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, TCP_PORT))
    s.listen(5)
    print(f"[*] Web Server HTTP (TCP) berjalan di port {TCP_PORT}")
    while True:
        client, addr = s.accept()
        # Wajib menangani beberapa client secara simultan
        threading.Thread(target=handle_tcp, args=(client, addr), daemon=True).start()

def start_udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, UDP_PORT))
    print(f"[*] QoS Echo Server (UDP) berjalan di port {UDP_PORT}")
    while True:
        msg, addr = s.recvfrom(1024)
        # Menerima dan memantulkan (echo) paket UDP tanpa mengubah payload
        s.sendto(msg, addr) 

if __name__ == "__main__":
    threading.Thread(target=start_tcp, daemon=True).start()
    threading.Thread(target=start_udp, daemon=True).start()
    while True: pass