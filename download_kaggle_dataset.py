#!/usr/bin/env python3
"""
Download ASL dataset from Kaggle using API
Much smaller than WLASL - only images, not videos
"""
import os
import sys

print("=" * 70)
print("Kaggle ASL Dataset Downloader")
print("=" * 70)

# Check if kaggle is installed
try:
    import kaggle
    print("✅ Kaggle library found")
except ImportError:
    print("❌ Kaggle library not installed")
    print("\nInstalling kaggle...")
    os.system("pip install kaggle")
    print("\n✅ Kaggle installed")

print("\n" + "=" * 70)
print("SETUP INSTRUCTIONS:")
print("=" * 70)
print("""
1. Go to: https://www.kaggle.com/settings/account
2. Scroll to 'API' section
3. Click 'Create New Token'
4. This downloads 'kaggle.json' to your Downloads folder

5. Move kaggle.json to: C:\\Users\\deskt\\.kaggle\\kaggle.json
   (Create the .kaggle folder if it doesn't exist)

6. Run this script again
""")

# Check if kaggle.json exists
kaggle_dir = os.path.expanduser("~/.kaggle")
kaggle_json = os.path.join(kaggle_dir, "kaggle.json")

if not os.path.exists(kaggle_json):
    print("⚠️  kaggle.json not found at:", kaggle_json)
    print("\nPlease follow the setup instructions above.")
    sys.exit(1)

print("✅ Found kaggle.json")

# Download the dataset
print("\n" + "=" * 70)
print("Downloading ASL Dataset from Kaggle...")
print("=" * 70)

dataset = "ayuraj/asl-dataset"
output_dir = "kaggle_asl_dataset"

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    
    print(f"\n📥 Downloading: {dataset}")
    print(f"📂 To folder: {output_dir}")
    print("\nThis may take a few minutes...")
    
    api.dataset_download_files(dataset, path=output_dir, unzip=True)
    
    print("\n" + "=" * 70)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 70)
    print(f"\nDataset location: {os.path.abspath(output_dir)}")
    print("\nContents:")
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isdir(item_path):
            count = len(os.listdir(item_path))
            print(f"  📁 {item}/ ({count} items)")
        else:
            size = os.path.getsize(item_path) / (1024*1024)
            print(f"  📄 {item} ({size:.1f} MB)")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("1. You have internet connection")
    print("2. kaggle.json is in the right location")
    print("3. You accepted the dataset terms on Kaggle website")
    sys.exit(1)
