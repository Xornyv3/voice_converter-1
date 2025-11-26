#!/usr/bin/env python3
"""
Faster-Whisper Voice to Sign Language Converter
All models auto-download on first run - no manual setup needed!
"""
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sounddevice as sd
import numpy as np
import time
import sys

# Check and install dependencies on first run
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("📦 First-time setup: Installing Faster-Whisper...")
    print("   This will download dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "faster-whisper", "--quiet"])
    from faster_whisper import WhisperModel
    print("✅ Installation complete!\n")

try:
    from wlasl_generator import WLASLGenerator
except ImportError:
    print("⚠️ WLASL generator not found. Video generation disabled.")
    WLASLGenerator = None

class FasterWhisperVoiceConverter:
    def __init__(self, model_size="base"):
        """
        Initialize Faster-Whisper model (auto-downloads on first run)
        
        Model sizes (download size):
        - tiny: ~75MB - Fastest, basic accuracy
        - base: ~150MB - Best balance (RECOMMENDED) ⭐
        - small: ~500MB - Better accuracy
        - medium: ~1.5GB - Very accurate
        - large: ~3GB - Best accuracy
        """
        print(f"📥 Loading Faster-Whisper '{model_size}' model...")
        print("   (First run: auto-downloads ~150MB model, then cached)")
        start = time.time()
        
        try:
            # Auto-downloads model on first run, caches for future use
            self.model = WhisperModel(
                model_size, 
                device="cpu",  # Use "cuda" if you have NVIDIA GPU
                compute_type="int8",  # Fast inference
                download_root=None  # Auto-downloads to default cache
            )
            
            load_time = time.time() - start
            print(f"✅ Model loaded in {load_time:.1f}s!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("   Trying to download model...")
            # Force download
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # Initialize video generator if available
        if WLASLGenerator:
            try:
                self.generator = WLASLGenerator()
                print("✅ WLASL video generator loaded")
            except:
                self.generator = None
                print("⚠️ Video generation disabled (WLASL not found)")
        else:
            self.generator = None
            print("⚠️ Video generation disabled (WLASL not found)")
        
        self.sample_rate = 16000
    
    def record_audio(self, silence_threshold=0.01, silence_duration=3):
        """Record audio with auto-stop on silence"""
        print(f"\n🎤 Recording... Speak now. Auto-stops after {silence_duration}s of silence (or Ctrl+C).")
        
        audio_data = []
        silence_frames = 0
        silence_limit = int(silence_duration * self.sample_rate / 1024)
        
        def callback(indata, frames, time_info, status):
            nonlocal silence_frames
            audio_data.append(indata.copy())
            
            # Detect silence
            volume = np.abs(indata).mean()
            if volume < silence_threshold:
                silence_frames += 1
            else:
                silence_frames = 0
                print("    🔊 Listening...", end='\r')
        
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, 
                              dtype='float32', callback=callback, blocksize=1024):
                while True:
                    if silence_frames >= silence_limit:
                        print("\n✋ Auto-stopped (silence detected)          ")
                        break
                    sd.sleep(100)
        except KeyboardInterrupt:
            print("\n✋ Stopped by user")
        
        if not audio_data:
            return None
        
        # Convert to numpy array
        audio_np = np.concatenate(audio_data, axis=0)
        return audio_np
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio using Faster-Whisper"""
        if audio_data is None:
            return ""
        
        print("🔄 Transcribing...")
        start = time.time()
        
        try:
            # Faster-Whisper transcription with VAD
            segments, info = self.model.transcribe(
                audio_data.flatten(),
                language="en",
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine all segments
            text = " ".join([segment.text for segment in segments]).strip()
            
            transcribe_time = time.time() - start
            
            if text:
                print(f"✅ Transcribed in {transcribe_time:.1f}s")
                print(f"   Text: \"{text}\"")
            else:
                print("⚠️ No speech detected")
            
            return text
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""
    
    def generate_video(self, text):
        """Generate ASL video from text"""
        if not text:
            return None
        
        if not self.generator:
            print("⚠️ Video generation skipped (WLASL not available)")
            return None
        
        print(f"\n🎬 Generating ASL video...")
        try:
            output_path = self.generator.generate_video(text)
            
            if output_path:
                print(f"✅ Video saved: {output_path}")
                return output_path
            else:
                print("❌ Video generation failed")
                return None
        except Exception as e:
            print(f"❌ Video generation error: {e}")
            return None
    
    def run(self):
        """Main pipeline: Record → Transcribe → Generate Video"""
        print("\n" + "="*60)
        print("🎙️ Faster-Whisper Voice to Sign Language Converter")
        print("="*60)
        print("💡 All models auto-download - no manual setup needed!")
        print("="*60 + "\n")
        
        while True:
            try:
                # Record audio
                audio = self.record_audio(silence_duration=3)
                
                # Transcribe
                text = self.transcribe_audio(audio)
                
                # Generate video
                if text:
                    self.generate_video(text)
                
                # Ask to continue
                print("\n" + "-"*60)
                response = input("🔄 Record again? (y/n): ").lower()
                if response != 'y':
                    print("👋 Goodbye!")
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    try:
        # Use "base" model - auto-downloads ~150MB on first run
        # Change to "tiny" for faster (75MB) or "small" for better accuracy (500MB)
        converter = FasterWhisperVoiceConverter(model_size="base")
        converter.run()
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
