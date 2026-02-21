import os
import time
import json
import subprocess
import urllib.request
import urllib.error
import gc

# Gunakan nama config.json agar sesuai dengan .gitignore di GitHub
CONFIG_FILE = "config.json"

def clear_screen():
    os.system("clear")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"webhook_url": "", "vip_link": ""}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def go_to_home_screen():
    """Menyembunyikan Termux ke latar belakang (kembali ke Home Screen)"""
    print("\n[+] Menyembunyikan Termux ke latar belakang...")
    time.sleep(1)
    os.system("su -c 'am start -a android.intent.action.MAIN -c android.intent.category.HOME > /dev/null 2>&1'")
    time.sleep(2)

def get_roblox_packages():
    """Mendeteksi semua aplikasi Roblox yang terinstal di Android"""
    packages = []
    try:
        output = subprocess.check_output("su -c 'pm list packages'", shell=True).decode('utf-8')
        for line in output.splitlines():
            if 'roblox' in line.lower():
                packages.append(line.split(':')[1])
    except:
        pass
    return packages

def get_ram_usage():
    """Membaca RAM langsung dari kernel Android (Hemat Memori Termux)"""
    try:
        output = subprocess.check_output("su -c 'cat /proc/meminfo'", shell=True).decode('utf-8')
        mem_total = 0
        mem_avail = 0
        for line in output.splitlines():
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1]) // 1024 
            elif line.startswith('MemAvailable:') or line.startswith('MemFree:'):
                if mem_avail == 0: 
                    mem_avail = int(line.split()[1]) // 1024
                    
        if mem_total > 0:
            mem_used = mem_total - mem_avail
            return f"{mem_used}MB/{mem_total}MB"
    except:
        pass
    return "N/A"

def deploy_telemetry_lua(packages):
    """Menyuntikkan Sensor Detak Jantung ke Folder Delta Lite"""
    lua_script = """
repeat task.wait() until game:IsLoaded()
local Players = game:GetService("Players")

local usn = Players.LocalPlayer and Players.LocalPlayer.Name or "Unknown"
local startTime = os.time()

-- Heartbeat setiap 30 detik (Sangat ringan untuk CPU)
while task.wait(30) do
    pcall(function()
        writefile("arsy_status.txt", usn .. "|" .. tostring(os.time()) .. "|" .. tostring(startTime))
    end)
end
"""
    for pkg in packages:
        # Jalur injeksi otomatis ke folder external Delta
        autoexec_path = f"/sdcard/Android/data/{pkg}/files/gloop/external/Autoexecute/arsy.lua"
        os.system(f"su -c 'mkdir -p \"$(dirname \"{autoexec_path}\")\" && echo \"{lua_script}\" > \"{autoexec_path}\"'")
        
        # Hapus file status lama agar tidak ada false-positive saat start awal
        status_path = f"/sdcard/Android/data/{pkg}/files/gloop/workspace/arsy_status.txt"
        os.system(f"su -c 'rm -f \"{status_path}\"'")

def get_instances_telemetry(packages):
    """Membaca detak jantung dan menghitung Uptime"""
    instances = []
    current_time = int(time.time()) 
    
    for pkg in packages:
        workspace_path = f"/sdcard/Android/data/{pkg}/files/gloop/workspace/arsy_status.txt"
        try:
            output = subprocess.check_output(f"su -c 'cat \"{workspace_path}\"'", shell=True, stderr=subprocess.DEVNULL).decode('utf-8').strip()
            if "|" in output:
                parts = output.split("|")
                usn = parts[0]
                lua_time = int(parts[1])
                start_time = int(parts[2]) if len(parts) > 2 else lua_time
                
                # Hitung Uptime
                uptime_sec = current_time - start_time
                hours, remainder = divmod(uptime_sec, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
                
                # Toleransi detak jantung 90 detik
                if current_time - lua_time > 90:
                    status_icon = "🔴"
                    uptime_str = "Offline"
                else:
                    status_icon = "🟢"
                    
                instances.append({"usn": usn, "icon": status_icon, "uptime": uptime_str})
            else:
                instances.append({"usn": "Menunggu...", "icon": "⏳", "uptime": "Memuat..."})
        except:
            instances.append({"usn": "Login...", "icon": "⚫", "uptime": "Offline"})
            
    return instances

def launch_to_vip_server(packages, vip_link):
    """Meluncurkan Roblox langsung ke Private Server via Intent"""
    for pkg in packages:
        intent_command = f"su -c 'am start -a android.intent.action.VIEW -d \"{vip_link}\" {pkg}'"
        os.system(intent_command)
        time.sleep(10) # Jeda 10 detik antar akun agar CPU Redfinger stabil

def clean_system_cache():
    """Membersihkan RAM tingkat Kernel Android"""
    os.system("su -c 'am kill-all' > /dev/null 2>&1")
    os.system("su -c 'sync; echo 3 > /proc/sys/vm/drop_caches' > /dev/null 2>&1")

def generate_log_text(instances, total_cleans):
    """Merakit teks log untuk layar Termux"""
    ram_usage = get_ram_usage()
    
    log_text = "ARSY MONITOR LOG\n\n"
    log_text += f"Ram ussage {ram_usage}\n"
    log_text += f"Clean Cycle  {total_cleans} X\n\n"
    
    for inst in instances:
        log_text += f"{inst['icon']} {inst['usn']} ({inst['uptime']})\n"
        
    return log_text

def send_discord_report(webhook_url, log_text):
    """Mengirim log ke Discord menggunakan module bawaan urllib"""
    if not webhook_url or "discord.com" not in webhook_url:
        return
        
    # Tambahkan format Bold (**) khusus untuk estetika Discord
    discord_text = log_text.replace("ARSY MONITOR LOG", "**ARSY MONITOR LOG**")
    
    embed = {
        "description": discord_text,
        "color": 5763719,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    }
    
    try:
        req = urllib.request.Request(webhook_url, method="POST")
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"embeds": [embed]}).encode('utf-8')
        urllib.request.urlopen(req, data=data, timeout=5)
    except:
        pass

def run_engine(config):
    """Mesin utama 24/7 AFK"""
    packages = get_roblox_packages()
    
    if not packages:
        print("\n[❌] Tidak ada aplikasi Roblox yang terinstal!")
        time.sleep(2)
        return

    # 1. Bawa Termux ke Layar Utama (Home Screen)
    go_to_home_screen()
    
    # 2. Persiapan Bersih
    for pkg in packages:
        os.system(f"su -c 'am force-stop {pkg}'")
    
    deploy_telemetry_lua(packages)
    time.sleep(2)
    
    launch_to_vip_server(packages, config["vip_link"])
    
    gc.collect() 
    loop_count = 0
    total_cleans = 0 

    # 3. Siklus Latar Belakang (Anti-Ghost Touch)
    while True:
        try:
            # Tertidur pulas selama 10 Menit
            time.sleep(600) 
            loop_count += 1
            
            # Setiap 30 menit (Loop ke-3), lakukan sapu bersih RAM
            if loop_count >= 3:
                clean_system_cache()
                total_cleans += 1 
                loop_count = 0 
                
            # Ambil data dan bentuk log
            instances_data = get_instances_telemetry(packages)
            log_text = generate_log_text(instances_data, total_cleans)
            
            # Tampilkan di Termux (Berjaga-jaga jika Termux dibuka kembali)
            clear_screen()
            print(log_text)
            print("\n[!] Mesin berjalan normal di latar belakang.")
            print("[!] Tekan CTRL+C dua kali dengan cepat untuk mematikan bot.")
            
            # Kirim ke Discord
            send_discord_report(config["webhook_url"], log_text)
            
            # Paksa pembuangan sampah memori Termux
            del instances_data
            del log_text
            gc.collect()
            
        except KeyboardInterrupt:
            # Mencegah Termux mati karena salah pencet
            print("\n[!] Peringatan: Input terdeteksi. Skrip menahan diri...")
            time.sleep(2)
        except Exception:
            # Abaikan jika ada error pembacaan sistem dan lanjut AFK
            pass

def main():
    config = load_config()
    
    while True:
        clear_screen()
        print("====================================")
        print("        ARSY V2.0 PURE AFK          ")
        print("====================================")
        print("[1] Jalankan")
        print("[2] Link Private server")
        print("[3] Link Discord")
        print("[0] Keluar")
        print("====================================")
        
        # Indikator status pengisian
        print(f"\n* VIP Link: {'[Terisi]' if config['vip_link'] else '[KOSONG]'}")
        print(f"* Discord:  {'[Terisi]' if config['webhook_url'] else '[KOSONG]'}")
        
        choice = input("\nPilih Menu (0-3): ")
        
        if choice == '1':
            if not config['vip_link'] or not config['webhook_url']:
                print("\n[!] Peringatan: Anda harus mengisi Link Private Server dan Discord terlebih dahulu!")
                time.sleep(2)
            else:
                run_engine(config)
                break 
        elif choice == '2':
            print(f"\nLink lama: {config['vip_link']}")
            new_vip = input("Masukkan Link VIP baru: ")
            if new_vip.strip():
                config['vip_link'] = new_vip.strip()
                save_config(config)
                print("[+] Disimpan!")
                time.sleep(1)
        elif choice == '3':
            print(f"\nLink lama: {config['webhook_url']}")
            new_web = input("Masukkan Webhook baru: ")
            if new_web.strip():
                config['webhook_url'] = new_web.strip()
                save_config(config)
                print("[+] Disimpan!")
                time.sleep(1)
        elif choice == '0':
            clear_screen()
            break
        else:
            print("Pilihan tidak valid.")
            time.sleep(1)

if __name__ == "__main__":
    main()
