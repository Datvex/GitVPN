import base64
import threading
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from config import load_config

_srv = None

# fix #5 — lock для кэша
_cache_lock = threading.RLock()
_cache = {"reg": "", "whi": ""}

_rate_limit = {}
_rate_limit_lock = threading.Lock()  # fix #6


def update_cache(r, w):
    with _cache_lock:  # fix #5
        _cache["reg"] = r
        _cache["whi"] = w

def update_cache(r, w):
    _cache["reg"], _cache["whi"] = r, w

def load_initial_cache():
    if os.path.exists("all_configs.txt"):
        try:
            with open("all_configs.txt", "r", encoding="utf-8") as f: 
                _cache["reg"] = f.read()
        except: pass
    if os.path.exists("white_configs.txt"):
        try:
            with open("white_configs.txt", "r", encoding="utf-8") as f: 
                _cache["whi"] = f.read()
        except: pass

class SubHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def do_GET(self):
        try:
            client_ip = self.client_address[0]
            now = time.time()

            # fix #6 — атомарная проверка rate limit
            with _rate_limit_lock:
                timestamps = [t for t in _rate_limit.get(client_ip, [])
                              if now - t < 60]
                if len(timestamps) >= 30:
                    self.send_error(429, "Too Many Requests")
                    return
                timestamps.append(now)
                _rate_limit[client_ip] = timestamps

            cfg = load_config()
            up = urlparse(self.path)
            qs = parse_qs(up.query)

            provided_token = qs.get("token", [None])[0]
            if provided_token != cfg.get("server_token"):
                self.send_error(403, "Forbidden: Invalid Token")
                return

            f_map = {"/sub": "reg", "/white": "whi"}
            if up.path in f_map:
                with _cache_lock:  # fix #5
                    content = _cache[f_map[up.path]]
                encoded = base64.b64encode(content.encode('utf-8'))
                
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Connection", "close")
                self.end_headers()
                
                self.wfile.write(encoded)
                self.wfile.flush()
            else:
                self.send_error(404)
        except Exception:
            pass

def start_server(host, port):
    global _srv
    if _srv: return False
    load_initial_cache()
    try:
        _srv = HTTPServer((host, port), SubHandler)
        _srv.allow_reuse_address = True
        threading.Thread(target=_srv.serve_forever, daemon=True).start()
        return True
    except Exception as e:
        return False

def stop_server():
    global _srv
    if _srv:
        _srv.shutdown()
        _srv.server_close()
        _srv = None