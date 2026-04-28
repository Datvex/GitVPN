# GitVPN

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
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

## Описание проекта

GitVPN представляет собой специализированное программное решение на языке Python, разработанное для автоматизации процессов агрегации, валидации и распределения конфигураций VPN. Архитектура системы оптимизирована для обеспечения высокой пропускной способности и стабильности при взаимодействии с распределенными источниками данных.

### Технические характеристики

* **Прямая инжекция данных:** Реализован механизм получения данных через Raw-запросы к инфраструктуре GitHub, что исключает зависимость от ограничений стандартного API.
* **Дифференциация потоков данных:** Система выполняет автоматическую сегментацию конфигураций на стандартные узлы (/sub) и специализированные решения для обхода ограничений белых списков (/white).
* **Конкурентная валидация:** Многопоточный движок обеспечивает проверку сетевых задержек и доступности узлов в режиме реального времени.
* **Terminal User Interface (TUI):** Интерактивный интерфейс управления на базе библиотеки Rich позволяет осуществлять мониторинг системных процессов и оперативное изменение параметров.
* **Параметрический контроль:** Реализована возможность детальной настройки лимитов, географической фильтрации и управления пулом источников через внутренние конфигурационные файлы.

## Установка

1. Выполните клонирование репозитория:
```bash
git clone https://github.com/Squnplee/GITVPN.git
cd GITVPN
```

2. Установите необходимые зависимости:
```bash
pip install -r requirements.txt
```

3. Инициализируйте приложение:
```bash
python main.py
```

*Read this in other languages: [English](README_EN.md)*
