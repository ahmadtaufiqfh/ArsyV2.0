import time, os, subprocess, json, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

CONFIG_FILE = "arsy_config.json"
PORT = 8080

config = {"ps_link": "", "discord_link": "", "apps": {}}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f: config.update(json.load(f))
    except: pass

try:
    raw_apps = subprocess.check_output("su -c 'pm list packages | grep roblox'", shell=True).decode('utf-8').strip().split('\n')
    apps = [p.replace('package:', '').strip() for p in raw_apps if p.strip()]
except: apps = ["com.roblox.client"]

if not apps: apps = ["com.roblox.client"]

app_states = {a: {"status": "🔴 Stopped", "start_time": time.time(), "last_ping": time.time(), "usn": config["apps"].get(a, a), "suspended": True} for a in apps}

def get_total_ram():
    try:
        out = subprocess.check_output("su -c 'free -m'", shell=True).decode('utf-8').split('\n')[1].split()
        return f"Sisa RAM Redfinger: {out[3]}MB / {out[1]}MB"
    except: return "Membaca RAM..."

def get_app_ram(pkg):
    try:
        out = subprocess.check_output(f"su -c 'dumpsys meminfo {pkg} | grep TOTAL'", shell=True).decode('utf-8')
        return f"{int(out.strip().split()[1]) // 1024} MB"
    except: return "0 MB"

def launch_app(pkg):
    # Bersihkan sisa crash lama
    subprocess.run(f"su -c 'am force-stop {pkg}'", shell=True)
    time.sleep(2)
    
    app_states[pkg]["suspended"] = False
    app_states[pkg]["status"] = "🟡 Menunggu Game..."
    
    # Gunakan perintah start standar tanpa flag berat
    subprocess.run(f"su -c 'monkey -p {pkg} -c android.intent.category.LAUNCHER 1'", shell=True)

def format_uptime(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

class ArsyServer(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass 
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        
        if parsed.path == '/':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            html = f"""
            <!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
            <style>
                body {{ background: #0f0f0f; color: #e0e0e0; font-family: sans-serif; margin: 0; padding: 10px; font-size: 12px; }}
                .box {{ background: #1a1a1a; padding: 10px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #333; }}
                input {{ width: 100%; padding: 6px; margin: 4px 0; background: #222; color: #fff; border: 1px solid #555; box-sizing: border-box; }}
                .btn {{ padding: 6px 10px; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; color: #fff; margin-right: 2px; text-decoration: none; display: inline-block; }}
                .b-save {{ background: #00c853; width: 100%; margin-top: 5px; text-align: center; }} .b-run {{ background: #2979ff; }} .b-stp {{ background: #ff1744; }} .b-rst {{ background: #ff9100; width: 100%; margin-top: 5px; text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 5px; }}
                th, td {{ border: 1px solid #333; padding: 6px; text-align: center; }}
                th {{ background: #222; color: #00c853; }}
                .on {{ color: #00c853; font-weight:bold; }} .wait {{ color: #ffea00; }} .off {{ color: #ff1744; }}
            </style>
            <script>
                function saveCfg() {{
                    let ps = document.getElementById('ps').value; let dc = document.getElementById('dc').value;
                    window.location.href = '/config?ps=' + encodeURIComponent(ps) + '&dc=' + encodeURIComponent(dc);
                }}
                setTimeout(() => window.location.reload(), 15000);
            </script>
            </head><body>
            <h3 style="color:#00c853; text-align:center; margin: 5px 0;">🚀 ARSY V2.0 PRO</h3>
            <div class="box">
                <b>⚙️ Pengaturan Server</b>
                <input type="text" id="ps" placeholder="Link Private Server" value="{config.get('ps_link', '')}">
                <input type="text" id="dc" placeholder="Link Webhook Discord" value="{config.get('discord_link', '')}">
                <button class="btn b-save" onclick="saveCfg()">Simpan Konfigurasi</button>
            </div>
            <div class="box">
                <b>📊 Analitik Sistem</b><br>
                <span style="color:#2979ff; font-weight:bold;">{get_total_ram()}</span>
                <a href="/reset" class="btn b-rst">🧹 Reset RAM</a>
            </div>
            <table><tr><th>Akun</th><th>Status</th><th>RAM</th><th>Uptime</th><th>Aksi</th></tr>
            """
            for a, state in app_states.items():
                up_str = "--:--:--" if state["suspended"] else format_uptime(time.time() - state["start_time"])
                c_stat = "on" if "🟢" in state["status"] else ("wait" if "🟡" in state["status"] else "off")
                ram_usg = get_app_ram(a) if not state["suspended"] else "0 MB"
                btns = f"<a href='/action?app={a}&type=restart' class='btn b-run'>▶️</a> <a href='/action?app={a}&type=suspend' class='btn b-stp'>⏹️</a>"
                html += f"<tr><td>{state['usn']}</td><td class='{c_stat}'>{state['status']}</td><td>{ram_usg}</td><td>{up_str}</td><td>{btns}</td></tr>"
            html += "</table></body></html>"; self.wfile.write(html.encode('utf-8')); return

        if parsed.path == '/config':
            config["ps_link"] = query.get('ps', [''])[0]; config["discord_link"] = query.get('dc', [''])[0]
            with open(CONFIG_FILE, "w") as f: json.dump(config, f)
            self.send_response(302); self.send_header('Location', '/'); self.end_headers(); return

        if parsed.path == '/reset':
            subprocess.run("su -c 'echo 3 > /proc/sys/vm/drop_caches'", shell=True) 
            self.send_response(302); self.send_header('Location', '/'); self.end_headers(); return

        if parsed.path == '/action':
            tgt = query.get('app', [''])[0]; act = query.get('type', [''])[0]
            if tgt in app_states:
                if act == 'restart': launch_app(tgt)
                elif act == 'suspend':
                    app_states[tgt]["suspended"] = True; app_states[tgt]["status"] = "🔴 Stopped"
                    subprocess.run(f"su -c 'am force-stop {tgt}'", shell=True)
            self.send_response(302); self.send_header('Location', '/'); self.end_headers(); return

        usn_sig = query.get('usn', [''])[0]
        if usn_sig:
            tgt = next((a for a, s in app_states.items() if s["usn"] == usn_sig or a == usn_sig), None)
            if tgt and not app_states[tgt]["suspended"]:
                if parsed.path == '/ping':
                    if "Menunggu" in app_states[tgt]["status"]:
                        app_states[tgt]["usn"] = usn_sig; config.setdefault("apps", {})[tgt] = usn_sig
                        with open(CONFIG_FILE, "w") as f: json.dump(config, f)
                    app_states[tgt]["status"] = "🟢 Connect"
                    app_states[tgt]["last_ping"] = time.time()
        self.send_response(200); self.end_headers(); return

try:
    server = HTTPServer(('127.0.0.1', PORT), ArsyServer)
    print(f"[SUCCESS] Server berjalan di http://127.0.0.1:{PORT}")
    threading.Thread(target=server.serve_forever, daemon=True).start()
except Exception as e:
    print(f"[ERROR] GAGAL START SERVER: {e}")

try:
    subprocess.run("termux-open-url http://127.0.0.1:8080", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except: pass

while True: time.sleep(10)
