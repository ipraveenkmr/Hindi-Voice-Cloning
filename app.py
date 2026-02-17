import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import time
from TTS.api import TTS
import torch

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VoiceClonerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CodingMSTR Voice Clone - XTTS v2")
        self.geometry("850x750")
        self.resizable(True, True)

        # State
        self.tts = None
        self.speaker_wav_path = None
        self.output_path = "output_cloned.wav"
        self.is_cloning = False

        self.build_ui()
        self.initialize_engine_async()

    # ================= UI =================

    def build_ui(self):

        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkLabel(
            self,
            text="CodingMSTR Voice Clone",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        header.pack(pady=(30, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Professional Hindi Voice Cloning (XTTS v2)",
            font=ctk.CTkFont(size=14),
        )
        subtitle.pack(pady=(0, 20))

        # Text Input
        self.textbox = ctk.CTkTextbox(
            self,
            height=180,
            corner_radius=12,
        )
        self.textbox.pack(padx=40, fill="x")
        self.textbox.insert(
            "0.0",
            "नमस्ते, आप कैसे हैं? (Paste your text here...)"
        )

        # File Section
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=20, padx=40, fill="x")

        self.select_btn = ctk.CTkButton(
            file_frame,
            text="Select Sample (.wav / .mp3)",
            command=self.select_sample,
        )
        self.select_btn.pack(side="left", padx=10, pady=10)

        self.sample_label = ctk.CTkLabel(
            file_frame,
            text="No voice sample selected"
        )
        self.sample_label.pack(side="left", padx=10)

        # Clone Button
        self.clone_btn = ctk.CTkButton(
            self,
            text="Start Cloning",
            state="disabled",
            command=self.start_cloning,
            height=40
        )
        self.clone_btn.pack(pady=10)

        # Status
        self.status_label = ctk.CTkLabel(
            self,
            text="Loading TTS engine...",
            font=ctk.CTkFont(size=13)
        )
        self.status_label.pack(pady=10)

        # Progress bar
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(padx=100, fill="x")
        self.progress.set(0)

        # Play Button
        self.play_btn = ctk.CTkButton(
            self,
            text="Play Generated Audio",
            command=self.play_audio,
            state="disabled"
        )
        self.play_btn.pack(pady=20)

    # ================= TTS Initialization =================

    def initialize_engine_async(self):
        thread = threading.Thread(target=self.initialize_engine)
        thread.daemon = True
        thread.start()

    def initialize_engine(self):
        try:
            self.update_status("Loading XTTS model...")
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts.to(device)

            self.update_status(f"System Ready ({device.upper()} mode)")
            self.check_inputs()

        except Exception as e:
            self.update_status(f"Initialization Error: {e}")

    # ================= File Selection =================

    def select_sample(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3")]
        )

        if file_path:
            self.speaker_wav_path = file_path
            self.sample_label.configure(
                text=f"Selected: {os.path.basename(file_path)}"
            )
            self.check_inputs()

    # ================= Validation =================

    def check_inputs(self):
        text = self.textbox.get("0.0", "end").strip()
        valid = bool(self.tts and self.speaker_wav_path and text)

        if valid:
            self.clone_btn.configure(state="normal")
        else:
            self.clone_btn.configure(state="disabled")

    # ================= Cloning =================

    def start_cloning(self):
        if self.is_cloning:
            return

        self.is_cloning = True
        self.clone_btn.configure(state="disabled")
        self.play_btn.configure(state="disabled")
        self.progress.start()
        self.update_status("Synthesis in progress...")

        thread = threading.Thread(target=self.run_cloning)
        thread.daemon = True
        thread.start()

    def run_cloning(self):
        try:
            start_time = time.time()

            text = self.textbox.get("0.0", "end").strip()

            self.tts.tts_to_file(
                text=text,
                speaker_wav=self.speaker_wav_path,
                language="hi",
                file_path=self.output_path,
            )

            elapsed = round(time.time() - start_time, 1)

            self.progress.stop()
            self.progress.set(1)

            self.update_status(f"Voice cloned in {elapsed}s!")
            self.play_btn.configure(state="normal")

        except Exception as e:
            self.update_status(f"Cloning Error: {e}")
        finally:
            self.is_cloning = False
            self.check_inputs()

    # ================= Audio =================

    def play_audio(self):
        if os.path.exists(self.output_path):
            os.startfile(self.output_path)
        else:
            messagebox.showerror("Error", "Audio file not found.")

    # ================= Helpers =================

    def update_status(self, text):
        self.status_label.configure(text=text)


if __name__ == "__main__":
    app = VoiceClonerApp()
    app.mainloop()
