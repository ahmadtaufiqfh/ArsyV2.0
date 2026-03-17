import os
import time
import json
import sys
import subprocess

CONFIG_FILE = "config.json"

def clear_screen():
    sys.stdout.write('\033c\033[3J')
    sys.stdout.flush()

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
    subprocess.run(["su", "-c", "am start -a android.intent.action.MAIN -c android.intent.category.HOME"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

def get_roblox_packages():
    packages = []
    try:
        output = subprocess.check_output(["su", "-c", "pm list packages"]).decode('utf-8')
        for line in output.splitlines():
            if 'roblox' in line.lower():
                packages.append(line.split(':')[1])
    except:
        pass
    return packages

def get_ram_usage():
    try:
        output = subprocess.check_output(["su", "-c", "cat /proc/meminfo"]).decode('utf-8')
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
        intent_command = f"am start -a android.intent.action.VIEW -d \"{vip_link}\" {pkg}"
        subprocess.run(["su", "-c", intent_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)

def clean_system_cache():
    subprocess.run(["su", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ==========================================
# PENAMBAHAN FUNGSI GRID LAYOUT (DIRECT INJECTION PIPING)
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

    # Membangun script shell langsung di memori (Tanpa buat file)
    commands = []
    for i, pkg in enumerate(sorted(packages)):
        c, r = i % cols, i // cols
        L = (c * cellW) + MARGIN
        R = ((c + 1) * cellW) - GAP
        T = (r * cellH) + OFFSET_TOP
        B = ((r + 1) * cellH) - GAP
        
        cmd = f"""
am force-stop {pkg}
PREF="/data/data/{pkg}/shared_prefs/{pkg}_preferences.xml"
mkdir -p /data/data/{pkg}/shared_prefs

# Simpan data XML lama ke dalam memori (Abaikan tag map)
OLD_DATA=$(grep -v 'app_cloner_current_window_' $PREF | grep -v '</map>' | grep -v '<?xml' 2>/dev/null)

# Tulis ulang XML dengan koordinat baru
echo '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>' > $PREF
echo '<map>' >> $PREF
if [ -n "$OLD_DATA" ]; then
    echo "$OLD_DATA" >> $PREF
fi
echo '    <int name="app_cloner_current_window_left" value="{L}" />' >> $PREF
echo '    <int name="app_cloner_current_window_top" value="{T}" />' >> $PREF
echo '    <int name="app_cloner_current_window_right" value="{R}" />' >> $PREF
echo '    <int name="app_cloner_current_window_bottom" value="{B}" />' >> $PREF
echo '</map>' >> $PREF

# Perbaiki Akses
OWNER=$(ls -ld /data/data/{pkg} | awk '{{print $3}}')
chown $OWNER:$OWNER $PREF
chmod 660 $PREF

# Jalankan monkey di BACKGROUND (&) agar script Python tidak Freeze!
monkey -p {pkg} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1 &
sleep 1.5
"""
        commands.append(cmd)
    
    full_script = "\n".join(commands)
    
    # Eksekusi langsung ke Root via Jalur Pipa (Subprocess Pipe)
    try:
        process = subprocess.Popen(['su'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.communicate(input=full_script.encode('utf-8'))
    except Exception as e:
        print(f"Error injeksi grid: {e}")
