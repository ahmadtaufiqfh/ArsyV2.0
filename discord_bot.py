import json
import time
import urllib.request
import urllib.error
from utils import get_ram_usage

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
    
    try:
        req = urllib.request.Request(webhook_url, method="POST")
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"embeds": [embed]}).encode('utf-8')
        urllib.request.urlopen(req, data=data, timeout=5)
    except:
        pass
