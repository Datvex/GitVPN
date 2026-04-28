import base64
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

_srv = None

class SubHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        f_map = {"/sub": "all_configs.txt", "/white": "white_configs.txt"}
        if self.path in f_map:
            try:
                with open(f_map[self.path], "r", encoding="utf-8") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(base64.b64encode(data.encode()))
            except:
                self.send_error(404)
        else:
            self.send_error(404)

def start_server(host, port):
    global _srv
    if _srv: return False
    _srv = HTTPServer((host, port), SubHandler)
    threading.Thread(target=_srv.serve_forever, daemon=True).start()
    return True

def stop_server():
    global _srv
    if _srv:
        _srv.shutdown()
        _srv = None