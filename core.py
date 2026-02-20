import time, os, subprocess, json, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8080
app_states = {"com.roblox.clienb": {"status": "🔴 Stopped", "usn": "com.roblox.clienb", "suspended": True}}

class ArsyServer(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        
        if parsed.path == '/':
            self.send_response(200); self.send_header('Content-type', 'text/html'); self.end_headers()
            state = app_states["com.roblox.clienb"]
            c_stat = "color:#00c853" if "🟢" in state["status"] else "color:#ffea00"
            html = f"""
            <html><body style="background:#000;color:#fff;font-family:sans-serif;text-align:center;">
                <h2>🚀 ARSY LITE STABLE</h2>
                <div style="border:1px solid #333;padding:20px;margin:20px;border-radius:10px;">
                    <b style="font-size:20px;">{state['usn']}</b><br>
                    <p style="{c_stat};font-weight:bold;font-size:18px;">{state['status']}</p>
                    <a href="/run" style="background:#2979ff;color:#fff;padding:15px 30px;text-decoration:none;border-radius:5px;display:inline-block;margin:10px;">▶️ MULAI GAME</a>
                    <a href="/stop" style="background:#ff1744;color:#fff;padding:15px 30px;text-decoration:none;border-radius:5px;display:inline-block;margin:10px;">⏹️ STOP</a>
                </div>
            </body></html>"""
            self.wfile.write(html.encode())
        
        elif parsed.path == '/run':
            pkg = "com.roblox.clienb"
            subprocess.run(f"su -c 'am force-stop {pkg}'", shell=True)
            time.sleep(3)
            app_states[pkg]["status"] = "🟡 Menunggu..."
            # Perintah paling stabil: Menggunakan Monkey tanpa Flags aneh
            subprocess.run(f"su -c 'monkey -p {pkg} -c android.intent.category.LAUNCHER 1'", shell=True)
            self.send_response(302); self.send_header('Location', '/'); self.end_headers()

        elif parsed.path == '/ping':
            usn = query.get('usn', [''])[0]
            if usn: 
                app_states["com.roblox.clienb"]["usn"] = usn
                app_states["com.roblox.clienb"]["status"] = "🟢 Connect"
            self.send_response(200); self.end_headers()

server = HTTPServer(('127.0.0.1', PORT), ArsyServer)
print("[SUCCESS] MONITORING AKTIF")
server.serve_forever()
