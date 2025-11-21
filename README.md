# YouTube Downloader GUI

**Version:** 1.0.0  
**Author:** You4eea  
**License:** Open Source

## Description

A user-friendly GUI application for downloading YouTube videos using yt-dlp. Features include real-time progress tracking, custom save location selection, automatic video information display, and a clickable folder icon to quickly open the download location.

## Features

- Simple, intuitive GUI interface
- Real-time download progress tracking with percentage display
- "Stand by - finishing up..." message during post-processing
- Custom save location selection with browse button
- Automatic video title and filename detection
- Success message with video details (Title, Filename, Location)
- Clickable folder icon (📁) to open download location in Windows File Explorer
- Cancel button to stop downloads if needed

## Requirements

### Python
- Python 3.6 or higher
- tkinter (usually included with Python installation)

### External Dependencies
- **yt-dlp.exe** - Must be in the same directory as `youtube-downloader.py`
- **ffmpeg** (optional, but recommended) - For best quality video/audio merging

## Installation

### 1. Install yt-dlp

**Windows:**
- Use Chocolatey: `choco install yt-dlp`
- Use Scoop: `scoop install yt-dlp`
- Or download the executable from: https://github.com/yt-dlp/yt-dlp/releases
- Place `yt-dlp.exe` in the same folder as `youtube-downloader.py`

**Linux:**
```bash
sudo wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp && sudo chmod a+rx /usr/local/bin/yt-dlp
```
Or use your package manager (apt, dnf, pacman, etc.)

### 2. Install ffmpeg (Recommended)

**Windows:**
- Use Chocolatey: `choco install ffmpeg`
- Or download from: https://ffmpeg.org

**Linux:**
- Most Linux distros: already in repos
- Check installation: `ffmpeg -version`
- Find path: `where ffmpeg` (Windows) or `which ffmpeg` (Linux)

## Usage

### Running the Application

```bash
python youtube-downloader.py
```

### How to Use

1. Enter a YouTube URL in the "YouTube URL:" field
2. (Optional) Click "Browse" to select a custom save location (defaults to Downloads folder)
3. Click the green "Download" button
4. Monitor progress in the progress bar
5. When complete, view video details in the success message
6. Click the folder icon (📁) next to "Location:" to open the file location

## yt-dlp Command Reference

For advanced users who want to use yt-dlp directly from the command line:

### Basic Commands

```bash
# Best quality single file (auto merges video + audio)
yt-dlp "https://www.youtube.com/watch?v=xxxxxx"

# Just the audio (Opus → convert to mp3)
yt-dlp -x --audio-format mp3 "https://youtu.be/xxxxxx"

# Specific format (e.g., 1080p + best audio)
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best" URL

# Download a whole playlist
yt-dlp -i --yes-playlist "https://www.youtube.com/playlist?list=xxxx"

# Download with custom filename template
yt-dlp -o "%(title)s [%(id)s].%(ext)s" URL

# Subtitles (English, auto-generated or manual)
yt-dlp --write-subs --sub-lang en URL
```

### Keep yt-dlp Updated

yt-dlp is open-source, has zero ads/malware, and is updated almost daily when YouTube tries new tricks. Keep it updated:

```bash
yt-dlp -U
```

## Notes

- The application automatically detects the video title before downloading
- File paths are automatically detected from yt-dlp output
- The success message appears only after the video is fully processed and ready
- The folder icon provides quick access to the downloaded file location
