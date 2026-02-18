import time, requests, json

def format_discord_uptime(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0: return f"{h}h {m}m"
    elif m > 0: return f"{m}m {s}s"
    else: return f"{s}s"

def update_discord_dashboard(config, current_status_dict, start_time_dict, ram_used, ram_total, mode_text):
    raw_webhook = config.get("webhook", "")
    if not raw_webhook: return
    
    webhook = raw_webhook.split("?")[0].rstrip("/")
    device_name = config.get("device_name", "DEVICE").upper()
    account_map = config.get("apps", {})
    
    ps_link = config.get("ps_link", "")
    network_status = "Private Server" if ps_link else "Public Server"
    
    all_statuses = list(current_status_dict.values())
    if any("🔴" in s or "⚠️" in s for s in all_statuses): embed_color = 16729344 
    elif any("🟡" in s for s in all_statuses): embed_color = 16776960 
    else: embed_color = 8306033 
    
    desc = f"**{device_name}**\n"
    desc += f"Memory (RAM): `{ram_used} MB / {ram_total} MB`\n"
    desc += f"Network: `{network_status}`\n\n"
    
    for a, status_text in current_status_dict.items():
        usn = account_map.get(a, a)
        
        if "🟢" in status_text: icon = "🟢"
        elif "🟡" in status_text: icon = "🟡"
        elif "🔴" in status_text: icon = "🔴"
        elif "⚠️" in status_text: icon = "⚠️"
        else: icon = "⚪"
        
        clean_status = status_text.replace(icon, "").strip()
        
        try: ram_str = get_app_ram(a)
        except: ram_str = "0 MB"
            
        uptime_sec = time.time() - start_time_dict[a]
        
        if "🔴" in status_text or "⚠️" in status_text:
            up_str = "--"
        else:
            up_str = format_discord_uptime(uptime_sec)
            
        # PENAMBAHAN SENSOR: Mengapit {usn} dengan || agar menjadi spoiler di Discord
        desc += f"{icon} ||**{usn}**|| `{clean_status}`\n"
        desc += f"|   `⏱️ {up_str} | 💾 {ram_str}`\n"

    embed = {
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
    
    # Menambahkan sensor spoiler juga pada notifikasi darurat / tag @here
    msg = f"@here ⚠️ **PERHATIAN!**\nAkun ||**{usn}**|| mengalami kendala: `{reason}`"
    try:
        requests.post(webhook, json={"content": msg}, timeout=5)
    except: pass
