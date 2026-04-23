import os
import requests
import subprocess
import sys

# 🔧 НАСТРОЙКА
REPO_RAW = "https://raw.githubusercontent.com/Squnplee/FreeVPN/main/"
PROJECT_DIR = "VPN"

FILES = {
    "parser.py": True,
    "server.py": True,
    "requirements.txt": True,
}


def download_file(filename):
    url = REPO_RAW + filename
    try:
        print(f"[+] Скачиваю {filename}")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[!] Ошибка загрузки {filename}: {e}")
        return None


def setup_project():
    os.makedirs(PROJECT_DIR, exist_ok=True)
    print(f"[+] Папка {PROJECT_DIR} готова")


def update_files():
    for filename, enabled in FILES.items():
        if not enabled:
            continue

        content = download_file(filename)
        if content is None:
            continue

        path = os.path.join(PROJECT_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[✔] Обновлён {filename}")


def install_requirements():
    path = os.path.join(PROJECT_DIR, "requirements.txt")

    if not os.path.exists(path):
        print("[!] requirements.txt не найден")
        return

    print("[+] Устанавливаю зависимости...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", path],
        check=False
    )


def ask_run(script_name):
    answer = input(f"Запустить {script_name}? (y/n): ").lower()
    if answer == "y":
        subprocess.run([sys.executable, script_name], cwd=PROJECT_DIR)


def main():
    print("=== VPN Installer / Updater ===")

    setup_project()
    update_files()
    install_requirements()

    print("\n[+] Установка / обновление завершено")

    ask_run("parser.py")
    ask_run("server.py")


if __name__ == "__main__":
    main()