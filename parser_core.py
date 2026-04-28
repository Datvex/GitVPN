import requests
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import json
import base64

def parse_hp(c):
    try:
        if c.startswith("vmess://"):
            d = json.loads(base64.b64decode(c[8:] + "==").decode('utf-8', errors='ignore'))
            return d.get("add"), int(d.get("port", 0))
        p = urlparse(c)
        return p.hostname, p.port
    except: return None, None

def check_l(c, t):
    h, p = parse_hp(c)
    if not h or not p: return None
    try:
        start = time.time()
        with socket.create_connection((h, p), timeout=t):
            return c, (time.time() - start) * 1000
    except: return None

def is_ru(c):
    return any(k in c.lower() for k in ["russia", "moscow", "ru", "россия", "москва", "🇷🇺"])

def parse_and_check(cfg, progress_cb=None):
    sources = [s for s in cfg["sources"] if s.get("enabled", True)]
    t_out = cfg.get("ping_timeout", 1.5)
    max_c = cfg.get("max_configs", 50)
    
    reg_pool, whi_pool = set(), set()
    
    for s in sources:
        try:
            if progress_cb: progress_cb(0, 0, f"Парсинг: {s['name']}")
            r = requests.get(s["url"], timeout=10).text
            for line in r.splitlines():
                line = line.strip()
                if not line or "://" not in line: continue
                if cfg.get("filter_russia") and is_ru(line): continue
                if s["type"] == "whitelist": whi_pool.add(line)
                else: reg_pool.add(line)
        except: continue

    def process_pool(pool):
        results = []
        with ThreadPoolExecutor(max_workers=50) as ex:
            futs = {ex.submit(check_l, c, t_out): c for c in pool}
            for f in as_completed(futs):
                res = f.result()
                if res: results.append(res)
        results.sort(key=lambda x: x[1])
        return [r[0] for r in results][:max_c]

    return process_pool(reg_pool), process_pool(whi_pool)

def save_all(reg, whi):
    with open("all_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(reg))
    with open("white_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(whi))