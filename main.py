import sys, os, threading, socket, time
sys.dont_write_bytecode = True

from datetime import datetime
from config import load_config, save_config, RAW_SOURCES, RAW_SOURCES
from utils import clear, print_banner, print_box, print_btn, input_c, set_active_theme, copy_to_clipboard
from parser_core import parse_and_check, save_all, update_counts_bg, get_source_counts
from server_core import start_server
from themes import get_theme_list
from lang import STRINGS

last_run_time = None

# ID системных источников (нельзя удалять и добавлять в них)
SYSTEM_IDS = {s["id"] for s in RAW_SOURCES}
SYSTEM_REPOS = {s["name"].split("/")[0].lower() for s in RAW_SOURCES}

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
    except:
        return "127.0.0.1"

def is_github_raw_url(url):
    """Проверяет что URL является github raw ссылкой"""
    return "raw.githubusercontent.com" in url or "raw.github.com" in url

def is_system_repo(repo_name):
    """Проверяет является ли репозиторий системным"""
    return repo_name.lower() in SYSTEM_REPOS

# ──────────────────────────────────────────────────────────────────────────────
# Меню внутри репозитория (список ссылок с пагинацией)
# ──────────────────────────────────────────────────────────────────────────────
def manage_repo_links(cfg, repos_map, repo_name):
    PAGE_SIZE = 5
    page = 0
    links = repos_map[repo_name]

    while True:
        clear()
        print_banner()
        counts = get_source_counts()

        total_pages = max(1, (len(links) + PAGE_SIZE - 1) // PAGE_SIZE)
        start = page * PAGE_SIZE
        end = min(start + PAGE_SIZE, len(links))
        page_links = links[start:end]

        txt = f"{t('repo', cfg)}{repo_name}  [{page+1}/{total_pages}]\n\n"
        for i, s in enumerate(page_links, start + 1):
            stat = "[+]" if s.get("enabled", True) else "[-]"
            txt += f"{i}. {stat} {s['name']}  ({counts.get(s['id'], 0)})\n"

        nav = ""
        if total_pages > 1:
            nav = "\n[A] ◀  Назад   [D] ▶  Вперёд\n"

        txt += f"{nav}\nНомер — вкл/выкл  |  {t('s_0', cfg)}"
        print_box(txt)

        ch = input_c(">").strip().upper()
        if ch in ("ESC", "0", ""):
            break
        elif ch == "A":
            if page > 0:
                page -= 1
        elif ch == "D":
            if page < total_pages - 1:
                page += 1
        else:
            try:
                idx = int(ch) - 1
                if start <= idx < end:
                    links[idx]["enabled"] = not links[idx].get("enabled", True)
                    save_config(cfg)
            except:
                pass

# ──────────────────────────────────────────────────────────────────────────────
# Главное меню управления источниками
# ──────────────────────────────────────────────────────────────────────────────
def manage_src(cfg):
    PAGE_SIZE = 5
    page = 0

    while True:
        clear()
        print_banner()
        sources = cfg["sources"]

        # Собираем карту репозиториев в порядке появления
        repos_map = {}
        for s in sources:
            r_name = s["name"].split("/")[0]
            if r_name not in repos_map:
                repos_map[r_name] = []
            repos_map[r_name].append(s)

        repo_names = list(repos_map.keys())
        counts = get_source_counts()

        total_pages = max(1, (len(repo_names) + PAGE_SIZE - 1) // PAGE_SIZE)
        page = min(page, total_pages - 1)
        start = page * PAGE_SIZE
        end = min(start + PAGE_SIZE, len(repo_names))
        page_repos = repo_names[start:end]

        txt = f"Источники  [{page+1}/{total_pages}]\n\n"
        for i, name in enumerate(page_repos, start + 1):
            links = repos_map[name]
            total = sum(counts.get(s["id"], 0) for s in links)
            active = any(s.get("enabled", True) for s in links)
            stat = "[+]" if active else "[-]"
            sys_mark = " 🔒" if is_system_repo(name) else " ✏️"
            txt += f"{i}. {stat} {name}{sys_mark}  ({t('src_all', cfg)}{total})\n"

        nav = ""
        if total_pages > 1:
            nav = "\n[A] ◀  [D] ▶\n"

        txt += (f"{nav}\n"
                f"[1] {t('src_1', cfg)}\n"
                f"[2] {t('src_2', cfg)}\n"
                f"[3] {t('src_3', cfg)}\n"
                f"[4] Удалить источник\n"
                f"{t('s_0', cfg)}")

        print_box(txt)
        ch = input_c(">").strip().upper()

        if ch in ("ESC", "0"):
            break

        elif ch == "A":
            if page > 0:
                page -= 1

        elif ch == "D":
            if page < total_pages - 1:
                page += 1

        # ── [1] Список ссылок репозитория ─────────────────────────────────
        elif ch == "1":
            clear()
            print_banner()
            print_box(f"Выберите номер репозитория (1-{len(repo_names)}):\n{t('s_0', cfg)}")
            res = input_c(">").strip()
            if res in ("ESC", "0", ""):
                continue
            try:
                idx = int(res) - 1
                if 0 <= idx < len(repo_names):
                    manage_repo_links(cfg, repos_map, repo_names[idx])
            except:
                pass

        # ── [2] Вкл/Выкл репозитория ──────────────────────────────────────
        elif ch == "2":
            clear()
            print_banner()
            print_box(f"Выберите номер репозитория (1-{len(repo_names)}):\n{t('s_0', cfg)}")
            res = input_c(">").strip()
            if res in ("ESC", "0", ""):
                continue
            try:
                idx = int(res) - 1
                if 0 <= idx < len(repo_names):
                    name = repo_names[idx]
                    target = not any(s.get("enabled", True) for s in repos_map[name])
                    for s in repos_map[name]:
                        s["enabled"] = target
                    save_config(cfg)
            except:
                pass

        # ── [3] Добавить источник/ссылку ──────────────────────────────────
        elif ch == "3":
            _add_source(cfg)

        # ── [4] Удалить источник ──────────────────────────────────────────
        elif ch == "4":
            _delete_source(cfg, repos_map, repo_names)


# ──────────────────────────────────────────────────────────────────────────────
# Добавление источника
# ──────────────────────────────────────────────────────────────────────────────
def _add_source(cfg):
    clear()
    print_banner()
    print_box(
        "Добавление источника\n\n"
        "Введите название репозитория:\n"
        "• Новое имя  → создаст новый репозиторий\n"
        "• Существующее (своё)  → добавит ссылку в него\n"
        "• Системный репозиторий → ❌ запрещено\n\n"
        "[0] Отмена"
    )

    repo_input = input_c(t('enter_repo', cfg)).strip()
    if repo_input in ("ESC", "0", ""):
        return

    if is_system_repo(repo_input):
        clear()
        print_banner()
        print_box(f"❌ {t('err_default', cfg)}")
        print_btn("Системные источники защищены от изменений")
        input_c("")
        return

    clear()
    print_banner()
    print_box(
        f"Репозиторий: {repo_input}\n\n"
        "Введите GitHub Raw URL подписки:\n"
        "Пример: https://raw.githubusercontent.com/...\n\n"
        "[0] Отмена"
    )

    url_input = input_c(t('enter_url', cfg)).strip()
    if url_input in ("ESC", "0", ""):
        return

    # Валидация URL
    if not is_github_raw_url(url_input):
        clear()
        print_banner()
        print_box(
            "❌ Неверный формат URL!\n\n"
            "Поддерживаются только GitHub Raw ссылки:\n"
            "raw.githubusercontent.com/...\n"
            "raw.github.com/..."
        )
        print_btn("Нажмите Enter...")
        input_c("")
        return

    new_id = max([s["id"] for s in cfg["sources"]], default=0) + 1
    existing_in_repo = [
        s for s in cfg["sources"]
        if s["name"].lower().startswith(repo_input.lower() + "/")
    ]
    sub_idx = len(existing_in_repo) + 1

    new_source = {
        "id": new_id,
        "name": f"{repo_input}/Link_{sub_idx}",
        "url": url_input,
        "type": "regular",
        "enabled": True
    }

    cfg["sources"].append(new_source)
    save_config(cfg)

    clear()
    print_banner()
    print_box(f"✅ Источник добавлен!\n\nРепозиторий: {repo_input}\nСсылка: {url_input}")
    print_btn("Нажмите Enter...")

    threading.Thread(
        target=update_counts_bg,
        args=([new_source],),
        daemon=True
    ).start()
    input_c("")


# ──────────────────────────────────────────────────────────────────────────────
# Удаление источника
# ──────────────────────────────────────────────────────────────────────────────
def _delete_source(cfg, repos_map, repo_names):
    # Только пользовательские репозитории
    user_repos = [n for n in repo_names if not is_system_repo(n)]

    if not user_repos:
        clear()
        print_banner()
        print_box("Нет пользовательских источников для удаления.\n\nСистемные источники удалить нельзя.")
        print_btn("Нажмите Enter...")
        input_c("")
        return

    clear()
    print_banner()
    txt = "Удаление источника\n(только пользовательские)\n\n"
    for i, name in enumerate(user_repos, 1):
        links = repos_map[name]
        txt += f"{i}. {name}  ({len(links)} ссылок)\n"
    txt += f"\n[0] Отмена"
    print_box(txt)

    res = input_c("Номер репозитория:").strip()
    if res in ("ESC", "0", ""):
        return

    try:
        idx = int(res) - 1
        if not (0 <= idx < len(user_repos)):
            return
        target_repo = user_repos[idx]
    except:
        return

    # Спросить: весь репозиторий или конкретную ссылку
    links = repos_map[target_repo]
    clear()
    print_banner()
    txt = f"Репозиторий: {target_repo}\n\n"
    for i, s in enumerate(links, 1):
        txt += f"{i}. {s['name']}\n"
    txt += "\n[A] Удалить весь репозиторий\nНомер → удалить конкретную ссылку\n[0] Отмена"
    print_box(txt)

    ch = input_c(">").strip().upper()
    if ch in ("ESC", "0", ""):
        return

    if ch == "A":
        # Удаляем все ссылки репозитория
        ids_to_remove = {s["id"] for s in links}
        cfg["sources"] = [s for s in cfg["sources"] if s["id"] not in ids_to_remove]
        save_config(cfg)
        clear()
        print_banner()
        print_box(f"✅ Репозиторий «{target_repo}» удалён.")
        print_btn("Нажмите Enter...")
        input_c("")
    else:
        try:
            link_idx = int(ch) - 1
            if 0 <= link_idx < len(links):
                target_id = links[link_idx]["id"]
                cfg["sources"] = [s for s in cfg["sources"] if s["id"] != target_id]
                save_config(cfg)
                clear()
                print_banner()
                print_box(f"✅ Ссылка удалена из «{target_repo}».")
                print_btn("Нажмите Enter...")
                input_c("")
        except:
            pass


# ──────────────────────────────────────────────────────────────────────────────
# Остальные функции (без изменений)
# ──────────────────────────────────────────────────────────────────────────────
def select_lang(cfg):
    while True:
        clear()
        print_banner()
        txt = "1. English\n2. Русский\n3. 简体中文\n\n" + str(t('s_0', cfg))
        print_box(txt)
        ch = input_c(">")
        if ch == "ESC":
            return
        if ch == "0":
            return
        elif ch == "1":
            cfg["lang"] = "English"; save_config(cfg); return
        elif ch == "2":
            cfg["lang"] = "Russian"; save_config(cfg); return
        elif ch == "3":
            cfg["lang"] = "Chinese"; save_config(cfg); return

def settings(cfg):
    while True:
        clear()
        print_banner()
        f_ru = t('on', cfg) if cfg["filter_russia"] else t('off', cfg)
        f_smart = t('on', cfg) if cfg.get("smart_filter") else t('off', cfg)
        t_type = t('test_fast', cfg) if cfg.get("test_type") == "TCP Ping" else t('test_tcp', cfg)
        box = (f"{t('s_1', cfg)}{f_ru}\n"
               f"{t('s_2', cfg)}{cfg['max_configs']}\n"
               f"{t('s_3', cfg)}{cfg.get('theme')}\n"
               f"{t('s_4', cfg)}\n"
               f"{t('s_5', cfg)}{t_type}\n"
               f"{t('s_6', cfg)}{f_smart}\n"
               f"{t('s_0', cfg)}")
        print_box(box)
        ch = input_c(">")
        if ch == "ESC":
            break
        if ch == "0":
            break
        elif ch == "1":
            cfg["filter_russia"] = not cfg["filter_russia"]
        elif ch == "2":
            res = input_c(":")
            if res == "ESC":
                save_config(cfg)
                continue
            try:
                cfg["max_configs"] = int(res)
            except Exception:
                pass
        elif ch == "3":
            clear()
            print_banner()
            themes = get_theme_list()
            txt = "\n".join([f"{i+1}. {x}" for i, x in enumerate(themes)])
            print_box(txt + f"\n\n{t('s_0', cfg)}")
            tch = input_c(">")
            if tch == "ESC":
                save_config(cfg)
                continue
            if tch != "0":
                try:
                    idx = int(tch) - 1
                    if 0 <= idx < len(themes):
                        cfg["theme"] = themes[idx]
                        set_active_theme(themes[idx])
                except:
                    pass
        elif ch == "4":
            manage_src(cfg)
        elif ch == "5":
            cfg["test_type"] = "TLS Handshake" if cfg.get("test_type") == "TCP Ping" else "TCP Ping"
        elif ch == "6":
            cfg["smart_filter"] = not cfg.get("smart_filter", False)
        save_config(cfg)

def show_subs(cfg):
    port, token = cfg['server_port'], cfg.get('server_token', '')
    reg_url = f"http://localhost:{port}/sub?token={token}"
    whi_url = f"http://localhost:{port}/white?token={token}"
    while True:
        clear()
        print_banner()
        print_box(
            f"{t('sub_reg', cfg)}\n{reg_url}\n\n"
            f"{t('sub_white', cfg)}\n{whi_url}\n\n"
            f"{t('copy_reg', cfg)}\n"
            f"{t('copy_white', cfg)}\n"
            f"{t('s_0', cfg)}"
        )
        ch = input_c(">")
        if ch == "ESC":
            break
        if ch == "0":
            break
        elif ch == "1":
            if copy_to_clipboard(reg_url):
                print_btn(t('copied', cfg))
            else:
                print_btn(t('copy_fail', cfg))
            input_c("")
        elif ch == "2":
            if copy_to_clipboard(whi_url):
                print_btn(t('copied', cfg))
            else:
                print_btn(t('copy_fail', cfg))
            input_c("")

def main():
    global last_run_time
    cfg = load_config()
    set_active_theme(cfg.get("theme", "Claude"))
    start_server(cfg["server_host"], cfg["server_port"])
    threading.Thread(target=update_counts_bg, args=(cfg["sources"],), daemon=True).start()

    while True:
        clear()
        print_banner()
        last_p_str = last_run_time if last_run_time else t('never', cfg)
        menu = (f"{t('m_1', cfg)}\n{t('m_2', cfg)}\n{t('m_3', cfg)}\n"
                f"{t('m_4', cfg)}\n{t('m_0', cfg)}\n\n"
                f"{t('m_last', cfg)}{last_p_str}")
        print_box(menu)
        ch = input_c(">")
        if ch == "ESC":
            os._exit(0)
        elif ch == "1":
            show_subs(cfg)
        elif ch == "2":
            settings(cfg)
        elif ch == "3":
            reg, whi = parse_and_check(cfg, t)
            save_all(reg, whi)  # внутри уже проверяет None и пустые списки
            if reg is not None:  # показываем время только если парсинг не упал
                last_run_time = datetime.now().strftime("%H:%M:%S")
            print_btn(t('enter', cfg))
            input_c("")
        elif ch == "4":
            select_lang(cfg)
        elif ch == "0":
            os._exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        os._exit(1)