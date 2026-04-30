import sys, os, threading, socket, time
sys.dont_write_bytecode = True

from datetime import datetime
from config import load_config, save_config
from utils import clear, print_banner, print_box, print_btn, input_c, set_active_theme
from parser_core import parse_and_check, save_all, update_counts_bg, get_source_counts
from server_core import start_server
from themes import get_theme_list
from lang import STRINGS

last_run_time = None
REPO_ORDER = ["igareck", "AvenCores", "Barry", "Ebrasha"]

def t(key, cfg): 
    lang = cfg.get("lang", "English")
    return str(STRINGS.get(lang, STRINGS["English"]).get(key, key))

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        res = s.getsockname()[0]
        s.close()
        return res
    except: return "127.0.0.1"

def manage_src(cfg):
    while True:
        clear(); print_banner()
        sources = cfg["sources"]
        repos = {n: [] for n in REPO_ORDER}
        others = []
        for s in sources:
            parts = s["name"].split('/')
            r_name = parts[0] if parts else "Unknown"
            if r_name in repos: repos[r_name].append(s)
            else: others.append(s)
        repo_data = [(n, repos[n]) for n in REPO_ORDER if repos.get(n)]
        if others: repo_data.append(("Others", others))
        
        counts = get_source_counts()
        txt = ""
        for i, (name, links) in enumerate(repo_data, 1):
            total = sum(counts.get(s["id"], 0) for s in links)
            active = any(s.get("enabled", True) for s in links)
            stat = "[+]" if active else "[-]"
            txt += f"{i}. {stat} {name} ({t('src_all', cfg)}{total})\n"
        
        print_box(txt + f"\n{t('src_1', cfg)}\n{t('src_2', cfg)}\n{t('s_0', cfg)}")
        ch = input_c(">")
        if ch == "0": break
        elif ch == "1":
            try:
                res = input_c("ID:")
                idx = int(res) - 1
                if 0 <= idx < len(repo_data): manage_repo_links(cfg, repo_data[idx][1], repo_data[idx][0])
            except: pass
        elif ch == "2":
            try:
                res = input_c("ID:")
                idx = int(res) - 1
                if 0 <= idx < len(repo_data):
                    target = not any(s.get("enabled", True) for s in repo_data[idx][1])
                    for s in repo_data[idx][1]: s["enabled"] = target
                    save_config(cfg)
            except: pass

def manage_repo_links(cfg, links, repo_name):
    while True:
        clear(); print_banner()
        counts = get_source_counts()
        txt = f"{t('repo', cfg)}{repo_name}\n\n"
        for i, s in enumerate(links, 1):
            stat = "[+]" if s.get("enabled", True) else "[-]"
            txt += f"{i}. {stat} {s['name']} ({counts.get(s['id'], 0)})\n"
        print_box(txt + f"\n{t('s_0', cfg)}")
        ch = input_c(">")
        if ch == "0": break
        try:
            idx = int(ch) - 1
            if 0 <= idx < len(links):
                links[idx]["enabled"] = not links[idx].get("enabled", True)
                save_config(cfg)
        except: pass

def select_lang(cfg):
    while True:
        clear(); print_banner()
        txt = "1. English\n2. Русский\n3. Chinese\n\n" + str(t('s_0', cfg))
        print_box(txt)
        ch = input_c(">")
        if ch == "0": return
        elif ch == "1": cfg["lang"] = "English"
        elif ch == "2": cfg["lang"] = "Russian"
        elif ch == "3": cfg["lang"] = "Chinese"
        save_config(cfg)
        return

def settings(cfg):
    while True:
        clear(); print_banner()
        f_ru = t('on', cfg) if cfg["filter_russia"] else t('off', cfg)
        box = (f"{t('s_1', cfg)}{f_ru}\n"
               f"{t('s_2', cfg)}{cfg['max_configs']}\n"
               f"{t('s_3', cfg)}{cfg.get('theme')}\n"
               f"{t('s_4', cfg)}\n{t('s_0', cfg)}")
        print_box(box)
        ch = input_c(">")
        if ch == "0": break
        elif ch == "1": 
            cfg["filter_russia"] = not cfg["filter_russia"]
        elif ch == "2":
            try: cfg["max_configs"] = int(input_c(":"))
            except: pass
        elif ch == "3":
            while True:
                clear(); print_banner()
                themes = get_theme_list()
                txt = "\n".join([f"{i+1}. {x}" for i,x in enumerate(themes)])
                print_box(txt + f"\n\n{t('s_0', cfg)}")
                tch = input_c(">")
                if tch == "0": break
                try:
                    idx = int(tch)-1
                    if 0 <= idx < len(themes):
                        cfg["theme"] = themes[idx]
                        set_active_theme(themes[idx])
                        save_config(cfg)
                except: pass
        elif ch == "4": manage_src(cfg)
        save_config(cfg)

def main():
    global last_run_time
    cfg = load_config()
    set_active_theme(cfg.get("theme", "Cyberpunk"))
    start_server(cfg["server_host"], cfg["server_port"])
    
    threading.Thread(target=update_counts_bg, args=(cfg["sources"],), daemon=True).start()
    
    while True:
        clear(); print_banner()
        last_p_str = last_run_time if last_run_time else t('never', cfg)
        menu = (f"{t('m_1', cfg)}\n{t('m_2', cfg)}\n{t('m_3', cfg)}\n"
                f"{t('m_4', cfg)}\n{t('m_0', cfg)}\n\n"
                f"{t('m_last', cfg)}{last_p_str}")
        print_box(menu)
        ch = input_c(">")
        if ch == "1":
            clear(); print_banner(); ip = get_ip()
            print_box(f"{t('sub_reg', cfg)}\nhttp://{ip}:{cfg['server_port']}/sub\n\n{t('sub_white', cfg)}\nhttp://{ip}:{cfg['server_port']}/white")
            print_btn(t('enter', cfg)); input()
        elif ch == "2": settings(cfg)
        elif ch == "3":
            reg, whi = parse_and_check(cfg)
            save_all(reg, whi)
            last_run_time = datetime.now().strftime("%H:%M:%S")
            print_btn(t('enter', cfg)); input()
        elif ch == "4": select_lang(cfg)
        elif ch == "0": os._exit(0)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: os._exit(0)
    except Exception: os._exit(1)