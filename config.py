import os
import json

CONFIG_FILE = os.path.join("configs", "user_config.json")

RAW_SOURCES = [
    {"id": 1, "name": "igareck/BLACK_VLESS_mobile", "url": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt", "type": "regular"},
    {"id": 2, "name": "igareck/BLACK_VLESS_full", "url": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt", "type": "regular"},
    {"id": 3, "name": "igareck/BLACK_SS_All", "url": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt", "type": "regular"},
    {"id": 4, "name": "igareck/WHITE_Reality_1", "url": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt", "type": "whitelist"},
    {"id": 5, "name": "igareck/WHITE_Reality_2", "url": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt", "type": "whitelist"},
    {"id": 6, "name": "igareck/WHITE_CIDR_All", "url": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt", "type": "whitelist"},
    {"id": 7, "name": "igareck/WHITE_CIDR_Checked", "url": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt", "type": "whitelist"},
    {"id": 8, "name": "igareck/WHITE_SNI_All", "url": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-SNI-RU-all.txt", "type": "whitelist"},
    {"id": 9, "name": "AvenCores/mirror_4", "url": "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/4.txt", "type": "regular"},
    {"id": 10, "name": "AvenCores/mirror_22", "url": "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/22.txt", "type": "regular"},
    {"id": 11, "name": "AvenCores/mirror_26", "url": "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/26.txt", "type": "whitelist"},
    {"id": 12, "name": "Barry/Sub1", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt", "type": "regular"},
    {"id": 13, "name": "Barry/Sub2", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub2.txt", "type": "regular"},
    {"id": 14, "name": "Barry/Sub3", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub3.txt", "type": "regular"},
    {"id": 15, "name": "Barry/Sub4", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub4.txt", "type": "regular"},
    {"id": 16, "name": "Barry/Sub5", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub5.txt", "type": "regular"},
    {"id": 17, "name": "Barry/Sub6", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub6.txt", "type": "regular"},
    {"id": 18, "name": "Barry/Sub7", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub7.txt", "type": "regular"},
    {"id": 19, "name": "Barry/Sub8", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub8.txt", "type": "regular"},
    {"id": 20, "name": "Ebrasha/All", "url": "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/all_extracted_configs.txt", "type": "regular"},
    {"id": 21, "name": "Ebrasha/Vless", "url": "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/vless_configs.txt", "type": "regular"},
    {"id": 22, "name": "Ebrasha/Vmess", "url": "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/vmess_configs.txt", "type": "regular"},
    {"id": 23, "name": "Ebrasha/Config", "url": "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/V2Ray-Config-By-EbraSha.txt", "type": "regular"},
    {"id": 24, "name": "Barry/Proto_Vmess", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vmess.txt", "type": "regular"},
    {"id": 25, "name": "Barry/Proto_Vless", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt", "type": "regular"},
    {"id": 26, "name": "Barry/Proto_SS", "url": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/ss.txt", "type": "regular"}
]

DEFAULT_CONFIG = {
    "filter_russia": True,
    "max_configs": 50,
    "parse_interval": 60,
    "ping_timeout": 1.5,
    "sources": RAW_SOURCES,
    "server_port": 8000,
    "server_host": "0.0.0.0"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    for src in RAW_SOURCES:
        if not any(s["id"] == src["id"] for s in cfg["sources"]):
            cfg["sources"].append(src)
    return cfg

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)