import os, sys, time, json, subprocess
import urllib.request
from rich.console import Console

console = Console()
CONFIG_FILE = "arsy_config.json"

# 👇 3 LINK RAW MODUL ANDA (SUDAH TERPASANG) 👇
MODULES_URL = [
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/ram_sensor.py",
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/discord_bot.py",
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/core.py"
]

# --- Cek Fitur Reset ---
if len(sys.argv) > 1 and sys.argv[1] == "--reset":
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        console.print("[bold green]✅ Reset Berhasil! Konfigurasi telah dihapus.[/bold green]")
    else:
        console.print("[yellow]⚠️ Tidak ada data untuk direset.[/yellow]")
    sys.exit()

def run_root(command):
    return subprocess.getoutput(f"su -c '{command}'")

def main_menu():
    os.system('clear')
    console.print("[bold cyan]╔══════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║           ARSY MONITOR LOG          ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]\n")
    console.print("[bold white]Silakan pilih menu:[/bold white]")
    console.print("[bold green][ 1 ][/bold green] 🚀 Mulai Farming & Monitoring")
    console.print("[bold yellow][ 2 ][/bold yellow] ⚙️ Reset / Ganti Pengaturan Device")
    console.print("[bold red][ 3 ][/bold red] ❌ Keluar Aplikasi\n")
    
    pilihan = input("👉 Masukkan angka (1/2/3): ").strip()
    
    if pilihan == '2':
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
            console.print("\n[bold green]✅ Data berhasil di-reset![/bold green]")
        else:
            console.print("\n[yellow]⚠️ Tidak ada data untuk direset.[/yellow]")
        time.sleep(2)
        return main_menu()
    elif pilihan == '3':
        console.print("\n[grey]Sampai jumpa...[/grey]")
        sys.exit()
    elif pilihan == '1':
        return # Lanjut
    else:
        return main_menu()

main_menu()

pkgs = subprocess.getoutput("pm list packages | grep roblox").split('\n')
apps = [p.split(':')[1].strip() for p in pkgs if p]

if not apps:
    console.print("\n[bold red]❌ Tidak ada aplikasi Roblox ditemukan![/bold red]")
    sys.exit()

console.print("\n[yellow]🧹 Membersihkan background service...[/yellow]")
for app in apps:
    run_root(f"am force-stop {app}")
time.sleep(1)

config = {"device_name": "", "ps_link": "", "webhook": "", "apps": {}, "live_msg_id": ""}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f: config.update(json.load(f))
    except: pass

new_setup = False
apps_to_configure = [app for app in apps if app not in config["apps"]]

if apps_to_configure or not os.path.exists(CONFIG_FILE):
    console.print(f"\n[bold magenta]🛠️ SETUP WIZARD[/bold magenta]")
    
    if not config.get("device_name"):
        config["device_name"] = input("👉 Nama Device (Misal: DEVICE 1): ").strip()
        new_setup = True

    if apps_to_configure:
        for app in apps_to_configure:
            acc_id = input(f"👉 Nama Akun untuk [{app}]: ").strip()
            config["apps"][app] = acc_id if acc_id else app
            new_setup = True

    if "ps_link" not in config or not os.path.exists(CONFIG_FILE):
        print("")
        config["ps_link"] = input("👉 Link Private Server (Kosong = Normal): ").strip()
        config["webhook"] = input("👉 URL Webhook Discord (Opsional): ").strip()
        new_setup = True

if new_setup:
    with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)
    console.print("[bold green]✅ Setup Disimpan![/bold green]\n")

# --- MENGUNDUH 3 MODUL INTI ---
console.print("☁️ [white]Menghubungkan ke Server Modular ARSY...[/white]")
try:
    global_env = globals()
    for i, url in enumerate(MODULES_URL, 1):
        console.print(f"[cyan]⬇️  Merakit modul {i}/{len(MODULES_URL)} ke RAM...[/cyan]")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            module_code = response.read().decode('utf-8')
        
        exec(module_code, global_env)
        time.sleep(0.5)
        
except Exception as e:
    console.print(f"[bold red]❌ Gagal terhubung ke server/merakit modul: {e}[/bold red]")
