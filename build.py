"""
PyInstaller Build Script for YouTube Downloader
================================================

This script builds a standalone executable using PyInstaller.

Requirements:
    - PyInstaller: pip install pyinstaller
    - yt-dlp.exe must be in the same directory
    - ffmpeg.exe (optional) - place in same directory if you want to bundle it

Usage:
    python build.py

Output:
    - dist/YouTube-Downloader.exe (single file executable)
"""

import subprocess
import sys
import os

def check_files():
    """Check if required files exist"""
    required = ["youtube-downloader.py", "yt-dlp.exe"]
    missing = []
    
    for file in required:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("ERROR: Missing required files:")
        for file in missing:
            print(f"  - {file}")
        return False
    
    print("✓ All required files found")
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Check for optional ffmpeg.exe
    ffmpeg_binary = ""
    if os.path.exists("ffmpeg.exe"):
        ffmpeg_binary = '--add-binary "ffmpeg.exe;."'
        print("✓ ffmpeg.exe found - will be bundled")
    else:
        print("⚠ ffmpeg.exe not found - will not be bundled (optional)")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name", "YouTube-Downloader",  # Output name
        "--add-binary", "yt-dlp.exe;.", # Bundle yt-dlp.exe
        "--clean",                      # Clean PyInstaller cache
        "youtube-downloader.py"
    ]
    
    # Add ffmpeg if it exists
    if ffmpeg_binary:
        cmd.insert(-1, "--add-binary")
        cmd.insert(-1, "ffmpeg.exe;.")
    
    print("\nBuilding executable...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✓ Build successful!")
        print(f"\nExecutable location: dist/YouTube-Downloader.exe")
        print(f"File size: ~80-140MB (depending on whether ffmpeg is included)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error: {e}")
        return False
    except FileNotFoundError:
        print("\n✗ ERROR: PyInstaller not found!")
        print("Please install it with: pip install pyinstaller")
        return False

def main():
    print("=" * 50)
    print("YouTube Downloader - PyInstaller Build Script")
    print("=" * 50)
    print()
    
    if not check_files():
        sys.exit(1)
    
    print()
    if build_executable():
        print("\n" + "=" * 50)
        print("Build complete! Check the 'dist' folder for your executable.")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("Build failed. Please check the errors above.")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()

