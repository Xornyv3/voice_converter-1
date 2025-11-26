#!/usr/bin/env python3
"""
Quick test script to verify installation
"""
import sys

print("=" * 60)
print("Testing Voice-to-Sign-Language Installation")
print("=" * 60)

# Test 1: Python version
print("\n1. Python Version:")
print(f"   {sys.version}")

# Test 2: Import dependencies
print("\n2. Testing Dependencies:")
dependencies = [
    "faster_whisper",
    "sounddevice",
    "numpy",
    "moviepy",
    "kagglehub",
]

failed = []
for dep in dependencies:
    try:
        __import__(dep)
        print(f"   ✅ {dep}")
    except ImportError as e:
        print(f"   ❌ {dep} - {e}")
        failed.append(dep)

# Test 3: Check WLASL dataset
print("\n3. Checking WLASL Dataset:")
import os
wlasl_path = os.path.join(os.path.expanduser("~"), ".cache", "kagglehub", 
                          "datasets", "risangbaskoro", "wlasl-processed", "versions", "5")
if os.path.exists(wlasl_path):
    videos_dir = os.path.join(wlasl_path, "videos")
    if os.path.exists(videos_dir):
        video_count = len([f for f in os.listdir(videos_dir) if f.endswith('.mp4')])
        print(f"   ✅ WLASL dataset found")
        print(f"   ✅ Videos: {video_count}")
    else:
        print(f"   ⚠️ Videos directory not found")
else:
    print(f"   ❌ WLASL dataset not found")
    print(f"   💡 Run: python download_wlasl.py")

# Test 4: Check Faster-Whisper model cache
print("\n4. Checking Faster-Whisper Model:")
model_cache = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", 
                           "hub", "models--Systran--faster-whisper-base")
if os.path.exists(model_cache):
    print(f"   ✅ Base model cached")
else:
    print(f"   ⚠️ Model not cached (will download on first run)")

# Test 5: Microphone
print("\n5. Testing Microphone Access:")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    if input_devices:
        print(f"   ✅ Found {len(input_devices)} input device(s)")
        default = sd.query_devices(kind='input')
        print(f"   Default: {default['name']}")
    else:
        print("   ⚠️ No input devices found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "=" * 60)
if failed:
    print(f"❌ SETUP INCOMPLETE - Missing: {', '.join(failed)}")
    print("\n💡 Install missing packages:")
    print("   pip install " + " ".join(failed))
else:
    print("✅ ALL DEPENDENCIES INSTALLED!")
    print("\nReady to run:")
    print("   .\\run_demo.bat (or .\\run_demo.ps1)")
    print("\nChoose option 1 to start!")
print("=" * 60)
