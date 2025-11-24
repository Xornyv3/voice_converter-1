#!/usr/bin/env python3
import os, re, queue, sys, json, time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from translate_sentence import generate_asl_video

lang_choice = input("Choisissez la langue (en/fr/ar) : ").strip().lower()
model_paths = { "en":"vosk-model-en-us-0.22", "fr":"vosk-model-fr-0.22", "ar":"vosk-model-ar-mgb2-0.4" }
lang = {"fr":"fr","ar":"ar"}.get(lang_choice,"en")
model_path = model_paths[lang]
model      = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

q = queue.Queue()
def callback(indata, frames, time_, status):
    if status: print(status, file=sys.stderr)
    q.put(bytes(indata))

CLASS_LIST      = "WLASL/wlasl_class_list.txt"
NSLT_JSON       = "WLASL/nslt_2000.json"
VIDEOS_DIR      = "WLASL/videos"
MANUAL_REORDERS = "manual_reorders.json"
ASL_OUT_DIR     = "asl_outputs"
os.makedirs(ASL_OUT_DIR, exist_ok=True)
manual_rules = json.load(open(MANUAL_REORDERS, encoding="utf-8")) if os.path.isfile(MANUAL_REORDERS) else {}

with sd.RawInputStream(samplerate=16000, blocksize=4000,
                       dtype="int16", channels=1,
                       callback=callback):
    print("🎤 Parlez… (Ctrl-C pour quitter)")
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

            print(f"STT ➔ «{cleaned}»")
            timestamp = int(time.time())
            out_file  = os.path.join(ASL_OUT_DIR, f"asl_{timestamp}.mp4")

            generate_asl_video(
                phrase=          cleaned,
                class_list_path= CLASS_LIST,
                nslt_json_path=  NSLT_JSON,
                videos_dir=      VIDEOS_DIR,
                out_path=        out_file,
                manual_reorders= manual_rules
            )

            print(f"🎞 ASL généré → {out_file}\n")

    except KeyboardInterrupt:
        print("\n👋 Arrêt !")
        sys.exit(0)
