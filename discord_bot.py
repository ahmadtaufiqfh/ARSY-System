import time, requests, json
def update_discord_dashboard(config, current_status_dict, start_time_dict, ram_used, ram_total, mode_text):
    webhook = config.get("webhook", "")
    if not webhook: return
    device_name = config.get("device_name", "DEVICE").upper()
    account_map = config.get("apps", {})
    total_apps = len(current_status_dict)
    online_apps = sum(1 for status in current_status_dict.values() if status == "ONLINE")
    embed_color = 689151 if online_apps == total_apps else 16729344
    
    desc = f"**{device_name}**\nMemory (RAM): `{ram_used} MB / {ram_total} MB`\nNetwork: `{mode_text}`\n\n"
    for a, status in current_status_dict.items():
        acc_id = account_map.get(a, a)
        icon = "🟢" if status == "ONLINE" else "🔴"
        desc += f"{icon} **{acc_id}**\n"
        if status == "ONLINE":
            desc += f"> ` ⏱️ {format_uptime(time.time() - start_time_dict[a])} | 💾 {get_app_ram(a)} MB `\n"
        else:
            desc += f"> ` ⏱️ OFFLINE | 💾 0 MB `\n"

    embed = {
        "author": {"name": " ARSY CONTROL CENTER"},
        "color": embed_color,
        "title": f"📱 Connected Devices ({online_apps}/{total_apps})",
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

def send_emergency_ping(config, acc_id):
    webhook, device = config.get("webhook", ""), config.get("device_name", "DEVICE")
    if not webhook: return
    try: requests.post(webhook, json={"content": f"🚨 **ALERT [{device}]:** `{acc_id}` MATI / TERTUTUP!"}, timeout=5)
    except: pass
