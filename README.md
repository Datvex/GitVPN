# VPN Config Manager (GITVPN)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/static/v1?label=UI&message=Rich&color=555555&labelColor=0078D4&style=for-the-badge" alt="UI | Rich">
</p>

---

## Contributors

<p align="center">
  <a href="https://github.com/Squnplee">
    <img src="https://img.shields.io/badge/Author-Squnplee-gray?style=for-the-badge&logo=github" alt="Squnplee">
  </a>
  <a href="https://github.com/Datvex">
    <img src="https://img.shields.io/badge/Developer-Datvex-gray?style=for-the-badge&logo=github" alt="Datvex">
  </a>
</p>

---

## Project Overview

VPN Config Manager — специализированная утилита на языке Python, предназначенная для автоматизации процессов сбора, валидации и дистрибуции конфигураций VPN. Архитектура системы ориентирована на высокую производительность и отказоустойчивость при обработке массивов данных из распределенных источников.

### Технические характеристики
*   **Прямая инжекция данных:** Механизм получения данных через Raw-запросы к инфраструктуре GitHub, исключающий ограничения стандартного API.
*   **Дифференцированная подписка:** Автоматическая сегментация конфигураций на стандартные узлы (`/sub`) и специализированные решения для обхода ограничений белых списков (`/white`).
*   **Конкурентная валидация:** Многопоточный движок для проверки доступности узлов и измерения сетевых задержек в режиме реального времени.
*   **Terminal User Interface (TUI):** Интерфейс командной строки на базе библиотеки Rich, обеспечивающий визуализацию процессов мониторинга и управления.
*   **Параметрический контроль:** Возможность тонкой настройки лимитов узлов, гео-фильтрации и управления источниками данных через внутреннюю конфигурацию.

## Installation

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Squnplee/GITVPN.git
cd GITVPN
```

2. Установите необходимые зависимости:
```bash
pip install -r requirements.txt
```

3. Выполните запуск приложения:
```bash
python main.py
```

---
*Read this in other languages: [English](README_EN.md)*
