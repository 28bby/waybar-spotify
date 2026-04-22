#!/usr/bin/env python3
import subprocess
import json
import os
import re
import time
import urllib.request
import urllib.parse

def load_alacritty_colors(toml_path):
    colors = {}
    full_path = os.path.expanduser(toml_path)
    try:
        with open(full_path, "r") as f:
            current_section = ""
            for line in f:
                line = line.strip()
                sec_match = re.match(r'^\[(.*)\]$', line)
                if sec_match:
                    current_section = sec_match.group(1)
                    continue
                
                val_match = re.match(r'^(\w+)\s*=\s*"([^"]+)"', line)
                if val_match:
                    key, val = val_match.groups()
                    colors[f"{current_section}.{key}"] = val
    except Exception as e:
        pass
    return colors

alacritty_theme_path = "~/.config/omarchy/current/theme/alacritty.toml"
sys_colors = load_alacritty_colors(alacritty_theme_path)

theme_colors = {
    "artist": sys_colors.get("colors.normal.magenta", "#F5C2E7"),
    "song": sys_colors.get("colors.normal.blue", "#89B4FA"),
    "lyrics": sys_colors.get("colors.bright.magenta", "#CBA6F7"),
    "status_playing": sys_colors.get("colors.normal.green", "#A6E3A1"),
    "status_stopped": sys_colors.get("colors.normal.red", "#F9E2AF"),
    "line": sys_colors.get("colors.bright.black", "#cdd6f4"),
    "volume": sys_colors.get("colors.normal.yellow", "#FFD700"),
    "spotify_header": sys_colors.get("colors.normal.green", "#a6d189"),
    "album": sys_colors.get("colors.normal.yellow", "#F9E2AF")
}
spotify_icon = ""
icon_color = sys_colors.get("colors.normal.green", "#8FCB9B")

def get(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except: return ""

def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if text else ""

def strip_html(s):
    return re.sub(r"<.*?>", "", s)

def center_text(text, width):
    temp = re.sub(r"[^\w\s<>/]", "XX", strip_html(text))
    pad = max((width - len(temp)) // 2, 0)
    return " " * pad + text

def parse_lrc(lrc_text):
    parsed = []
    for line in lrc_text.split('\n'):
        match = re.match(r'\[(\d+):(\d+(?:\.\d+)?)\](.*)', line)
        if match:
            m, s, txt = match.groups()
            ts = int(m) * 60 + float(s)
            if txt.strip(): parsed.append((ts, txt.strip()))
    return parsed

def fetch_lyrics(title, artist):
    if not title: return []
    clean_title = re.sub(r'\(.*?\)|\[.*?\]|-.*', '', title).strip()
    query = urllib.parse.quote(f"{clean_title} {artist}")
    url = f"https://lrclib.net/api/search?q={query}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WaybarLyrics/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            results = data if isinstance(data, list) else [data]
            for res in results:
                if res.get('syncedLyrics'): return parse_lrc(res['syncedLyrics'])
    except: pass
    return []

current_id = ""
current_lyrics = []

while True:
    status = get("playerctl --player=spotify status")
    status_low = status.lower()

    if status_low not in ["playing", "paused"]:
        print(json.dumps({"text": f"<span foreground='{icon_color}'>{spotify_icon}</span>\u00A0\u00A0Spotify"}), flush=True)
        time.sleep(3)
        continue

    title_raw = get("playerctl --player=spotify metadata title")
    artist_raw = get("playerctl --player=spotify metadata artist")
    album_raw = get("playerctl --player=spotify metadata album")
    vol_raw = get("playerctl --player=spotify volume") or "0"
    pos_raw = get("playerctl --player=spotify position") or "0"
    len_raw = get("playerctl --player=spotify metadata mpris:length") or "0"
    
    try:
        length_sec = int(len_raw) // 1000000
        pos_sec = int(float(pos_raw))
        length_fmt = f"{length_sec // 60}:{length_sec % 60:02d}"
        pos_fmt = f"{pos_sec // 60}:{pos_sec % 60:02d}"
    except:
        length_fmt, pos_fmt, length_sec, pos_sec = "0:00", "0:00", 0, 0

    if f"{title_raw}{artist_raw}" != current_id:
        current_id = f"{title_raw}{artist_raw}"
        current_lyrics = fetch_lyrics(title_raw, artist_raw)

    active_lyric = "🎶"
    for ts, txt in current_lyrics:
        if pos_sec >= ts: active_lyric = txt
        else: break

    status_glyph = "▶" if status_low == "playing" else "⏸"
    status_color = theme_colors['status_playing'] if status_low == "playing" else theme_colors['status_stopped']
    row_emojis = ["🎵", "👤", "💿", "⏱️"]
    volume_text = f"🔊 Volume: {int(float(vol_raw)*100)}%"
    
    all_lengths = [len(title_raw), len(artist_raw), len(album_raw), len(f"{pos_fmt} / {length_fmt}"), 25]
    line_width = max(all_lengths) + 6

    header_line = center_text(f"<span foreground='{theme_colors['spotify_header']}'>{spotify_icon} Spotify</span> "
                              f"<span foreground='{status_color}'>{status_glyph} {status.capitalize()}</span>", line_width)
    separator = f"<span foreground='{theme_colors['line']}'>{'─'*line_width}</span>"
    
    tooltip = "\n".join([
        header_line,
        separator,
        f"{row_emojis[0]} <span foreground='{theme_colors['song']}'>{escape(title_raw)}</span>",
        f"{row_emojis[1]} <span foreground='{theme_colors['artist']}'>{escape(artist_raw)}</span>",
        f"{row_emojis[2]} <span foreground='{theme_colors['album']}'>{escape(album_raw)}</span>",
        f"{row_emojis[3]} <span foreground='white'>{pos_fmt} / {length_fmt}</span>",
        separator,
        center_text(f"<span foreground='{theme_colors['volume']}'>{volume_text}</span>", line_width)
    ])

    prefix = f"<span foreground='{icon_color}'>{spotify_icon}</span>\u00A0\u00A0"
    bar_text = (f"{prefix}<span foreground='{theme_colors['artist']}'>{escape(artist_raw)}</span>"
                f"<span foreground='{theme_colors['line']}'> - </span>"
                f"<span foreground='{theme_colors['song']}'><i>{escape(title_raw)}</i></span>"
                f"<span foreground='{theme_colors['line']}'> | </span>"
                f"<span foreground='{theme_colors['lyrics']}'>{escape(active_lyric)}</span>")

    print(json.dumps({
        "text": bar_text,
        "tooltip": tooltip,
        "markup": "pango",
        "class": status_low
    }), flush=True)

    time.sleep(0.8)
