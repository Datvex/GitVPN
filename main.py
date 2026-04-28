import sys, time, threading, socket
from datetime import datetime
from config import load_config, save_config
from utils import clear, print_banner, print_box, print_btn, input_c, pause
from parser_core import parse_and_check, save_all
from server_core import start_server, stop_server, _srv

last_p = "Никогда"
stop_ev = threading.Event()

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except: return "127.0.0.1"

def settings(cfg):
    while True:
        clear()
        print_banner()
        f_ru = "ВКЛ" if cfg["filter_russia"] else "ВЫКЛ"
        box = (f"[1] Фильтр Россия: {f_ru}\n"
               f"[2] Лимит конфигов: {cfg['max_configs']}\n"
               f"[3] Интервал парсинга: {cfg['parse_interval']} мин\n"
               f"[4] Управление источниками\n"
               f"[5] Назад")
        print_box(box)
        ch = input_c("> ")
        if ch == "1": cfg["filter_russia"] = not cfg["filter_russia"]
        elif ch == "2":
            try: cfg["max_configs"] = int(input_c("Кол-во (1-1000): "))
            except: pass
        elif ch == "3":
            try: cfg["parse_interval"] = int(input_c("Минуты: "))
            except: pass
        elif ch == "4": manage_src(cfg)
        elif ch == "5": break
        save_config(cfg)

def manage_src(cfg):
    while True:
        clear()
        print_banner()
        txt = ""
        for i, s in enumerate(cfg["sources"], 1):
            stat = "[+]" if s.get("enabled", True) else "[-]"
            txt += f"{i}. {stat} {s['name']}\n"
        print_box(txt + "\n[0] Назад")
        ch = input_c("ID > ")
        if ch == "0": break
        try:
            idx = int(ch) - 1
            cfg["sources"][idx]["enabled"] = not cfg["sources"][idx].get("enabled", True)
            save_config(cfg)
        except: pass

def main():
    global last_p
    cfg = load_config()
    while True:
        clear()
        print_banner()
        srv_s = "ВКЛ" if _srv else "ВЫКЛ"
        print_box(f"[1] Ссылки на подписку\n[2] Настройки\n[3] Парсить сейчас\n[4] Сервер: {srv_s}\n[5] Выход\n\nПоследний запуск: {last_p}")
        ch = input_c("> ")
        if ch == "1":
            clear()
            print_banner()
            ip = get_ip()
            print_box(f"ОБЫЧНЫЙ VPN:\nhttp://{ip}:{cfg['server_port']}/sub\n\nБЕЛЫЕ СПИСКИ:\nhttp://{ip}:{cfg['server_port']}/white")
            pause()
        elif ch == "2": settings(cfg)
        elif ch == "3":
            def pb(d, t, s): 
                sys.stdout.write(f"\r  {s}...")
                sys.stdout.flush()
            reg, whi = parse_and_check(cfg, pb)
            save_all(reg, whi)
            last_p = datetime.now().strftime("%H:%M:%S")
            print("\n")
            pause()
        elif ch == "4":
            if _srv: stop_server()
            else: start_server(cfg["server_host"], cfg["server_port"])
        elif ch == "5": sys.exit(0)

if __name__ == "__main__": main()