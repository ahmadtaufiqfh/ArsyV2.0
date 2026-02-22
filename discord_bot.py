import json
import time
import urllib.request
import urllib.error
import os
from utils import get_ram_usage

MESSAGE_ID_FILE = "discord_msg_id.txt"

def generate_log_text(instances, total_cleans):
    ram_usage = get_ram_usage()
    
    log_text = "ARSY MONITOR LOG\n\n"
    log_text += f"Ram ussage {ram_usage}\n"
    log_text += f"Clean Cycle  {total_cleans} X\n\n"
    
    for inst in instances:
        log_text += f"{inst['icon']} {inst['usn']} ({inst['uptime']})\n"
        
    return log_text

def send_discord_report(webhook_url, log_text):
    if not webhook_url or "discord.com" not in webhook_url:
        return
        
    discord_text = log_text.replace("ARSY MONITOR LOG", "**ARSY MONITOR LOG**")
    
    embed = {
        "description": discord_text,
        "color": 5763719,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    }
    
    payload = json.dumps({"embeds": [embed]}).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }
    
    message_id = None
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            message_id = f.read().strip()

    # Fungsi khusus untuk mengirim pesan BARU
    def post_new_message():
        try:
            post_url = f"{webhook_url}?wait=true"
            req = urllib.request.Request(post_url, data=payload, headers=headers, method="POST")
            response = urllib.request.urlopen(req, timeout=10)
            
            res_json = json.loads(response.read().decode('utf-8'))
            if res_json.get("id"):
                with open(MESSAGE_ID_FILE, "w") as f:
                    f.write(str(res_json["id"]))
        except Exception:
            pass

    # Logika Cerdas: Coba Edit dulu, kalau gagal langsung Kirim Baru!
    if message_id:
        try:
            edit_url = f"{webhook_url}/messages/{message_id}"
            req = urllib.request.Request(edit_url, data=payload, headers=headers, method="PATCH")
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            # GAGAL EDIT? Langsung hapus memori lama dan buat pesan baru!
            if os.path.exists(MESSAGE_ID_FILE):
                os.remove(MESSAGE_ID_FILE)
            post_new_message()
    else:
        # Belum ada memori? Langsung buat pesan baru!
        post_new_message()
