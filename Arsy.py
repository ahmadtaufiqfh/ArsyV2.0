import os
import time
import json
import subprocess
import urllib.request
import urllib.error
import gc

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
    print("\n[+] Menyembunyikan Termux ke latar belakang...")
    time.sleep(1)
    os.system("su -c 'am start -a android.intent.action.MAIN -c android.intent.category.HOME > /dev/null 2>&1'")
    time.sleep(2)

def get_roblox_packages():
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
    # LUA SCRIPT: UI Minimalis, Tipis, di Atas Tengah Layar
    lua_script = """if not game:IsLoaded() then game.Loaded:Wait() end
task.wait(2)
local Players = game:GetService("Players")
local usn = Players.LocalPlayer and Players.LocalPlayer.Name or "Unknown"
local startTime = os.time()

pcall(function()
    local sg = Instance.new("ScreenGui")
    sg.Name = "ArsyNotif"
    local target = game:GetService("CoreGui") or Players.LocalPlayer:WaitForChild("PlayerGui")
    sg.Parent = target
    
    local tl = Instance.new("TextLabel")
    tl.Parent = sg
    tl.Size = UDim2.new(0, 200, 0, 30) -- Ukuran sangat kecil dan tipis
    tl.Position = UDim2.new(0.5, -100, 0, 15) -- Di atas tengah layar
    tl.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
    tl.BackgroundTransparency = 0.4
    tl.TextColor3 = Color3.fromRGB(0, 255, 0) 
    tl.TextScaled = false
    tl.TextSize = 14 -- Huruf font kecil
    tl.Font = Enum.Font.Code
    tl.Text = "Arsy V2 | " .. usn
    
    task.delay(5, function() sg:Destroy() end)
end)

while task.wait(30) do
    pcall(function() writefile("arsy_status.txt", usn .. "|" .. tostring(os.time()) .. "|" .. tostring(startTime)) end)
end
"""
    with open("temp_arsy.lua", "w") as f:
        f.write(lua_script)

    for pkg in packages:
        auto_paths = [
            f"/sdcard/Android/data/{pkg}/files/gloop/external/Autoexecute/arsy.lua",
            f"/sdcard/Android/data/{pkg}/files/gloop/external/autoexec/arsy.lua"
        ]
        
        # PERBAIKAN: Membuat dan memberi izin pada DUA kemungkinan nama folder Workspace
        w_lower = f"/sdcard/Android/data/{pkg}/files/gloop/workspace"
        w_upper = f"/sdcard/Android/data/{pkg}/files/gloop/Workspace"
        
        os.system(f"su -c 'mkdir -p \"{w_lower}\"'")
        os.system(f"su -c 'mkdir -p \"{w_upper}\"'")
        os.system(f"su -c 'chmod 777 \"{w_lower}\"'")
        os.system(f"su -c 'chmod 777 \"{w_upper}\"'")
        
        for a_path in auto_paths:
            os.system(f"su -c 'mkdir -p \"$(dirname \"{a_path}\")\"'")
            os.system(f"cat temp_arsy.lua | su -c 'tee \"{a_path}\" > /dev/null'")
            os.system(f"su -c 'chmod 777 \"{a_path}\"'")
            
        os.system(f"su -c 'rm -f \"{w_lower}/arsy_status.txt\"'")
        os.system(f"su -c 'rm -f \"{w_upper}/arsy_status.txt\"'")
        
    if os.path.exists("temp_arsy.lua"):
        os.remove("temp_arsy.lua")

def get_instances_telemetry(packages):
    instances = []
    current_time = int(time.time()) 
    
    for pkg in packages:
        # PERBAIKAN: Menyuruh Termux membaca dari kedua folder (Workspace besar maupun kecil)
        read_cmd = f"su -c 'cat /sdcard/Android/data/{pkg}/files/gloop/workspace/arsy_status.txt 2>/dev/null || cat /sdcard/Android/data/{pkg}/files/gloop/Workspace/arsy_status.txt 2>/dev/null'"
        
        try:
            output = subprocess.check_output(read_cmd, shell=True).decode('utf-8').strip()
            if "|" in output:
                parts = output.split("|")
                usn = parts[0]
                lua_time = int(parts[1])
                start_time = int(parts[2]) if len(parts) > 2 else lua_time
                
                uptime_sec = current_time - start_time
                hours, remainder = divmod(uptime_sec, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
                
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
    for pkg in packages:
        intent_command = f"su -c 'am start -a android.intent.action.VIEW -d \"{vip_link}\" {pkg}'"
        os.system(intent_command)
        time.sleep(10)

def clean_system_cache():
    os.system("su -c 'am kill-all' > /dev/null 2>&1")
    os.system("su -c 'sync; echo 3 > /proc/sys/vm/drop_caches' > /dev/null 2>&1")

def generate_log_text(instances, total_cleans):
    ram_usage = get_ram_usage()
    log_text = "ARSY MONITOR LOG\r\n\r\n"
    log_text += f"Ram ussage {ram_usage}\r\n"
    log_text += f"Clean Cycle  {total_cleans} X\r\n\r\n"
    
    for inst in instances:
        log_text += f"{inst['icon']} {inst['usn']} ({inst['uptime']})\r\n"
        
    return log_text

def send_discord_report(webhook_url, log_text):
    if not webhook_url or "discord.com" not in webhook_url:
        return
        
    discord_text = log_text.replace("ARSY MONITOR LOG", "**ARSY MONITOR LOG**").replace('\r', '')
    embed = {
        "description": discord_text,
        "color": 5763719,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    }
    
    try:
        req = urllib.request.Request(webhook_url, method="POST")
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 'Mozilla/5.0') 
        data = json.dumps({"embeds": [embed]}).encode('utf-8')
        urllib.request.urlopen(req, data=data, timeout=5)
    except Exception as e:
        print(f"\r\n[!] Gagal mengirim Discord: {e}")

def run_engine(config):
    packages = get_roblox_packages()
    if not packages:
        print("\n[❌] Tidak ada aplikasi Roblox yang terinstal!")
        time.sleep(2)
        return

    go_to_home_screen()
    
    for pkg in packages:
        os.system(f"su -c 'am force-stop {pkg}'")
    
    deploy_telemetry_lua(packages)
    time.sleep(2)
    
    launch_to_vip_server(packages, config["vip_link"])
    time.sleep(15)
    
    gc.collect() 
    loop_count = 0
    total_cleans = 0 

    while True:
        try:
            instances_data = get_instances_telemetry(packages)
            log_text = generate_log_text(instances_data, total_cleans)
            
            clear_screen()
            print(log_text)
            print("\r\n[!] Mesin berjalan normal di latar belakang.")
            print("\r\n[!] Tekan CTRL+C dua kali dengan cepat untuk mematikan bot.")
            
            send_discord_report(config["webhook_url"], log_text)
            
            del instances_data
            del log_text
            gc.collect()
            
            time.sleep(600) 
            loop_count += 1
            
            if loop_count >= 3:
                clean_system_cache()
                total_cleans += 1 
                loop_count = 0 
            
        except KeyboardInterrupt:
            print("\r\n[!] Peringatan: Input terdeteksi. Skrip menahan diri...")
            time.sleep(2)
        except Exception as e:
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
        print
