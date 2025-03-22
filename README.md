# 🎬 AI Video Translator – Subtitle Wizard with a Brain 🧠✨

This Python script is a tool that automates the process of downloading or processing videos/audio (from YouTube or local files), transcribing the audio using [OpenAI Whisper](https://github.com/openai/whisper), translating the subtitles to another language using Hugging Face's MarianMT model, and optionally burning the translated subtitles back into the video using `ffmpeg`.

---

## 🚀 Features

- 🎥 Supports **YouTube URLs** *and* local video/audio files.
- 🗣️ Transcribes speech using **Whisper** (large model).
- 🌍 Translates subtitles to another language using **MarianMT**.
- 🧾 Outputs `.srt` subtitle files (translated).
- 🔥 Optionally burns subtitles into the video using **FFmpeg**.
- 📂 All files are saved neatly inside a user-defined temp/output directory.

---

## 📦 Requirements

Make sure you have the following installed:

- Python 3.8+
- [Whisper](https://github.com/openai/whisper)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- ffmpeg
- torch
- transformers
- sentencepiece
- huggingface_hub

Install the Python dependencies with:

```bash
pip install torch transformers sentencepiece
```

> **Note**: You also need to download the Whisper large model once using:
```bash
whisper --model large --help
```

---

## 🛠️ Installation

Clone this repo and navigate into the folder:

```bash
git clone https://github.com/yourusername/video-translator-ai.git
cd video-translator-ai
```

Edit the paths in the script to match your environment:
- `YTDLP` path
- `TRANSLATE_MODEL_PATH` (HuggingFace MarianMT model folder)

---

## 🎯 Usage

### Translate YouTube video:

```bash
python translator.py --url "https://youtube.com/watch?v=xyz123" /path/to/output_dir
```

### Translate local video file:

```bash
python translator.py --file "/path/to/video.mp4" /path/to/output_dir
```

### Translate local audio file:

```bash
python translator.py --file "/path/to/audio.mp3" /path/to/output_dir
```

---

## 📁 Output

- `.mp3` – Extracted or downloaded audio
- `.srt` – Transcribed subtitle file
- `-fin.srt` – Translated subtitle file
- `-FIN.mp4` – Final video with burned-in subtitles (if video input)

---

## 👋 Credits

- Whisper by OpenAI
- MarianMT by Hugging Face
- yt-dlp for YouTube downloading
- FFmpeg for video processing

---

## 📃 License

MIT – Free to use, modify and share. But if it makes you a million dollars, buy me coffee ☕ 😄
