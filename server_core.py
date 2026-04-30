import base64
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

_srv = None

class SubHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        f_map = {"/sub": "all_configs.txt", "/white": "white_configs.txt"}
        if self.path in f_map:
            try:
                content = ""
                if os.path.exists(f_map[self.path]):
                    with open(f_map[self.path], "r", encoding="utf-8") as f:
                        content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(base64.b64encode(content.encode('utf-8')))
            except:
                self.send_error(500)
        else:
            self.send_error(404)

def start_server(host, port):
    global _srv
    if _srv: return False
    try:
        _srv = HTTPServer((host, port), SubHandler)
        threading.Thread(target=_srv.serve_forever, daemon=True).start()
        return True
    except: return False

def stop_server():
    global _srv
    if _srv:
        _srv.shutdown()
        _srv.server_close()
        _srv = None