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

player_icons = {
    "spotify": "", 
    "cliamp": ""
}

player_names = {
    "spotify": "Spotify",
    "cliamp": "Cliamp"
}

icon_color = sys_colors.get("colors.normal.green", "#8FCB9B")

def clean_string(s):
    if not s: 
        return ""
    # Limpiar códigos ANSI que suelen escupir los reproductores de consola
    s = re.sub(r'\x1b\[[0-9;]*m', '', s)
    return ''.join(c for c in s if c.isprintable() or c in ['\n', '\t']).strip()

def get(cmd):
    try:
        res = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        return clean_string(res)
    except: 
        return ""

def escape(text):
    if not text: return ""
    # Escape estricto para Pango (Waybar)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Evita que el formateador interno de Waybar crashee si hay llaves en el título
    text = text.replace("{", "{{").replace("}", "}}")
    return text

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
    if not title or title in ["Desconocido"]: return []
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
    active_player = None
    status_low = "stopped"

    for player in ["spotify", "cliamp"]:
        status = get(f"playerctl --player={player} status").lower()
        if status in ["playing", "paused"]:
            active_player = player
            status_low = status
            break

    if not active_player:
        print(json.dumps({"text": f"<span foreground='{icon_color}'></span>\u00A0\u00A0No hay música"}), flush=True)
        time.sleep(3)
        continue

    # NUEVO SISTEMA: Hacemos una sola petición general en lugar de sobrecargar el reproductor
    raw_meta = get(f"playerctl --player={active_player} metadata")
    meta_dict = {}
    if raw_meta:
        for line in raw_meta.split('\n'):
            parts = line.split(maxsplit=2)
            if len(parts) >= 3:
                prop = parts[1].lower()
                val = parts[2].strip()
                meta_dict[prop] = val

    # Extraemos los datos del diccionario (con fallbacks garantizados)
    title_raw = meta_dict.get("xesam:title", meta_dict.get("title", "Desconocido"))
    artist_raw = meta_dict.get("xesam:artist", meta_dict.get("artist", "Artista desconocido"))
    album_raw = meta_dict.get("xesam:album", meta_dict.get("album", "Álbum desconocido"))
    len_raw = meta_dict.get("mpris:length", meta_dict.get("length", "0"))
    
    # Volumen y posición van en peticiones separadas porque no son "metadata" estática
    vol_raw = get(f"playerctl --player={active_player} volume")
    pos_raw = get(f"playerctl --player={active_player} position")

    # Cálculos matemáticos protegidos contra fallos (ej. si el reproductor no reporta tiempo)
    try:
        length_sec = int(len_raw) // 1000000 if len_raw and len_raw != "0" else 0
        length_fmt = f"{length_sec // 60}:{length_sec % 60:02d}"
    except:
        length_sec, length_fmt = 0, "0:00"

    try:
        pos_sec = int(float(pos_raw)) if pos_raw else 0
        pos_fmt = f"{pos_sec // 60}:{pos_sec % 60:02d}"
    except:
        pos_sec, pos_fmt = 0, "0:00"

    try:
        vol_float = float(vol_raw) if vol_raw else 0.0
        vol_percent = int(vol_float) if vol_float > 1.0 else int(vol_float * 100)
    except:
        vol_percent = 0

    if f"{title_raw}{artist_raw}" != current_id:
        current_id = f"{title_raw}{artist_raw}"
        current_lyrics = fetch_lyrics(title_raw, artist_raw)

    active_lyric = "🎶"
    for ts, txt in current_lyrics:
        if pos_sec >= ts: active_lyric = txt
        else: break

    current_icon = player_icons.get(active_player, "")
    current_name = player_names.get(active_player, active_player.capitalize())

    status_glyph = "▶" if status_low == "playing" else "⏸"
    status_color = theme_colors['status_playing'] if status_low == "playing" else theme_colors['status_stopped']
    row_emojis = ["🎵", "👤", "💿", "⏱️"]
    volume_text = f"🔊 Volume: {vol_percent}%"
    
    all_lengths = [len(title_raw), len(artist_raw), len(album_raw), len(f"{pos_fmt} / {length_fmt}"), 25]
    line_width = max(all_lengths) + 6

    header_line = center_text(f"<span foreground='{theme_colors['spotify_header']}'>{current_icon} {current_name}</span> "
                              f"<span foreground='{status_color}'>{status_glyph} {status_low.capitalize()}</span>", line_width)
    separator = f"<span foreground='{theme_colors['line']}'>{'─'*line_width}</span>"
    
    # Tooltip formateado y purgado de caracteres conflictivos
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

    prefix = f"<span foreground='{icon_color}'>{current_icon}</span>\u00A0\u00A0"
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
