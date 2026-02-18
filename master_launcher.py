import os, sys, time, json
import urllib.request
from rich.console import Console

console = Console()
CONFIG_FILE = "arsy_config.json"

MODULES_URL = [
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/discord_bot.py",
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/core.py"
]

def safe_input(prompt_text, required=True):
    while True:
        console.print(prompt_text, end="")
        start_time = time.time() 
        try:
            ans = input().strip()
        except EOFError:
            ans = ""
            
        elapsed = time.time() - start_time 
        
        if ans == "" and elapsed < 0.2:
            continue
            
        if ans: return ans
        if not required: return ""
        
        console.print("[red]⚠ Bagian ini wajib diisi![/red]\n")

config = {"device_name": "", "ps_link": "", "webhook": "", "live_msg_id": ""}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f: config.update(json.load(f))
    except: pass

def save_config():
    with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)

def reset_menu():
    while True:
        os.system('clear')
        console.print("[bold magenta]PENGATURAN DATA ARSY[/bold magenta]\n")
        console.print("[bold white][ 1 ][/bold white] Ganti Link Private Server Saja")
        console.print("[bold white][ 2 ][/bold white] Ganti Webhook Discord Saja")
        console.print("[bold white][ 3 ][/bold white] Kembali ke Menu Utama\n")
        
        p = safe_input("[bold yellow]Pilih menu (1/2/3): [/bold yellow]")
        if p == '1':
            config["ps_link"] = safe_input("\n[bold yellow]Masukkan Link Private Server Baru (Kosong=Normal):\n> [/bold yellow]", required=False)
            save_config()
            console.print("[bold green]Link Private Server berhasil diperbarui![/bold green]")
            time.sleep(1)
        elif p == '2':
            config["webhook"] = safe_input("\n[bold yellow]Masukkan URL Webhook Discord Baru:\n> [/bold yellow]", required=False)
            save_config()
            console.print("[bold green]Webhook Discord berhasil diperbarui![/bold green]")
            time.sleep(1)
        elif p == '3': break

def main_menu():
    while True:
        os.system('clear')
        console.print("[bold cyan]╔══════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║          ARSY MONITOR LOG            ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]\n")
        console.print("[bold white]Silakan pilih menu:[/bold white]")
        console.print("[bold green][ 1 ][/bold green] Mulai Monitoring & Auto-Farming")
        console.print("[bold yellow][ 2 ][/bold yellow] Pengaturan (Ganti Link / Webhook)")
        console.print("[bold red][ 3 ][/bold red] Keluar Aplikasi\n")
        
        p = safe_input("[bold yellow]Masukkan angka (1/2/3): [/bold yellow]")
        if p == '1': return
        elif p == '2': reset_menu()
        elif p == '3': sys.exit()

if not config.get("device_name"):
    os.system('clear')
    console.print("[bold magenta]SETUP WIZARD (HANYA 1X)[/bold magenta]\n")
    config["device_name"] = safe_input("[bold yellow]Nama Device (Misal: DEVICE 1):\n> [/bold yellow]", required=True)
    config["ps_link"] = safe_input("\n[bold yellow]Link Private Server (Kosong = Normal):\n> [/bold yellow]", required=False)
    config["webhook"] = safe_input("\n[bold yellow]URL Webhook Discord (Opsional):\n> [/bold yellow]", required=False)
    save_config()
    console.print("\n[bold green]Setup Tersimpan! Memasuki Sistem...[/bold green]")
    time.sleep(1)

main_menu()

os.system('clear')
console.print("\n[bold white]Process.........[/bold white]")
try:
    global_env = globals()
    for url in MODULES_URL:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            exec(response.read().decode('utf-8'), global_env)
except Exception as e:
    console.print(f"\n[bold red]Gagal merakit modul: {e}[/bold red]")
    sys.exit()
