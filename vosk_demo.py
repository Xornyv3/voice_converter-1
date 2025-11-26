#!/usr/bin/env python3
# vosk_demo.py — Record → auto-stop on silence → transcript → (EN only) ASL video

# Suppress Vosk verbose logging (must be set BEFORE importing vosk)
import os
os.environ['VOSK_LOG_LEVEL'] = '-1'

import re, sys, json, time, queue
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel
SetLogLevel(-1)  # Suppress Vosk logs

from translate_sentence import generate_asl_video
# --- Console UTF-8 (quand possible)
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# --- RTL helper (Arabic shaping + bidi)
from arabic_reshaper import reshape
from bidi.algorithm import get_display

def rtl(text: str) -> str:
    """Prépare un texte arabe pour affichage en console (droite→gauche, lettres liées)."""
    return get_display(reshape(text))

# ── Setup ─────────────────────────────────────────────────────────────────────
# Default to English (comment out the line below to enable language selection)
lang = "en"
# Uncomment these lines to enable language selection:
# lang_choice = input("Choisissez la langue (en/fr/ar) : ").strip().lower()
# lang = {"fr": "fr", "ar": "ar"}.get(lang_choice, "en")

model_paths = {
    "en": "vosk-model-en-us-0.22",
    "fr": "vosk-model-fr-0.22",
    "ar": "vosk-model-ar-mgb2-0.4",
}
model_path = model_paths.get(lang)
if not model_path or not os.path.isdir(model_path):
    print(f"❌ Model not found for '{lang}'", file=sys.stderr)
    sys.exit(1)

print(f"📥 Loading Vosk model (English)...")
model      = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)
print("✅ Model loaded successfully!")

# Audio queue
q = queue.Queue()
def callback(indata, frames, time_, status):
    if status:
        print(f"\n⚠️ {status}", file=sys.stderr)
    q.put(bytes(indata))

# ASL config
CLASS_LIST      = "WLASL/wlasl_class_list.txt"
NSLT_JSON       = "WLASL/nslt_2000.json"
VIDEOS_DIR      = "WLASL/videos"
MANUAL_REORDERS = "manual_reorders.json"
ASL_OUTPUT_DIR  = "asl_outputs"
os.makedirs(ASL_OUTPUT_DIR, exist_ok=True)
manual_rules = {}
if os.path.isfile(MANUAL_REORDERS):
    manual_rules = json.load(open(MANUAL_REORDERS, encoding="utf-8"))

# Silence detection (simple RMS)
SAMPLE_RATE     = 16000
BLOCKSIZE       = 8000          # 0.5s blocs
SILENCE_SEC     = 5.0           # stop after 5 seconds of silence
RMS_THRESHOLD   = 300.0         # à ajuster si besoin (micro trop faible/fort)

def clean_text(t: str) -> str:
    t = (t or "").strip()
    t = re.sub(r'^(?:the\s+)+', '', t, flags=re.I)
    t = re.sub(r'(?:\s+the)+$', '', t, flags=re.I)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    segments = []
    start_ts = time.time()
    print("🎤  Recording... Speak now. Auto-stops after 5s of silence (or Ctrl+C).")
    print("    Listening...\n")

    silence_start = None
    has_spoken    = False       # devient True dès qu’on détecte de la voix (ou 1er segment)
    stopped_by_silence = False

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE,
            dtype="int16", channels=1, callback=callback
        ):
            spinner = "|/-\\"
            si = 0
            while True:
                print(f"\r⏺️  {spinner[si % len(spinner)]}  {int(time.time()-start_ts)}s", end="", flush=True)
                si += 1

                data_bytes = q.get()
                # RMS (énergie) du bloc
                audio = np.frombuffer(data_bytes, dtype=np.int16).astype(np.float32)
                rms   = float(np.sqrt(np.mean(audio * audio))) if audio.size else 0.0

                # Détection de silence après qu’on a commencé à parler
                if has_spoken and rms < RMS_THRESHOLD:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= SILENCE_SEC:
                        stopped_by_silence = True
                        break
                else:
                    silence_start = None
                    if rms >= RMS_THRESHOLD:
                        has_spoken = True

                # Stocke seulement les résultats finaux
                if recognizer.AcceptWaveform(data_bytes):
                    res   = json.loads(recognizer.Result())
                    text  = clean_text(res.get("text", ""))
                    if text:
                        segments.append(text)
                        has_spoken = True  # on a une phrase valide

    except KeyboardInterrupt:
        pass  # handle finalization right after

    # Get the last partial chunk before closing
    try:
        final = json.loads(recognizer.FinalResult())
        tail  = clean_text(final.get("text", ""))
        if tail:
            segments.append(tail)
    except Exception:
        pass

    print("\n")
    if stopped_by_silence:
        print("🛑 Auto-stopped after silence.")
    else:
        print("🛑 Recording ended.")

    full_text = clean_text(" ".join(segments))
    if not full_text:
        print("…No speech recognized. Nothing to generate.")
        sys.exit(0)

    display_text = rtl(full_text) if lang == "ar" else full_text
    print(f"📝 Transcript: «{display_text}»")


    # FR/AR → texte seulement ; EN → texte + vidéo
    if lang != "en":
        print("ℹ️  Non-English language → ASL output not available.")
        sys.exit(0)

    # Generate ASL output (EN only)
    print("\n🎨 Generating ASL sign language output...")
    
    # Try image-based generation first (Kaggle dataset)
    try:
        from asl_image_generator import generate_asl_output
        
        # Generate all three formats
        gif_path = generate_asl_output(full_text, 'gif')
        print(f"✅ ASL GIF created → {gif_path}")
        
        img_path = generate_asl_output(full_text, 'image')
        print(f"✅ ASL image strip created → {img_path}")
        
        print(f"\n🎉 Success! Open the files to see your ASL translation!")
        sys.exit(0)
        
    except Exception as img_error:
        print(f"⚠️  Image generation failed: {img_error}")
        print("ℹ️  Trying video generation (WLASL dataset)...")
        
        # Fallback to video generation if available
        ts = int(time.time())
        out_path = os.path.join(ASL_OUTPUT_DIR, f"asl_{ts}.mp4")
        try:
            generate_asl_video(
                phrase=           full_text,
                class_list_path=  CLASS_LIST,
                nslt_json_path=   NSLT_JSON,
                videos_dir=       VIDEOS_DIR,
                out_path=         out_path,
                manual_reorders=  manual_rules
            )
            print(f"🎞 ASL video generated → {out_path}\n")
        except Exception as e:
            print(f"❌ Both generation methods failed")
            print(f"💡 Make sure either:")
            print(f"   - Kaggle ASL dataset is in: kaggle_asl_dataset/asl_dataset/")
            print(f"   - WLASL videos are in: WLASL/videos/")
            sys.exit(1)

if __name__ == "__main__":
    main()
