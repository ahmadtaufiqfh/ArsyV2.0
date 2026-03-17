import os
import time
import json
import subprocess

CONFIG_FILE = "config.json"

def clear_screen():
    os.system("stty sane")
    os.system("clear")

def load_config():
    default_config = {
        "webhook_url": "", 
        "vip_link": "", 
        "vip_limit": 0, 
        "public_link": ""
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                for k, v in default_config.items():
                    if k not in config:
                        config[k] = v
                return config
        except:
            pass
    return default_config

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

def launch_to_vip_server(packages, vip_link, vip_limit=0, public_link=""):
    sorted_packages = sorted(packages)
    
    if vip_limit <= 0 or vip_limit > len(sorted_packages):
        vip_limit = len(sorted_packages)
        
    for i, pkg in enumerate(sorted_packages):
        if i < vip_limit:
            if vip_link:
                intent_command = f"su -c 'am start -a android.intent.action.VIEW -d \"{vip_link}\" {pkg} > /dev/null 2>&1'"
                print(f" -> [{pkg}] Membuka Link VIP...")
            else:
                intent_command = f"su -c 'monkey -p {pkg} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1'"
                print(f" -> [{pkg}] Membuka Menu Utama (Link VIP Kosong)...")
        else:
            if public_link:
                intent_command = f"su -c 'am start -a android.intent.action.VIEW -d \"{public_link}\" {pkg} > /dev/null 2>&1'"
                print(f" -> [{pkg}] Membuka Link Public...")
            else:
                intent_command = f"su -c 'monkey -p {pkg} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1'"
                print(f" -> [{pkg}] Membuka Menu Utama (Sisa Akun)...")
        
        os.system(intent_command)
        time.sleep(10)

def clean_system_cache():
    os.system("su -c 'sync; echo 3 > /proc/sys/vm/drop_caches > /dev/null 2>&1'")

def apply_grid_layout(packages):
    count = len(packages)
    if count == 0:
        return

    grid_count = count
    if grid_count % 2 != 0 and grid_count > 1:
        grid_count += 1

    cols = 1
    while (cols * cols) < grid_count:
        cols += 1
    rows = (grid_count + cols - 1) // cols

    W, H = 1280, 720
    TOP_MARGIN = 45      
    BOTTOM_MARGIN = 15   
    TITLE_BAR_GAP = 32   
    GAP = 2 

    USABLE_W = W
    USABLE_H = H - TOP_MARGIN - BOTTOM_MARGIN
    TARGET_RATIO = 1.77 

    max_W_by_width = (USABLE_W - ((cols - 1) * GAP)) / cols
    max_H_by_width = max_W_by_width / TARGET_RATIO
    max_H_by_height = (USABLE_H - ((rows - 1) * TITLE_BAR_GAP) - ((rows - 1) * GAP)) / rows
    max_W_by_height = max_H_by_height * TARGET_RATIO

    app_W = int(min(max_W_by_width, max_W_by_height))
    app_H = int(app_W / TARGET_RATIO)

    total_grid_W = (cols * app_W) + ((cols - 1) * GAP)
    total_grid_H = (rows * app_H) + ((rows - 1) * (TITLE_BAR_GAP + GAP))

    start_X = (USABLE_W - total_grid_W) // 2
    start_Y = TOP_MARGIN + ((USABLE_H - total_grid_H) // 2)

    script_content = "#!/system/bin/sh\n"
    for i, pkg in enumerate(sorted(packages)):
        c, r = i % cols, i // cols
        
        L = start_X + (c * (app_W + GAP))
        R = L + app_W
        T = start_Y + (r * (app_H + TITLE_BAR_GAP + GAP))
        B = T + app_H
        
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

    import os
    local_path = "temp_grid.sh"
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    os.system(f"cp {local_path} /sdcard/run_grid.sh")
    os.system("su -c 'sh /sdcard/run_grid.sh'")
    
    os.system("su -c 'rm /sdcard/run_grid.sh'")
    if os.path.exists(local_path):
        os.remove(local_path)
