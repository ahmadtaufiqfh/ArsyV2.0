import os
import time
import json
import subprocess

CONFIG_FILE = "config.json"

def clear_screen():
    os.system("stty sane")
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
# PENAMBAHAN FUNGSI GRID LAYOUT (MATEMATIKA ANTI-TUMPUK TITLE BAR)
# ==========================================
def apply_grid_layout(packages):
    count = len(packages)
    if count == 0:
        return

    # Algoritma Penentu Kolom & Baris
    cols = 1
    while (cols * cols) < count:
        cols += 1
    rows = (count + cols - 1) // cols

    W, H = 1280, 720

    # KUNCI BARU: Spasi Khusus untuk Title Bar Android
    TOP_MARGIN = 65     # Jarak dari atas layar (Untuk Status bar + Title bar baris ke-1)
    BOTTOM_MARGIN = 45  # Jarak dari bawah layar (Untuk tombol Navigasi)
    TITLE_BAR_GAP = 40  # RUANG KOSONG khusus antar baris agar bar biru tidak menabrak!
    GAP = 2             # Jarak tipis horizontal antar aplikasi

    # Hitung tinggi yang benar-benar bisa dipakai (dikurangi total celah Title Bar)
    total_vertical_gaps = (rows - 1) * TITLE_BAR_GAP
    USABLE_H = H - TOP_MARGIN - BOTTOM_MARGIN - total_vertical_gaps

    cellW = W // cols
    cellH = USABLE_H // rows

    script_content = "#!/system/bin/sh\n"
    for i, pkg in enumerate(sorted(packages)):
        c, r = i % cols, i // cols
        
        # Horizontal (Kiri-Kanan) tidak ada masalah, tetap pakai GAP
        L = (c * cellW) + GAP
        R = ((c + 1) * cellW) - GAP
        
        # Vertikal (Atas-Bawah) disisipkan TITLE_BAR_GAP untuk setiap baris baru
        T = TOP_MARGIN + (r * (cellH + TITLE_BAR_GAP)) + GAP
        B = T + cellH - (GAP * 2)
        
        script_content += f"""
echo "-> Memproses {pkg}"
am force-stop {pkg}

PREF_FILE="/data/data/{pkg}/shared_prefs/{pkg}_preferences.xml"
TMP_FILE="/data/local/tmp/prefs_{pkg}.tmp"

grep -v 'app_cloner_current_window_' $PREF_FILE | grep -v '</map>' > $TMP_FILE 2>/dev/null

check_file=$(cat $TMP_FILE 2>/dev/null)
if [ -z "$check_file" ]; then
    echo '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>' > $TMP_FILE
    echo '<map>' >> $TMP_FILE
fi

echo '    <int name="app_cloner_current_window_left" value="{L}" />' >> $TMP_FILE
echo '    <int name="app_cloner_current_window_top" value="{T}" />' >> $TMP_FILE
echo '    <int name="app_cloner_current_window_right" value="{R}" />' >> $TMP_FILE
echo '    <int name="app_cloner_current_window_bottom" value="{B}" />' >> $TMP_FILE
echo '</map>' >> $TMP_FILE

mv $TMP_FILE $PREF_FILE

OWNER=$(ls -ld /data/data/{pkg} | awk '{{print $3}}')
chown $OWNER:$OWNER $PREF_FILE
chmod 660 $PREF_FILE

monkey -p {pkg} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1
sleep 4
"""

    # Buat file secara lokal
    local_path = "temp_grid.sh"
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Kopi ke SDCARD agar Root PASTI bisa membacanya
    import os
    os.system(f"cp {local_path} /sdcard/run_grid.sh")
    os.system("su -c 'sh /sdcard/run_grid.sh'")
    
    # Bersihkan sampah
    os.system("su -c 'rm /sdcard/run_grid.sh'")
    if os.path.exists(local_path):
        os.remove(local_path)
