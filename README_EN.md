# 🌐 VPN Config Manager (GITVPN)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-F7DF1E?style=for-the-badge&logo=python&logoColor=black" alt="Python">
  <img src="https://img.shields.io/badge/UI-Sunset%20Gradient-orange?style=for-the-badge" alt="UI">
  <img src="https://img.shields.io/badge/Status-Stable-green?style=for-the-badge" alt="Status">
</p>

---

## 👥 Authors

<p align="center">
  <a href="https://github.com/Squnplee">
    <img src="https://img.shields.io/badge/Founder-Squnplee-FF4500?style=for-the-badge&logo=github&logoColor=white" alt="Squnplee">
  </a>
  <a href="https://github.com/Datvex">
    <img src="https://img.shields.io/badge/Developer-Datvex-FFD700?style=for-the-badge&logo=github&logoColor=black" alt="Datvex">
  </a>
</p>

---

## 🇺🇸 English Description

**VPN Config Manager** is a high-performance Python tool designed to aggregate, test, and serve VPN configurations. It focuses on extreme speed and reliability by utilizing direct data sources and multi-threaded latency testing.

### ✨ Key Features
*   **🚀 Zero API Usage:** Completely bypasses GitHub API rate limits. The script fetches data via direct Raw URLs for unlimited daily updates.
*   **🛡️ Dual Subscriptions:** Smart separation into regular VPN configs (`/sub`) and specialized "Whitelists" (`/white`) for bypassing censorship.
*   **⚡ Extreme Speed:** A multi-threaded checker validates hundreds of servers in seconds, keeping only the most reliable nodes.
*   **🎨 Stunning UI:** A unique Terminal UI featuring "Sunset" style dynamic gradients for a premium look and feel.
*   **⚙️ Total Control:** Adjust limits (up to 1000 nodes), filter Russian servers, and toggle 26+ sources directly from the settings menu.

### 🛠 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Datvex/GitVPN
   cd GITVPN
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the manager:
   ```bash
   python main.py
   ```

### 📡 Subscription Endpoints
| Type | Path | Description |
| :--- | :--- | :--- |
| **Regular VPN** | `/sub` | General list of tested high-speed servers |
| **Whitelists** | `/white` | Specialized configs for whitelist-based bypasses |

---
*Read this in other languages: [Русский](README.md)*
