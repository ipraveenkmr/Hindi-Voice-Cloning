from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

text = "नमस्ते, यह एक हिंदी टेक्स्ट टू स्पीच उदाहरण है"

tts.tts_to_file(
    text=text,
    speaker_wav="Recording.wav",   # your voice sample
    language="hi",
    file_path="output.wav"
)

print("Audio saved as output.wav")
