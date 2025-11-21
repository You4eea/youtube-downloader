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
    
    print("[OK] All required files found")
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Check for optional ffmpeg.exe and DLLs
    ffmpeg_dlls = []
    if os.path.exists("ffmpeg.exe"):
        print("[OK] ffmpeg.exe found - will be bundled")
        # Check for required DLLs in the ffmpeg bin folder
        ffmpeg_bin_path = "ffmpeg-master-latest-win64-gpl-shared-v7.1.1/bin"
        required_dlls = [
            "avcodec-62.dll",
            "avformat-62.dll",
            "avutil-60.dll",
            "avfilter-11.dll",
            "avdevice-62.dll",
            "swscale-9.dll",
            "swresample-6.dll"
        ]
        
        for dll in required_dlls:
            dll_path = os.path.join(ffmpeg_bin_path, dll)
            if os.path.exists(dll_path):
                ffmpeg_dlls.append(dll_path)
                print(f"[OK] {dll} found - will be bundled")
            else:
                print(f"[WARN] {dll} not found in {ffmpeg_bin_path}")
    else:
        print("[INFO] ffmpeg.exe not found - will not be bundled (optional)")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name", "YouTube-Downloader",  # Output name
        "--add-binary", "yt-dlp.exe;.", # Bundle yt-dlp.exe
        "--clean",                      # Clean PyInstaller cache
        "youtube-downloader.py"
    ]
    
    # Add ffmpeg.exe and all DLLs if they exist
    if os.path.exists("ffmpeg.exe"):
        cmd.insert(-1, "--add-binary")
        cmd.insert(-1, "ffmpeg.exe;.")
        
        # Add all ffmpeg DLLs
        for dll_path in ffmpeg_dlls:
            dll_name = os.path.basename(dll_path)
            cmd.insert(-1, "--add-binary")
            cmd.insert(-1, f"{dll_path};.")
    
    print("\nBuilding executable...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n[SUCCESS] Build successful!")
        print(f"\nExecutable location: dist/YouTube-Downloader.exe")
        print(f"File size: ~80-140MB (depending on whether ffmpeg is included)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed with error: {e}")
        return False
    except FileNotFoundError:
        print("\n[ERROR] PyInstaller not found!")
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

