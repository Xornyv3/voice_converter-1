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

    # Generate ASL video (EN only) - Optimized WLASL word-level
    print("\n🎨 Generating ASL sign language video...")
    
    try:
        from wlasl_generator import WLASLGenerator
        
        # Initialize generator (loads vocabulary once)
        generator = WLASLGenerator()
        
        # Generate video
        output_path = generator.generate_video(full_text)
        
        print(f"\n🎉 Success! ASL video created!")
        print(f"📺 Open: {output_path}")
        sys.exit(0)
        
    except FileNotFoundError as fnf_error:
        print(f"❌ WLASL dataset not found: {fnf_error}")
        print(f"💡 Solution: Run 'python download_wlasl.py' to download the dataset")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error generating ASL video: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
