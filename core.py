import os
import json
import secrets
import copy
import requests
import socket
import time
import sys
import base64
import re
import threading
import ssl
import random
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, unquote
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

CONFIG_FILE = os.path.join("configs", "user_config.json")
SOURCES_VERSION = 2

RAW_SOURCES = [
    {"id": 1, "name": "igareck/BLACK_VLESS", "url": "https://raw.githack.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS.txt", "type": "regular", "enabled": True},
    {"id": 2, "name": "igareck/BLACK_SS_All", "url": "https://raw.githack.com/igareck/vpn-configs-for-russia/main/BLACK_SS%2BAll_RUS.txt", "type": "regular", "enabled": False},
    {"id": 3, "name": "AvenCores/mirror_1", "url": "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/1.txt", "type": "regular", "enabled": False},
    {"id": 4, "name": "AvenCores/mirror_23", "url": "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/23.txt", "type": "regular", "enabled": False},
    {"id": 5, "name": "igareck/WHITE_CIDR_All", "url": "https://raw.githack.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-all.txt", "type": "whitelist", "enabled": True},
    {"id": 6, "name": "igareck/WHITE_CIDR_Checked", "url": "https://raw.githack.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt", "type": "whitelist", "enabled": False},
    {"id": 7, "name": "AvenCores/mirror_26", "url": "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/26.txt", "type": "whitelist", "enabled": False},
    {"id": 8, "name": "igareck/WHITE_SNI_All", "url": "https://raw.githack.com/igareck/vpn-configs-for-russia/main/WHITE-SNI-RU-all.txt", "type": "whitelist", "enabled": False}
]

DEFAULT_CONFIG = {
    "filter_russia": True,
    "max_configs": 150,
    "smart_filter": False,
    "test_type": "TCP Ping",
    "parse_interval": 60,
    "ping_timeout": 1.5,
    "sources": RAW_SOURCES,
    "sources_version": SOURCES_VERSION,
    "server_port": 8000,
    "server_host": "127.0.0.1",
    "server_token": secrets.token_hex(8),
    "theme": "Claude",
    "lang": "English",
    "filters": {
        "filter_by_name": {
            "enabled": True,
            "mode": "blacklist",
            "blacklist": ["russia", "moscow", "ru", "russian", "россия", "москва", "🇷"],
            "whitelist": [],
            "case_sensitive": False
        }
    }
}

def load_config():
    if not os.path.exists("configs"):
        os.makedirs("configs")
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        
        final_cfg = copy.deepcopy(DEFAULT_CONFIG)
        keys = ["filter_russia", "max_configs", "parse_interval", "ping_timeout", 
                "server_port", "server_host", "server_token", "theme", "lang", 
                "filters", "test_type", "smart_filter"]
        
        for key in keys:
            if key in user_data:
                final_cfg[key] = user_data[key]

        if user_data.get("sources_version") == SOURCES_VERSION:
            raw_ids = {s["id"] for s in RAW_SOURCES}
            user_sources = user_data.get("sources", [])
            
            updated_sources = []
            user_states = {s["id"]: s.get("enabled", True) for s in user_sources}
            
            for rs in RAW_SOURCES:
                new_src = rs.copy()
                if rs["id"] in user_states:
                    new_src["enabled"] = user_states[rs["id"]]
                updated_sources.append(new_src)
                
            for us in user_sources:
                if us["id"] not in raw_ids:
                    updated_sources.append(us)
                    
            final_cfg["sources"] = updated_sources
        else:
            final_cfg["sources"] = [s.copy() for s in RAW_SOURCES]
            
        return final_cfg
    except Exception:
        return DEFAULT_CONFIG

def save_config(cfg):
    tmp_path = CONFIG_FILE + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, CONFIG_FILE)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0 Safari/537.36"
]

MIRROR_ORDER = ["githack", "jsdelivr", "raw", "github"]
_mirror_lock = threading.Lock()
_preferred_mirror = None

def parse_github_url(url):
    patterns = [
        r"^https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/(?:refs/heads/)?(.+)$",
        r"^https?://raw\.githack\.com/([^/]+)/([^/]+)/(?:refs/heads/)?(.+)$",
        r"^https?://raw\.github\.com/([^/]+)/([^/]+)/(?:refs/heads/)?(.+)$",
        r"^https?://github\.com/([^/]+)/([^/]+)/raw/(?:refs/heads/)?(.+)$",
    ]
    for p in patterns:
        m = re.match(p, url)
        if m:
            user, repo, rest = m.groups()
            branch, _, path = rest.partition("/")
            if not path:
                return None
            return user, repo, branch, path
    return None

def _mirror_urls(parsed):
    user, repo, branch, path = parsed
    urls = {
        "githack": f"https://raw.githack.com/{user}/{repo}/{branch}/{path}",
        "jsdelivr": f"https://cdn.jsdelivr.net/gh/{user}/{repo}@{branch}/{path}",
        "raw": f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}",
        "github": f"https://github.com/{user}/{repo}/raw/refs/heads/{branch}/{path}",
    }
    with _mirror_lock:
        pref = _preferred_mirror
    order = ([pref] if pref in urls else []) + [m for m in MIRROR_ORDER if m != pref]
    return [urls[m] for m in order]

def _mirror_name(url):
    if "raw.githack.com" in url:
        return "githack"
    if "cdn.jsdelivr.net" in url:
        return "jsdelivr"
    if "raw.githubusercontent.com" in url or "raw.github.com" in url:
        return "raw"
    if "github.com" in url:
        return "github"
    return None

def fetch_text(url):
    global _preferred_mirror
    parsed = parse_github_url(url)
    candidates = _mirror_urls(parsed) if parsed else [url]
    for u in candidates:
        try:
            r = requests.get(u, timeout=6, headers={"User-Agent": random.choice(USER_AGENTS)})
            if r.status_code == 200 and r.text:
                name = _mirror_name(u)
                if name:
                    with _mirror_lock:
                        _preferred_mirror = name
                return r.text
        except Exception:
            continue
    return None

_counts = {}
_counts_lock = threading.Lock()

def get_source_counts():
    with _counts_lock:
        return dict(_counts)

def update_counts_bg(sources):
    def fetch(s):
        text = fetch_text(s["url"])
        count = len(re.findall(r"://", text)) if text else 0
        with _counts_lock:
            _counts[s["id"]] = count

    with ThreadPoolExecutor(max_workers=10) as ex:
        for s in sources:
            ex.submit(fetch, s)

_dns_cache = {}
_dns_lock = threading.Lock()

def resolve_host(h):
    with _dns_lock:
        if h in _dns_cache:
            return _dns_cache[h]
    try:
        ip = socket.gethostbyname(h)
    except Exception:
        ip = None
    with _dns_lock:
        _dns_cache[h] = ip
    return ip

def clear_dns_cache():
    with _dns_lock:
        _dns_cache.clear()

def decode_vmess(c):
    try:
        data = c[8:]
        if "#" in data: data = data.split("#")[0]
        missing_padding = len(data) % 4
        if missing_padding: data += '=' * (4 - missing_padding)
        return json.loads(base64.b64decode(data).decode('utf-8', errors='ignore'))
    except: return None

def parse_hp(c):
    try:
        if c.startswith("vmess://"):
            d = decode_vmess(c)
            if d: return d.get("add"), int(d.get("port", 0))
        match = re.search(r'@([^/?#]+)', c)
        if match:
            hp = match.group(1)
            if ":" in hp:
                h, p = hp.rsplit(":", 1)
                return h, int(p)
        p = urlparse(c)
        return p.hostname, p.port
    except: return None, None

def check_l(c, t, filters, test_mode="TCP Ping"):
    try:
        name_part = unquote(c.split("#")[-1]).lower() if "#" in c else ""
        f_name = filters.get("filter_by_name", {})
        if f_name.get("enabled"):
            bl = f_name.get("blacklist", [])
            if any(word.lower() in name_part for word in bl): return None

        h, p = parse_hp(c)
        if not h or not p: return None

        ip = resolve_host(h)
        if not ip: return None

        start = time.perf_counter()

        if test_mode == "TLS Handshake":
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((ip, p), timeout=t) as sock:
                with context.wrap_socket(sock, server_hostname=h) as ssock:
                    latency = (time.perf_counter() - start) * 1000
                    return (c, latency, ip)
        else:
            with socket.create_connection((ip, p), timeout=t) as sock:
                sock.settimeout(t)
                latency = (time.perf_counter() - start) * 1000
                return (c, latency, ip)
    except:
        return None

def extract_links(text):
    found = []
    for line in text.splitlines():
        line = line.strip()
        if "://" in line:
            found.append(line)
    if len(found) < 3:
        try:
            clean_text = text.replace("\n", "").replace("\r", "").strip()
            decoded = base64.b64decode(clean_text + '=' * (-len(clean_text) % 4)).decode('utf-8', errors='ignore')
            for line in decoded.splitlines():
                line = line.strip()
                if "://" in line:
                    found.append(line)
        except:
            pass
    return found

def get_config_key(url):
    return url.split('#')[0] if '#' in url else url

def fetch_source(s):
    return s, fetch_text(s["url"])

def _term_width():
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80

def _clear_line():
    w = _term_width()
    sys.stdout.write("\r" + " " * (w - 1) + "\r")
    sys.stdout.flush()

def _progress_line(text, margin="", width=None):
    w = width or _term_width()
    avail = max(10, w - len(margin) - 1)
    s = str(text)
    if len(s) > avail:
        s = s[:avail]
    sys.stdout.write("\r" + margin + s + " " * max(0, avail - len(s)))
    sys.stdout.flush()

def animate_loading(stop_event, label, margin="", width=None):
    frames = ["  ", ". ", "..", "..."]
    i = 0
    while not stop_event.is_set():
        _progress_line(f"{label}{frames[i % 4]}", margin, width)
        i += 1
        time.sleep(0.3)

def parse_and_check(cfg, t_func, margin="", width=None):
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    try:
        clear_dns_cache()
        sources = [s for s in cfg["sources"] if s.get("enabled", True)]
        t_out = cfg.get("ping_timeout", 1.5)
        max_c = cfg.get("max_configs", 150)
        filters = cfg.get("filters", {})
        test_mode = cfg.get("test_type", "TCP Ping")
        use_smart = cfg.get("smart_filter", False)

        stop_loading = threading.Event()
        load_label = t_func('parsing', cfg)
        loading_thread = threading.Thread(target=animate_loading, args=(stop_loading, load_label, margin, width), daemon=True)
        loading_thread.start()

        reg_pool, whi_pool = [], []

        with ThreadPoolExecutor(max_workers=max(len(sources), 1)) as ex:
            futures = {ex.submit(fetch_source, s): s for s in sources}
            for future in as_completed(futures):
                try:
                    src, text = future.result()
                    if text:
                        links = extract_links(text)
                        if src["type"] == "whitelist":
                            whi_pool.extend(links)
                        else:
                            reg_pool.extend(links)
                except Exception:
                    continue

        stop_loading.set()
        loading_thread.join()

        raw_reg_count = len(reg_pool)
        raw_whi_count = len(whi_pool)

        if use_smart:
            reg_pool = list(set(reg_pool))
            whi_pool = list(set(whi_pool))
            _clear_line()
            print(f"{margin}[i] {t_func('smart_info', cfg)}{raw_reg_count - len(reg_pool)} | {raw_whi_count - len(whi_pool)}")
            sys.stdout.flush()

            unique_reg = {}
            for link in reg_pool:
                key = get_config_key(link)
                if key not in unique_reg:
                    unique_reg[key] = link
            reg_pool = list(unique_reg.values())

            unique_whi = {}
            for link in whi_pool:
                key = get_config_key(link)
                if key not in unique_whi:
                    unique_whi[key] = link
            whi_pool = list(unique_whi.values())
        else:
            reg_pool = list(set(reg_pool))
            whi_pool = list(set(whi_pool))
            _clear_line()

        def process(pool, label):
            if not pool: return []
            valid_results = []
            total = len(pool)
            done = 0

            with ThreadPoolExecutor(max_workers=60) as ex:
                futs = [ex.submit(check_l, c, t_out, filters, test_mode) for c in pool]
                for f in as_completed(futs):
                    done += 1
                    res = f.result()
                    if res:
                        valid_results.append((res[0], res[1]))
                    if done % 5 == 0 or done == total:
                        _progress_line(f"{label}: {done}/{total} | OK: {len(valid_results)}", margin, width)

            sys.stdout.write("\n")
            sys.stdout.flush()
            valid_results.sort(key=lambda x: x[1])
            return [x[0] for x in valid_results[:max_c]]

        r_res = process(reg_pool, t_func('sub_reg', cfg))
        w_res = process(whi_pool, t_func('sub_white', cfg))

        return r_res, w_res

    except Exception:
        return None, None
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def save_all(reg, whi):
    if reg is None or whi is None:
        return

    if not reg and not whi:
        return

    r_txt = "\n".join(reg)
    w_txt = "\n".join(whi)

    _write_atomic("all_configs.txt", r_txt)
    _write_atomic("white_configs.txt", w_txt)
    update_cache(r_txt, w_txt)

def _write_atomic(path, content):
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

_srv = None
_cache_lock = threading.RLock()
_cache = {"reg": "", "whi": ""}
_rate_limit = {}
_rate_limit_lock = threading.Lock()

_cfg_cache = {"mtime": None, "cfg": None}
_cfg_cache_lock = threading.Lock()

def get_server_config():
    with _cfg_cache_lock:
        try:
            mtime = os.path.getmtime(CONFIG_FILE)
        except Exception:
            mtime = None
        if _cfg_cache["cfg"] is None or _cfg_cache["mtime"] != mtime:
            _cfg_cache["cfg"] = load_config()
            _cfg_cache["mtime"] = mtime
        return _cfg_cache["cfg"]

def update_cache(r, w):
    with _cache_lock:
        _cache["reg"] = r
        _cache["whi"] = w

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

            with _rate_limit_lock:
                if len(_rate_limit) > 500:
                    for ip in list(_rate_limit.keys()):
                        _rate_limit[ip] = [x for x in _rate_limit[ip] if now - x < 60]
                        if not _rate_limit[ip]:
                            del _rate_limit[ip]
                timestamps = [x for x in _rate_limit.get(client_ip, []) if now - x < 60]
                if len(timestamps) >= 30:
                    self.send_error(429, "Too Many Requests")
                    return
                timestamps.append(now)
                _rate_limit[client_ip] = timestamps

            cfg = get_server_config()
            up = urlparse(self.path)
            qs = parse_qs(up.query)

            provided_token = qs.get("token", [None])[0]
            if provided_token != cfg.get("server_token"):
                self.send_error(403, "Forbidden: Invalid Token")
                return

            f_map = {"/sub": "reg", "/white": "whi"}
            if up.path in f_map:
                with _cache_lock:
                    content = _cache[f_map[up.path]]
                encoded = base64.b64encode(content.encode('utf-8'))
                
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("profile-update-interval", "12")
                self.send_header("profile-title", "base64:Z2l0VlBO")
                self.send_header("content-disposition", 'attachment; filename="gitVPN"')
                self.send_header("subscription-userinfo", "upload=0; download=0; total=0; expire=0")
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