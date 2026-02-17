import time, os
from rich.table import Table
from rich import box
from rich.panel import Panel

CHECK_INTERVAL = 30
DISCORD_UPDATE_INTERVAL = 60

ps_link = config.get("ps_link", "")
account_map = config.get("apps", {})

console.print(f"\n[bold cyan]🚀 Menjalankan {len(apps)} Aplikasi...[/bold cyan]")
for app in apps:
    acc_id = account_map.get(app, app)
    console.print(f"[yellow]🔄 Membuka {acc_id}...[/yellow]")
    if ps_link == "": run_root(f'am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -p {app} -f 0x10008000')
    else: run_root(f'am start -a android.intent.action.VIEW -d "{ps_link}" -p {app} -f 0x10008000')
    time.sleep(12)

last_status = {a: "OFFLINE" for a in apps}
current_status_dict = {a: "OFFLINE" for a in apps}
start_time_dict = {a: 0 for a in apps}
last_clean, last_discord_update = time.time(), 0 

console.print("\n[bold green]✅ Selesai! Memasuki Mode Monitor...[/bold green]")
time.sleep(2)

while True:
    console.clear() 
    if time.time() - last_clean > 1800:
        for a in apps: run_root(f"rm -rf /data/data/{a}/cache/*")
        last_clean = time.time()

    table = Table(title=f"[bold cyan]ARSY MONITOR ({config.get('device_name', 'DEV')})[/bold cyan]", box=box.ROUNDED, expand=True)
    table.add_column("Nama Akun", style="white")
    table.add_column("Uptime", justify="center")
    table.add_column("Status", justify="center")

    for a in apps:
        check_window = run_root(f"dumpsys window windows | grep {a}")
        current = "ONLINE" if check_window.strip() else "OFFLINE"
        current_status_dict[a] = current
        acc_id = account_map.get(a, a)
        
        if current == "ONLINE" and last_status[a] == "OFFLINE": start_time_dict[a] = time.time()
        elif current == "OFFLINE": start_time_dict[a] = 0
        
        if current == "OFFLINE" and last_status[a] == "ONLINE": send_emergency_ping(config, acc_id)
        last_status[a] = current
        
        color = "green" if current == "ONLINE" else "red"
        up_str = format_uptime(time.time() - start_time_dict[a]) if current == "ONLINE" else "-"
        table.add_row(acc_id, f"[cyan]{up_str}[/cyan]", f"[bold {color}]{current}[/bold {color}]")

    try:
        mem_total, mem_avail = 0, 0
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            mem_total = int(lines[0].split()[1]) // 1024
            for line in lines:
                if "MemAvailable" in line: mem_avail = int(line.split()[1]) // 1024; break
            if mem_avail == 0:
                for line in lines:
                     if "MemFree" in line: mem_avail = int(line.split()[1]) // 1024; break
        used_mb = mem_total - mem_avail
    except: used_mb, mem_total = 0, 0

    mode_text = "Private Server" if ps_link != "" else "Normal"
    console.print(table)
    console.print(Panel(f"[bold green]RAM: {used_mb}MB / {mem_total}MB | Mode: {mode_text}[/bold green]"))
    
    if time.time() - last_discord_update >= DISCORD_UPDATE_INTERVAL:
        update_discord_dashboard(config, current_status_dict, start_time_dict, used_mb, mem_total, mode_text)
        last_discord_update = time.time()

    time.sleep(CHECK_INTERVAL)
