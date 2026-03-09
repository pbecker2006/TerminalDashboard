import subprocess
import sys

required_packages = ["psutil", "rich"]

for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        print(f"{pkg} nicht gefunden. Installiere...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

from rich.console import Console, Group
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import psutil
import socket
import platform
import time
from datetime import timedelta

console = Console()
console.clear()

def get_ip_addresses():
    ips = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ips.append(f"{iface}: {addr.address}")
    return ips

def get_top_processes(limit=5):
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(p.info)
        except:
            pass
    top_cpu = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    top_ram = sorted(procs, key=lambda x: x['memory_percent'], reverse=True)[:limit]
    return top_cpu, top_ram

def format_bytes(size):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def system_usage(prev_net):
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    cores_logical = psutil.cpu_count(logical=True)
    cores_physical = psutil.cpu_count(logical=False)
    freq = psutil.cpu_freq().current
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()
    net1 = prev_net
    net2 = psutil.net_io_counters()
    download_speed = (net2.bytes_recv - net1.bytes_recv) / 1024
    upload_speed = (net2.bytes_sent - net1.bytes_sent) / 1024
    hostname = socket.gethostname()
    os_name = platform.system()
    kernel = platform.release()
    uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))
    users = [u.name for u in psutil.users()]
    process_count = len(psutil.pids())
    return {
        'cpu_percent': cpu_percent,
        'cpu_per_core': cpu_per_core,
        'cores_logical': cores_logical,
        'cores_physical': cores_physical,
        'freq': freq,
        'ram_percent': vm.percent,
        'ram_total': vm.total,
        'ram_used': vm.used,
        'ram_free': vm.available,
        'swap_total': swap.total,
        'swap_used': swap.used,
        'swap_free': swap.free,
        'disk_percent': disk.percent,
        'disk_used': disk.used,
        'disk_free': disk.free,
        'disk_io_read': disk_io.read_bytes,
        'disk_io_write': disk_io.write_bytes,
        'download_speed': download_speed,
        'upload_speed': upload_speed,
        'hostname': hostname,
        'os_name': os_name,
        'kernel': kernel,
        'uptime': uptime,
        'users': users,
        'process_count': process_count,
        'prev_net': net2
    }

progress = Progress(
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
)
cpu_task = progress.add_task("[red]CPU", total=100)
ram_task = progress.add_task("[green]RAM", total=100)
disk_task = progress.add_task("[blue]Disk", total=100)
prev_net = psutil.net_io_counters()

with Live(console=console, refresh_per_second=1) as live:
    while True:
        data = system_usage(prev_net)
        prev_net = data['prev_net']
        progress.update(cpu_task, completed=data['cpu_percent'])
        progress.update(ram_task, completed=data['ram_percent'])
        progress.update(disk_task, completed=data['disk_percent'])

        cpu_text = Text()
        cpu_text.append("CPU Usage: ", style="bold red")
        cpu_text.append(f"{data['cpu_percent']:.1f}%\n", style="grey62")
        cpu_text.append("Cores (L/P): ", style="bold purple")
        cpu_text.append(f"{data['cores_logical']}/{data['cores_physical']}\n", style="grey62")
        cpu_text.append("Frequency: ", style="bold purple")
        cpu_text.append(f"{data['freq']:.1f} MHz\n", style="grey62")
        cpu_text.append("Per Core: ", style="bold purple")
        cpu_text.append(", ".join(f"{c}%" for c in data['cpu_per_core']), style="grey62")

        ram_text = Text()
        ram_text.append("RAM Usage: ", style="bold green")
        ram_text.append(f"{data['ram_percent']:.1f}%\n", style="grey62")
        ram_text.append("Used/Free: ", style="bold purple")
        ram_text.append(f"{format_bytes(data['ram_used'])} / {format_bytes(data['ram_free'])}\n", style="grey62")
        ram_text.append("Swap Used/Free: ", style="bold purple")
        ram_text.append(f"{format_bytes(data['swap_used'])} / {format_bytes(data['swap_free'])}\n", style="grey62")

        disk_text = Text()
        disk_text.append("Disk Usage: ", style="bold blue")
        disk_text.append(f"{data['disk_percent']:.1f}%\n", style="grey62")
        disk_text.append("Used/Free: ", style="bold purple")
        disk_text.append(f"{format_bytes(data['disk_used'])} / {format_bytes(data['disk_free'])}\n", style="grey62")
        disk_text.append("Disk I/O: ", style="bold purple")
        disk_text.append(f"Read {format_bytes(data['disk_io_read'])} | Write {format_bytes(data['disk_io_write'])}\n", style="grey62")

        net_text = Text()
        net_text.append("Network: ", style="bold yellow")
        net_text.append(f"Down: {data['download_speed']:.1f} KB/s | Up: {data['upload_speed']:.1f} KB/s\n", style="grey62")

        sys_text = Text()
        sys_text.append(f"Hostname: ", style="bold purple")
        sys_text.append(f"{data['hostname']}\n", style="grey62")
        sys_text.append(f"OS / Kernel: ", style="bold purple")
        sys_text.append(f"{data['os_name']} / {data['kernel']}\n", style="grey62")
        sys_text.append(f"Uptime: ", style="bold purple")
        sys_text.append(f"{data['uptime']}\n", style="grey62")
        sys_text.append(f"Users: ", style="bold purple")
        sys_text.append(f"{', '.join(data['users'])}\n", style="grey62")
        sys_text.append(f"Processes: ", style="bold purple")
        sys_text.append(f"{data['process_count']}\n", style="grey62")
        ips = get_ip_addresses()
        sys_text.append(f"IP(s): ", style="bold purple")
        sys_text.append(f"{', '.join(ips)}\n", style="grey62")

        top_cpu, top_ram = get_top_processes()
        table = Table(title="Top Processes", show_edge=False, padding=(0,1))
        table.add_column("PID", style="grey62")
        table.add_column("Name", style="grey62")
        table.add_column("CPU %", style="red")
        table.add_column("RAM %", style="green")
        for p1, p2 in zip(top_cpu, top_ram):
            table.add_row(str(p1['pid']), p1['name'], f"{p1['cpu_percent']:.1f}", f"{p2['memory_percent']:.1f}")

        layout = Panel(
            Group(progress, cpu_text, ram_text, disk_text, net_text, sys_text, table),
            title="System Dashboard",
            border_style="cyan",
            padding=(1,2)
        )

        live.update(layout)
        time.sleep(0.5)