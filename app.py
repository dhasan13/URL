import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import yt_dlp


# ============================================================
# SETTINGS
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# COLORS
# ============================================================

BG = "#202020"
PANEL = "#292929"
ENTRY = "#303030"
BLUE = "#1976B9"
BLUE_HOVER = "#155F92"
TEXT = "#FFFFFF"
SECONDARY = "#BDBDBD"
GREEN = "#35C759"
RED = "#D9534F"


# ============================================================
# APPLICATION
# ============================================================

class MediaDownloader(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Media Downloader")
        self.geometry("1050x650")
        self.minsize(900, 600)

        self.configure(fg_color=BG)

        # State
        self.downloading = False
        self.stop_requested = False
        self.download_thread = None

        # Default directory
        self.download_directory = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )

        self.create_ui()

    # ========================================================
    # UI
    # ========================================================

    def create_ui(self):

        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------

        top_bar = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=0,
            height=70
        )

        top_bar.pack(
            fill="x",
            padx=20,
            pady=(20, 0)
        )

        top_bar.pack_propagate(False)

        # Theme
        theme_label = ctk.CTkLabel(
            top_bar,
            text="Theme:",
            text_color=TEXT,
            font=("Segoe UI", 14, "bold")
        )

        theme_label.pack(
            side="left",
            padx=(20, 8)
        )

        self.theme_menu = ctk.CTkOptionMenu(
            top_bar,
            values=[
                "Dark",
                "Light",
                "System"
            ],
            width=170,
            height=40,
            command=self.change_theme
        )

        self.theme_menu.set("Dark")

        self.theme_menu.pack(
            side="left"
        )

        # Language
        language_label = ctk.CTkLabel(
            top_bar,
            text="Language:",
            text_color=TEXT,
            font=("Segoe UI", 14, "bold")
        )

        language_label.pack(
            side="right",
            padx=(10, 8)
        )

        self.language_menu = ctk.CTkOptionMenu(
            top_bar,
            values=[
                "English",
                "Tamil"
            ],
            width=170,
            height=40,
            command=self.change_language
        )

        self.language_menu.set("English")

        self.language_menu.pack(
            side="right",
            padx=(0, 20)
        )

        # ----------------------------------------------------
        # MAIN PANEL
        # ----------------------------------------------------

        main = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=12
        )

        main.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        self.title_label = ctk.CTkLabel(
            main,
            text="Media Downloader",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT
        )

        self.title_label.pack(
            pady=(25, 25)
        )

        # ----------------------------------------------------
        # URL AREA
        # ----------------------------------------------------

        url_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )

        url_frame.pack(
            fill="x",
            padx=30
        )

        self.url_entry = ctk.CTkEntry(
            url_frame,
            height=48,
            placeholder_text="Enter Media URL",
            font=("Segoe UI", 14),
            fg_color=ENTRY,
            border_color="#555555",
            border_width=2
        )

        self.url_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.clear_button = ctk.CTkButton(
            url_frame,
            text="Clear",
            width=140,
            height=48,
            font=("Segoe UI", 14, "bold"),
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=self.clear_url
        )

        self.clear_button.pack(
            side="right",
            padx=(12, 0)
        )

        # ----------------------------------------------------
        # OPTIONS
        # ----------------------------------------------------

        options_frame = ctk.CTkFrame(
            main,
            fg_color="#252525",
            corner_radius=8
        )

        options_frame.pack(
            fill="x",
            padx=30,
            pady=18
        )

        # Format
        format_label = ctk.CTkLabel(
            options_frame,
            text="Format:",
            font=("Segoe UI", 14, "bold")
        )

        format_label.pack(
            side="left",
            padx=(15, 8)
        )

        self.format_menu = ctk.CTkOptionMenu(
            options_frame,
            values=[
                "best",
                "mp4",
                "mp3",
                "webm"
            ],
            width=150,
            height=42
        )

        self.format_menu.set("best")

        self.format_menu.pack(
            side="left"
        )

        # Quality
        quality_label = ctk.CTkLabel(
            options_frame,
            text="Quality:",
            font=("Segoe UI", 14, "bold")
        )

        quality_label.pack(
            side="left",
            padx=(25, 8)
        )

        self.quality_menu = ctk.CTkOptionMenu(
            options_frame,
            values=[
                "best",
                "1080p",
                "720p",
                "480p",
                "360p",
                "audio"
            ],
            width=150,
            height=42
        )

        self.quality_menu.set("best")

        self.quality_menu.pack(
            side="left"
        )

        # Subtitle checkbox
        self.subtitle_var = tk.BooleanVar(
            value=False
        )

        self.subtitle_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Download Subtitles",
            variable=self.subtitle_var,
            font=("Segoe UI", 14)
        )

        self.subtitle_checkbox.pack(
            side="left",
            padx=25
        )

        # ----------------------------------------------------
        # DIRECTORY
        # ----------------------------------------------------

        directory_frame = ctk.CTkFrame(
            main,
            fg_color="#252525",
            corner_radius=8
        )

        directory_frame.pack(
            fill="x",
            padx=30
        )

        self.directory_label = ctk.CTkLabel(
            directory_frame,
            text=f"Directory: {self.download_directory}",
            font=("Segoe UI", 14),
            anchor="w"
        )

        self.directory_label.pack(
            side="left",
            fill="x",
            expand=True,
            padx=15
        )

        self.directory_button = ctk.CTkButton(
            directory_frame,
            text="Select Directory",
            width=180,
            height=45,
            font=("Segoe UI", 14, "bold"),
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=self.select_directory
        )

        self.directory_button.pack(
            side="right",
            padx=8,
            pady=8
        )

        # ----------------------------------------------------
        # PROGRESS AREA
        # ----------------------------------------------------

        progress_frame = ctk.CTkFrame(
            main,
            fg_color="#252525",
            corner_radius=8,
            height=110
        )

        progress_frame.pack(
            fill="x",
            padx=30,
            pady=18
        )

        progress_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready",
            font=("Segoe UI", 14),
            text_color=SECONDARY
        )

        self.status_label.pack(
            pady=(15, 8)
        )

        self.progress = ctk.CTkProgressBar(
            progress_frame,
            height=14,
            corner_radius=10,
            progress_color=BLUE
        )

        self.progress.pack(
            fill="x",
            padx=30
        )

        self.progress.set(0)

        self.progress_percent = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=("Segoe UI", 12)
        )

        self.progress_percent.pack(
            pady=5
        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        button_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=30,
            pady=(5, 20)
        )

        self.download_button = ctk.CTkButton(
            button_frame,
            text="Download",
            height=55,
            font=("Segoe UI", 16, "bold"),
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=self.start_download
        )

        self.download_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 6)
        )

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop Download",
            height=55,
            font=("Segoe UI", 16, "bold"),
            fg_color="#444444",
            hover_color="#555555",
            state="disabled",
            command=self.stop_download
        )

        self.stop_button.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(6, 0)
        )

    # ========================================================
    # THEME
    # ========================================================

    def change_theme(self, choice):

        if choice == "Dark":

            ctk.set_appearance_mode("dark")

        elif choice == "Light":

            ctk.set_appearance_mode("light")

        else:

            ctk.set_appearance_mode("system")

    # ========================================================
    # LANGUAGE
    # ========================================================

    def change_language(self, choice):

        if choice == "Tamil":

            self.title_label.configure(
                text="மீடியா டவுன்லோடர்"
            )

            self.clear_button.configure(
                text="அழி"
            )

            self.download_button.configure(
                text="பதிவிறக்கம்"
            )

            self.stop_button.configure(
                text="நிறுத்து"
            )

        else:

            self.title_label.configure(
                text="Media Downloader"
            )

            self.clear_button.configure(
                text="Clear"
            )

            self.download_button.configure(
                text="Download"
            )

            self.stop_button.configure(
                text="Stop Download"
            )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear_url(self):

        self.url_entry.delete(
            0,
            tk.END
        )

        self.status_label.configure(
            text="Ready"
        )

        self.progress.set(0)

        self.progress_percent.configure(
            text="0%"
        )

    # ========================================================
    # DIRECTORY
    # ========================================================

    def select_directory(self):

        directory = filedialog.askdirectory(
            title="Select Download Directory",
            initialdir=self.download_directory
        )

        if directory:

            self.download_directory = directory

            self.directory_label.configure(
                text=f"Directory: {directory}"
            )

    # ========================================================
    # START DOWNLOAD
    # ========================================================

    def start_download(self):

        if self.downloading:
            return

        url = self.url_entry.get().strip()

        if not url:

            messagebox.showwarning(
                "Missing URL",
                "Please enter a media URL."
            )

            return

        self.downloading = True
        self.stop_requested = False

        self.download_button.configure(
            state="disabled"
        )

        self.stop_button.configure(
            state="normal"
        )

        self.status_label.configure(
            text="Starting download..."
        )

        self.progress.set(0)

        self.progress_percent.configure(
            text="0%"
        )

        self.download_thread = threading.Thread(
            target=self.download_media,
            args=(url,),
            daemon=True
        )

        self.download_thread.start()

    # ========================================================
    # DOWNLOAD
    # ========================================================

    def download_media(self, url):

        try:

            selected_format = self.format_menu.get()
            quality = self.quality_menu.get()

            # ------------------------------------------------
            # Format
            # ------------------------------------------------

            if selected_format == "mp3":

                format_string = "bestaudio/best"

                postprocessors = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }
                ]

            elif selected_format == "mp4":

                format_string = (
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                    "best[ext=mp4]/best"
                )

                postprocessors = []

            elif selected_format == "webm":

                format_string = (
                    "bestvideo[ext=webm]+bestaudio[ext=webm]/best"
                )

                postprocessors = []

            else:

                format_string = (
                    "bestvideo+bestaudio/best"
                )

                postprocessors = []

            # ------------------------------------------------
            # Quality
            # ------------------------------------------------

            if quality == "1080p":

                format_string = (
                    "bestvideo[height<=1080]+bestaudio/"
                    "best[height<=1080]"
                )

            elif quality == "720p":

                format_string = (
                    "bestvideo[height<=720]+bestaudio/"
                    "best[height<=720]"
                )

            elif quality == "480p":

                format_string = (
                    "bestvideo[height<=480]+bestaudio/"
                    "best[height<=480]"
                )

            elif quality == "360p":

                format_string = (
                    "bestvideo[height<=360]+bestaudio/"
                    "best[height<=360]"
                )

            elif quality == "audio":

                format_string = "bestaudio/best"

                postprocessors = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }
                ]

            # ------------------------------------------------
            # Output
            # ------------------------------------------------

            output_template = os.path.join(
                self.download_directory,
                "%(title)s.%(ext)s"
            )

            options = {
                "format": format_string,

                "outtmpl": output_template,

                "merge_output_format": "mp4",

                "postprocessors": postprocessors,

                "progress_hooks": [
                    self.progress_hook
                ],

                "quiet": True,

                "no_warnings": True,

                "noplaylist": True,
            }

            # ------------------------------------------------
            # Subtitles
            # ------------------------------------------------

            if self.subtitle_var.get():

                options.update({
                    "writesubtitles": True,
                    "writeautomaticsub": True,
                    "subtitleslangs": ["en"],
                    "subtitlesformat": "srt"
                })

            # ------------------------------------------------
            # Download
            # ------------------------------------------------

            with yt_dlp.YoutubeDL(options) as ydl:

                ydl.download([url])

            if self.stop_requested:
                return

            self.after(
                0,
                self.download_finished
            )

        except Exception as error:

            if self.stop_requested:
                return

            self.after(
                0,
                lambda e=str(error):
                self.download_failed(e)
            )

    # ========================================================
    # PROGRESS
    # ========================================================

    def progress_hook(self, data):

        if self.stop_requested:
            raise Exception(
                "Download stopped by user."
            )

        if data.get("status") == "downloading":

            total = (
                data.get("total_bytes")
                or
                data.get("total_bytes_estimate")
            )

            downloaded = data.get(
                "downloaded_bytes",
                0
            )

            if total:

                percentage = (
                    downloaded / total
                )

                percentage = max(
                    0,
                    min(
                        percentage,
                        1
                    )
                )

                self.after(
                    0,
                    lambda p=percentage:
                    self.update_progress(p)
                )

        elif data.get("status") == "finished":

            self.after(
                0,
                lambda:
                self.status_label.configure(
                    text="Processing..."
                )
            )

    # ========================================================
    # UPDATE PROGRESS
    # ========================================================

    def update_progress(self, percentage):

        self.progress.set(
            percentage
        )

        self.progress_percent.configure(
            text=f"{percentage * 100:.1f}%"
        )

        self.status_label.configure(
            text="Downloading..."
        )

    # ========================================================
    # STOP
    # ========================================================

    def stop_download(self):

        if not self.downloading:
            return

        self.stop_requested = True
        self.downloading = False

        self.progress.set(0)

        self.progress_percent.configure(
            text="0%"
        )

        self.status_label.configure(
            text="Download stopped"
        )

        self.download_button.configure(
            state="normal"
        )

        self.stop_button.configure(
            state="disabled"
        )

    # ========================================================
    # FINISHED
    # ========================================================

    def download_finished(self):

        self.downloading = False

        self.progress.set(1)

        self.progress_percent.configure(
            text="100%"
        )

        self.status_label.configure(
            text="Download completed successfully!"
        )

        self.download_button.configure(
            state="normal"
        )

        self.stop_button.configure(
            state="disabled"
        )

        messagebox.showinfo(
            "Complete",
            "Media downloaded successfully!"
        )

    # ========================================================
    # ERROR
    # ========================================================

    def download_failed(self, error):

        self.downloading = False

        self.download_button.configure(
            state="normal"
        )

        self.stop_button.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="Download failed"
        )

        messagebox.showerror(
            "Download Error",
            error
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app = MediaDownloader()

    app.mainloop()