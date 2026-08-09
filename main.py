import sys, os, re, threading, time
sys.dont_write_bytecode = True

from datetime import datetime
from core import (load_config, save_config, RAW_SOURCES, parse_and_check, save_all,
                  update_counts_bg, start_server, parse_github_url)
from ui import (enable_ansi, restore_console, clear_screen, draw_logo, draw_header, 
                draw_menu_item, draw_sys_item, print_tip, kilo_input, show_floating_modal, 
                print_status, copy_to_clipboard, RawInput, get_event, flush_input_events,
                C_BLUE, C_YELLOW, C_GRAY, C_WHITE, C_RESET, get_layout)

last_run_time = None
SYSTEM_IDS = {s["id"] for s in RAW_SOURCES}

STRINGS = {
    "Russian": {
        "m_1": "Ссылки на подписку", "m_2": "Настройки", "m_3": "Парсить сейчас",
        "m_0": "Выход", "m_last": "Последний запуск: ",
        "s_1": "Фильтр РОС. Серверов", "s_2": "Лимит конфигов", "s_3": "Тема",
        "s_4": "Управление источниками", "s_5": "Тип теста", "s_6": "Фильтр дубликатов",
        "s_7": "Язык", "s_0": "Назад", "on": "ВКЛ", "off": "ВЫКЛ",
        "src_1": "Список источников", "src_2": "Вкл/Выкл Репозиторий", "src_3": "Добавить свой источник",
        "src_all": "Всего", "repo": "Репозиторий", "enter": "Нажмите Enter...", "num_repo": "ID репозитория",
        "parsing": "Загрузка", "sub_reg": "ОБЫЧНЫЙ VPN", "sub_white": "БЕЛЫЕ СПИСКИ", "choice": "Номер темы",
        "never": "Никогда", "test_fast": "TCP Пинг", "test_tcp": "TLS Handshake (Точный)",
        "copy_reg": "Копировать обычную", "copy_white": "Копировать белую",
        "copied": "✓ Скопировано!", "copy_fail": "✗ Не удалось скопировать",
        "err_default": "Ошибка: Нельзя добавлять в дефолтные источники!",
        "enter_repo": "Название источника (при вводе существующего - добавит в него)",
        "enter_url": "Введите URL ссылку на подписку", "smart_info": "Удалено дублей",
        "p_title": "Парсинг", "p_progress": "Прогресс", "p_done": "Готово!",
        "p_fail": "Ошибка парсинга", "any_key": "Нажмите любую кнопку...",
        "src_title": "Источники", "src_add": "Добавить источник", "src_delete": "Удалить источник",
        "src_type": "Тип источника", "src_regular": "Обычный", "src_white": "Белый список",
        "src_locked": "Источник 1 всегда включён", "src_bad_url": "Поддерживаются только ссылки GitHub/Githack",
        "src_added": "Источник добавлен", "src_no_custom": "Нет пользовательских источников",
        "mm_title": "Главное меню", "mm_actions": "Действия",
        "mm_tip": "Введите номер для выбора, или Ctrl+C для выхода",
        "mm_prompt": "Действие:", "sel_prompt": "Выбор:", "tip": "Tip"
    },
    "English": {
        "m_1": "Subscription Links", "m_2": "Settings", "m_3": "Fetch Configs",
        "m_0": "Exit", "m_last": "Last run: ",
        "s_1": "Filter RU Servers", "s_2": "Nodes Limit", "s_3": "UI Theme",
        "s_4": "Source Management", "s_5": "Test Type", "s_6": "Duplicates Filter",
        "s_7": "Language", "s_0": "Back", "on": "ON", "off": "OFF",
        "src_1": "Source List", "src_2": "Toggle Repository", "src_3": "Add custom source",
        "src_all": "Total", "repo": "Repository", "enter": "Press Enter...", "num_repo": "Repository ID",
        "parsing": "Fetching", "sub_reg": "STANDARD VPN", "sub_white": "WHITE LISTS", "choice": "Theme number",
        "never": "Never", "test_fast": "TCP Ping", "test_tcp": "TLS Handshake (Accurate)",
        "copy_reg": "Copy regular link", "copy_white": "Copy whitelist link",
        "copied": "✓ Copied!", "copy_fail": "✗ Failed to copy",
        "err_default": "Error: Cannot add to default sources!",
        "enter_repo": "Source name (if exists, will add to it)",
        "enter_url": "Enter subscription URL", "smart_info": "Duplicates removed",
        "p_title": "Parsing", "p_progress": "Progress", "p_done": "Done!",
        "p_fail": "Parse error", "any_key": "Press any key...",
        "src_title": "Sources", "src_add": "Add source", "src_delete": "Delete source",
        "src_type": "Source type", "src_regular": "Regular", "src_white": "Whitelist",
        "src_locked": "Source 1 is always on", "src_bad_url": "Only GitHub/Githack links supported",
        "src_added": "Source added", "src_no_custom": "No custom sources",
        "mm_title": "Main Menu", "mm_actions": "Actions",
        "mm_tip": "Enter a number to select, or Ctrl+C to exit",
        "mm_prompt": "Action:", "sel_prompt": "Select:", "tip": "Tip"
    },
    "Chinese": {
        "m_1": "订阅链接", "m_2": "设置", "m_3": "立即抓取",
        "m_0": "退出", "m_last": "上次运行: ",
        "s_1": "过滤俄罗斯服务器", "s_2": "配置限制", "s_3": "主题",
        "s_4": "来源管理", "s_5": "测试类型", "s_6": "重复过滤器",
        "s_7": "语言", "s_0": "返回", "on": "开启", "off": "关闭",
        "src_1": "来源列表", "src_2": "开启/关闭 仓库", "src_3": "添加自定义来源",
        "src_all": "总计", "repo": "仓库", "enter": "按回车键...", "num_repo": "仓库 ID",
        "parsing": "正在抓取", "sub_reg": "普通 VPN", "sub_white": "白名单", "choice": "主题编号",
        "never": "从未", "test_fast": "TCP Ping", "test_tcp": "TLS 握手 (精确)",
        "copy_reg": "复制普通链接", "copy_white": "复制白名单链接",
        "copied": "✓ 已复制!", "copy_fail": "✗ 复制失败",
        "err_default": "错误：不能添加到默认来源！",
        "enter_repo": "来源名称（如果已存在，将添加到其中）",
        "enter_url": "输入订阅 URL", "smart_info": "重复项已删除",
        "p_title": "解析中", "p_progress": "进度", "p_done": "完成!",
        "p_fail": "解析错误", "any_key": "按任意键...",
        "src_title": "来源", "src_add": "添加来源", "src_delete": "删除来源",
        "src_type": "来源类型", "src_regular": "普通", "src_white": "白名单",
        "src_locked": "来源 1 始终开启", "src_bad_url": "仅支持 GitHub/Githack 链接",
        "src_added": "来源已添加", "src_no_custom": "没有自定义来源",
        "mm_title": "主菜单", "mm_actions": "操作",
        "mm_tip": "输入编号进行选择，或 Ctrl+C 退出",
        "mm_prompt": "操作:", "sel_prompt": "选择:", "tip": "提示"
    }
}

def t(key, cfg):
    lang = cfg.get("lang", "English")
    return str(STRINGS.get(lang, STRINGS["English"]).get(key, key))

def is_github_raw_url(url):
    if "raw.githubusercontent.com" in url or "raw.github.com" in url or "raw.githack.com" in url:
        return True
    return bool(re.search(r"github\.com/[^/]+/[^/]+/raw/", url))

def _bg(title):
    def render():
        clear_screen(16)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(margin, width, title)
        return _, width, margin
    return render

def wait_any_key():
    flush_input_events()
    with RawInput():
        while True:
            ev = get_event()
            if ev is None or ev == "IGNORE":
                continue
            if isinstance(ev, tuple) and ev[0] == "HOVER":
                continue
            break
    flush_input_events()

def message_screen(cfg, text):
    clear_screen(16)
    draw_logo()
    _, width, margin = get_layout()
    draw_header(margin, width, "GitVPN")
    print(f"{margin}{C_WHITE}{text}{C_RESET}")
    print(f"\n{margin}{C_GRAY}{t('any_key', cfg)}{C_RESET}")
    sys.stdout.flush()
    wait_any_key()

def sources_menu(cfg):
    while True:
        items = [{"type": "category", "label": t("src_title", cfg)}]
        for s in cfg["sources"]:
            state = t('on', cfg) if s.get("enabled", True) else t('off', cfg)
            items.append({"type": "item", "id": f"toggle_{s['id']}", "label": s["name"], "shortcut": state})
        items.append({"type": "item", "id": "add", "label": t("src_add", cfg), "shortcut": ""})
        items.append({"type": "item", "id": "delete", "label": t("src_delete", cfg), "shortcut": ""})
        
        choice = show_floating_modal(t("s_4", cfg), items, _bg(t("s_4", cfg)))
        
        if choice is None:
            break
        if choice.startswith("toggle_"):
            sid = int(choice.split("_")[1])
            src = next((x for x in cfg["sources"] if x["id"] == sid), None)
            if not src:
                continue
            if sid == 1 and src.get("enabled", True):
                message_screen(cfg, t("src_locked", cfg))
                continue
            src["enabled"] = not src.get("enabled", True)
            save_config(cfg)
        elif choice == "add":
            _add_source(cfg)
        elif choice == "delete":
            _delete_source(cfg)

def _add_source(cfg):
    url = kilo_input(t("enter_url", cfg), _bg(t("src_add", cfg)))
    if url in ("esc", ""):
        return
    url = url.strip()
    
    if not is_github_raw_url(url):
        message_screen(cfg, t("src_bad_url", cfg))
        return
    
    items = [
        {"type": "category", "label": t("src_type", cfg)},
        {"type": "item", "id": "regular", "label": t("src_regular", cfg), "shortcut": ""},
        {"type": "item", "id": "whitelist", "label": t("src_white", cfg), "shortcut": ""},
    ]
    type_choice = show_floating_modal(t("src_type", cfg), items, _bg(t("src_add", cfg)))
    if not type_choice:
        return
    
    parsed = parse_github_url(url)
    if parsed:
        user, repo, branch, path = parsed
        base = path.split("/")[-1].split(".")[0]
        name = f"{user}/{base}"
    else:
        n = len([s for s in cfg["sources"] if s["id"] not in SYSTEM_IDS]) + 1
        name = f"custom/Link_{n}"
    
    new_id = max([s["id"] for s in cfg["sources"]], default=0) + 1
    new_source = {
        "id": new_id,
        "name": name,
        "url": url,
        "type": type_choice,
        "enabled": True
    }
    cfg["sources"].append(new_source)
    save_config(cfg)
    
    threading.Thread(target=update_counts_bg, args=([new_source],), daemon=True).start()
    message_screen(cfg, t("src_added", cfg))

def _delete_source(cfg):
    customs = [s for s in cfg["sources"] if s["id"] not in SYSTEM_IDS]
    if not customs:
        message_screen(cfg, t("src_no_custom", cfg))
        return
    
    items = [{"type": "category", "label": t("src_delete", cfg)}]
    for s in customs:
        items.append({"type": "item", "id": str(s["id"]), "label": s["name"], "shortcut": ""})
    
    choice = show_floating_modal(t("src_delete", cfg), items, _bg(t("src_delete", cfg)))
    if choice:
        cfg["sources"] = [x for x in cfg["sources"] if x["id"] != int(choice)]
        save_config(cfg)

def select_lang(cfg):
    items = [
        {"type": "category", "label": t("s_7", cfg)},
        {"type": "item", "id": "English", "label": "English", "shortcut": ""},
        {"type": "item", "id": "Russian", "label": "Русский", "shortcut": ""},
        {"type": "item", "id": "Chinese", "label": "简体中文", "shortcut": ""},
    ]
    choice = show_floating_modal(t("s_7", cfg), items, _bg(t("m_2", cfg)))
    if choice:
        cfg["lang"] = choice
        save_config(cfg)

def select_filter_russia(cfg):
    items = [
        {"type": "category", "label": t("s_1", cfg)},
        {"type": "item", "id": "toggle", "label": t("on", cfg), "shortcut": "●" if cfg["filter_russia"] else ""},
        {"type": "item", "id": "toggle", "label": t("off", cfg), "shortcut": "●" if not cfg["filter_russia"] else ""},
    ]
    choice = show_floating_modal(t("s_1", cfg), items, _bg(t("m_2", cfg)))
    if choice == "toggle":
        cfg["filter_russia"] = not cfg["filter_russia"]
        save_config(cfg)

def select_max_configs(cfg):
    items = [
        {"type": "category", "label": t("s_2", cfg)},
        {"type": "item", "id": "50", "label": "50", "shortcut": "●" if cfg["max_configs"] == 50 else ""},
        {"type": "item", "id": "100", "label": "100", "shortcut": "●" if cfg["max_configs"] == 100 else ""},
        {"type": "item", "id": "150", "label": "150", "shortcut": "●" if cfg["max_configs"] == 150 else ""},
        {"type": "item", "id": "200", "label": "200", "shortcut": "●" if cfg["max_configs"] == 200 else ""},
        {"type": "item", "id": "300", "label": "300", "shortcut": "●" if cfg["max_configs"] == 300 else ""},
    ]
    choice = show_floating_modal(t("s_2", cfg), items, _bg(t("m_2", cfg)))
    if choice:
        cfg["max_configs"] = int(choice)
        save_config(cfg)

def select_test_type(cfg):
    current_fast = cfg.get("test_type") == "TCP Ping"
    items = [
        {"type": "category", "label": t("s_5", cfg)},
        {"type": "item", "id": "tcp", "label": t("test_fast", cfg), "shortcut": "●" if current_fast else ""},
        {"type": "item", "id": "tls", "label": t("test_tcp", cfg), "shortcut": "●" if not current_fast else ""},
    ]
    choice = show_floating_modal(t("s_5", cfg), items, _bg(t("m_2", cfg)))
    if choice == "tcp":
        cfg["test_type"] = "TCP Ping"
        save_config(cfg)
    elif choice == "tls":
        cfg["test_type"] = "TLS Handshake"
        save_config(cfg)

def select_smart_filter(cfg):
    items = [
        {"type": "category", "label": t("s_6", cfg)},
        {"type": "item", "id": "toggle", "label": t("on", cfg), "shortcut": "●" if cfg.get("smart_filter") else ""},
        {"type": "item", "id": "toggle", "label": t("off", cfg), "shortcut": "●" if not cfg.get("smart_filter") else ""},
    ]
    choice = show_floating_modal(t("s_6", cfg), items, _bg(t("m_2", cfg)))
    if choice == "toggle":
        cfg["smart_filter"] = not cfg.get("smart_filter", False)
        save_config(cfg)

def settings_menu(cfg):
    while True:
        f_ru = t('on', cfg) if cfg["filter_russia"] else t('off', cfg)
        f_smart = t('on', cfg) if cfg.get("smart_filter") else t('off', cfg)
        t_type = t('test_fast', cfg) if cfg.get("test_type") == "TCP Ping" else t('test_tcp', cfg)
        
        items = [
            {"type": "category", "label": t("m_2", cfg)},
            {"type": "item", "id": "filter_russia", "label": t("s_1", cfg), "shortcut": f_ru},
            {"type": "item", "id": "max_configs", "label": t("s_2", cfg), "shortcut": str(cfg['max_configs'])},
            {"type": "item", "id": "test_type", "label": t("s_5", cfg), "shortcut": t_type},
            {"type": "item", "id": "smart_filter", "label": t("s_6", cfg), "shortcut": f_smart},
            {"type": "item", "id": "lang", "label": t("s_7", cfg), "shortcut": cfg.get("lang")},
            {"type": "item", "id": "sources", "label": t("s_4", cfg), "shortcut": ""},
        ]
        
        choice = show_floating_modal(t("m_2", cfg), items, _bg(t("m_2", cfg)))
        
        if choice is None:
            break
        elif choice == "filter_russia":
            select_filter_russia(cfg)
        elif choice == "max_configs":
            select_max_configs(cfg)
        elif choice == "test_type":
            select_test_type(cfg)
        elif choice == "smart_filter":
            select_smart_filter(cfg)
        elif choice == "lang":
            select_lang(cfg)
        elif choice == "sources":
            sources_menu(cfg)

def show_subs(cfg):
    port, token = cfg['server_port'], cfg.get('server_token', '')
    reg_url = f"http://localhost:{port}/sub?token={token}"
    whi_url = f"http://localhost:{port}/white?token={token}"
    last_msg = ""
    
    def render_subs():
        clear_screen(16)
        draw_logo()
        _, width, margin = get_layout()
        draw_header(margin, width, t("m_1", cfg))
        print(f"{margin}{C_YELLOW}{t('sub_reg', cfg)}{C_RESET}")
        print(f"{margin}{C_GRAY}{reg_url}{C_RESET}")
        print()
        print(f"{margin}{C_YELLOW}{t('sub_white', cfg)}{C_RESET}")
        print(f"{margin}{C_GRAY}{whi_url}{C_RESET}")
        print()
        draw_menu_item(margin, "1", t("copy_reg", cfg))
        draw_menu_item(margin, "2", t("copy_white", cfg))
        if last_msg:
            print(f"\n{margin}{C_WHITE}{last_msg}{C_RESET}")
        print_tip(t("enter", cfg), margin, width, t("tip", cfg))
        return _, width, margin
    
    while True:
        choice = kilo_input(t("sel_prompt", cfg), render_subs)
        if choice == "esc":
            break
        if choice == "1":
            last_msg = t('copied', cfg) if copy_to_clipboard(reg_url) else t('copy_fail', cfg)
        elif choice == "2":
            last_msg = t('copied', cfg) if copy_to_clipboard(whi_url) else t('copy_fail', cfg)

def run_parse(cfg):
    global last_run_time
    flush_input_events()
    clear_screen(16)
    draw_logo()
    _, width, margin = get_layout()
    draw_header(margin, width, t("p_title", cfg))
    print(f"{margin}{C_YELLOW}● {t('p_progress', cfg)}{C_RESET}")
    sys.stdout.flush()

    with RawInput():
        reg, whi = parse_and_check(cfg, t, margin + "  ", width)
        flush_input_events()
        save_all(reg, whi)

        print()
        if reg is not None:
            last_run_time = datetime.now().strftime("%H:%M:%S")
            print(f"{margin}{C_YELLOW}● {t('p_done', cfg)}{C_RESET}")
            print(f"{margin}  {C_WHITE}{t('sub_reg', cfg)}: {C_BLUE}{len(reg)}{C_RESET}")
            print(f"{margin}  {C_WHITE}{t('sub_white', cfg)}: {C_BLUE}{len(whi)}{C_RESET}")
            print(f"{margin}  {C_GRAY}{t('m_last', cfg)}{last_run_time}{C_RESET}")
        else:
            print(f"{margin}{C_GRAY}● {t('p_fail', cfg)}{C_RESET}")

        print(f"\n{margin}{C_GRAY}{t('any_key', cfg)}{C_RESET}")
        sys.stdout.flush()
        wait_any_key()

    flush_input_events()

def main_menu(cfg):
    def render_main_menu():
        clear_screen(16)
        draw_logo()
        terminal_width, width, margin = get_layout()
        draw_header(margin, width, t("mm_title", cfg))
        print(f"{margin}{C_YELLOW}{t('mm_actions', cfg)}{C_RESET}")
        draw_menu_item(margin, "1", t("m_1", cfg))
        draw_menu_item(margin, "2", t("m_2", cfg))
        draw_menu_item(margin, "3", t("m_3", cfg))
        print()
        last_p_str = last_run_time if last_run_time else t('never', cfg)
        print_status(f"{t('m_last', cfg)}{last_p_str}", margin)
        print_tip(t("mm_tip", cfg), margin, width, t("tip", cfg))
        return terminal_width, width, margin

    while True:
        choice = kilo_input(t("mm_prompt", cfg), render_main_menu)
        
        if choice == "esc":
            continue
        if choice == "1":
            show_subs(cfg)
        elif choice == "2":
            settings_menu(cfg)
        elif choice == "3":
            run_parse(cfg)
        elif choice == "0":
            break

def main():
    enable_ansi()
    try:
        cfg = load_config()
        start_server(cfg["server_host"], cfg["server_port"])
        threading.Thread(target=update_counts_bg, args=(cfg["sources"],), daemon=True).start()
        main_menu(cfg)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        restore_console()

if __name__ == "__main__":
    sys.exit(main())