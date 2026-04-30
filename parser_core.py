import requests, socket, time, os, sys, base64, json, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, unquote

_counts = {}

def get_source_counts():
    return _counts

def update_counts_bg(sources):
    headers = {"User-Agent": "Mozilla/5.0 VPN-Manager"}
    def fetch(s):
        try:
            r = requests.get(s["url"], timeout=7, headers=headers)
            if r.status_code == 200:
                _counts[s["id"]] = len(re.findall(r"://", r.text))
            else:
                _counts[s["id"]] = 0
        except:
            _counts[s["id"]] = 0

    with ThreadPoolExecutor(max_workers=25) as ex:
        for s in sources:
            ex.submit(fetch, s)

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

def check_l(c, t, filters):
    try:
        name_part = unquote(c.split("#")[-1]).lower() if "#" in c else ""
        f_name = filters.get("filter_by_name", {})
        if f_name.get("enabled"):
            bl = f_name.get("blacklist", [])
            if any(word.lower() in name_part for word in bl): return None
        
        h, p = parse_hp(c)
        if not h or not p: return None
        
        start = time.perf_counter()
        with socket.create_connection((h, p), timeout=t):
            latency = (time.perf_counter() - start) * 1000
            return (c, latency)
    except:
        return None

def parse_and_check(cfg):
    try:
        sources = [s for s in cfg["sources"] if s.get("enabled", True)]
        t_out = cfg.get("ping_timeout", 1.5)
        max_c = cfg.get("max_configs", 50)
        filters = cfg.get("filters", {})
        
        reg_pool, whi_pool = set(), set()
        headers = {"User-Agent": "Mozilla/5.0 VPN-Manager"}
        for s in sources:
            try:
                r = requests.get(s["url"], timeout=10, headers=headers).text
                for line in r.splitlines():
                    line = line.strip()
                    if "://" in line:
                        if s["type"] == "whitelist": whi_pool.add(line)
                        else: reg_pool.add(line)
            except: continue

        def process(pool):
            valid_results = []
            if not pool: return []
            with ThreadPoolExecutor(max_workers=50) as ex:
                futs = [ex.submit(check_l, c, t_out, filters) for c in pool]
                for f in as_completed(futs):
                    res = f.result()
                    if res:
                        valid_results.append(res)
                        if len(valid_results) >= max_c * 2:
                            for fut in futs: fut.cancel()
                            break
            valid_results.sort(key=lambda x: x[1])
            return [x[0] for x in valid_results[:max_c]]

        return process(reg_pool), process(whi_pool)
    except:
        return [], []

def save_all(reg, whi):
    with open("all_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(reg))
    with open("white_configs.txt", "w", encoding="utf-8") as f: f.write("\n".join(whi))