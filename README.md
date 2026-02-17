# Voice Cloning with Coqui TTS (XTTS v2)

A powerful and efficient voice cloning application using the Coqui TTS library and the XTTS v2 model. This project allows you to clone voices from short audio samples and generate high-quality, natural-sounding speech in multiple languages, including Hindi.

## 🔑 Keywords
`Voice Cloning` `Coqui TTS` `XTTS v2` `AI Voice` `Text-to-Speech` `Deep Learning` `Python` `Multilingual TTS` `Hindi TTS` `Speech Synthesis`

## 🚀 Features
- **Zero-Shot Voice Cloning**: Clone any voice using just a short audio sample (`.wav`).
- **Multilingual Support**: Generate speech in various languages (Hindi, English, etc.).
- **High Fidelity**: Powered by the state-of-the-art XTTS v2 model.
- **Simple Integration**: Easy-to-use Python scripts for generation.

## 📋 Prerequisites
- **Python**: 3.10 (Recommended)
- **C++ Build Tools**: Microsoft Visual C++ 14.0 or greater is required (needed for `TTS` package compilation).
- **GPU (Optional)**: CUDA-enabled GPU for faster inference.

## 🛠️ Installation

1. **Create a Virtual Environment**:
   ```powershell
   py -3.10 -m venv env
   .\env\Scripts\activate
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## 📖 Usage

### 1. Prepare your voice sample
Place a clear audio recording of the target voice in the root directory and name it `Recording.wav`.

### 2. Generate Speech
Run the main script to generate the cloned voice:
```powershell
python main.py
```

### 3. Output
The generated speech will be saved as `output.wav`.

## 📂 Project Structure
- `main.py`: The primary script for text-to-speech generation.
- `test.py`: A simple script to verify model loading.
- `requirements.txt`: List of required Python packages.
- `details.txt`: Specific setup notes and troubleshooting.
- `.gitignore`: Git exclusion rules.

## ⚖️ License
This project is for educational and research purposes. Please ensure you have the rights to use any voice data you clone.
