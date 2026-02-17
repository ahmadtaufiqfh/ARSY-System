import os, sys, time, json, subprocess
import urllib.request
from rich.console import Console

console = Console()
CONFIG_FILE = "arsy_config.json"

# 👇 3 LINK RAW MODUL ANDA 👇
MODULES_URL = [
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/ram_sensor.py",
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/discord_bot.py",
    "https://raw.githubusercontent.com/ahmadtaufiqfh/ARSY-System/main/core.py"
]

# --- JURUS SAKTI: SMART INPUT (ANTI GHOST ENTER & ANTI SPAM) ---
def smart_input(prompt_text, required=True):
    while True:
        start_time = time.time()
        ans = console.input(prompt_text).strip()
        elapsed = time.time() - start_time
        
        if ans:
            return ans
            
        # Jika Enter sangat cepat (< 0.2 detik), itu pasti Ghost Enter.
        # Hapus baris tersebut dan ulang tanpa sisa visual!
        if elapsed < 0.2:
            sys.stdout.write("\033[1A\033[2K") 
            sys.stdout.flush()
            continue
            
        # Jika kosong dan opsional (manusia yang tekan Enter)
        if not required:
            return ""
            
        # Jika kosong tapi wajib isi, hapus baris dan paksa isi ulang
        sys.stdout.write("\033[1A\033[2K")
        sys.stdout.flush()

# --- Cek Fitur Reset ---
if len(sys.argv) > 1 and sys.argv[1] == "--reset":
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        console.print("[bold green]✅ Reset Berhasil! Konfigurasi telah dihapus.[/bold green]")
    else:
        console.print("\n[yellow]⚠️ Tidak ada data untuk direset.[/yellow]")
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
    
    pilihan = smart_input("[bold yellow]👉 Masukkan angka (1/2/3): [/bold yellow]")
    
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

# 1. PERBAIKAN BUG: Kembalikan metode pencarian aplikasi yang akurat
pkgs = subprocess.getoutput("pm list packages | grep roblox").split('\n')
apps = [p.split(':')[1].strip() for p in pkgs if ':' in p and 'roblox' in p]

if not apps:
    console.print("\n[bold red]❌ Tidak ada aplikasi Roblox ditemukan![/bold red]")
    sys.exit()

# 2. SETUP WIZARD (Menggunakan Smart Input)
config = {"device_name": "", "ps_link": "", "webhook": "", "apps": {}, "live_msg_id": ""}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f: config.update(json.load(f))
    except: pass

new_setup = False
apps_to_configure = [app for app in apps if app not in config["apps"]]

if apps_to_configure or not config.get("device_name"):
    console.print(f"\n[bold magenta]🛠️ SETUP WIZARD[/bold magenta]")
    
    if not config.get("device_name"):
        config["device_name"] = smart_input("[bold yellow]👉 Nama Device (Misal: DEVICE 1): [/bold yellow]", required=True)
        new_setup = True

    if apps_to_configure:
        for app in apps_to_configure:
            config["apps"][app] = smart_input(f"[bold yellow]👉 Nama Akun untuk [[white]{app}[/white]]: [/bold yellow]", required=True)
            new_setup = True

    if "ps_link" not in config or not os.path.exists(CONFIG_FILE):
        console.print("\n[bold cyan]-- Pengaturan Jaringan & Discord --[/bold cyan]")
        config["ps_link"] = smart_input("[bold yellow]👉 Link Private Server (Kosong = Normal): [/bold yellow]", required=False)
        config["webhook"] = smart_input("[bold yellow]👉 URL Webhook Discord (Opsional): [/bold yellow]", required=False)
        new_setup = True

if new_setup:
    with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)
    console.print("\n[bold green]✅ Setup Disimpan![/bold green]\n")

# 3. PEMBERSIHAN (Baru menggunakan Root)
console.print("[yellow]🧹 Membersihkan background service...[/yellow]")
for app in apps:
    run_root(f"am force-stop {app}")
time.sleep(1)

# 4. MENGUNDUH 3 MODUL INTI
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
