# Waybar Spotify with Synced Lyrics 🎵

A clean, responsive, and highly customizable custom module for [Waybar](https://github.com/Alexays/Waybar) that displays the currently playing track, artist, and real-time synced lyrics for both Spotify and cliamp. 

It uses `playerctl` to fetch local metadata, automatically detects the active player, dynamically changes its icon, and uses the [LRCLIB API](https://lrclib.net/) to fetch and sync lyrics without requiring any API keys or tokens.

## ✨ Features
- **Multi-Player Support:** Automatically detects whether you are using Spotify or cliamp (prioritizing Spotify if both are open) and changes the display name and icon accordingly.
- **Real-time Synced Lyrics:** Lyrics update line-by-line as the song plays.
- **Robust Metadata Handling:** Specifically designed to handle terminal music players (like cliamp). It safely strips hidden ANSI color codes and provides clean fallbacks if the player misses some metadata (like album or duration) to prevent Waybar from crashing.
- **Smart Fallback:** If synced lyrics aren't found, or if no music is playing, it gracefully falls back to a minimal music icon.
- **Full Playback Controls:** Click to play/pause, right-click for next, middle-click for previous (works for both players!).
- **Dynamic Tooltip:** Hover to see a beautifully formatted tooltip with song details, album, and current playback time.
- **Zero Dependencies:** Uses standard Python libraries (no `requests` installation needed).
## 📦 Prerequisites

Make sure you have the following installed on your system:
- `python3`
- `playerctl` (Usually available in your distro's repositories)
- Spotify (Linux desktop app) and/or `cliamp`

## 🚀 Installation

1. Download the `spotify.py` script and place it in your Waybar scripts folder (create it if it doesn't exist):
   ```bash
   mkdir -p ~/.config/waybar/scripts
   # Move the downloaded file here
   ```
2. Make the script executable:
   ```bash
   chmod +x ~/.config/waybar/scripts/spotify.py
   ```
## ⚙️ Configuration
1. Waybar Config (config.jsonc)
Add the custom module to your Waybar configuration file. The mouse click actions are handled directly by Waybar for maximum reliability.
```bash
"custom/spotify": {
    "exec": "python3 ~/.config/waybar/scripts/spotify.py",
    "return-type": "json",
    "format": "{}",
    "on-click": "playerctl --player=spotify,cliamp play-pause",
    "on-click-right": "playerctl --player=spotify,cliamp next",
    "on-click-middle": "playerctl --player=spotify,cliamp previous",
    "smooth-scrolling-threshold": 10, // Optional: prevents accidental scrolls
    "max-length": 80 // Highly recommended to prevent bar breakage on long lyric lines
}
```

Don't forget to add `"custom/spotify"` to your `modules-left`, `modules-center`, or `modules-right` array at the top of your config.
2. Styling (style.css)
The script automatically tries to read your existing Waybar style.css to match your system colors (specifically looking for a @define-color line variable).

If you want to style the module container itself, you can add this to your style.css:
```bash
#custom-spotify {
    padding: 0 10px;
    font-family: "JetBrainsMono Nerd Font", "Roboto", sans-serif;
}
```
## 🎨 Modifying Colors
This script is designed to seamlessly integrate with your environment. It automatically reads your terminal colors from your Alacritty configuration located at ~/.config/omarchy/current/theme/alacritty.toml.
- Artist: Uses colors.normal.magenta
- Song: Uses colors.normal.blue
- Lyrics: Uses colors.bright.magenta
- Icons/Header: Uses colors.normal.green
- Separators: Uses colors.bright.black
Don't use Alacritty? No problem! If the script cannot find the file, it will gracefully fall back to a beautifully curated default color palette.

You can also change the path to your own configuration file by editing the alacritty_theme_path variable at the top of spotify.py.
## 🤝 Acknowledgments
Lyrics provided by the excellent [LRCLIB](https://lrclib.net/) project.
