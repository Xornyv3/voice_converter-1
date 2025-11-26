# Voice to Sign Language - Setup Complete! ✅

## Installation Status

✅ Python environment configured (Python 3.13.7)
✅ All dependencies installed:
- vosk (speech recognition)
- sounddevice (audio recording)
- numpy (numerical processing)
- moviepy (video processing)
- num2words (number conversion)
- arabic-reshaper & python-bidi (Arabic support)
- openai-whisper (alternative speech recognition)
- pyaudio (audio I/O)

✅ Vosk English model found: `vosk-model-en-us-0.22`
✅ WLASL data files present
✅ Videos directory created

## ⚠️ IMPORTANT: Missing ASL Videos

The WLASL video dataset is NOT included in this repository. You need to:

1. Download WLASL videos from: https://www.bu.edu/av/asllrp/dai-asllvd.html
2. Place video files in: `WLASL/videos/` directory
3. Videos should be named like: `00001.mp4`, `00002.mp4`, etc.

**Without these videos, the ASL video generation will not work!**
However, speech-to-text transcription will still function.

## How to Run

### Option 1: Voice Demo with Auto-Stop (Recommended for Testing)
```bash
"D:/Users/deskt/OneDrive/Desktop/voice to sign language/voice_converter/.venv/Scripts/python.exe" vosk_demo.py
```
- Choose language: `en` (English)
- Speak into your microphone
- Stops automatically after 5 seconds of silence
- Generates transcript and ASL video (if videos available)

### Option 2: Continuous Pipeline
```bash
"D:/Users/deskt/OneDrive/Desktop/voice to sign language/voice_converter/.venv/Scripts/python.exe" vosk_pipeline.py
```
- Continuous listening mode
- Press Ctrl+C to stop
- Processes each sentence as you speak

### Option 3: Whisper Live Captioning
```bash
"D:/Users/deskt/OneDrive/Desktop/voice to sign language/voice_converter/.venv/Scripts/python.exe" start.py
```
- Uses OpenAI Whisper model (downloads on first run ~240MB)
- Real-time captions
- English only

## Quick Test (Text-to-Text only)

Since you might not have the videos yet, you can test the speech recognition:

1. Run: `"D:/Users/deskt/OneDrive/Desktop/voice to sign language/voice_converter/.venv/Scripts/python.exe" vosk_demo.py`
2. Type: `en` when prompted
3. Say something like "Hello, how are you today?"
4. Wait 5 seconds of silence
5. You should see the transcript

The system will attempt to generate ASL video but will warn if videos are missing.

## Troubleshooting

### Microphone Issues
- Make sure your microphone is connected and working
- Check Windows sound settings
- Grant microphone permissions to Python

### Model Missing
- Download from: https://alphacephei.com/vosk/models
- Extract to project root
- Folder should be named exactly: `vosk-model-en-us-0.22`

### French/Arabic Support
You need to download additional models:
- French: `vosk-model-fr-0.22`
- Arabic: `vosk-model-ar-mgb2-0.4`

Place them in the project root directory.

## Next Steps

1. Download WLASL videos for full functionality
2. Test with simple phrases first
3. Check `asl_outputs/` folder for generated videos
4. Experiment with different languages (if models downloaded)

Enjoy your voice-to-sign-language converter! 🎤➡️👋
