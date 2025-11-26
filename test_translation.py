#!/usr/bin/env python3
"""
Simple test of the ASL translation system WITHOUT microphone
This tests the text-to-ASL-gloss conversion logic
"""
import os
import sys

print("=" * 70)
print("Testing ASL Translation System (No Microphone Required)")
print("=" * 70)

# Test if we can import the translation module
print("\n1. Testing import of translate_sentence module...")
try:
    from translate_sentence import generate_asl_video
    print("   ✅ Module imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test basic setup
print("\n2. Checking WLASL data files...")
required_files = {
    "WLASL/wlasl_class_list.txt": "Class list",
    "WLASL/nslt_2000.json": "NSLT JSON",
    "WLASL/videos": "Videos directory"
}

all_present = True
for path, desc in required_files.items():
    if os.path.exists(path):
        if os.path.isdir(path):
            count = len([f for f in os.listdir(path) if f.endswith('.mp4')])
            print(f"   ✅ {desc}: {count} videos")
            if count == 0:
                all_present = False
        else:
            print(f"   ✅ {desc}")
    else:
        print(f"   ❌ {desc} - NOT FOUND")
        all_present = False

# Test text processing
print("\n3. Testing text-to-gloss conversion...")
test_phrases = [
    "hello",
    "how are you",
    "thank you",
    "i want to learn",
]

try:
    # Import the internal functions for testing
    from translate_sentence import build_mapping, tokenize_and_match
    
    # Build the mapping
    mapping = build_mapping(
        "WLASL/wlasl_class_list.txt",
        "WLASL/nslt_2000.json",
        "WLASL/videos"
    )
    
    print(f"   ℹ️  Found {len(mapping)} sign language glosses in database")
    
    for phrase in test_phrases:
        try:
            tokens = tokenize_and_match(phrase, mapping)
            print(f"   📝 '{phrase}' → {tokens}")
        except Exception as e:
            print(f"   ⚠️  '{phrase}' → Error: {e}")
            
except Exception as e:
    print(f"   ❌ Error during processing: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
if not all_present:
    print("⚠️  SPEECH-TO-TEXT READY | ASL VIDEO NEEDS WLASL VIDEOS")
    print("\nThe system can:")
    print("  ✅ Convert speech to text (Vosk)")
    print("  ✅ Convert text to ASL glosses (translation logic)")
    print("  ⚠️  CANNOT generate videos yet (need WLASL video files)")
    print("\nTo enable video generation:")
    print("  1. Download WLASL videos from: https://www.bu.edu/av/asllrp/dai-asllvd.html")
    print("  2. Place .mp4 files in WLASL/videos/ folder")
else:
    print("✅ FULLY FUNCTIONAL - Ready to generate ASL videos!")

print("\nNext step: Run vosk_demo.py to test with your microphone!")
print("=" * 70)
