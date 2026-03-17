import os
import time
import json
import subprocess

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

def launch_to_vip_server(packages, vip_link):
    for pkg in packages:
        intent_command = f"su -c 'am start -a android.intent.action.VIEW -d \"{vip_link}\" {pkg}'"
        os.system(intent_command)
        time.sleep(10)

def clean_system_cache():
    os.system("su -c 'sync; echo 3 > /proc/sys/vm/drop_caches' > /dev/null 2>&1")

# ==========================================
# PENAMBAHAN FUNGSI GRID LAYOUT (FIXED PATH & EXECUTION)
# ==========================================
def apply_grid_layout(packages):
    count = len(packages)
    if count == 0:
        return

    # Algoritma Matematika Grid Presisi
    cols = 1
    while (cols * cols) < count:
        cols += 1
    rows = (count + cols - 1) // cols

    W, H = 1280, 720
    cellW, cellH = W // cols, H // rows
    MARGIN, GAP, OFFSET_TOP = 2, 1, 35

    script_content = "#!/system/bin/sh\n"
    for i, pkg in enumerate(sorted(packages)):
        c, r = i % cols, i // cols
        L = (c * cellW) + MARGIN
        R = ((c + 1) * cellW) - GAP
        T = (r * cellH) + OFFSET_TOP
        B = ((r + 1) * cellH) - GAP
        
        script_content += f"""
am force-stop {pkg}
PREF="/data/data/{pkg}/shared_prefs/{pkg}_preferences.xml"
TMP="/data/local/tmp/prefs_{pkg}.tmp"

grep -v 'app_cloner_current_window_' $PREF | grep -v '</map>' | grep -v '<?xml' > $TMP 2>/dev/null

echo '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>' > $PREF
echo '<map>' >> $PREF
cat $TMP >> $PREF
echo '    <int name="app_cloner_current_window_left" value="{L}" />' >> $PREF
echo '    <int name="app_cloner_current_window_top" value="{T}" />' >> $PREF
echo '    <int name="app_cloner_current_window_right" value="{R}" />' >> $PREF
echo '    <int name="app_cloner_current_window_bottom" value="{B}" />' >> $PREF
echo '</map>' >> $PREF

OWNER=$(ls -ld /data/data/{pkg} | awk '{{print $3}}')
chown $OWNER:$OWNER $PREF
chmod 660 $PREF
monkey -p {pkg} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1
sleep 1.5
"""
    
    # 1. Dapatkan Alamat Mutlak (Absolute Path) dari lokasi script saat ini
    abs_path = os.path.abspath("temp_grid.sh")
    
    # 2. Tulis file bash sementaranya
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # 3. Minta Root untuk mengeksekusi file tersebut langsung dari lokasinya!
    os.system(f"su -c 'sh {abs_path}'")
    
    # 4. Hapus file sementara setelah proses selesai
    if os.path.exists(abs_path):
        os.remove(abs_path)
