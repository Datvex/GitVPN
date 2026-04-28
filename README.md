# 🌐 VPN Config Manager (GITVPN)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  <img src="https://img.shields.io/badge/UI%20%7C%20Rich-blue?style=for-the-badge" alt="UI | Rich">
</p>

---

## 👥 Авторы

<p align="center">
  <a href="https://github.com/Squnplee">
    <img src="https://img.shields.io/badge/Основатель-Squnplee-FF4500?style=for-the-badge&logo=github&logoColor=white" alt="Squnplee">
  </a>
  <a href="https://github.com/Datvex">
    <img src="https://img.shields.io/badge/Разработчик-Datvex-FFD700?style=for-the-badge&logo=github&logoColor=black" alt="Datvex">
  </a>
</p>

---

## Описание проекта

**VPN Config Manager** — утилита на Python для автоматизации сбора, валидации и распространения VPN-конфигураций. Решение оптимизировано для высокой производительности и стабильности, использует прямые источники данных и многопоточную проверку задержек.

### ✨ Ключевые особенности
*   **🚀 Прямое получение данных:** Работа через Raw-ссылки GitHub без ограничений стандартного API.
*   **🛡️ Двойная подписка:** Автоматическое разделение на обычные сервера (`/sub`) и «Белые списки» (`/white`) — специальные конфигурации для обхода белых списков.
*   **⚡ Многопоточная валидация:** Параллельная проверка доступности и задержек серверов.
*   **💻 Интерфейс командной строки:** Интуитивный TUI на базе библиотеки Rich для удобного управления и мониторинга.
*   **⚙️ Гибкая настройка:** Конфигурация лимитов узлов, фильтрация по регионам и управление источниками через встроенное меню.

### 🛠 Установка
1. Клонируйте репозиторий:
```bash
   git clone https://github.com/Squnplee/GITVPN.git
   cd GITVPN
```
2. Установите зависимости:
```bash
   pip install -r requirements.txt
```
3. Запустите программу:
```bash
   python main.py
```

---
*Read this in other languages: [English](README_EN.md)*
