import time, os, subprocess, json, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys

class QuietLogger(object):
    def write(self, *args, **kwargs): pass
    def flush(self): pass
sys.stderr = QuietLogger()

CONFIG_FILE = "arsy_config.json"
PORT = 8080

config = {}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f: config.update(json.load(f))
    except: pass

ps_link = config.get("ps_link", "")

# ==========================================
# 🤖 SMART PACKAGE DETECTOR
# ==========================================
try:
    # Mencari semua aplikasi pihak ketiga (-3) yang diinstal manual di Redfinger
    raw_apps = subprocess.check_output("su -c 'pm list packages -3'", shell=True).decode('utf-8').strip().split('\n')
    
    # Daftar aplikasi bawaan/tools yang harus diabaikan oleh bot
    ignore_list = ['termux', 'google', 'android', 'browser', 'launcher', 'webview', 'keyboard', 'redfinger', 'vending']
    
    apps = []
    for p in raw_apps:
        pkg = p.replace('package:', '').strip()
        if pkg and not any(ig in pkg.lower() for ig in ignore_list):
            apps.append(pkg)
            
    # Jika gagal menemukan, gunakan nama standar
    if not apps: apps = ["com.roblox.client"]
except:
    apps = ["com.roblox.client"]

account_map = config.get("apps", {})
app_states = {a: {"status": "🟡 Reconnect", "start_time": time.time(), "last_ping": time.time(), "usn": account_map.get(a, a), "suspended": False} for a in apps}

# ==========================================
# 🚀 LAUNCHER KENDALI APLIKASI
# ==========================================
def launch_app(pkg):
    subprocess.run(f"su -c 'am force-stop {pkg}'", shell=True, stdout=subprocess.DEVNULL)
    time.sleep(2)
    app_states[pkg]["start_time"] = time.time()
    app_states[pkg]["last_ping"] = time.time()
    app_states[pkg]["status"] = "🟡 Reconnect"
    app_states[pkg]["suspended"] = False
    
    if ps_link == "": subprocess.run(f"su -c 'am start -a android.intent.action.MAIN -p {pkg} -f 0x10008000'", shell=True, stdout=subprocess.DEVNULL)
    else: subprocess.run(f"su -c 'am start -a android.intent.action.VIEW -d \"{ps_link}\" -p {pkg} -f 0x10008000'", shell=True, stdout=subprocess.DEVNULL)

for a in apps: launch_app(a)
time.sleep(12)

def format_uptime(seconds):
    h = int(seconds // 3600); m = int((seconds % 3600) // 60); s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ==========================================
# 🌐 WEB SERVER & API DASHBOARD
# ==========================================
class ArsyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        
        if parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
            <!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
            <title>ARSY V2.0</title>
            <style>
                body { background: #0f0f0f; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 15px; }
                h2 { color: #00e676; text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }
                th, td { border: 1px solid #333; padding: 12px; text-align: center; }
                th { background: #222; color: #00e676; }
                tr:nth-child(even) { background-color: #1a1a1a; }
                .btn { padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin: 2px; }
                .btn-res { background: #2979ff; color: #fff; }
                .btn-stp { background: #ff1744; color: #fff; }
                .on { color: #00e676; font-weight: bold; } .wait { color: #ffea00; } .off { color: #ff1744; }
            </style>
            <script>
                function action(app, act) { fetch('/action?app=' + app + '&type=' + act).then(() => location.reload()); }
                setTimeout(() => location.reload(), 15000);
            </script>
            </head><body>
            <h2>🚀 ARSY V2.0 CONTROL CENTER</h2>
            <table><tr><th>Akun (USN)</th><th>Status</th><th>Uptime</th><th>Aksi</th></tr>
            """
            for a, state in app_states.items():
                up_sec = time.time() - state["start_time"]
                up_str = "--:--:--" if "Disconnect" in state["status"] or state["suspended"] else format_uptime(up_sec)
                
                c_stat = "on" if "🟢" in state["status"] else ("wait" if "🟡" in state["status"] else "off")
                btns = f"<button class='btn btn-res' onclick=\"action('{a}', 'restart')\">🔄</button> <button class='btn btn-stp' onclick=\"action('{a}', 'suspend')\">⏸️</button>"
                
                html += f"<tr><td>{state['usn']}</td><td class='{c_stat}'>{state['status']}</td><td>{up_str}</td><td>{btns}</td></tr>"
            
            html += "</table><div style='text-align:center; margin-top:20px; font-size:12px; color:#666;'>Engine: Auto-Detect Active | Auto-Flush: ON</div></body></html>"
            self.wfile.write(html.encode('utf-8'))
            return

        if parsed.path == '/action':
            tgt = query.get('app', [''])[0]
            act = query.get('type', [''])[0]
            if tgt in app_states:
                if act == 'restart': launch_app(tgt)
                elif act == 'suspend':
                    app_states[tgt]["suspended"] = True
                    app_states[tgt]["status"] = "⚠️ Suspended"
                    subprocess.run(f"su -c 'am force-stop {tgt}'", shell=True)
            self.send_response(200)
            self.end_headers()
            return

        usn_sig = query.get('usn', [''])[0]
        tgt = next((a for a, s in app_states.items() if s["usn"] == usn_sig or a == usn_sig), None)
        
        if tgt and not app_states[tgt]["suspended"]:
            if parsed.path == '/ping':
                if "Reconnect" in app_states[tgt]["status"]:
                    app_states[tgt]["usn"] = usn_sig
                    account_map[tgt] = usn_sig
                    config["apps"] = account_map
                    try:
                        with open(CONFIG_FILE, "w") as f: json.dump(config, f)
                    except: pass
                app_states[tgt]["status"] = "🟢 Connect | scriptON"
                app_states[tgt]["last_ping"] = time.time()
            elif parsed.path == '/warn':
                app_states[tgt]["status"] = "🔴 Disconnect (Warn)"
                launch_app(tgt)
                
        self.send_response(200)
        self.end_headers()

threading.Thread(target=lambda: HTTPServer(('127.0.0.1', PORT), ArsyServer).serve_forever(), daemon=True).start()

last_ram_clear = time.time()
while True:
    for a, state in app_states.items():
        if not state["suspended"]:
            uptime_sec = time.time() - state["start_time"]
            time_since_last_ping = time.time() - state["last_ping"]
            
            if time_since_last_ping > 180 and uptime_sec > 180: launch_app(a)
            if uptime_sec > 14400: launch_app(a)
    
    if time.time() - last_ram_clear > 3600:
        subprocess.run("su -c 'echo 3 > /proc/sys/vm/drop_caches'", shell=True, stdout=subprocess.DEVNULL)
        last_ram_clear = time.time()
        
    time.sleep(10)
