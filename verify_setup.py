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
    "vosk",
    "sounddevice",
    "numpy",
    "moviepy",
    "num2words",
    "arabic_reshaper",
    "bidi.algorithm",
]

failed = []
for dep in dependencies:
    try:
        __import__(dep)
        print(f"   ✅ {dep}")
    except ImportError as e:
        print(f"   ❌ {dep} - {e}")
        failed.append(dep)

# Test 3: Check model
print("\n3. Checking Vosk Model:")
import os
model_path = "vosk-model-en-us-0.22"
if os.path.isdir(model_path):
    print(f"   ✅ English model found at {model_path}")
    # Check for key files
    required = ["am/final.mdl", "graph/HCLG.fst", "graph/words.txt"]
    for req in required:
        full_path = os.path.join(model_path, req)
        if os.path.exists(full_path):
            print(f"      ✅ {req}")
        else:
            print(f"      ❌ {req} missing")
else:
    print(f"   ❌ Model directory not found: {model_path}")

# Test 4: Check WLASL data
print("\n4. Checking WLASL Data:")
wlasl_files = [
    "WLASL/wlasl_class_list.txt",
    "WLASL/nslt_2000.json",
    "WLASL/videos"
]
for wf in wlasl_files:
    if os.path.exists(wf):
        if os.path.isdir(wf):
            vid_count = len([f for f in os.listdir(wf) if f.endswith('.mp4')])
            print(f"   ✅ {wf} ({vid_count} videos)")
        else:
            print(f"   ✅ {wf}")
    else:
        print(f"   ❌ {wf} missing")

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
        print("   ⚠️  No input devices found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "=" * 60)
if failed:
    print(f"❌ SETUP INCOMPLETE - Missing: {', '.join(failed)}")
else:
    print("✅ ALL DEPENDENCIES INSTALLED!")
    print("\nReady to run:")
    print('   python vosk_demo.py')
print("=" * 60)
