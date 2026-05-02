import requests, socket, time, os, sys, base64, json, re, threading, ssl, random
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, unquote

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0 Safari/537.36"
]

GITHUB_PROXIES = [
    "https://ghproxy.net/",
    "https://ghproxy.com/",
    "https://mirror.ghproxy.com/"
]

_counts = {}
_counts_lock = threading.Lock()  # fix #4


def get_source_counts():
    with _counts_lock:
        return dict(_counts)  # возвращаем копию

def get_proxied_url(url):
    if "raw.githubusercontent.com" in url or "raw.github.com" in url:
        return f"{random.choice(GITHUB_PROXIES)}{url}"
    return url

def update_counts_bg(sources):
    def fetch(s):
        try:
            target_url = get_proxied_url(s["url"])
            r = requests.get(target_url, timeout=7,
                             headers={"User-Agent": random.choice(USER_AGENTS)})
            count = len(re.findall(r"://", r.text)) if r.status_code == 200 else 0
        except Exception:
            count = 0
        with _counts_lock:
            _counts[s["id"]] = count

    with ThreadPoolExecutor(max_workers=10) as ex:
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

def check_l(c, t, filters, test_mode="TCP Ping"):
    try:
        name_part = unquote(c.split("#")[-1]).lower() if "#" in c else ""
        f_name = filters.get("filter_by_name", {})
        if f_name.get("enabled"):
            bl = f_name.get("blacklist", [])
            if any(word.lower() in name_part for word in bl): return None

        h, p = parse_hp(c)
        if not h or not p: return None

        try:
            ip = socket.gethostbyname(h)
        except: return None

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
    """Загрузка одного источника с быстрым fallback"""
    urls_to_try = []
    
    if "raw.githubusercontent.com" in s["url"]:
        urls_to_try.append(f"https://ghproxy.net/{s['url']}")
        urls_to_try.append(s["url"])
    else:
        urls_to_try.append(s["url"])

    for url in urls_to_try:
        try:
            r = requests.get(
                url,
                timeout=5,
                headers={"User-Agent": random.choice(USER_AGENTS)},
                stream=False
            )
            if r.status_code == 200 and r.text:
                return s, r.text
        except Exception:
            continue
    return s, None

def animate_loading(stop_event, label):
    from utils import print_progress
    frames = ["  ", ". ", "..", "..."]
    i = 0
    while not stop_event.is_set():
        print_progress(f"{label}{frames[i % 4]}")
        i += 1
        time.sleep(0.3)

def parse_and_check(cfg, t_func):
    from utils import print_progress
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    try:
        sources = [s for s in cfg["sources"] if s.get("enabled", True)]
        t_out = cfg.get("ping_timeout", 1.5)
        max_c = cfg.get("max_configs", 150)
        filters = cfg.get("filters", {})
        test_mode = cfg.get("test_type", "TCP Ping")
        use_smart = cfg.get("smart_filter", False)

        stop_loading = threading.Event()
        load_label = t_func('parsing', cfg)
        loading_thread = threading.Thread(target=animate_loading, args=(stop_loading, load_label), daemon=True)
        loading_thread.start()

        reg_pool, whi_pool = [], []

        # Параллельная загрузка всех источников (без глобального timeout)
        with ThreadPoolExecutor(max_workers=max(len(sources), 1)) as ex:
            futures = {ex.submit(fetch_source, s): s for s in sources}
            for future in as_completed(futures):  # fix #8 — убрали timeout=30
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
        # ───────────────────────────────────────────────────────────────────

        stop_loading.set()
        loading_thread.join()

        raw_reg_count = len(reg_pool)
        raw_whi_count = len(whi_pool)

        if use_smart:
            reg_pool = list(set(reg_pool))
            whi_pool = list(set(whi_pool))
            sys.stdout.write("\r" + " " * 80 + "\r")
            print(f" [i] {t_func('smart_info', cfg)}{raw_reg_count - len(reg_pool)} (Обычные) | {raw_whi_count - len(whi_pool)} (Белые)")
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
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()

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
                        print_progress(f"{label}: {done}/{total} | OK: {len(valid_results)}")

            sys.stdout.write("\n")
            sys.stdout.flush()
            valid_results.sort(key=lambda x: x[1])
            return [x[0] for x in valid_results[:max_c]]

        r_res = process(reg_pool, t_func('sub_reg', cfg))
        w_res = process(whi_pool, t_func('sub_white', cfg))

        return r_res, w_res

    except Exception:
        return None, None  # fix #1 — None сигнализирует об ошибке, не []
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def save_all(reg, whi):
    """fix #1 — не сохраняем если парсинг упал (None) или оба пустые"""
    if reg is None or whi is None:
        return  # ошибка парсинга — не трогаем файлы

    if not reg and not whi:
        return  # оба пустых — не затираем старые данные

    r_txt = "\n".join(reg)
    w_txt = "\n".join(whi)

    from server_core import update_cache

    # fix #22 — сначала диск, потом кэш
    _write_atomic("all_configs.txt", r_txt)
    _write_atomic("white_configs.txt", w_txt)
    update_cache(r_txt, w_txt)


def _write_atomic(path, content):
    """fix #21 — атомарная запись через temp файл"""
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)  # атомарно на POSIX и Windows
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass