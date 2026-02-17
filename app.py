import flet as ft
import os
import asyncio
import time
from TTS.api import TTS

# Modern Glassmorphism Voice Cloner App (Async Version)
# Architecture:
# - Flet (Flutter for Python) for the Desktop UI
# - TTS (Coqui) for the backend logic
# - Async architecture for modern Flet (0.21+) compatibility


class VoiceClonerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.tts = None
        self.speaker_wav_path = None
        self.is_cloning = False
        self.output_path = "output_cloned.wav"

    async def init(self):
        # Configure Page
        self.page.title = "CodingMSTRVoiceClone - Premium Voice Cloning"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 900
        self.page.window_height = 850
        self.page.bgcolor = ft.Colors.BLACK
        self.page.window_resizable = True

        await self.setup_ui()
        self.page.update()

        # Start engine initialization as a background task
        asyncio.create_task(self.initialize_engine())

    async def setup_ui(self):
        # 1. Background Decor
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

        # self.file_picker = ft.FilePicker(on_result=self.on_file_result)
        # self.page.overlay.append(self.file_picker)
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self.on_file_result
        self.page.services.append(self.file_picker)

        self.sample_btn = ft.FilledButton(
            "Select Sample (.wav)",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.pick_sample,
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

        self.clone_btn = ft.FilledButton(
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
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
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

    async def initialize_engine(self):
        await self.set_status("Loading TTS models... (Downloading if missing)", True)
        try:
            # Running synchronous heavy initialization in a separate thread to keep UI alive
            loop = asyncio.get_running_loop()
            self.tts = await loop.run_in_executor(
                None, lambda: TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            )

            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts.to(device)

            await self.set_status(f"System Ready ({device.upper()} mode)")
            await self.validate_inputs(None)
        except Exception as e:
            await self.set_status(
                f"Initialization Error: {str(e)}", False, ft.Colors.RED_400
            )

    async def pick_sample(self, e):
        await self.file_picker.pick_files(
            allow_multiple=False, allowed_extensions=["wav", "mp3"]
        )

    async def on_file_result(self, e):
        if e.files:
            self.speaker_wav_path = e.files[0].path
            self.sample_info.value = (
                f"Selected: {os.path.basename(self.speaker_wav_path)}"
            )
            await self.validate_inputs(None)

    async def validate_inputs(self, e):
        valid = bool(self.tts and self.speaker_wav_path and self.textarea.value.strip())
        self.clone_btn.disabled = not valid
        await self.page.update_async()

    async def set_status(self, text, loading=False, color=None):
        self.status_text.value = text
        if color:
            self.status_text.color = color
        else:
            self.status_text.color = ft.Colors.WHITE70
        self.progress_ring.visible = loading
        await self.page.update_async()

    async def start_cloning(self, e):
        if self.is_cloning:
            return

        self.is_cloning = True
        self.clone_btn.disabled = True
        self.play_btn.visible = False
        await self.set_status(
            "Synthesis in progress... Please wait", True, ft.Colors.CYAN_200
        )

        # Run cloning logic as a background task
        asyncio.create_task(self.run_cloning_logic())

    async def run_cloning_logic(self):
        start_time = time.time()
        try:
            # Running synchronous heavy TTS in a separate thread
            loop = asyncio.get_running_loop()
            text = self.textarea.value.strip()
            speaker_wav = self.speaker_wav_path

            await loop.run_in_executor(
                None,
                lambda: self.tts.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language="hi",
                    file_path=self.output_path,
                ),
            )

            elapsed = round(time.time() - start_time, 1)
            await self.set_status(
                f"Voice cloned in {elapsed}s!", False, ft.Colors.GREEN_400
            )

            if self.audio_player:
                self.audio_player.src = self.output_path
            self.play_btn.visible = True
            await self.page.update_async()

        except Exception as e:
            await self.set_status(f"Cloning Error: {str(e)}", False, ft.Colors.RED_400)
        finally:
            self.is_cloning = False
            await self.validate_inputs(None)

    async def play_audio(self, e):
        if self.audio_player and self.audio_player.src:
            await self.audio_player.play_async()
        elif os.path.exists(self.output_path):
            os.startfile(self.output_path)


async def main(page: ft.Page):
    app = VoiceClonerApp(page)
    await app.init()


if __name__ == "__main__":
    ft.run(main)
