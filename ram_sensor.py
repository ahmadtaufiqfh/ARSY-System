import subprocess
def run_root(command):
    return subprocess.getoutput(f"su -c '{command}'")

def format_uptime(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    if h > 0: return f"{h}h {m}m"
    elif m > 0: return f"{m}m {int(seconds % 60)}s"
    return f"{int(seconds)}s"

def get_app_ram(pkg):
    try:
        out = run_root(f"dumpsys meminfo {pkg}")
        for line in out.splitlines():
            if "TOTAL" in line and ":" in line:
                for part in line.split():
                    if part.isdigit(): return int(part) // 1024
    except: pass
    return 0
