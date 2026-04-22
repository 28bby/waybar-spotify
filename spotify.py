#!/usr/bin/env python3
import subprocess
import json
import os
import re
import time
import urllib.request
import urllib.parse

css_file = os.path.expanduser("~/.config/waybar/style.css")
def get_css_color(var_name):
    try:
        with open(css_file, "r") as f:
            for line in f:
                match = re.match(rf"@define-color\s+{var_name}\s+([#\w]+);", line.strip())
                if match: return match.group(1)
    except: pass
    return None

colors = {
    "artist": "#F5C2E7", "song": "#89B4FA", "lyrics": "#CBA6F7",
    "line": get_css_color("line") or "#cdd6f4",
    "header": "#a6d189", "album": "#F9E2AF", "vol": "#FFD700"
}
spotify_icon = ""
icon_color = "#8FCB9B"

def get(cmd):
    try: return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except: return ""

def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if text else ""

def fetch_lyrics(title, artist):
    if not title: return []
    clean = re.sub(r'\(.*?\)|\[.*?\]|-.*', '', title).strip()
    url = f"https://lrclib.net/api/search?q={urllib.parse.quote(clean + ' ' + artist)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WaybarLyrics'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            for res in data:
                if res.get('syncedLyrics'):
                    parsed = []
                    for line in res['syncedLyrics'].split('\n'):
                        m = re.match(r'\[(\d+):(\d+(?:\.\d+)?)\](.*)', line)
                        if m:
                            ts = int(m.group(1)) * 60 + float(m.group(2))
                            if m.group(3).strip(): parsed.append((ts, m.group(3).strip()))
                    return parsed
    except: pass
    return []

cur_id, cur_lyr = "", []

while True:
    status = get("playerctl --player=spotify status").lower()
    if status not in ["playing", "paused"]:
        print(json.dumps({"text": f"<span foreground='{icon_color}'>{spotify_icon}</span>\u00A0\u00A0Spotify"}), flush=True)
        time.sleep(3)
        continue

    title = get("playerctl --player=spotify metadata title")
    artist = get("playerctl --player=spotify metadata artist")
    album = get("playerctl --player=spotify metadata album")
    pos = float(get("playerctl --player=spotify position") or 0)
    length = int(get("playerctl --player=spotify metadata mpris:length") or 0) // 1000000
    vol = int(float(get("playerctl --player=spotify volume") or 0) * 100)

    if f"{artist}{title}" != cur_id:
        cur_id, cur_lyr = f"{artist}{title}", fetch_lyrics(title, artist)

    active_l = "🎶"
    for ts, txt in cur_lyr:
        if pos >= ts: active_l = txt
        else: break

    tt = (f"<span foreground='{colors['header']}'>{spotify_icon} Spotify</span> ({status.capitalize()})\n"
          f"<span foreground='{colors['line']}'>──────────────────────────</span>\n"
          f"🎵 <span foreground='{colors['song']}'>{escape(title)}</span>\n"
          f"👤 <span foreground='{colors['artist']}'>{escape(artist)}</span>\n"
          f"💿 <span foreground='{colors['album']}'>{escape(album)}</span>\n"
          f"⏱️ {int(pos)//60}:{int(pos)%60:02d} / {length//60}:{length%60:02d}\n"
          f"<span foreground='{colors['line']}'>──────────────────────────</span>\n"
          f"🔊 <span foreground='{colors['vol']}'>Volume: {vol}%</span>")

    bar = (f"<span foreground='{icon_color}'>{spotify_icon}</span>\u00A0\u00A0"
           f"<span foreground='{colors['artist']}'>{escape(artist)}</span>"
           f"<span foreground='{colors['line']}'> - </span>"
           f"<span foreground='{colors['song']}'><i>{escape(title)}</i></span>"
           f"<span foreground='{colors['line']}'> | </span>"
           f"<span foreground='{colors['lyrics']}'>{escape(active_l)}</span>")

    print(json.dumps({"text": bar, "tooltip": tt, "class": status}), flush=True)
    time.sleep(0.8)
