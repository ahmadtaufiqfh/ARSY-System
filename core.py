import time, os, subprocess, json
from rich.table import Table
from rich import box
from rich.panel import Panel

CHECK_INTERVAL = 15
CONFIG_FILE = "arsy_config.json"

config = {}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f: config.update(json.load(f))
    except: pass

ps_link = config.get("ps_link", "")

try:
    raw_apps = subprocess.check_output("su -c 'pm list packages | grep roblox'", shell=True).decode('utf-8').strip().split('\n')
    apps = [p.replace('package:', '').strip() for p in raw_apps if p.strip()]
except:
    apps = ["com.roblox.client"]

account_map = config.get("apps", {})
app_states = {}
for a in apps:
    app_states[a] = {
        "status": "🟡 Reconnect", 
        "start_time": time.time(),
        "usn": account_map.get(a, a),
        "script_on": False,
        "fail_count": 0,
        "suspended": False
    }

last_ram_clear = time.time()

def scan_for_usn():
    for a in apps:
        paths_to_check = [
            f"/sdcard/Android/data/{a}/files/gloop/external/workspace",
            f"/data/media/0/Android/data/{a}/files/gloop/external/workspace",
            f"/sdcard/Delta/workspace"
        ]
        
        for check_path in paths_to_check:
            try:
                cmd = f"su -c 'ls {check_path}/arsy_usn_*.txt 2>/dev/null'"
                res = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                
                if res:
                    filepath = res.split('\n')[0].strip()
                    usn = filepath.split("arsy_usn_")[-1].replace(".txt", "").strip()
                    subprocess.run(f"su -c 'rm -f \"{filepath}\"'", shell=True)
                    return usn
            except:
                pass
    return None

def get_app_ram(pkg):
    try:
        res = subprocess.check_output(f"su -c 'dumpsys meminfo {pkg} | grep \"TOTAL:\"'", shell=True).decode('utf-8')
        if res: return str(int(res.split()[1]) // 1024) + " MB"
    except: pass
    return "0 MB"

def launch_app(pkg):
    subprocess.run(f"su -c 'am force-stop {pkg}'", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    if ps_link == "": 
        subprocess.run(f"su -c 'am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -p {pkg} -f 0x10008000'", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else: 
        subprocess.run(f"su -c 'am start -a android.intent.action.VIEW -d \"{ps_link}\" -p {pkg} -f 0x10008000'", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for a in apps:
    launch_app(a)
    time.sleep(12)

def format_uptime(seconds):
    h = int(seconds // 3600); m = int((seconds % 3600) // 60); s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

while True:
    os.system('clear')
    
    # PERBAIKAN UI TERMUX: Menghapus expand=True dan menetapkan batasan teks (no_wrap) agar garis sejajar sempurna
    table = Table(title=f"[bold cyan]ARSY MONITOR LOG ({config.get('device_name', 'DEV')})[/bold cyan]", box=box.ROUNDED)
    table.add_column("IDs", style="white", no_wrap=True, min_width=15)
    table.add_column("STATUS", justify="left", no_wrap=True, min_width=22)
    table.add_column("UPTIME", justify="center", no_wrap=True, min_width=10)
    table.add_column("RAM USAGE", justify="center", no_wrap=True, min_width=10)

    for a in apps:
        state = app_states[a]
        uptime_sec = time.time() - state["start_time"]
        
        try:
            check_win = subprocess.check_output(f"su -c 'dumpsys window windows | grep {a}'", shell=True).decode('utf-8').strip()
            is_open = bool(check_win)
        except: is_open = False
        
        if not is_open:
            if state.get("suspended"):
                state["status"] = "⚠️ Suspended"
            else:
                state["script_on"] = False
                state["status"] = "🟡 Reconnect"
                state["start_time"] = time.time() 
                launch_app(a)
        else:
            if not state["script_on"]:
                if state.get("suspended"):
                    state["status"] = "⚠️ Suspended"
                else:
                    state["status"] = "🟢 Connect"
                    new_usn = scan_for_usn()
                    
                    if new_usn:
                        state["usn"] = new_usn
                        state["script_on"] = True
                        state["status"] = "🟢 Connect | scriptON"
                        state["fail_count"] = 0
                        account_map[a] = new_usn
                        config["apps"] = account_map
                        with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)
                    else:
                        if uptime_sec > 180:
                            state["fail_count"] = state.get("fail_count", 0) + 1
                            if state["fail_count"] >= 2:
                                state["suspended"] = True
                                state["status"] = "⚠️ Suspended"
                                try:
                                    if "send_emergency_ping" in globals():
                                        send_emergency_ping(config, state["usn"], f"Gagal memuat script 2x. Aplikasi {state['usn']} dibiarkan terbuka (Suspended).")
                                except: pass
                            else:
                                state["status"] = "🔴 Disconnect"
                                subprocess.run(f"su -c 'am force-stop {a}'", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                state["status"] = "🟢 Connect | scriptON"
                state["fail_count"] = 0

        color = "green" if "🟢" in state["status"] else ("yellow" if "🟡" in state["status"] else "red")
        up_str = format_uptime(time.time() - state["start_time"])
        ram_str = get_app_ram(a)
        table.add_row(state["usn"], f"[{color}]{state['status']}[/{color}]", f"[cyan]{up_str}[/cyan]", f"[white]{ram_str}[/white]")

    console.print(table)
    
    if time.time() - last_ram_clear > 1800:
        try:
            subprocess.run("su -c 'echo 3 > /proc/sys/vm/drop_caches'", shell=True)
            last_ram_clear = time.time()
        except: pass

    try:
        mem_tot, mem_avl = 0, 0
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            mem_tot = int(lines[0].split()[1]) // 1024
            for l in lines:
                if "MemAvailable" in l: mem_avl = int(l.split()[1]) // 1024; break
        used_mb = mem_tot - mem_avl
    except: used_mb, mem_tot = 0, 0

    console.print(Panel(f"[bold green]RAM: {used_mb}MB / {mem_tot}MB[/bold green]", expand=False))
    
    try:
        if "update_discord_dashboard" in globals():
            update_discord_dashboard(config, {k: app_states[k]["status"] for k in apps}, {k: app_states[k]["start_time"] for k in apps}, used_mb, mem_tot, "")
    except: pass
    
    time.sleep(CHECK_INTERVAL)
