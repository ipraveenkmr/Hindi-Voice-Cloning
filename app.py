import flet as ft
import os
import threading
import time
from TTS.api import TTS

# Modern Glassmorphism Voice Cloner App
# Architecture:
# - Flet (Flutter for Python) for the Desktop UI
# - TTS (Coqui) for the backend logic
# - Backdrop blur and semi-transparency for Glassmorphism


class VoiceClonerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.tts = None
        self.speaker_wav_path = None
        self.is_cloning = False
        self.output_path = "output_cloned.wav"

        # Configure Page
        self.page.title = "CodingMSTRVoiceClone - Premium Voice Cloning"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 900
        self.page.window_height = 850
        self.page.bgcolor = ft.Colors.BLACK
        self.page.window_resizable = True

        self.setup_ui()

    def setup_ui(self):
        # 1. Background Decor (Animated-like static glow)
        self.bg_glow = ft.Stack(
            [
                ft.Container(
                    width=500,
                    height=500,
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.PURPLE_900),
                    border_radius=250,
                    blur=ft.Blur(100, 100),
                    top=-150,
                    right=-150,
                ),
                ft.Container(
                    width=400,
                    height=400,
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.CYAN_900),
                    border_radius=200,
                    blur=ft.Blur(80, 80),
                    bottom=-100,
                    left=-100,
                ),
            ]
        )

        # 2. Components
        self.status_text = ft.Text(
            "Checking environment...", color=ft.Colors.WHITE70, italic=True
        )
        self.progress_ring = ft.ProgressRing(
            visible=True, width=24, height=24, stroke_width=3, color=ft.Colors.CYAN_400
        )

        self.textarea = ft.TextField(
            label="Text to Clone",
            hint_text="नमस्ते, आप कैसे हैं? (Paste your text here...)",
            multiline=True,
            min_lines=6,
            max_lines=10,
            border_radius=15,
            border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            cursor_color=ft.Colors.CYAN_400,
            focused_border_color=ft.Colors.CYAN_400,
            text_style=ft.TextStyle(size=14, color=ft.Colors.WHITE),
            on_change=self.validate_inputs,
        )

        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self.on_file_result
        self.page.services.append(self.file_picker)

        self.sample_btn = ft.ElevatedButton(
            "Select Sample (.wav)",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=False, allowed_extensions=["wav", "mp3"]
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

        self.sample_info = ft.Text(
            "No voice sample attached", color=ft.Colors.WHITE38, size=12
        )

        self.clone_btn = ft.ElevatedButton(
            "Start Cloning",
            icon=ft.Icons.ROCKET_LAUNCH,
            on_click=self.start_cloning,
            disabled=True,
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                bgcolor=ft.Colors.CYAN_400,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

        if hasattr(ft, "Audio"):
            self.audio_player = ft.Audio(
                src="",
                autoplay=False,
            )
            self.page.overlay.append(self.audio_player)
        else:
            self.audio_player = None

        self.play_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.PLAY_CIRCLE_FILL, color=ft.Colors.CYAN_400, size=32
                    ),
                    ft.Text(
                        "Play Generated Audio", color=ft.Colors.CYAN_400, weight="bold"
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            on_click=self.play_audio,
            # visible=False,
            padding=10,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.CYAN_400),
        )

        # 3. Glass Card Design
        self.glass_card = ft.Container(
            content=ft.Column(
                [
                    # Header
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.FINGERPRINT, color=ft.Colors.CYAN_400, size=40
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "CodingMSTRVoiceClone",
                                        size=28,
                                        weight="bold",
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        "Professional Hindi Voice Cloning",
                                        size=14,
                                        color=ft.Colors.CYAN_200,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(
                        height=40, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
                    ),
                    # Input Section
                    self.textarea,
                    # File Section
                    ft.Row(
                        [
                            ft.Column([self.sample_btn, self.sample_info], spacing=5),
                            self.clone_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(
                        height=40, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
                    ),
                    # Status & Progress
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        self.progress_ring,
                                        self.status_text,
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=15,
                                ),
                                ft.AnimatedSwitcher(
                                    self.play_btn,
                                    transition=ft.AnimatedSwitcherTransition.SCALE,
                                    duration=500,
                                ),
                            ],
                            spacing=20,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=20,
                        border_radius=20,
                        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
                    ),
                    # Footer
                    ft.Text(
                        "Powered by Coqui XTTS v2",
                        size=10,
                        color=ft.Colors.WHITE24,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=40,
            width=700,
            border_radius=30,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            blur=ft.Blur(25, 25),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        )

        # Main Layout
        self.page.add(
            ft.Stack(
                [
                    self.bg_glow,
                    ft.Container(
                        content=self.glass_card,
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                        padding=20,
                    ),
                ],
                expand=True,
            )
        )

        # Initial background tasks
        threading.Thread(target=self.initialize_engine, daemon=True).start()

    def initialize_engine(self):
        self.set_status("Loading TTS models... (Downloading if missing)", True)
        try:
            # TTS initialization will automatically download XTTS_v2 if not present
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts.to(device)
            self.set_status(f"System Ready ({device.upper()} mode)")
            self.validate_inputs(None)
        except Exception as e:
            self.set_status(f"Initialization Error: {str(e)}", False, ft.Colors.RED_400)

    def on_file_result(self, e):
        if e.files:
            self.speaker_wav_path = e.files[0].path
            self.sample_info.value = (
                f"Selected: {os.path.basename(self.speaker_wav_path)}"
            )
            self.validate_inputs(None)

    def validate_inputs(self, e):
        # Enable button only if text, sample, and model are ready
        valid = bool(self.tts and self.speaker_wav_path and self.textarea.value.strip())
        self.clone_btn.disabled = not valid
        self.page.update()

    def set_status(self, text, loading=False, color=None):
        self.status_text.value = text
        if color:
            self.status_text.color = color
        else:
            self.status_text.color = ft.Colors.WHITE70
        self.progress_ring.visible = loading
        self.page.update()

    def start_cloning(self, e):
        if self.is_cloning:
            return

        self.is_cloning = True
        self.clone_btn.disabled = True
        self.play_btn.visible = False
        self.set_status(
            "Synthesis in progress... Please wait", True, ft.Colors.CYAN_200
        )

        threading.Thread(target=self.run_cloning_logic, daemon=True).start()

    def run_cloning_logic(self):
        start_time = time.time()
        try:
            # Run TTS
            self.tts.tts_to_file(
                text=self.textarea.value.strip(),
                speaker_wav=self.speaker_wav_path,
                language="hi",
                file_path=self.output_path,
            )

            elapsed = round(time.time() - start_time, 1)
            self.set_status(f"Voice cloned in {elapsed}s!", False, ft.Colors.GREEN_400)

            # Setup Playback
            if self.audio_player:
                self.audio_player.src = self.output_path
            self.play_btn.visible = True

        except Exception as e:
            self.set_status(f"Cloning Error: {str(e)}", False, ft.Colors.RED_400)
        finally:
            self.is_cloning = False
            self.validate_inputs(None)

    def play_audio(self, e):
        if self.audio_player and self.audio_player.src:
            self.audio_player.play()
        elif os.path.exists(self.output_path):
            import subprocess

            os.startfile(self.output_path)


def main():
    ft.app(target=VoiceClonerApp)


if __name__ == "__main__":
    main()
