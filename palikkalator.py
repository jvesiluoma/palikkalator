import subprocess
import sys
import os
import datetime
import logging
import argparse
from pathlib import Path
from transformers import MarianTokenizer, MarianMTModel

# Configuration
YTDLP = "./yt-dlp/yt-dlp"
TRANSLATE_MODEL_PATH = "./opus-mt-en-fi-converted"

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def run_command(command, description):
    logging.info(f"{description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f"{description} done.")
    except subprocess.CalledProcessError:
        logging.error(f"Failed: {description}")
        sys.exit(1)

def generate_temp_basename(tmp_dir):
    dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(tmp_dir, f"{dt}-video")

def download_audio(url, base):
    audio_path = f"{base}-audio.mp3"
    cmd = f'{YTDLP} -f "ba" -x --audio-format "mp3" --audio-quality "320" -o "{base}-audio" "{url}"'
    run_command(cmd, "Downloading audio")
    return audio_path

def download_video(url, base):
    video_path = f"{base}.mp4"
    cmd = f'{YTDLP} --recode-video "mp4" -o "{base}" "{url}"'
    run_command(cmd, "Downloading video")
    return video_path

def transcribe_audio(audio_path, output_dir):
    cmd = f'whisper "{audio_path}" --model large --output_dir "{output_dir}"'
    run_command(cmd, "Transcribing audio to subtitles")
    srt_path = os.path.join(output_dir, Path(audio_path).stem + ".srt")
    return srt_path

def load_translation_model(model_path):
    tokenizer = MarianTokenizer.from_pretrained(model_path)
    model = MarianMTModel.from_pretrained(model_path)
    return tokenizer, model

def translate_text(text, tokenizer, model, max_tokens=510):
    if not text.strip():
        return text
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    if len(token_ids) <= max_tokens:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        translated = model.generate(**inputs)
        return tokenizer.decode(translated[0], skip_special_tokens=True)
    else:
        translations = []
        for i in range(0, len(token_ids), max_tokens):
            chunk_ids = token_ids[i:i + max_tokens]
            chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
            inputs = tokenizer(chunk_text, return_tensors="pt", padding=True, truncation=True)
            translated = model.generate(**inputs)
            translations.append(tokenizer.decode(translated[0], skip_special_tokens=True))
        return " ".join(translations)

def translate_srt(input_srt, output_srt, tokenizer, model):
    with open(input_srt, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
    translated_blocks = []

    for idx, block in enumerate(blocks, 1):
        lines = block.split('\n')
        if len(lines) < 3:
            translated_blocks.append(block)
            continue

        header = '\n'.join(lines[:2])
        text_lines = lines[2:]

        translated_text = []
        for line in text_lines:
            translated_line = translate_text(line, tokenizer, model)
            translated_text.append(translated_line)

        translated_block = f"{header}\n" + '\n'.join(translated_text)
        translated_blocks.append(translated_block)
        print(f"Translated block {idx}/{len(blocks)}")

    with open(output_srt, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(translated_blocks))

def burn_subtitles(video_path, srt_path, output_path):
    cmd = f'ffmpeg -i "{video_path}" -vf "subtitles={srt_path}" -c:a copy "{output_path}"'
    run_command(cmd, "Burning subtitles into video")

def main():
    parser = argparse.ArgumentParser(description="YouTube or local video translator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="YouTube video URL")
    group.add_argument("--file", help="Path to local video/audio file")
    parser.add_argument("output_dir", help="Directory to store all intermediate and output files")

    args = parser.parse_args()
    tmp_dir = args.output_dir
    os.makedirs(tmp_dir, exist_ok=True)
    base = generate_temp_basename(tmp_dir)

    # Step 1: Get input file
    if args.url:
        logging.info("Processing YouTube URL...")
        audio_path = download_audio(args.url, base)
        video_path = download_video(args.url, base)
    else:
        input_path = Path(args.file).resolve()
        ext = input_path.suffix.lower()

        if ext in [".mp3", ".wav", ".m4a"]:
            logging.info("Processing local audio file...")
            audio_path = str(input_path)
            video_path = None  # No video, just transcript + translation
        elif ext in [".mp4", ".mkv", ".mov", ".avi"]:
            logging.info("Processing local video file...")
            video_path = str(input_path)
            audio_path = os.path.join(tmp_dir, input_path.stem + "-extracted.mp3")
            # Extract audio
            cmd = f'ffmpeg -i "{video_path}" -q:a 0 -map a "{audio_path}" -y'
            run_command(cmd, "Extracting audio from video")
        else:
            logging.error("Unsupported file type. Please provide a valid audio or video file.")
            sys.exit(1)

    # Step 2: Transcribe
    srt_path = transcribe_audio(audio_path, tmp_dir)

    # Step 3: Translate SRT
    translated_srt = srt_path.replace(".srt", "-fin.srt")
    logging.info("Loading MarianMT model for translation...")
    tokenizer, model = load_translation_model(TRANSLATE_MODEL_PATH)
    translate_srt(srt_path, translated_srt, tokenizer, model)

    # Step 4: Burn subtitles
    if video_path:
        final_video = os.path.join(tmp_dir, Path(video_path).stem + "-FIN.mp4")
        burn_subtitles(video_path, translated_srt, final_video)
        logging.info(f"✅ Done! Final translated video: {final_video}")
    else:
        logging.info(f"✅ Done! Translated subtitles saved to: {translated_srt}")


if __name__ == "__main__":
    main()
