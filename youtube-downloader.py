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
    # Midnight Theme Colors
    BG_MAIN = "#050814"
    BG_CARD = "#0d1224"
    BG_CODE = "#050914"
    ACCENT = "#5ad0ff"
    ACCENT_STRONG = "#23a6ff"
    TEXT_MAIN = "#e4e9ff"
    TEXT_MUTED = "#8a90b2"
    BORDER_SUBTLE = "#1b2138"
    SUCCESS = "#35d399"
    DANGER = "#ff6b81"
    TEXT_DARK = "#02030a"
    
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("800x550")
        self.root.resizable(True, True)
        self.root.minsize(800, 550)
        self.root.configure(bg=self.BG_CARD)
        
        # Configure ttk styles for midnight theme
        self.setup_styles()
        
        # Variables
        self.download_process = None
        self.is_downloading = False
        self.save_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.downloaded_file_path = None
        self.video_title = None
        self.downloaded_filename = None
        
        # Create UI
        self.create_widgets()
    
    def setup_styles(self):
        """Configure ttk styles for midnight theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Progress bar style - deep maroon red fill, no border
        style.configure("Midnight.Horizontal.TProgressbar",
                       background="#8B0000",  # Deep maroon red
                       troughcolor=self.BG_CODE,
                       borderwidth=0,
                       relief='flat',
                       lightcolor="#8B0000",
                       darkcolor="#8B0000")
    
    def create_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle (pill shape) on canvas"""
        fill_color = kwargs.get('fill', '')
        outline_color = kwargs.get('outline', fill_color)
        
        # Draw the middle rectangle
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=fill_color, outline=fill_color, width=0)
        
        # Draw the left semicircle
        canvas.create_arc(x1, y1, x1 + 2*radius, y2, start=90, extent=180, fill=fill_color, outline=fill_color, width=0, style="pieslice")
        
        # Draw the right semicircle
        canvas.create_arc(x2 - 2*radius, y1, x2, y2, start=270, extent=180, fill=fill_color, outline=fill_color, width=0, style="pieslice")
    
    def create_rounded_button(self, parent, text, command, bg_color, hover_color, text_color, width=140, height=40, state="normal"):
        """Create a rounded button using Canvas (pill-shaped like HTML copy buttons)"""
        # Create canvas for rounded button
        canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=self.BG_CARD,
            highlightthickness=0,
            relief="flat",
            borderwidth=0
        )
        
        # Draw rounded rectangle (pill shape) - radius is half the height for full pill
        radius = height // 2
        
        # Draw the button background with rounded corners
        self.create_rounded_rect(canvas, 0, 0, width, height, radius, fill=bg_color, outline=bg_color)
        button_id = canvas.find_all()  # Get all shapes (the rounded rect parts)
        
        # Add text
        text_id = canvas.create_text(
            width // 2,
            height // 2,
            text=text,
            fill=text_color,
            font=("Segoe UI", 11, "bold")
        )
        
        # Store button state and properties
        canvas.button_bg = bg_color
        canvas.button_hover = hover_color
        canvas.button_text_color = text_color
        canvas.button_state = state
        canvas.button_command = command
        canvas.button_width = width
        canvas.button_height = height
        canvas.button_radius = radius
        
        # Update appearance based on state
        if state == "disabled":
            # Redraw with disabled colors
            canvas.delete("all")
            self.create_rounded_rect(canvas, 0, 0, width, height, radius, fill=self.BORDER_SUBTLE, outline=self.BORDER_SUBTLE)
            button_id = canvas.find_all()
            canvas.create_text(width // 2, height // 2, text=text, fill=self.TEXT_MUTED, font=("Segoe UI", 11, "bold"))
            canvas.button_bg = self.BORDER_SUBTLE
        
        # Click handler
        def on_click(event):
            if canvas.button_state == "normal" and canvas.button_command:
                canvas.button_command()
        
        # Hover handlers
        def on_enter(event):
            if canvas.button_state == "normal":
                # Redraw with hover color
                canvas.delete("all")
                self.create_rounded_rect(canvas, 0, 0, width, height, radius, fill=hover_color, outline=hover_color)
                canvas.create_text(width // 2, height // 2, text=text, fill=text_color, font=("Segoe UI", 11, "bold"))
                canvas.config(cursor="hand2")
        
        def on_leave(event):
            if canvas.button_state == "normal":
                # Redraw with normal color
                canvas.delete("all")
                self.create_rounded_rect(canvas, 0, 0, width, height, radius, fill=canvas.button_bg, outline=canvas.button_bg)
                canvas.create_text(width // 2, height // 2, text=text, fill=canvas.button_text_color, font=("Segoe UI", 11, "bold"))
            canvas.config(cursor="")
        
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        
        # Method to update button state
        def update_state(new_state):
            canvas.button_state = new_state
            canvas.delete("all")
            if new_state == "disabled":
                self.create_rounded_rect(canvas, 0, 0, width, height, radius, fill=self.BORDER_SUBTLE, outline=self.BORDER_SUBTLE)
                canvas.create_text(width // 2, height // 2, text=text, fill=self.TEXT_MUTED, font=("Segoe UI", 11, "bold"))
            else:
                self.create_rounded_rect(canvas, 0, 0, width, height, radius, fill=canvas.button_bg, outline=canvas.button_bg)
                canvas.create_text(width // 2, height // 2, text=text, fill=canvas.button_text_color, font=("Segoe UI", 11, "bold"))
        
        canvas.update_state = update_state
        
        return canvas
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # Running as script (not bundled)
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_path, relative_path)
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="You4eea's Youtube\nVideo Downloader", 
            font=("Segoe UI", 16, "bold"),
            bg=self.BG_CARD,
            fg=self.ACCENT,  # Button blue color
            justify="center"
        )
        title_label.pack(pady=10)
        
        # URL Input Frame
        url_frame = tk.Frame(self.root, bg=self.BG_CARD)
        url_frame.pack(pady=10, padx=20, fill="x")
        
        url_label = tk.Label(
            url_frame, 
            text="YouTube URL:", 
            font=("Segoe UI", 10),
            bg=self.BG_CARD,
            fg=self.TEXT_MAIN
        )
        url_label.pack(anchor="w")
        
        self.url_entry = tk.Entry(
            url_frame, 
            font=("Segoe UI", 10), 
            width=50,
            bg=self.BG_MAIN,
            fg=self.TEXT_MAIN,
            insertbackground=self.ACCENT,
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.BORDER_SUBTLE,
            highlightcolor=self.ACCENT
        )
        self.url_entry.pack(fill="x", pady=(5, 0))
        
        # Save Location Frame
        save_frame = tk.Frame(self.root, bg=self.BG_CARD)
        save_frame.pack(pady=10, padx=20, fill="x")
        
        save_label = tk.Label(
            save_frame, 
            text="Save Location:", 
            font=("Segoe UI", 10),
            bg=self.BG_CARD,
            fg=self.TEXT_MAIN
        )
        save_label.pack(anchor="w")
        
        location_frame = tk.Frame(save_frame, bg=self.BG_CARD)
        location_frame.pack(fill="x", pady=(5, 0))
        
        self.path_entry = tk.Entry(
            location_frame, 
            textvariable=self.save_path, 
            font=("Segoe UI", 10), 
            width=40,
            bg=self.BG_MAIN,
            fg=self.TEXT_MAIN,
            insertbackground=self.ACCENT,
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.BORDER_SUBTLE,
            highlightcolor=self.ACCENT
        )
        self.path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(
            location_frame, 
            text="Browse", 
            command=self.browse_folder,
            font=("Segoe UI", 9),
            width=10,
            bg=self.BG_MAIN,
            fg=self.ACCENT,
            activebackground=self.ACCENT,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.BORDER_SUBTLE,
            cursor="hand2"
        )
        browse_btn.pack(side="right", padx=(5, 0))
        
        # Browse button hover effects
        def browse_enter(e):
            browse_btn.config(bg=self.ACCENT, fg=self.TEXT_DARK, highlightbackground=self.ACCENT)
        def browse_leave(e):
            browse_btn.config(bg=self.BG_MAIN, fg=self.ACCENT, highlightbackground=self.BORDER_SUBTLE)
        browse_btn.bind("<Enter>", browse_enter)
        browse_btn.bind("<Leave>", browse_leave)
        
        # Progress Bar Frame
        progress_frame = tk.Frame(self.root, bg=self.BG_CARD)
        progress_frame.pack(pady=10, padx=20, fill="x")
        
        self.progress_label = tk.Label(
            progress_frame, 
            text="Ready to download", 
            font=("Segoe UI", 9),
            bg=self.BG_CARD,
            fg=self.TEXT_MUTED
        )
        self.progress_label.pack(anchor="w")
        
        # Progress bar (no border)
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='determinate',
            length=760,
            style="Midnight.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(5, 0))
        
        # Button Frame
        button_frame = tk.Frame(self.root, bg=self.BG_CARD)
        button_frame.pack(pady=20)
        
        # Create rounded buttons using Canvas
        self.download_btn = self.create_rounded_button(
            button_frame,
            text="Start Download",
            command=self.start_download,
            bg_color=self.ACCENT,
            hover_color=self.ACCENT_STRONG,
            text_color=self.TEXT_DARK,
            width=140,
            height=40
        )
        self.download_btn.pack(side="left", padx=10)
        
        self.cancel_btn = self.create_rounded_button(
            button_frame,
            text="Stop Download",
            command=self.cancel_download,
            bg_color=self.DANGER,
            hover_color="#e55a6f",
            text_color="white",
            width=140,
            height=40,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=10)
        
        # Success Message Frame (initially hidden)
        self.success_frame = tk.Frame(
            self.root, 
            bg=self.BG_MAIN, 
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.BORDER_SUBTLE
        )
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
        
        # Get path to yt-dlp.exe (works in both dev and PyInstaller bundled mode)
        yt_dlp_path = self.get_resource_path("yt-dlp.exe")
        
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
                                self.progress_label.config(text="Stand by - finishing up...", fg=self.DANGER)
                            else:
                                self.progress_label.config(text=f"Downloading... {progress:.1f}%", fg=self.ACCENT)
                        else:
                            self.progress_label.config(text=f"Downloading... {progress:.1f}%", fg=self.ACCENT)
                    else:
                        # If we hit 100% and process is still running, show finishing message
                        if progress_reached_100 and self.download_process.poll() is None:
                            if '[Merger]' in line or '[ExtractAudio]' in line or 'Merging' in line:
                                self.progress_label.config(text="Stand by - finishing up...", fg=self.DANGER)
                            elif '[download]' not in line.lower():
                                self.progress_label.config(text="Stand by - finishing up...", fg=self.DANGER)
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
                    self.progress_label.config(text="Download completed successfully!", fg=self.SUCCESS)
                    
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
                    self.progress_label.config(text="Download failed", fg=self.DANGER)
                    messagebox.showerror("Error", "Download failed. Please check the URL and try again.")
                    self.reset_ui()
            
        except Exception as e:
            if self.is_downloading:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                self.progress_label.config(text="Error occurred", fg=self.DANGER)
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
        self.download_btn.update_state("disabled")
        self.cancel_btn.update_state("normal")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting download...", fg=self.ACCENT)
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_video, daemon=True)
        thread.start()
    
    def cancel_download(self):
        """Cancel the current download"""
        if self.download_process and self.is_downloading:
            self.download_process.terminate()
            self.is_downloading = False
            self.progress_label.config(text="Download cancelled", fg=self.DANGER)
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
            font=("Segoe UI", 12, "bold"),
            bg=self.BG_MAIN,
            fg=self.ACCENT  # Same blue as buttons/border
        )
        success_title.pack(anchor="w", pady=(10, 5), padx=10)
        
        # Details frame
        details_frame = tk.Frame(self.success_frame, bg=self.BG_MAIN)
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Title
        if self.video_title:
            title_label = tk.Label(
                details_frame,
                text=f"Title: {self.video_title}",
                font=("Segoe UI", 10),
                bg=self.BG_MAIN,
                fg=self.TEXT_MAIN,
                anchor="w"
            )
            title_label.pack(anchor="w", pady=2)
        else:
            title_label = tk.Label(
                details_frame,
                text="Title: (Not available)",
                font=("Segoe UI", 10),
                bg=self.BG_MAIN,
                fg=self.TEXT_MUTED,
                anchor="w"
            )
            title_label.pack(anchor="w", pady=2)
        
        # Filename
        if self.downloaded_filename:
            filename_label = tk.Label(
                details_frame,
                text=f"Filename: {self.downloaded_filename}",
                font=("Segoe UI", 10),
                bg=self.BG_MAIN,
                fg=self.TEXT_MAIN,
                anchor="w"
            )
            filename_label.pack(anchor="w", pady=2)
        else:
            filename_label = tk.Label(
                details_frame,
                text="Filename: (Not available)",
                font=("Segoe UI", 10),
                bg=self.BG_MAIN,
                fg=self.TEXT_MUTED,
                anchor="w"
            )
            filename_label.pack(anchor="w", pady=2)
        
        # Location with clickable folder icon
        location_row = tk.Frame(details_frame, bg=self.BG_MAIN)
        location_row.pack(anchor="w", pady=2, fill="x")
        
        if self.downloaded_file_path:
            location_path = os.path.dirname(self.downloaded_file_path)
            
            # Clickable folder icon/link (to the left of "Location:")
            folder_link = tk.Label(
                location_row,
                text="📁",
                font=("Segoe UI", 12),
                bg=self.BG_MAIN,
                fg=self.ACCENT,
                cursor="hand2"
            )
            folder_link.pack(side="left", padx=(0, 5))
            folder_link.bind("<Button-1>", lambda e, p=location_path: self.open_file_location(p))
            folder_link.bind("<Enter>", lambda e: folder_link.config(fg=self.ACCENT_STRONG))
            folder_link.bind("<Leave>", lambda e: folder_link.config(fg=self.ACCENT))
            
            location_label = tk.Label(
                location_row,
                text=f"Location: {location_path}",
                font=("Segoe UI", 10),
                bg=self.BG_MAIN,
                fg=self.TEXT_MAIN,
                anchor="w",
                wraplength=650
            )
            location_label.pack(side="left", fill="x", expand=True)
        else:
            location_label = tk.Label(
                location_row,
                text=f"Location: {self.save_path.get()}",
                font=("Segoe UI", 10),
                bg=self.BG_MAIN,
                fg=self.TEXT_MUTED,
                anchor="w",
                wraplength=700
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
        self.download_btn.update_state("normal")
        self.cancel_btn.update_state("disabled")
        if self.progress_bar['value'] != 100:
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready to download", fg=self.TEXT_MUTED)
        
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

