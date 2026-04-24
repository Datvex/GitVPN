import requests
import socket
import base64
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

REPO_API = "https://api.github.com/repos/igareck/vpn-configs-for-russia/contents/"
BASE_RAW = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/"

OUTPUT_FILE = "all_configs.txt"

VALID_PREFIXES = (
    "vless://",
    "vmess://",
    "trojan://",
    "ss://",
    "ssr://"
)

TIMEOUT = 1.5
MAX_THREADS = 50

FILTER_RUSSIA_BY_NAME=True


# ---------- получаем ВСЕ txt файлы ----------
def get_txt_files():
    try:
        r = requests.get(REPO_API, timeout=10)
        r.raise_for_status()
        data = r.json()

        files = [
            item["name"]
            for item in data
            if item["name"].endswith(".txt")
        ]

        print(f"[+] Найдено txt файлов: {len(files)}")
        return files

    except Exception as e:
        print("[!] Ошибка получения списка файлов:", e)
        return []


# ---------- скачивание ----------
def download_file(filename):
    url = BASE_RAW + filename
    try:
        print(f"[+] Качаю {filename}")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except:
        return ""

# ---------- Проверка на русский сервер ----------
def is_not_russia_by_name(config):
    text = config.lower()

    bad_keywords = [
        "russia",
        "moscow",
        "ru",
        "russian",
        "россия",
        "москва",
        "🇷🇺"
    ]

    return not any(word in text for word in bad_keywords)

# ---------- извлечение ----------
def extract_configs(text):
    configs = []

    for line in text.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue
        
        if FILTER_RUSSIA_BY_NAME:
            if not is_not_russia_by_name(line):
                continue

        if line.startswith(VALID_PREFIXES):
            configs.append(line)

    return configs


# ---------- парсинг host/port ----------
def parse_host_port(config):
    try:
        if config.startswith("vmess://"):
            data = base64.b64decode(config[8:] + "==").decode()
            j = json.loads(data)
            return j.get("add"), int(j.get("port"))
        else:
            parsed = urlparse(config)
            return parsed.hostname, parsed.port
    except:
        return None, None


# ---------- проверка ----------
def check_config(config):
    host, port = parse_host_port(config)

    if not host or not port:
        return None

    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return config
    except:
        return None


# ---------- main ----------
def main():
    files = get_txt_files()

    all_configs = []

    for filename in files:
        text = download_file(filename)
        configs = extract_configs(text)

        print(f"{filename}: {len(configs)}")
        all_configs.extend(configs)

    # убираем дубликаты
    all_configs = list(dict.fromkeys(all_configs))

    print(f"\nВсего до проверки: {len(all_configs)}")

    alive = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(check_config, c) for c in all_configs]

        for f in as_completed(futures):
            result = f.result()
            if result:
                alive.append(result)

    print(f"Живых: {len(alive)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(alive))

    print("Готово 🚀")


if __name__ == "__main__":
    main()
