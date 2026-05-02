# GitVPN

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  <img src="https://img.shields.io/static/v1?label=UI&message=Rich&color=555555&labelColor=FF8C00&style=for-the-badge" alt="UI | Rich">
</p>

## Authors

<p align="center">
  <a href="https://github.com/Squnplee">
    <img src="https://img.shields.io/badge/Founder-Squnplee-FF4500?style=for-the-badge&logo=github&logoColor=white" alt="Squnplee">
  </a>
  <a href="https://github.com/Datvex">
    <img src="https://img.shields.io/badge/Developer-Datvex-FFD700?style=for-the-badge&logo=github&logoColor=black" alt="Datvex">
  </a>
</p>

## About

GitVPN is a Python tool for collecting, validating and distributing VPN configurations. It fetches data directly via GitHub Raw, bypassing standard API rate limits.

## Features

**Two configuration types** — standard nodes via `/sub` and configurations for bypassing whitelist restrictions via `/white`.

**Node validation** — multi-threaded latency and availability checks in real time.

**Terminal interface** — management and monitoring via TUI powered by the Rich library.

**Flexible configuration** — limits, country filtering and source pool management via config files.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Datvex/GitVPN
```

2. Navigate to the project directory:
```bash
cd GitVPN
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

*Read this in other languages: [Russian](README.md)*
