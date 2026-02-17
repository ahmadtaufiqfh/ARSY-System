import os, sys, time, json, subprocess
import urllib.request
from rich.console import Console

# Import modul termios untuk membilas (flush) keyboard buffer
try:
    import termios
except ImportError:
    pass

console = Console()
CONFIG_FILE = "arsy_config.json"

# 👇 3 LINK RAW MODUL ANDA 👇
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
    
    pilihan = console.input("[bold yellow]👉 Masukkan angka (1/2/3): [/bold yellow]").strip()
    
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

# 1. PERBAIKAN BUG: Filter Pencarian Aplikasi Super Ketat
raw_pkgs = subprocess.getoutput("pm list packages | grep roblox")
apps = []
for line in raw_pkgs.split('\n'):
    line = line.strip()
    if line.startswith("package:"): # Hanya ambil yang benar-benar nama aplikasi
        pkg_name = line.replace("package:", "").strip()
        if pkg_name:
            apps.append(pkg_name)

if not apps:
    console.print("\n[bold red]❌ Tidak ada aplikasi Roblox ditemukan![/bold red]")
    sys.exit()

# ==========================================
# JURUS SAKTI 1: MEMBILAS KEYBOARD BUFFER
# ==========================================
try:
    termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
except:
    pass
time.sleep(0.5)
# ==========================================

# 2. SETUP WIZARD
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
        while True:
            dn = console.input("[bold yellow]👉 Nama Device (Misal: DEVICE 1): [/bold yellow]").strip()
            if dn:
                config["device_name"] = dn
                new_setup = True
                break
            # Jika kosong, abaikan diam-diam dan ulang pertanyaan

    if apps_to_configure:
        for app in apps_to_configure:
            while True:
                acc_id = console.input(f"[bold yellow]👉 Nama Akun untuk [{app}]: [/bold yellow]").strip()
                if acc_id:
                    config["apps"][app] = acc_id
                    new_setup = True
                    break
                # Jika kosong, abaikan diam-diam

    # --- PENGATURAN LINK & DISCORD ---
    if "ps_link" not in config or not os.path.exists(CONFIG_FILE):
        
        # Bilas buffer ke-2: Mencegah sisa ketikan enter dari nama akun
        try:
            termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
        except:
            pass
        time.sleep(0.2)
        
        console.print("\n[bold cyan]-- Pengaturan Jaringan & Discord --[/bold cyan]")
        
        # Format Baru: Memaksa input diketik di baris baru (\n➤) agar UI tidak tabrakan
        config["ps_link"] = console.input("[bold yellow]👉 Link Private Server (Kosong = Normal):\n➤ [/bold yellow]").strip()
        config["webhook"] = console.input("\n[bold yellow]👉 URL Webhook Discord (Opsional):\n➤ [/bold yellow]").strip()
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
console.print("\n☁️ [white]Menghubungkan ke Server Modular ARSY...[/white]")
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
