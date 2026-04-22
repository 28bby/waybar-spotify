# Waybar Spotify with Synced Lyrics 🎵

A clean, responsive, and highly customizable custom module for [Waybar](https://github.com/Alexays/Waybar) that displays the currently playing Spotify track, artist, and **real-time synced lyrics**. 

It uses `playerctl` to fetch local metadata and the [LRCLIB API](https://lrclib.net/) to fetch and sync lyrics dynamically without requiring any API keys or tokens.

## ✨ Features
- **Real-time Synced Lyrics:** Lyrics update line-by-line as the song plays.
- **Smart Fallback:** If synced lyrics aren't found, it gracefully falls back to a minimal music icon.
- **Full Playback Controls:** Click to play/pause, right-click for next, middle-click for previous.
- **Dynamic Tooltip:** Hover to see a beautifully formatted tooltip with song details, album, and current playback time.
- **Zero Dependencies:** Uses standard Python libraries (no `requests` installation needed).

## 📦 Prerequisites

Make sure you have the following installed on your system:
- `python3`
- `playerctl` (Usually available in your distro's repositories)
- Spotify (Linux desktop app)

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
    "on-click": "playerctl --player=spotify play-pause",
    "on-click-right": "playerctl --player=spotify next",
    "on-click-middle": "playerctl --player=spotify previous",
    "smooth-scrolling-threshold": 10, // Optional: prevents accidental scrolls
    "max-length": 80 // Highly recommended to prevent bar breakage on long lyric lines
}
```

Don't forget to add "custom/spotify" to your modules-left, modules-center, or modules-right array at the top of your config.
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
If you want to change the text colors of the artist, song, or lyrics, you can easily do so by editing the colors dictionary at the top of the spotify.py script:
```bash
colors = {
    "artist": "#F5C2E7",  // Pink
    "song": "#89B4FA",    // Blue
    "lyrics": "#CBA6F7",  // Purple
    "header": "#a6d189",  // Green
    "album": "#F9E2AF",   // Yellow
    "vol": "#FFD700"      // Gold
}
```
## 🤝 Acknowledgments
Lyrics provided by the excellent [LRCLIB](https://lrclib.net/) project.
