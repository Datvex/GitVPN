import requests, socket, time, os, sys, base64, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

_counts = {}
_ip_cache = {}

def get_source_counts(): return _counts

def update_counts_bg(sources):
    def fetch(s):
        try:
            r = requests.get(s["url"], timeout=5).text
            _counts[s["id"]] = len([l for l in r.splitlines() if "://" in l])
        except: _counts[s["id"]] = 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        for s in sources: ex.submit(fetch, s)

def is_ip_ru(host):
    if not host or host in _ip_cache: return _ip_cache.get(host, False)
    try:
        ip = socket.gethostbyname(host)
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=2).json()
        res = r.get("countryCode") == "RU"
        _ip_cache[host] = res
        return res
    except: return False

def parse_hp(c):
    try:
        if c.startswith("vmess://"):
            d = json.loads(base64.b64decode(c[8:] + "==").decode('utf-8', errors='ignore'))
            return d.get("add"), int(d.get("port", 0))
        p = urlparse(c)
        return p.hostname, p.port
    except: return None, None

def check_l(c, t, f_ru):
    h, p = parse_hp(c)
    if not h or not p or (f_ru and is_ip_ru(h)): return None
    try:
        with socket.create_connection((h, p), timeout=t): return c
    except: return None

def parse_and_check(cfg):
    try:
        sources = [s for s in cfg["sources"] if s.get("enabled", True)]
        t_out, max_c, f_ru = cfg.get("ping_timeout", 1.5), cfg.get("max_configs", 50), cfg.get("filter_russia", True)
        reg_pool, whi_pool = set(), set()
        for s in sources:
            try:
                r = requests.get(s["url"], timeout=10).text
                for line in r.splitlines():
                    line = line.strip()
                    if "://" not in line: continue
                    if s["type"] == "whitelist": whi_pool.add(line)
                    else: reg_pool.add(line)
            except: continue
        def process(pool):
            res = []
            with ThreadPoolExecutor(max_workers=50) as ex:
                futs = [ex.submit(check_l, c, t_out, f_ru) for c in pool]
                for f in as_completed(futs):
                    r = f.result()
                    if r: res.append(r)
                    if len(res) >= max_c: break
            return res[:max_c]
        return process(reg_pool), process(whi_pool)
    except: os._exit(0)

def save_all(reg, whi):
    with open("all_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(reg))
    with open("white_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(whi))