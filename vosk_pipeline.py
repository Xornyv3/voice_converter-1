#!/usr/bin/env python3
# Suppress Vosk verbose logging (must be set BEFORE importing vosk)
import os
os.environ['VOSK_LOG_LEVEL'] = '-1'

import re, queue, sys, json, time
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel
SetLogLevel(-1)  # Suppress Vosk logs

# Import WLASL generator
from wlasl_generator import WLASLGenerator

# Default to English
lang = "en"
model_paths = { "en":"vosk-model-en-us-0.22", "fr":"vosk-model-fr-0.22", "ar":"vosk-model-ar-mgb2-0.4" }
model_path = model_paths[lang]
print("📥 Loading Vosk model (English)...")
model      = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)
print("✅ Model loaded successfully!")

# Initialize WLASL generator (loads vocabulary once for efficiency)
print("📚 Loading WLASL vocabulary...")
try:
    wlasl_gen = WLASLGenerator()
    print("✅ WLASL ready!")
except Exception as e:
    print(f"❌ Error loading WLASL: {e}")
    print(f"💡 Run: python download_wlasl.py")
    sys.exit(1)

q = queue.Queue()
def callback(indata, frames, time_, status):
    if status: print(status, file=sys.stderr)
    q.put(bytes(indata))

ASL_OUT_DIR = "asl_outputs"
os.makedirs(ASL_OUT_DIR, exist_ok=True)

with sd.RawInputStream(samplerate=16000, blocksize=4000,
                       dtype="int16", channels=1,
                       callback=callback):
    print("🎤 Speak now... (Ctrl+C to quit)")
    try:
        while True:
            data = q.get()
            if not recognizer.AcceptWaveform(data):
                continue
            res     = json.loads(recognizer.Result())
            cleaned = re.sub(r"\s+", " ", 
                              re.sub(r'(?:the\s+)+$', "", 
                                re.sub(r'^(?:the\s+)+','', res.get("text",""), flags=re.I),
                              flags=re.I)).strip()
            if not cleaned:
                continue

            print(f"\n📝 Heard: «{cleaned}»")
            print(f"🎬 Generating ASL video...")
            
            try:
                out_file = wlasl_gen.generate_video(cleaned)
                print(f"✅ Video: {out_file}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

    except KeyboardInterrupt:
        print("\n👋 Stopped!")
        sys.exit(0)
