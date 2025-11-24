# start.py  –  minimal live-caption demo
import queue, sys, threading
import whisper, pyaudio, numpy as np

# 1) load the speech-to-text model (first run will download ±240 MB)
model = whisper.load_model("small.en")      # use "small" for other languages

RATE  = 16_000      # microphone sample-rate
CHUNK = RATE // 2   # 0.5-second chunks

audio_q = queue.Queue()

def capture():
    """Background thread that pushes audio chunks into audio_q."""
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=CHUNK)
    while True:
        audio_q.put(stream.read(CHUNK))

threading.Thread(target=capture, daemon=True).start()

print("🎤  Speak…  (Ctrl-C to quit)\n")

while True:
    raw = audio_q.get()                                    # 0.5 s of audio
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    result = model.transcribe(audio, language="en", fp16=False)
    sys.stdout.write('\r' + result["text"].strip() + ' ' * 10)
    sys.stdout.flush()
