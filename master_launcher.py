import os, sys, time, json
import urllib.request
from rich.console import Console

console = Console()
CONFIG_FILE = "arsy_config.json"

MODULES_URL = [
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/discord_bot.py",
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/core.py"
]

# 👇 FUNGSI INPUT SENSOR WAKTU ANTI-GHOST ENTER 👇
def safe_input(prompt_text, required=True):
    while True:
        console.print(prompt_text, end="")
        start_time = time.time() # Mulai Stopwatch
        try:
            ans = input().strip()
        except EOFError:
            ans = ""
            
        elapsed = time.time() - start_time # Hentikan Stopwatch
        
        # Jika masuknya kilat (< 0.2 detik) dan kosong, itu pasti ulah Redfinger. Abaikan!
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
        console.print("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]\
