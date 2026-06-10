import socket
import time
import argparse
import statistics

# =====================================================================
# --- KONFIGURASI PROXY (Ganti sesuai IP mesin Proxy lu) ---
# =====================================================================
PROXY_HOST = '10.130.3.21'       # IP mesin Proxy (bukan localhost lagi)
PROXY_PORT = 8080                 # Port Proxy untuk TCP & UDP
# =====================================================================

def test_tcp(path="/index.html"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((PROXY_HOST, PROXY_PORT))
        
        # Header Host ditembak ke IP Proxy, urusan kelanjutannya ada di internal proxy
        request = f"GET {path} HTTP/1.1\r\nHost: {PROXY_HOST}\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())
        
        # Menerima dan menampilkan response HTML pada terminal
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print("[*] HTTP Response (Header) dari Proxy:\n")
        print(response.split("\r\n\r\n")[0]) # Tampilkan header saja agar rapi
    except Exception as e:
        print(f"[!] Gagal konek ke Proxy lewat TCP: {e}")
    finally:
        s.close()

def test_udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1.0) # Timeout per paket: maksimal 1 detik
    
    rtt_list = []
    lost_packets = 0
    total_packets = 10 
    
    print(f"[*] Memulai UDP Ping ke Proxy ({PROXY_HOST}:{PROXY_PORT})")
    
    for seq in range(1, total_packets + 1):
        timestamp = time.time()
        # Format payload: "Ping <seq> <timestamp>"
        message = f"Ping {seq} {timestamp}" 
        
        try:
            s.sendto(message.encode(), (PROXY_HOST, PROXY_PORT))
            data, _ = s.recvfrom(1024)
            rtt = (time.time() - timestamp) * 1000
            rtt_list.append(rtt)
            print(f"Reply from {PROXY_HOST}: seq={seq} time={rtt:.2f} ms")
        except socket.timeout:
            lost_packets += 1
            print(f"Request timed out for seq={seq}")
        except Exception as e:
            print(f"[!] Error saat kirim/terima paket UDP: {e}")
            
    # Kalkulasi QoS 
    if rtt_list:
        min_rtt = min(rtt_list)
        max_rtt = max(rtt_list)
        avg_rtt = sum(rtt_list) / len(rtt_list)
        
        jitter_list = [abs(rtt_list[i] - rtt_list[i-1]) for i in range(1, len(rtt_list))]
        jitter = statistics.mean(jitter_list) if jitter_list else 0.0
    else:
        min_rtt = max_rtt = avg_rtt = jitter = 0.0
        
    loss_percent = (lost_packets / total_packets) * 100
    
    # Statistik akhir: Min/Avg/Max RTT, Packet Loss (%), dan Jitter
    print("\n--- UDP QoS Statistics ---")
    print(f"Packet Loss : {loss_percent:.1f}%")
    print(f"RTT (ms)    : Min={min_rtt:.2f} / Avg={avg_rtt:.2f} / Max={max_rtt:.2f}")
    print(f"Jitter (ms) : {jitter:.2f}")
    s.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-mode", choices=['tcp', 'udp'], required=True, help="Mode pengujian")
    parser.add_argument("-path", default='/index.html', help="Path file HTML (hanya untuk mode tcp)")
    args = parser.parse_args()
    
    if args.mode == 'tcp':
        test_tcp(args.path)
    elif args.mode == 'udp':
        test_udp()