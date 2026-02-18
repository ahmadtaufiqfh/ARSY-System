import time, requests, json

def format_discord_uptime(seconds):
    h = int(seconds // 3600); m = int((seconds % 3600) // 60); s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def update_discord_dashboard(config, current_status_dict, start_time_dict, ram_used, ram_total, mode_text):
    raw_webhook = config.get("webhook", "")
    if not raw_webhook: return
    
    webhook = raw_webhook.split("?")[0].rstrip("/")
    device_name = config.get("device_name", "DEVICE").upper()
    account_map = config.get("apps", {})
    
    all_statuses = list(current_status_dict.values())
    if any("🔴" in s or "⚠️" in s for s in all_statuses): embed_color = 16729344 
    elif any("🟡" in s for s in all_statuses): embed_color = 16776960 
    else: embed_color = 689151 
    
    desc = f"**RAM Usage:** `{ram_used} MB / {ram_total} MB`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for a, status_text in current_status_dict.items():
        usn = account_map.get(a, a)
        
        try: ram_str = get_app_ram(a)
        except: ram_str = "0 MB"
            
        uptime_sec = time.time() - start_time_dict[a]
        
        if "🔴" in status_text or "⚠️" in status_text:
            up_str = "--:--:--"
        else:
            up_str = format_discord_uptime(uptime_sec)
            
        # Format Minimalis Anti-Berantakan
        desc += f"👤 **{usn}**\n"
        desc += f"└ {status_text}  |  ⏱️ {up_str}  |  💾 {ram_str}\n\n"

    embed = {
        "author": {"name": f"ARSY MONITOR LOG - [{device_name}]"},
        "color": embed_color,
        "description": desc,
        "footer": {"text": f"Updated dynamically • {time.strftime('%H:%M:%S WIB')}"}
    }

    msg_id = config.get("live_msg_id", "")
    try:
        if msg_id:
            res = requests.patch(f"{webhook}/messages/{msg_id}", json={"embeds": [embed]}, timeout=5)
            if res.status_code in [200, 204]: return 
        
        res = requests.post(f"{webhook}?wait=true", json={"embeds": [embed]}, timeout=5)
        if res.status_code in [200, 201]:
            config["live_msg_id"] = res.json().get("id")
            with open("arsy_config.json", "w") as f: json.dump(config, f, indent=4)
    except: pass

def send_emergency_ping(config, usn, reason=""):
    raw_webhook = config.get("webhook", "")
    if not raw_webhook: return
    webhook = raw_webhook.split("?")[0].rstrip("/")
    
    # Mengirim Pesan Peringatan Terpisah di Luar Dashboard
    msg = f"@here ⚠️ **PERHATIAN!**\nAkun **{usn}** mengalami kendala: `{reason}`"
    try:
        requests.post(webhook, json={"content": msg}, timeout=5)
    except: pass
