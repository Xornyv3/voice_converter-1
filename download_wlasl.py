#!/usr/bin/env python3
"""
Download WLASL processed dataset using kagglehub
This is the proper word-level ASL dataset for video generation
"""
import os
import sys

print("=" * 70)
print("WLASL Dataset Downloader (Word-Level ASL Videos)")
print("=" * 70)
print()

try:
    import kagglehub
    print("✅ kagglehub library found")
except ImportError:
    print("Installing kagglehub...")
    os.system(f"{sys.executable} -m pip install kagglehub")
    import kagglehub
    print("✅ kagglehub installed")

print("\n📥 Downloading WLASL processed dataset...")
print("ℹ️  This may take several minutes depending on your connection...")
print()

try:
    # Download latest version
    path = kagglehub.dataset_download("risangbaskoro/wlasl-processed")
    
    print("\n" + "=" * 70)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 70)
    print(f"\nDataset location: {path}")
    print("\nExploring dataset structure...")
    
    # Show what was downloaded
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}📁 {os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files[:10]:  # Show first 10 files
            size = os.path.getsize(os.path.join(root, file)) / (1024*1024)
            print(f'{subindent}📄 {file} ({size:.1f} MB)')
        if len(files) > 10:
            print(f'{subindent}... and {len(files)-10} more files')
        if level > 2:  # Don't go too deep
            break
    
    print("\n" + "=" * 70)
    print("Next step: Integrating with voice converter...")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error downloading dataset: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Make sure you're logged into Kaggle")
    print("3. Verify you have enough disk space")
    import traceback
    traceback.print_exc()
    sys.exit(1)
