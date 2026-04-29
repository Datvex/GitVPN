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

## Project Description

GitVPN is a professional Python-based software solution designed to automate the aggregation, validation, and distribution of VPN configurations. The system architecture is optimized to ensure high throughput and stability when interacting with distributed data sources.

### Technical Features

* **Direct Data Injection:** Implements a specialized mechanism for fetching data via raw requests to GitHub infrastructure, bypassing standard API rate limits and constraints.
* **Data Stream Differentiation:** Automatically segments configurations into standard nodes (`/sub`) and specialized solutions optimized for bypassing whitelist restrictions (`/white`).
* **Concurrent Validation:** Features a high-performance multi-threaded engine for real-time latency testing and node availability verification.
* **Terminal User Interface (TUI):** Includes an interactive management dashboard powered by the Rich library, enabling real-time monitoring of system processes and rapid parameter adjustments.
* **Parametric Control:** Provides granular configuration of limits, geographic filtering, and source pool management via internal configuration files.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Datvex/GitVPN
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the application:
```bash
python main.py
```

*Read this in other languages: [Russian](README.md)*
