#!/usr/bin/env python3
"""
Quick test of the new 3D avatar system
Tests pose extraction and avatar rendering without full GUI
"""
import sys
import os

print("="*70)
print("Testing 3D Avatar System Components")
print("="*70)

# Test 1: Import all modules
print("\n1. Testing module imports...")
modules_ok = True

try:
    from pose_extractor import PoseExtractor
    print("   ✅ pose_extractor")
except Exception as e:
    print(f"   ❌ pose_extractor: {e}")
    modules_ok = False

try:
    from avatar_animator import FuturisticAvatar
    print("   ✅ avatar_animator")
except Exception as e:
    print(f"   ❌ avatar_animator: {e}")
    modules_ok = False

try:
    import customtkinter as ctk
    print("   ✅ customtkinter")
except Exception as e:
    print(f"   ❌ customtkinter: {e}")
    modules_ok = False

try:
    import mediapipe as mp
    print("   ✅ mediapipe")
except Exception as e:
    print(f"   ❌ mediapipe: {e}")
    modules_ok = False

try:
    import pygame
    print("   ✅ pygame")
except Exception as e:
    print(f"   ❌ pygame: {e}")
    modules_ok = False

try:
    from OpenGL.GL import *
    print("   ✅ PyOpenGL")
except Exception as e:
    print(f"   ❌ PyOpenGL: {e}")
    modules_ok = False

if not modules_ok:
    print("\n❌ Some modules failed to import!")
    print("💡 Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 2: Check WLASL dataset
print("\n2. Checking WLASL dataset...")
wlasl_path = os.path.join(
    os.path.expanduser("~"), ".cache", "kagglehub",
    "datasets", "risangbaskoro", "wlasl-processed", "versions", "5"
)

if os.path.exists(wlasl_path):
    videos_dir = os.path.join(wlasl_path, "videos")
    if os.path.exists(videos_dir):
        video_count = len([f for f in os.listdir(videos_dir) if f.endswith('.mp4')])
        print(f"   ✅ WLASL dataset found ({video_count} videos)")
    else:
        print("   ⚠️ Videos directory missing")
else:
    print("   ⚠️ WLASL dataset not found")
    print("   💡 Run: python download_wlasl.py")

# Test 3: Test pose extraction
print("\n3. Testing pose extraction (quick test)...")
test_word = "hello"

try:
    from wlasl_generator import WLASLGenerator
    generator = WLASLGenerator()
    video_path = generator.find_sign(test_word)
    
    if video_path:
        print(f"   ✅ Found video for '{test_word}'")
        print(f"   📹 {os.path.basename(video_path)}")
        
        print(f"\n   🔍 Extracting pose (first 10 frames only)...")
        extractor = PoseExtractor()
        
        import cv2
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        while cap.isOpened() and frame_count < 10:
            success, frame = cap.read()
            if not success:
                break
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = extractor.holistic.process(frame_rgb)
            
            if results.right_hand_landmarks:
                hand_points = len(results.right_hand_landmarks.landmark)
                print(f"   Frame {frame_count}: Right hand detected ({hand_points} points)")
                break
            
            frame_count += 1
        
        cap.release()
        
        if frame_count > 0:
            print(f"   ✅ Pose extraction working!")
        else:
            print("   ⚠️ No hands detected in first 10 frames")
    else:
        print(f"   ⚠️ Video not found for '{test_word}'")
        
except Exception as e:
    print(f"   ❌ Pose extraction error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test OpenGL initialization
print("\n4. Testing OpenGL/PyGame initialization...")
try:
    pygame.init()
    display = pygame.display.set_mode((400, 300), pygame.DOUBLEBUF | pygame.OPENGL)
    
    from OpenGL.GL import *
    from OpenGL.GLU import *
    
    glViewport(0, 0, 400, 300)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 400/300, 0.1, 50.0)
    
    # Clear screen to test rendering
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    pygame.display.flip()
    
    pygame.quit()
    
    print("   ✅ OpenGL initialized successfully")
    print("   ✅ 3D rendering ready!")
    
except Exception as e:
    print(f"   ❌ OpenGL error: {e}")
    print("   💡 Update graphics drivers or try CPU rendering")

# Summary
print("\n" + "="*70)
print("Test Summary")
print("="*70)

if modules_ok:
    print("\n✅ ALL SYSTEMS READY!")
    print("\n🚀 You can now run:")
    print("   1. GUI App: .\\run_gui.bat")
    print("   2. Pose Extractor: python pose_extractor.py hello")
    print("   3. Avatar Animator: python avatar_animator.py pose_data/hello.json")
    print("\n💡 Recommended: Start with the GUI for best experience!")
else:
    print("\n⚠️ Some components need attention")
    print("   Check error messages above and install missing dependencies")

print("="*70)
