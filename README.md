# GitVPN

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  <img src="https://img.shields.io/static/v1?label=UI&message=Custom%20TUI&color=555555&labelColor=FF8C00&style=for-the-badge" alt="UI | Custom TUI">
</p>

<p align="center">
  🌐 <b>🇷🇺 Русский</b> | <a href="README_EN.md"><b>🇬🇧 English</b></a> | <a href="README_CN.md"><b>🇨🇳 简体中文</b></a>
</p>

## Авторы

<p align="center">
  <a href="https://github.com/Squnplee">
    <img src="https://img.shields.io/badge/Founder-Squnplee-FF4500?style=for-the-badge&logo=github&logoColor=white" alt="Squnplee">
  </a>
  <a href="https://github.com/Datvex">
    <img src="https://img.shields.io/badge/Developer-Datvex-FFD700?style=for-the-badge&logo=github&logoColor=black" alt="Datvex">
  </a>
</p>

## О проекте

GitVPN это инструмент на Python для сбора, проверки и раздачи VPN-конфигураций. Забирает данные напрямую через GitHub Raw, без ограничений стандартного API.

## Возможности

**Два типа конфигураций:** обычные узлы через `/sub` и конфигурации для обхода белых списков через `/white`.

**Проверка узлов:** многопоточная проверка пинга и доступности в реальном времени.

**Кастомный TUI:** собственный терминальный интерфейс с поддержкой клавиатуры, мыши и сенсорных экранов.

**Сервер подписок:** встроенный HTTP сервер раздаёт подписку для любых VPN клиентов.

**Гибкая настройка:** лимиты, фильтрация по странам и управление источниками.

## Установка

### Termux (Android)

1. Установите Termux из F-Droid или GitHub (версия из Google Play устарела).

2. Обновите пакеты и установите зависимости:
```bash
pkg update && pkg upgrade
pkg install python git
```

3. Клонируйте репозиторий:
```bash
git clone https://github.com/Datvex/GitVPN
```

4. Перейдите в папку проекта и установите зависимости:
```bash
cd GitVPN
pip install -r requirements.txt
```

5. Запустите приложение:
```bash
python main.py
```

### Windows

1. Установите Python 3.10 или новее с python.org, обязательно отметьте галочку "Add Python to PATH".

2. Клонируйте репозиторий:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. Перейдите в папку проекта:
```bash
cd GitVPN
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Запустите приложение:
```bash
python main.py
```

### Linux

1. Установите Python, pip и git (пример для Ubuntu/Debian):
```bash
sudo apt update && sudo apt install python3 python3-pip git
```

2. Клонируйте репозиторий:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. Перейдите в папку проекта:
```bash
cd GitVPN
```

4. Установите зависимости:
```bash
pip3 install -r requirements.txt
```

5. Запустите приложение:
```bash
python3 main.py
```

### macOS

1. Установите Homebrew (если нет) и Python с git:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python git
```

2. Клонируйте репозиторий:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. Перейдите в папку проекта:
```bash
cd GitVPN
```

4. Установите зависимости:
```bash
pip3 install -r requirements.txt
```

5. Запустите приложение:
```bash
python3 main.py
```
