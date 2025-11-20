"""
YouTube Downloader GUI
======================

Name: youtube-downloader.py
Version: 1.0.0
Description: A user-friendly GUI application for downloading YouTube videos using yt-dlp.
             Features include progress tracking, file location management, and automatic
             video information display.

Requirements:
    - Python 3.6 or higher
    - tkinter (usually included with Python)
    - yt-dlp.exe (must be in the same directory as this script)
    - ffmpeg (optional, but recommended for best quality video/audio merging)

Author: You4eea
License: Open Source

Usage:
    python youtube-downloader.py

Features:
    - Simple GUI interface for YouTube video downloads
    - Real-time download progress tracking
    - Custom save location selection
    - Automatic video title and filename detection
    - Clickable folder icon to open download location
    - "Stand by - finishing up..." message during post-processing
    - Success message with video details

"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import re
import sys

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("800x550")
        self.root.resizable(True, True)
        self.root.minsize(800, 550)
        
        # Variables
        self.download_process = None
        self.is_downloading = False
        self.save_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.downloaded_file_path = None
        self.video_title = None
        self.downloaded_filename = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="YouTube Video Downloader", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # URL Input Frame
        url_frame = tk.Frame(self.root)
        url_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(url_frame, text="YouTube URL:", font=("Arial", 10)).pack(anchor="w")
        self.url_entry = tk.Entry(url_frame, font=("Arial", 10), width=50)
        self.url_entry.pack(fill="x", pady=(5, 0))
        
        # Save Location Frame
        save_frame = tk.Frame(self.root)
        save_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(save_frame, text="Save Location:", font=("Arial", 10)).pack(anchor="w")
        location_frame = tk.Frame(save_frame)
        location_frame.pack(fill="x", pady=(5, 0))
        
        self.path_entry = tk.Entry(location_frame, textvariable=self.save_path, font=("Arial", 10), width=40)
        self.path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(
            location_frame, 
            text="Browse", 
            command=self.browse_folder,
            font=("Arial", 9),
            width=10
        )
        browse_btn.pack(side="right", padx=(5, 0))
        
        # Progress Bar Frame
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=10, padx=20, fill="x")
        
        self.progress_label = tk.Label(
            progress_frame, 
            text="Ready to download", 
            font=("Arial", 9),
            fg="gray"
        )
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='determinate',
            length=760
        )
        self.progress_bar.pack(fill="x", pady=(5, 0))
        
        # Button Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.download_btn = tk.Button(
            button_frame,
            text="Download",
            command=self.start_download,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2
        )
        self.download_btn.pack(side="left", padx=10)
        
        self.cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_download,
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            width=15,
            height=2,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=10)
        
        # Success Message Frame (initially hidden)
        self.success_frame = tk.Frame(self.root, bg="#e8f5e9", relief=tk.RAISED, bd=2)
        self.success_frame.pack(pady=20, padx=20, fill="x", after=button_frame)
        self.success_frame.pack_forget()  # Hide initially
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_path.get())
        if folder:
            self.save_path.set(folder)
    
    def validate_url(self, url):
        """Basic URL validation"""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
        ]
        for pattern in youtube_patterns:
            if re.search(pattern, url):
                return True
        return False
    
    def parse_progress(self, line):
        """Parse yt-dlp progress output"""
        # Look for percentage in the output
        # yt-dlp outputs like: [download]  45.2% of   50.00MiB at  5.00MiB/s ETA 00:01
        match = re.search(r'(\d+\.?\d*)%', line)
        if match:
            try:
                return float(match.group(1))
            except:
                return None
        
        # Also check for [download] lines with file size info
        if '[download]' in line.lower():
            # Try to extract any percentage
            match = re.search(r'(\d+\.?\d*)%', line)
            if match:
                try:
                    return float(match.group(1))
                except:
                    return None
        return None
    
    def parse_video_info(self, line):
        """Parse video title and filename from yt-dlp output"""
        # yt-dlp outputs: [download] Destination: filename.ext
        if '[download]' in line and 'Destination:' in line:
            match = re.search(r'Destination:\s*(.+)', line)
            if match:
                full_path = match.group(1).strip()
                if os.path.isabs(full_path):
                    self.downloaded_file_path = full_path
                else:
                    self.downloaded_file_path = os.path.join(self.save_path.get(), full_path)
                self.downloaded_filename = os.path.basename(full_path)
        
        # yt-dlp outputs: [download] filename.ext has already been downloaded
        if '[download]' in line and 'has already been downloaded' in line:
            match = re.search(r'\[download\]\s*(.+?)\s+has already been downloaded', line)
            if match:
                filename = match.group(1).strip()
                self.downloaded_file_path = os.path.join(self.save_path.get(), filename)
                self.downloaded_filename = filename
        
        # yt-dlp outputs: [Merger] Merging formats into "filename.ext"
        if '[Merger]' in line or '[ExtractAudio]' in line:
            match = re.search(r'into\s+"(.+)"', line)
            if match:
                full_path = match.group(1).strip()
                if os.path.isabs(full_path):
                    self.downloaded_file_path = full_path
                else:
                    self.downloaded_file_path = os.path.join(self.save_path.get(), full_path)
                self.downloaded_filename = os.path.basename(full_path)
    
    def download_video(self):
        """Download video in a separate thread"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            self.reset_ui()
            return
        
        if not self.validate_url(url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            self.reset_ui()
            return
        
        save_dir = self.save_path.get()
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create save directory: {str(e)}")
                self.reset_ui()
                return
        
        # Get path to yt-dlp.exe
        script_dir = os.path.dirname(os.path.abspath(__file__))
        yt_dlp_path = os.path.join(script_dir, "yt-dlp.exe")
        
        if not os.path.exists(yt_dlp_path):
            messagebox.showerror("Error", f"yt-dlp.exe not found at: {yt_dlp_path}")
            self.reset_ui()
            return
        
        # Get video title first
        try:
            title_cmd = [yt_dlp_path, url, "--get-title", "--no-warnings"]
            title_result = subprocess.run(
                title_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                timeout=10
            )
            if title_result.returncode == 0 and title_result.stdout.strip():
                self.video_title = title_result.stdout.strip()
        except:
            pass  # If we can't get title, we'll try to parse it from download output
        
        # Prepare command
        output_template = os.path.join(save_dir, "%(title)s.%(ext)s")
        cmd = [
            yt_dlp_path,
            url,
            "-o", output_template,
            "--newline",  # Force newline output for progress parsing
            "--progress",  # Show progress
        ]
        
        try:
            self.download_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            progress_reached_100 = False
            # Read output line by line
            for line in iter(self.download_process.stdout.readline, ''):
                if not self.is_downloading:
                    break
                
                line = line.strip()
                if line:
                    # Parse video info (title, filename)
                    self.parse_video_info(line)
                    
                    # Update progress bar
                    progress = self.parse_progress(line)
                    if progress is not None:
                        self.progress_bar['value'] = progress
                        if progress >= 100:
                            progress_reached_100 = True
                            # Check if process is still running (merging/processing)
                            if self.download_process.poll() is None:
                                self.progress_label.config(text="Stand by - finishing up...", fg="orange")
                            else:
                                self.progress_label.config(text=f"Downloading... {progress:.1f}%")
                        else:
                            self.progress_label.config(text=f"Downloading... {progress:.1f}%")
                    else:
                        # If we hit 100% and process is still running, show finishing message
                        if progress_reached_100 and self.download_process.poll() is None:
                            if '[Merger]' in line or '[ExtractAudio]' in line or 'Merging' in line:
                                self.progress_label.config(text="Stand by - finishing up...", fg="orange")
                            elif '[download]' not in line.lower():
                                self.progress_label.config(text="Stand by - finishing up...", fg="orange")
                        else:
                            # Update label with current status
                            if '[download]' in line.lower():
                                self.progress_label.config(text=line[:60] + "..." if len(line) > 60 else line)
                    
                    self.root.update_idletasks()
            
            # Wait for process to complete
            self.download_process.wait()
            
            if self.is_downloading:
                if self.download_process.returncode == 0:
                    self.progress_bar['value'] = 100
                    self.progress_label.config(text="Download completed successfully!", fg="green")
                    
                    # If we don't have the file path yet, try to find it
                    if not self.downloaded_file_path:
                        # Try to find the most recently created file in the save directory
                        try:
                            files = [os.path.join(save_dir, f) for f in os.listdir(save_dir) 
                                    if os.path.isfile(os.path.join(save_dir, f))]
                            if files:
                                # Get the most recently modified file
                                self.downloaded_file_path = max(files, key=os.path.getmtime)
                                self.downloaded_filename = os.path.basename(self.downloaded_file_path)
                                # If we don't have a title yet, try to extract it from filename (remove extension)
                                if not self.video_title and self.downloaded_filename:
                                    self.video_title = os.path.splitext(self.downloaded_filename)[0]
                        except:
                            pass
                    
                    # Reset UI state but keep success message visible
                    self.is_downloading = False
                    self.download_process = None
                    self.download_btn.config(state="normal")
                    self.cancel_btn.config(state="disabled")
                    
                    # Show success message in the UI (on main thread)
                    self.root.after(0, self.show_success_message)
                else:
                    self.progress_label.config(text="Download failed", fg="red")
                    messagebox.showerror("Error", "Download failed. Please check the URL and try again.")
                    self.reset_ui()
            
        except Exception as e:
            if self.is_downloading:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                self.progress_label.config(text="Error occurred", fg="red")
                self.reset_ui()
            else:
                self.reset_ui()
    
    def start_download(self):
        """Start download in a separate thread"""
        if self.is_downloading:
            return
        
        # Hide success frame if visible
        self.success_frame.pack_forget()
        
        # Reset download info
        self.downloaded_file_path = None
        self.video_title = None
        self.downloaded_filename = None
        
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting download...", fg="blue")
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_video, daemon=True)
        thread.start()
    
    def cancel_download(self):
        """Cancel the current download"""
        if self.download_process and self.is_downloading:
            self.download_process.terminate()
            self.is_downloading = False
            self.progress_label.config(text="Download cancelled", fg="orange")
            messagebox.showinfo("Cancelled", "Download has been cancelled.")
            self.reset_ui()
    
    def show_success_message(self):
        """Display success message with video details"""
        # Clear any existing widgets in success frame
        for widget in self.success_frame.winfo_children():
            widget.destroy()
        
        # Success title
        success_title = tk.Label(
            self.success_frame,
            text="Your video downloaded successfully!",
            font=("Arial", 12, "bold"),
            bg="#e8f5e9",
            fg="#2e7d32"
        )
        success_title.pack(anchor="w", pady=(10, 5), padx=10)
        
        # Details frame
        details_frame = tk.Frame(self.success_frame, bg="#e8f5e9")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Title
        if self.video_title:
            title_label = tk.Label(
                details_frame,
                text=f"Title: {self.video_title}",
                font=("Arial", 10),
                bg="#e8f5e9",
                anchor="w"
            )
            title_label.pack(anchor="w", pady=2)
        else:
            title_label = tk.Label(
                details_frame,
                text="Title: (Not available)",
                font=("Arial", 10),
                bg="#e8f5e9",
                anchor="w",
                fg="gray"
            )
            title_label.pack(anchor="w", pady=2)
        
        # Filename
        if self.downloaded_filename:
            filename_label = tk.Label(
                details_frame,
                text=f"Filename: {self.downloaded_filename}",
                font=("Arial", 10),
                bg="#e8f5e9",
                anchor="w"
            )
            filename_label.pack(anchor="w", pady=2)
        else:
            filename_label = tk.Label(
                details_frame,
                text="Filename: (Not available)",
                font=("Arial", 10),
                bg="#e8f5e9",
                anchor="w",
                fg="gray"
            )
            filename_label.pack(anchor="w", pady=2)
        
        # Location with clickable folder icon
        location_row = tk.Frame(details_frame, bg="#e8f5e9")
        location_row.pack(anchor="w", pady=2, fill="x")
        
        if self.downloaded_file_path:
            location_path = os.path.dirname(self.downloaded_file_path)
            
            # Clickable folder icon/link (to the left of "Location:")
            folder_link = tk.Label(
                location_row,
                text="📁",
                font=("Arial", 12),
                bg="#e8f5e9",
                fg="#1976d2",
                cursor="hand2"
            )
            folder_link.pack(side="left", padx=(0, 5))
            folder_link.bind("<Button-1>", lambda e, p=location_path: self.open_file_location(p))
            folder_link.bind("<Enter>", lambda e: folder_link.config(fg="#0d47a1"))
            folder_link.bind("<Leave>", lambda e: folder_link.config(fg="#1976d2"))
            
            location_label = tk.Label(
                location_row,
                text=f"Location: {location_path}",
                font=("Arial", 10),
                bg="#e8f5e9",
                anchor="w",
                wraplength=650
            )
            location_label.pack(side="left", fill="x", expand=True)
        else:
            location_label = tk.Label(
                location_row,
                text=f"Location: {self.save_path.get()}",
                font=("Arial", 10),
                bg="#e8f5e9",
                anchor="w",
                wraplength=700,
                fg="gray"
            )
            location_label.pack(side="left", fill="x", expand=True)
        
        # Show the success frame
        self.success_frame.pack(pady=20, padx=20, fill="x")
        self.root.update_idletasks()
    
    def open_file_location(self, path):
        """Open the file location in Windows File Explorer"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            else:
                # For other platforms
                subprocess.run(['xdg-open', path] if sys.platform == "linux" else ['open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file location: {str(e)}")
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.is_downloading = False
        self.download_process = None
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        if self.progress_bar['value'] != 100:
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready to download", fg="gray")
        
        # Hide success frame
        self.success_frame.pack_forget()
        
        # Reset download info
        self.downloaded_file_path = None
        self.video_title = None
        self.downloaded_filename = None

def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()

