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
