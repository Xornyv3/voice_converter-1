#!/usr/bin/env python3
"""
Pose Extractor - Extract hand, body, and face landmarks from ASL videos using MediaPipe
Converts video movements into pose data that can be used to animate a 3D avatar
"""
import os
import cv2
import json
import mediapipe as mp
import numpy as np
from pathlib import Path

class PoseExtractor:
    """Extract pose landmarks from ASL videos using MediaPipe Holistic"""
    
    def __init__(self):
        """Initialize MediaPipe Holistic solution"""
        print("🔧 Initializing MediaPipe Holistic...")
        
        # Initialize MediaPipe solutions
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Create holistic model
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,  # 0=Lite, 1=Full, 2=Heavy
            enable_segmentation=False,
            refine_face_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        print("✅ MediaPipe ready!")
    
    def extract_from_video(self, video_path, max_frames=None):
        """
        Extract pose landmarks from a video file
        
        Args:
            video_path: Path to video file
            max_frames: Maximum frames to process (None = all)
        
        Returns:
            dict with pose data: {
                'frames': list of frame data,
                'fps': video fps,
                'duration': video duration
            }
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        print(f"📹 Processing: {os.path.basename(video_path)}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        print(f"   FPS: {fps:.1f} | Frames: {frame_count} | Duration: {duration:.1f}s")
        
        frames_data = []
        frame_idx = 0
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            if max_frames and frame_idx >= max_frames:
                break
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.holistic.process(frame_rgb)
            
            # Extract landmarks
            frame_data = {
                'frame_idx': frame_idx,
                'timestamp': frame_idx / fps if fps > 0 else 0,
                'pose': self._landmarks_to_list(results.pose_landmarks),
                'left_hand': self._landmarks_to_list(results.left_hand_landmarks),
                'right_hand': self._landmarks_to_list(results.right_hand_landmarks),
                'face': self._landmarks_to_list(results.face_landmarks)
            }
            
            frames_data.append(frame_data)
            frame_idx += 1
            
            # Progress indicator
            if frame_idx % 30 == 0:
                print(f"   Processed {frame_idx}/{frame_count} frames...", end='\r')
        
        cap.release()
        
        print(f"\n✅ Extracted {len(frames_data)} frames of pose data")
        
        return {
            'frames': frames_data,
            'fps': fps,
            'duration': duration,
            'frame_count': len(frames_data)
        }
    
    def _landmarks_to_list(self, landmarks):
        """Convert MediaPipe landmarks to list of coordinates"""
        if not landmarks:
            return None
        
        return [
            {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility if hasattr(landmark, 'visibility') else 1.0
            }
            for landmark in landmarks.landmark
        ]
    
    def extract_from_wlasl_word(self, word, wlasl_dir=None, output_dir="pose_data"):
        """
        Extract pose data from WLASL video for a specific word
        
        Args:
            word: ASL word to extract
            wlasl_dir: WLASL dataset directory
            output_dir: Where to save extracted pose data
        
        Returns:
            Path to saved JSON file
        """
        # Default WLASL path
        if wlasl_dir is None:
            wlasl_dir = os.path.join(
                os.path.expanduser("~"), ".cache", "kagglehub",
                "datasets", "risangbaskoro", "wlasl-processed", "versions", "5"
            )
        
        # Find video for this word
        from wlasl_generator import WLASLGenerator
        generator = WLASLGenerator(wlasl_dir)
        
        video_path = generator.find_sign(word.lower())
        
        if not video_path:
            raise ValueError(f"No WLASL video found for word: {word}")
        
        print(f"\n🎯 Extracting pose for '{word}'")
        print(f"   Video: {os.path.basename(video_path)}")
        
        # Extract pose data
        pose_data = self.extract_from_video(video_path)
        pose_data['word'] = word
        pose_data['video_path'] = video_path
        
        # Save to JSON
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{word.lower()}.json")
        
        with open(output_file, 'w') as f:
            json.dump(pose_data, f, indent=2)
        
        print(f"💾 Saved pose data: {output_file}")
        
        return output_file
    
    def visualize_pose(self, video_path, output_path=None):
        """
        Create visualization of extracted poses overlaid on video
        
        Args:
            video_path: Input video
            output_path: Output video with pose overlay (None = display only)
        """
        print(f"🎨 Visualizing poses from: {os.path.basename(video_path)}")
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer if saving
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            # Convert to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.holistic.process(frame_rgb)
            
            # Draw landmarks on frame
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
            
            if results.left_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style()
                )
            
            if results.right_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style()
                )
            
            # Save or display
            if writer:
                writer.write(frame)
            else:
                cv2.imshow('MediaPipe Holistic', frame)
                if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
                    break
        
        cap.release()
        if writer:
            writer.release()
            print(f"✅ Saved visualization: {output_path}")
        else:
            cv2.destroyAllWindows()
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'holistic'):
            self.holistic.close()


# CLI usage
if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("MediaPipe Pose Extractor for ASL Videos")
    print("="*70)
    
    extractor = PoseExtractor()
    
    # Test with a WLASL word
    test_word = sys.argv[1] if len(sys.argv) > 1 else "hello"
    
    try:
        print(f"\n🎯 Testing with word: '{test_word}'")
        output_file = extractor.extract_from_wlasl_word(test_word)
        
        print(f"\n✅ Success! Pose data saved to: {output_file}")
        print("\n💡 You can now use this data to animate a 3D avatar!")
        
        # Load and show summary
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        print(f"\n📊 Pose Data Summary:")
        print(f"   Word: {data['word']}")
        print(f"   Frames: {data['frame_count']}")
        print(f"   Duration: {data['duration']:.2f}s")
        print(f"   FPS: {data['fps']:.1f}")
        
        # Check first frame
        if data['frames']:
            frame = data['frames'][0]
            print(f"\n   First frame landmarks:")
            print(f"     - Pose points: {len(frame['pose']) if frame['pose'] else 0}")
            print(f"     - Left hand: {len(frame['left_hand']) if frame['left_hand'] else 0}")
            print(f"     - Right hand: {len(frame['right_hand']) if frame['right_hand'] else 0}")
            print(f"     - Face: {len(frame['face']) if frame['face'] else 0}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
