# GitVPN

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  <img src="https://img.shields.io/static/v1?label=UI&message=Custom%20TUI&color=555555&labelColor=FF8C00&style=for-the-badge" alt="UI | Custom TUI">
</p>

<p align="center">
  🌐 <a href="README.md"><b>🇷🇺 俄语</b></a> | <a href="README_EN.md"><b>🇬🇧 英语</b></a> | <b>🇨🇳 简体中文</b>
</p>

## 作者

<p align="center">
  <a href="https://github.com/Squnplee">
    <img src="https://img.shields.io/badge/Founder-Squnplee-FF4500?style=for-the-badge&logo=github&logoColor=white" alt="Squnplee">
  </a>
  <a href="https://github.com/Datvex">
    <img src="https://img.shields.io/badge/Developer-Datvex-FFD700?style=for-the-badge&logo=github&logoColor=black" alt="Datvex">
  </a>
</p>

## 关于项目

GitVPN 是一个用于收集、验证和分发 VPN 配置的 Python 工具。直接通过 GitHub Raw 获取数据，不受标准 API 限制。

## 功能

**两种配置类型:** 通过 `/sub` 提供普通节点，通过 `/white` 提供白名单配置。

**节点检测:** 多线程实时延迟和可用性检查。

**自定义 TUI:** 自研终端界面，支持键盘、鼠标和触摸屏。

**订阅服务器:** 内置 HTTP 服务器，可向任意 VPN 客户端提供订阅。

**灵活配置:** 数量限制、国家过滤和来源管理。

## 安装

### Termux (Android)

1. 安装 Termux（F-Droid 或 GitHub，Google Play 版本已过时）。

2. 更新包并安装依赖:
```bash
pkg update && pkg upgrade
pkg install python git
```

3. 克隆仓库:
```bash
git clone https://github.com/Datvex/GitVPN
```

4. 进入项目目录并安装依赖:
```bash
cd GitVPN
pip install -r requirements.txt
```

5. 运行:
```bash
python main.py
```

### Windows

1. 从 python.org 安装 Python 3.10 或更高版本，务必勾选 "Add Python to PATH"。

2. 克隆仓库:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. 进入项目目录:
```bash
cd GitVPN
```

4. 安装依赖:
```bash
pip install -r requirements.txt
```

5. 运行:
```bash
python main.py
```

### Linux

1. 安装 Python、pip 和 git（以 Ubuntu/Debian 为例）:
```bash
sudo apt update && sudo apt install python3 python3-pip git
```

2. 克隆仓库:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. 进入项目目录:
```bash
cd GitVPN
```

4. 安装依赖:
```bash
pip3 install -r requirements.txt
```

5. 运行:
```bash
python3 main.py
```

### macOS

1. 安装 Homebrew（如未安装）以及 Python 和 git:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python git
```

2. 克隆仓库:
```bash
git clone https://github.com/Datvex/GitVPN
```

3. 进入项目目录:
```bash
cd GitVPN
```

4. 安装依赖:
```bash
pip3 install -r requirements.txt
```

5. 运行:
```bash
python3 main.py
```
