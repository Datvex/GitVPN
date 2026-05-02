# GitVPN

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  <img src="https://img.shields.io/static/v1?label=UI&message=Rich&color=555555&labelColor=FF8C00&style=for-the-badge" alt="UI | Rich">
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

GitVPN — инструмент на Python для сбора, проверки и раздачи VPN-конфигураций. Забирает данные напрямую через GitHub Raw, без ограничений стандартного API.

## Возможности

**Два типа конфигураций** — обычные узлы через `/sub` и конфигурации для обхода белых списков через `/white`.

**Проверка узлов** — многопоточная проверка пинга и доступности в реальном времени.

**Терминальный интерфейс** — управление и мониторинг через TUI на базе библиотеки Rich.

**Гибкая настройка** — лимиты, фильтрация по странам и управление источниками через конфиги.

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Datvex/GitVPN
```

2. Перейдите в директорию проекта:
```bash
cd GitVPN
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Запустите приложение:
```bash
python main.py
```

*Read this in other languages: [English](README_EN.md)*
