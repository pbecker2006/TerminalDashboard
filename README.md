# Terminal Dashboard – System Monitoring Tool

A futuristic terminal dashboard that displays **real-time CPU, RAM, disk, and network statistics**. It also shows system information like **users, hostname, IP addresses, OS version, kernel, uptime**, and **top processes by CPU and RAM usage**.

## Features
- Live progress bars for CPU, RAM, and disk usage
- Per-core CPU usage and frequency
- RAM and swap usage with used/free values
- Disk usage and I/O (Read/Write)
- Network speed (Download/Upload)
- System info: Hostname, OS, Kernel, Uptime, Users, IP addresses
- Top processes by CPU and RAM usage
- Automatic installation of missing packages (`psutil`, `rich`)

## Requirements
- Python 3.8+
- Optional: virtual environment (`venv`) recommended for development
- Script automatically installs missing packages

## Installation & Usage
1. Download the script or extract the GitHub ZIP
2. Open a terminal in the script folder
3. Run the dashboard:

```bash
python3 dashboard_example.py
