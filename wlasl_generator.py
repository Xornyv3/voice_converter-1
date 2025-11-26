#!/usr/bin/env python3
"""
WLASL Video Generator - Optimized for word-level ASL video generation
Converts English text to ASL video sequences using the WLASL processed dataset
"""
import os
import json
import re
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips

# WLASL dataset path (from kagglehub)
WLASL_CACHE_PATH = os.path.join(os.path.expanduser("~"), ".cache", "kagglehub", 
                                 "datasets", "risangbaskoro", "wlasl-processed", "versions", "5")

# Project paths
OUTPUT_DIR = "asl_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class WLASLGenerator:
    """Optimized WLASL video generator"""
    
    def __init__(self, wlasl_dir=None):
        """Initialize with WLASL dataset directory"""
        self.wlasl_dir = wlasl_dir or WLASL_CACHE_PATH
        
        if not os.path.exists(self.wlasl_dir):
            raise FileNotFoundError(
                f"WLASL dataset not found at {self.wlasl_dir}\n"
                f"Run: python download_wlasl.py"
            )
        
        # Load metadata
        self.class_list = os.path.join(self.wlasl_dir, "wlasl_class_list.txt")
        self.nslt_json = os.path.join(self.wlasl_dir, "nslt_2000.json")
        self.videos_dir = os.path.join(self.wlasl_dir, "videos")
        
        # Build word-to-video mapping
        print("📚 Loading WLASL vocabulary...")
        self.word_to_video = self._build_mapping()
        print(f"✅ Loaded {len(self.word_to_video)} ASL signs")
    
    def _build_mapping(self):
        """Build optimized word to video file mapping"""
        mapping = {}
        
        # Load class list (word -> class_id)
        word_to_class = {}
        with open(self.class_list, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    class_id = int(parts[0])
                    word = " ".join(parts[1:]).lower()
                    word_to_class[word] = class_id
        
        # Load video metadata (video_id -> class_id)
        with open(self.nslt_json, 'r', encoding='utf-8') as f:
            video_meta = json.load(f)
        
        # Map class_id to video files
        class_to_videos = {}
        for video_id, meta in video_meta.items():
            action = meta.get("action")
            if isinstance(action, list) and action:
                class_id = int(action[0])
                if class_id not in class_to_videos:
                    class_to_videos[class_id] = []
                class_to_videos[class_id].append(video_id)
        
        # Build final word -> video path mapping (use first available video)
        for word, class_id in word_to_class.items():
            if class_id in class_to_videos:
                for video_id in class_to_videos[class_id]:
                    video_path = os.path.join(self.videos_dir, f"{int(video_id):05d}.mp4")
                    if os.path.exists(video_path):
                        mapping[word] = video_path
                        break
        
        return mapping
    
    def text_to_words(self, text):
        """Convert text to list of words, handling common ASL patterns"""
        # Clean text
        text = text.lower().strip()
        
        # Remove punctuation but keep spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Split into words
        words = text.split()
        
        return words
    
    def find_sign(self, word):
        """Find video for a word, with fallback strategies"""
        # Direct match
        if word in self.word_to_video:
            return self.word_to_video[word]
        
        # Try without common suffixes
        for suffix in ['s', 'ed', 'ing', 'ly']:
            if word.endswith(suffix):
                base = word[:-len(suffix)]
                if base in self.word_to_video:
                    return self.word_to_video[base]
        
        # Try common variations
        variations = [
            word.replace('dont', "don't"),
            word.replace('cant', "can't"),
            word.replace('wont', "won't"),
        ]
        for var in variations:
            if var in self.word_to_video:
                return self.word_to_video[var]
        
        return None
    
    def generate_video(self, text, output_path=None):
        """
        Generate ASL video from text
        
        Args:
            text: English text to convert
            output_path: Where to save video (auto-generated if None)
        
        Returns:
            Path to generated video
        """
        words = self.text_to_words(text)
        
        if not words:
            raise ValueError("No words to convert")
        
        print(f"\n🎬 Converting: '{text}'")
        print(f"📝 Words: {words}")
        
        # Find videos for each word
        clips_to_concat = []
        found_words = []
        missing_words = []
        
        for word in words:
            video_path = self.find_sign(word)
            if video_path:
                try:
                    clip = VideoFileClip(video_path)
                    clips_to_concat.append(clip)
                    found_words.append(word)
                    print(f"  ✅ '{word}' → {os.path.basename(video_path)}")
                except Exception as e:
                    print(f"  ⚠️  '{word}' - Error loading video: {e}")
                    missing_words.append(word)
            else:
                print(f"  ❌ '{word}' - No sign found")
                missing_words.append(word)
        
        if not clips_to_concat:
            raise ValueError(f"No videos found for any words in: {text}")
        
        # Generate output path if not provided
        if output_path is None:
            safe_text = re.sub(r'[^\w\s]', '', text)[:30].replace(' ', '_')
            timestamp = int(__import__('time').time())
            output_path = os.path.join(OUTPUT_DIR, f"asl_{safe_text}_{timestamp}.mp4")
        
        # Concatenate videos
        print(f"\n🎞️  Concatenating {len(clips_to_concat)} video clips...")
        final_clip = concatenate_videoclips(clips_to_concat, method="compose")
        
        # Write output
        print(f"💾 Writing video to: {output_path}")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio=False  # ASL videos don't need audio
        )
        
        # Clean up
        for clip in clips_to_concat:
            clip.close()
        final_clip.close()
        
        # Summary
        print(f"\n✅ Video generated successfully!")
        print(f"📊 Statistics:")
        print(f"   - Total words: {len(words)}")
        print(f"   - Found: {len(found_words)}")
        print(f"   - Missing: {len(missing_words)}")
        if missing_words:
            print(f"   - Missing words: {', '.join(missing_words)}")
        print(f"\n📁 Output: {output_path}")
        
        return output_path


# Standalone usage
if __name__ == "__main__":
    import sys
    
    # Test text
    test_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hello how are you"
    
    try:
        generator = WLASLGenerator()
        output = generator.generate_video(test_text)
        print(f"\n🎉 Success! Video saved to: {output}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
