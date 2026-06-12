import socket
import threading
import os
import time

PROXY_PORT = 8080
SERVER_HOST = '10.130.2.153' 
SERVER_PORT = 8000
CACHE_DIR = "cache"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def handle_client(client_socket, addr):
    try:
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')
        if not request: return

        first_line = request.split('\n')[0]
        url = first_line.split()[1]
        
        # Membuat nama file cache valid (mengamankan karakter /)
        cache_filename = url.replace("/", "_")
        if cache_filename == "_": cache_filename = "_index.html"
        cache_path = os.path.join(CACHE_DIR, cache_filename)

        start_time = time.time()

        if os.path.exists(cache_path):
            # Cache HIT: Mengirim response langsung dari berkas cache tanpa menghubungi server
            with open(cache_path, 'rb') as f:
                response = f.read()
            client_socket.sendall(response)
            elapsed = (time.time() - start_time) * 1000
            print(f"[PROXY] {addr[0]} | {url} | CACHE HIT | {elapsed:.2f} ms")
        else:
            # Cache MISS: Meneruskan request ke server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((SERVER_HOST, SERVER_PORT))
            server_socket.sendall(request.encode())
            
            # Loop untuk membaca seluruh data (penting agar asset HTML/Video tidak terpotong)
            response = b""
            while True:
                data = server_socket.recv(4096)
                if not data: break
                response += data
            
            # Menyimpan response HTTP ke berkas lokal berdasarkan jalur URL
            if b"200 OK" in response:
                with open(cache_path, 'wb') as f:
                    f.write(response)
                    
            client_socket.sendall(response)
            server_socket.close()
            elapsed = (time.time() - start_time) * 1000
            print(f"[PROXY] {addr[0]} | {url} | CACHE MISS | {elapsed:.2f} ms")

    except Exception as e:
        print(f"[PROXY ERROR] {e}")
    finally:
        client_socket.close()

def start_proxy():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PROXY_PORT))
    s.listen(10)
    print(f"[*] Proxy Server berjalan di port {PROXY_PORT}")
    
    while True:
        client, addr = s.accept()
        # Wajib menangani beberapa client secara simultan
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()

if __name__ == "__main__":
    start_proxy()