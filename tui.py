import os
import json
import time
import base64
import socket
import shutil
import threading
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from concurrent.futures import ThreadPoolExecutor, as_completed
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, Input, Switch,
    Label, Log, TabbedContent, TabPane, ProgressBar,
    Collapsible
)
from textual.binding import Binding
from textual import work, on
from textual.screen import ModalScreen

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─────────────────────────────────────────────────────────────────────────────
# Работа с конфигурациями
# ─────────────────────────────────────────────────────────────────────────────
CONFIG_DIR = "configs"
DEFAULT_FILE = os.path.join(CONFIG_DIR, "default_config.json")
USER_FILE = os.path.join(CONFIG_DIR, "user_config.json")

BASE_DEFAULT_DATA = {
    "source": {
        "repo_api": "https://api.github.com/repos/igareck/vpn-configs-for-russia/contents/",
        "base_raw": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/",
        "file_extension": ".txt",
        "github_token": ""
    },
    "protocols": {
        "vless": True, "vmess": True, "trojan": True, 
        "ss": True, "ssr": True,
        "check_enabled": True          # ← Новая настройка
    },
    "filters": {
        "filter_by_name": {
            "enabled": True,
            "mode": "blacklist",
            "blacklist": "russia, moscow, ru, russian, россия, москва, 🇷🇺",
            "case_sensitive": False
        }
    },
    "checker": {
        "enabled": True, 
        "timeout": 1.5, 
        "max_threads": 50
    },
    "server": {
        "port": 8000, 
        "host": "0.0.0.0", 
        "path": "/sub"
    }
}

def init_system():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(DEFAULT_FILE):
        with open(DEFAULT_FILE, "w", encoding="utf-8") as f:
            json.dump(BASE_DEFAULT_DATA, f, indent=2, ensure_ascii=False)
    if not os.path.exists(USER_FILE):
        shutil.copy(DEFAULT_FILE, USER_FILE)

# ─────────────────────────────────────────────────────────────────────────────
# Парсинг и проверка
# ─────────────────────────────────────────────────────────────────────────────
def parse_host_port(config):
    try:
        if config.startswith("vmess://"):
            data = base64.b64decode(config[8:] + "==").decode()
            j = json.loads(data)
            return j.get("add"), int(j.get("port"))
        parsed = urlparse(config)
        return parsed.hostname, parsed.port
    except:
        return None, None

def check_socket(config, timeout):
    h, p = parse_host_port(config)
    if not h or not p:
        return None
    try:
        with socket.create_connection((h, p), timeout=timeout):
            return config
    except:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# Интерфейс
# ─────────────────────────────────────────────────────────────────────────────
class ConfirmModal(ModalScreen):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-box"):
            yield Label(self.message)
            with Horizontal(classes="modal-btns"):
                yield Button("Да", id="yes", variant="error")
                yield Button("Нет", id="no", variant="primary")

    def on_button_pressed(self, event):
        self.dismiss(event.button.id == "yes")


class VPNManagerApp(App):
    TITLE = "VPN Config Manager"
    CSS = """
    Screen { background: #0d1117; }
    #modal-box { align: center middle; padding: 1 2; background: #161b22; border: thick $accent; width: 50; height: auto; margin: 10 35; }
    .modal-btns { height: 3; align: center middle; margin-top: 1; }
    .modal-btns Button { margin: 0 1; }
    .setting-item { height: 3; align: left middle; padding: 0 1; }
    .label-title { width: 22; color: #8b949e; }
    .label-sub { margin-left: 4; width: 22; color: #8b949e; }
    Log { background: #000; border: solid #30363d; height: 1fr; margin: 1; }
    .stat-box { background: #161b22; border: solid #30363d; height: 5; content-align: center middle; margin: 1; width: 1fr; }
    .stat-val { color: cyan; text-style: bold; }
    Collapsible { background: #161b22; margin: 0 1; border-top: solid #30363d; }
    Input { width: 1fr; }
    .button-row { height: 3; margin: 1; }
    #srv-status { margin: 1; text-style: bold; }
    .status-off { color: red; }
    .status-on { color: green; }
    """

    BINDINGS = [
        Binding("f1", "show_tab('parser')", "Парсер"),
        Binding("f2", "show_tab('settings')", "Настройки"),
        Binding("f3", "show_tab('server')", "Сервер"),
        Binding("q", "quit", "Выход"),           # ← Новая горячая клавиша
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent(id="tabs"):
            # ПАРСЕР
            with TabPane("🚀 ПАРСЕР", id="parser"):
                with Horizontal():
                    with Vertical(classes="stat-box"):
                        yield Static("0", id="st-found", classes="stat-val")
                        yield Label("Найдено")
                    with Vertical(classes="stat-box"):
                        yield Static("0", id="st-alive", classes="stat-val")
                        yield Label("Рабочих")
                yield ProgressBar(total=100, id="progress", show_eta=False)

                with Horizontal(classes="button-row"):
                    yield Button("▶ ЗАПУСК", id="btn-run", variant="success")
                    yield Button("⏹ СТОП", id="btn-stop", variant="error", disabled=True)
                    yield Button("🚪 ВЫХОД", id="btn-exit", variant="default")  # ← Новая кнопка

                yield Log(id="log-parser")

            # НАСТРОЙКИ
            with TabPane("⚙ НАСТРОЙКИ", id="settings"):
                with ScrollableContainer():
                    with Collapsible(title="🌐 GitHub Источники", collapsed=False):
                        yield from self.ui_field("API URL", "cfg-repo-api")
                        yield from self.ui_field("Raw URL", "cfg-base-raw")
                        yield from self.ui_field("Token", "cfg-token")

                    with Collapsible(title="🛡 Протоколы", collapsed=False):
                        with Horizontal(classes="setting-item"):
                            yield Label("Проверять протоколы", classes="label-title")
                            yield Switch(id="cfg-check-protocols", value=True)  # ← Новая настройка

                        with Horizontal(classes="setting-item"):
                            yield Label("VLESS", classes="label-title")
                            yield Switch(id="cfg-vless")
                        with Horizontal(classes="setting-item"):
                            yield Label("VMESS", classes="label-sub")
                            yield Switch(id="cfg-vmess")
                        with Horizontal(classes="setting-item"):
                            yield Label("Trojan", classes="label-title")
                            yield Switch(id="cfg-trojan")
                        with Horizontal(classes="setting-item"):
                            yield Label("Shadowsocks", classes="label-sub")
                            yield Switch(id="cfg-ss")

                    with Collapsible(title="🔍 Фильтрация"):
                        yield from self.ui_field("Черный список", "cfg-blacklist")
                        with Horizontal(classes="setting-item"):
                            yield Label("Регистр букв", classes="label-title")
                            yield Switch(id="cfg-case")

                    with Collapsible(title="⚡ Чекер"):
                        yield from self.ui_field("Таймаут (сек)", "cfg-timeout")
                        yield from self.ui_field("Потоки", "cfg-threads")

                    with Collapsible(title="🖥 Локальный Сервер"):
                        yield from self.ui_field("Порт", "cfg-port")
                        yield from self.ui_field("Хост", "cfg-host")

                    with Horizontal(classes="button-row"):
                        yield Button("💾 СОХРАНИТЬ", id="btn-save", variant="success")
                        yield Button("🔄 СБРОС", id="btn-reset", variant="primary")

            # СЕРВЕР
            with TabPane("🌐 СЕРВЕР", id="server"):
                yield Static("СТАТУС: ВЫКЛЮЧЕН", id="srv-status", classes="status-off")
                with Horizontal(classes="button-row"):
                    yield Button("▶ ВКЛЮЧИТЬ", id="btn-srv-start", variant="success")
                    yield Button("⏹ ВЫКЛЮЧИТЬ", id="btn-srv-stop", variant="error", disabled=True)
                yield Log(id="log-server")

        yield Footer()

    def ui_field(self, label, id):
        with Horizontal(classes="setting-item"):
            yield Label(label, classes="label-title")
            yield Input(id=id)

    # ─────────────────────────────────────────────────────────────────────────────
    # Загрузка / Сохранение настроек
    # ─────────────────────────────────────────────────────────────────────────────
    def on_mount(self):
        init_system()
        self.load_settings_to_ui()

    def load_settings_to_ui(self):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            c = json.load(f)

        self.query_one("#cfg-repo-api").value = str(c["source"]["repo_api"])
        self.query_one("#cfg-base-raw").value = str(c["source"]["base_raw"])
        self.query_one("#cfg-token").value = str(c["source"]["github_token"])

        # Протоколы
        self.query_one("#cfg-check-protocols").value = c["protocols"].get("check_enabled", True)
        self.query_one("#cfg-vless").value = c["protocols"].get("vless", True)
        self.query_one("#cfg-vmess").value = c["protocols"].get("vmess", True)
        self.query_one("#cfg-trojan").value = c["protocols"].get("trojan", True)
        self.query_one("#cfg-ss").value = c["protocols"].get("ss", True)

        # Фильтры
        f_data = c["filters"]["filter_by_name"]
        bl = f_data.get("blacklist", "")
        self.query_one("#cfg-blacklist").value = ", ".join(bl) if isinstance(bl, list) else str(bl)
        self.query_one("#cfg-case").value = f_data.get("case_sensitive", False)

        self.query_one("#cfg-timeout").value = str(c["checker"]["timeout"])
        self.query_one("#cfg-threads").value = str(c["checker"]["max_threads"])
        self.query_one("#cfg-port").value = str(c["server"]["port"])
        self.query_one("#cfg-host").value = str(c["server"]["host"])

    @on(Button.Pressed, "#btn-save")
    def save_settings(self):
        try:
            c = {
                "source": {
                    "repo_api": self.query_one("#cfg-repo-api").value,
                    "base_raw": self.query_one("#cfg-base-raw").value,
                    "file_extension": ".txt",
                    "github_token": self.query_one("#cfg-token").value
                },
                "protocols": {
                    "vless": self.query_one("#cfg-vless").value,
                    "vmess": self.query_one("#cfg-vmess").value,
                    "trojan": self.query_one("#cfg-trojan").value,
                    "ss": self.query_one("#cfg-ss").value,
                    "ssr": True,
                    "check_enabled": self.query_one("#cfg-check-protocols").value   # ← сохраняем
                },
                "filters": {
                    "filter_by_name": {
                        "enabled": True,
                        "mode": "blacklist",
                        "blacklist": self.query_one("#cfg-blacklist").value,
                        "case_sensitive": self.query_one("#cfg-case").value
                    }
                },
                "checker": {
                    "enabled": True,
                    "timeout": float(self.query_one("#cfg-timeout").value or 1.5),
                    "max_threads": int(self.query_one("#cfg-threads").value or 50)
                },
                "server": {
                    "port": int(self.query_one("#cfg-port").value or 8000),
                    "host": self.query_one("#cfg-host").value,
                    "path": "/sub"
                }
            }

            with open(USER_FILE, "w", encoding="utf-8") as f:
                json.dump(c, f, indent=2, ensure_ascii=False)

            self.notify("Настройки успешно сохранены ✅")
        except Exception as e:
            self.notify(f"Ошибка сохранения: {e}", severity="error")

    @on(Button.Pressed, "#btn-reset")
    def reset_settings(self):
        def do_reset(confirmed):
            if confirmed:
                shutil.copy(DEFAULT_FILE, USER_FILE)
                self.load_settings_to_ui()
                self.notify("Настройки сброшены к дефолту")
        self.push_screen(ConfirmModal("Сбросить настройки к значениям по умолчанию?"), do_reset)

    # ─────────────────────────────────────────────────────────────────────────────
    # Парсер
    # ─────────────────────────────────────────────────────────────────────────────
    def _log(self, msg, tab="parser"):
        self.query_one(f"#log-{tab}", Log).write_line(f"[{time.strftime('%H:%M:%S')}] {msg}")

    @on(Button.Pressed, "#btn-run")
    def start_parsing(self):
        self.query_one("#btn-run").disabled = True
        self.query_one("#btn-stop").disabled = False
        with open(USER_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        self.worker = self.parser_task(cfg)

    @on(Button.Pressed, "#btn-stop")
    def stop_parsing(self):
        if hasattr(self, "worker"):
            self.worker.cancel()

    @on(Button.Pressed, "#btn-exit")   # ← Обработка кнопки выхода
    def action_quit(self):
        self.exit()

    @work(exclusive=True, thread=True)
    def parser_task(self, cfg):
        try:
            if not HAS_REQUESTS:
                raise Exception("Библиотека requests не установлена")

            headers = {"Authorization": f"token {cfg['source']['github_token']}"} if cfg['source']['github_token'] else {}

            self.call_from_thread(self._log, "Загрузка списка файлов из GitHub...")

            r = requests.get(cfg["source"]["repo_api"], headers=headers, timeout=10)
            r.raise_for_status()
            files = [f["name"] for f in r.json() if f["name"].endswith(".txt")]

            all_configs = []
            check_protocols = cfg["protocols"].get("check_enabled", True)

            for f_name in files:
                self.call_from_thread(self._log, f"Чтение {f_name}...")
                raw_text = requests.get(cfg["source"]["base_raw"] + f_name, headers=headers, timeout=10).text

                for line in raw_text.splitlines():
                    line = line.strip()
                    if self.is_valid_config(line, cfg, check_protocols):
                        all_configs.append(line)

            all_configs = list(set(all_configs))
            self.call_from_thread(self.query_one("#st-found").update, str(len(all_configs)))

            # Проверка живых конфигов
            alive = []
            if cfg["checker"]["enabled"] and all_configs:
                timeout = cfg["checker"]["timeout"]
                threads = cfg["checker"]["max_threads"]
                self.call_from_thread(self._log, f"Проверка {len(all_configs)} конфигов...")

                with ThreadPoolExecutor(max_workers=threads) as pool:
                    futures = [pool.submit(check_socket, c, timeout) for c in all_configs]
                    for i, f in enumerate(as_completed(futures)):
                        res = f.result()
                        if res:
                            alive.append(res)
                        if i % 10 == 0:
                            progress = int((i + 1) / len(all_configs) * 100)
                            self.call_from_thread(self.query_one("#progress").update, progress=progress)
                        self.call_from_thread(self.query_one("#st-alive").update, str(len(alive)))

            configs_to_save = alive if cfg["checker"]["enabled"] else all_configs
            with open("all_configs.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(configs_to_save))

            self.call_from_thread(self._log, f"Готово! Сохранено живых: {len(alive)}")

        except Exception as e:
            self.call_from_thread(self._log, f"Ошибка: {e}")
        finally:
            self.call_from_thread(self.parsing_done)

    def parsing_done(self):
        self.query_one("#btn-run").disabled = False
        self.query_one("#btn-stop").disabled = True
        self.query_one("#progress").progress = 100

    def is_valid_config(self, line, cfg, check_protocols=True):
        if not line or line.startswith("#"):
            return False

        # Проверка протоколов
        if check_protocols:
            protos = cfg.get("protocols", {})
            if not any(line.startswith(f"{p}://") for p, e in protos.items() if e and p != "check_enabled"):
                return False

        # Фильтрация по имени
        f_name = cfg.get("filters", {}).get("filter_by_name", {})
        if f_name.get("enabled"):
            text = line if f_name.get("case_sensitive") else line.lower()
            raw_bl = f_name.get("blacklist", "")
            bl_words = raw_bl if isinstance(raw_bl, list) else [w.strip() for w in str(raw_bl).split(",") if w.strip()]

            for word in bl_words:
                match_word = word if f_name.get("case_sensitive") else word.lower()
                if match_word in text:
                    return False

        return True

    # ─────────────────────────────────────────────────────────────────────────────
    # Локальный сервер
    # ─────────────────────────────────────────────────────────────────────────────
    @on(Button.Pressed, "#btn-srv-start")
    def server_start(self):
        global _server_instance
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                s_cfg = json.load(f)["server"]

            class SubHandler(BaseHTTPRequestHandler):
                def log_message(self, *args): pass

                def do_GET(self):
                    try:
                        with open("all_configs.txt", "r", encoding="utf-8") as f:
                            data = f.read()
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(base64.b64encode(data.encode()))
                    except:
                        self.send_error(404)

            _server_instance = HTTPServer((s_cfg["host"], s_cfg["port"]), SubHandler)
            threading.Thread(target=_server_instance.serve_forever, daemon=True).start()

            st = self.query_one("#srv-status")
            st.update(f"СТАТУС: ЗАПУЩЕН[](http://{s_cfg['host']}:{s_cfg['port']}/sub)")
            st.remove_class("status-off").add_class("status-on")
            self.query_one("#btn-srv-start").disabled = True
            self.query_one("#btn-srv-stop").disabled = False
            self._log("Сервер успешно запущен", "server")

        except Exception as e:
            self._log(f"Ошибка запуска сервера: {e}", "server")

    @on(Button.Pressed, "#btn-srv-stop")
    def server_stop(self):
        global _server_instance
        if _server_instance:
            _server_instance.shutdown()
            _server_instance = None

        st = self.query_one("#srv-status")
        st.update("СТАТУС: ВЫКЛЮЧЕН")
        st.remove_class("status-on").add_class("status-off")
        self.query_one("#btn-srv-start").disabled = False
        self.query_one("#btn-srv-stop").disabled = True
        self._log("Сервер остановлен", "server")


if __name__ == "__main__":
    VPNManagerApp().run()