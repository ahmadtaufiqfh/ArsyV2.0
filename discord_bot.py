import json
import time
import urllib.request
import urllib.error
import os
from utils import get_ram_usage

# File untuk menyimpan ID pesan agar bisa diedit terus-menerus
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
    
    # Mengecek apakah bot sudah pernah mengirim pesan sebelumnya
    message_id = None
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            message_id = f.read().strip()
            
    try:
        if message_id:
            # JIKA SUDAH ADA PESAN: Gunakan metode PATCH untuk MENGEDIT pesan lama
            edit_url = f"{webhook_url}/messages/{message_id}"
            req = urllib.request.Request(edit_url, data=payload, method="PATCH")
            req.add_header('Content-Type', 'application/json')
            urllib.request.urlopen(req, timeout=10) # Waktu tunggu diperpanjang agar tidak mudah timeout
        else:
            # JIKA BELUM ADA PESAN: Kirim pesan baru dan simpan ID-nya
            post_url = f"{webhook_url}?wait=true"
            req = urllib.request.Request(post_url, data=payload, method="POST")
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req, timeout=10)
            
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            new_message_id = res_json.get("id")
            
            # Simpan ID pesan ke dalam file
            if new_message_id:
                with open(MESSAGE_ID_FILE, "w") as f:
                    f.write(str(new_message_id))
                    
    except urllib.error.HTTPError as e:
        # PENTING: Jika error 404 (Artinya pesan benar-benar Anda hapus manual di Discord)
        # Barulah bot diizinkan menghapus file memori ID-nya
        if e.code == 404:
            if os.path.exists(MESSAGE_ID_FILE):
                os.remove(MESSAGE_ID_FILE)
    except Exception:
        # Jika error karena baru restart, tidak ada sinyal, atau timeout
        # ABAIKAN SAJA (Pass) dan JANGAN hapus file ID. Bot akan mencoba lagi nanti.
        pass
