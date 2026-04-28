# 🌐 VPN Config Manager (GITVPN)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  <img src="https://img.shields.io/badge/UI-Sunset%20Gradient-orange?style=for-the-badge" alt="UI">
  <img src="https://img.shields.io/badge/Status-Stable-green?style=for-the-badge" alt="Status">
</p>

---

## 👥 Авторы

<p align="center">
  <a href="https://github.com/Squnplee">
    <img src="https://img.shields.io/badge/Founder-Squnplee-FF4500?style=for-the-badge&logo=github&logoColor=white" alt="Squnplee">
  </a>
  <a href="https://github.com/Datvex">
    <img src="https://img.shields.io/badge/Developer-Datvex-FFD700?style=for-the-badge&logo=github&logoColor=black" alt="Datvex">
  </a>
</p>

---

## 🇷🇺 Описание проекта

**VPN Config Manager** — это мощный инструмент на Python для автоматического сбора, проверки и раздачи VPN-конфигураций. Программа ориентирована на максимальную скорость и стабильность, используя прямые источники данных и многопоточную проверку задержки.

### ✨ Ключевые особенности
*   **🚀 Полный отказ от API:** Скрипт работает через прямые Raw-ссылки GitHub. Это полностью снимает ограничения GitHub API (60 запросов/час), позволяя обновлять базу данных неограниченно.
*   **🛡️ Двойная подписка:** Автоматическое разделение на обычные сервера (`/sub`) и «Белые списки» (`/white`) — специальные конфигурации для эффективного обхода блокировок.
*   **⚡ Высокая скорость:** Многопоточный чекер проверяет сотни серверов за считанные секунды, оставляя в списке только самые быстрые и стабильные узлы.
*   **🎨 Градиентный интерфейс:** Уникальный терминальный интерфейс (TUI) с динамическими градиентами в стиле «Sunset» для комфортной работы.
*   **⚙️ Полный контроль:** Управляйте лимитами (до 1000 узлов), фильтруйте российские сервера и переключайте 26+ источников прямо из меню настроек.

### 🛠 Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Squnplee/GITVPN.git
   cd GITVPN
   ```
2. Установите необходимые зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите программу:
   ```bash
   python main.py
   ```

### 📡 Ссылки на подписки
| Тип подписки | Путь | Описание |
| :--- | :--- | :--- |
| **Обычный VPN** | `/sub` | Общий список проверенных высокоскоростных серверов |
| **Белые списки** | `/white` | Конфиги для обхода ограничений (White-list bypass) |

---
*Read this in other languages: [English](README_EN.md)*
