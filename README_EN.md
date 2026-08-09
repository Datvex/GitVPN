# GitVPN

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  <img src="https://img.shields.io/static/v1?label=UI&message=Custom%20TUI&color=555555&labelColor=FF8C00&style=for-the-badge" alt="UI | Custom TUI">
</p>

<p align="center">
  🌐 <a href="README.md"><b>🇷🇺 Russian</b></a> | <b>🇬🇧 English</b> | <a href="README_CN.md"><b>🇨🇳 简体中文</b></a>
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

**Two configuration types:** standard nodes via `/sub` and whitelist bypass configurations via `/white`.

**Node validation:** multi-threaded latency and availability checks in real time.

**Custom TUI:** own terminal interface with keyboard, mouse and touch screen support.

**Subscription server:** built-in HTTP server serves the subscription to any VPN client.

**Flexible configuration:** limits, country filtering and source pool management.

## Installation

### Termux (Android)

1. Install Termux from F-Droid or GitHub (the Google Play version is outdated).

2. Update packages and install dependencies:
```bash
pkg update && pkg upgrade
pkg install python git
```

3. Clone the repository:
```bash
git clone https://github.com/Datvex/GitVPN
```

4. Navigate to the project folder and install dependencies:
```bash
cd GitVPN
pip install -r requirements.txt
```

5. Run the application:
```bash
python main.py
```

### Windows

1. Install Python 3.10 or newer from python.org and make sure to check "Add Python to PATH".

2. Clone the repository:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. Navigate to the project folder:
```bash
cd GitVPN
```

4. Install the dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python main.py
```

### Linux

1. Install Python, pip and git (example for Ubuntu/Debian):
```bash
sudo apt update && sudo apt install python3 python3-pip git
```

2. Clone the repository:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. Navigate to the project folder:
```bash
cd GitVPN
```

4. Install the dependencies:
```bash
pip3 install -r requirements.txt
```

5. Run the application:
```bash
python3 main.py
```

### macOS

1. Install Homebrew (if missing) and Python with git:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python git
```

2. Clone the repository:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. Navigate to the project folder:
```bash
cd GitVPN
```

4. Install the dependencies:
```bash
pip3 install -r requirements.txt
```

5. Run the application:
```bash
python3 main.py
```
