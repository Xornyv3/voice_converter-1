#!/usr/bin/env python3
"""
GUI Application - Visual Interface for Voice to Sign Language with Avatar
Beautiful modern interface using CustomTkinter
"""
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import customtkinter as ctk
import threading
import time
from pathlib import Path
import json

# Import our modules
try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

try:
    from wlasl_generator import WLASLGenerator
except ImportError:
    WLASLGenerator = None

try:
    from pose_extractor import PoseExtractor
except ImportError:
    PoseExtractor = None

try:
    from avatar_animator import FuturisticAvatar
except ImportError:
    FuturisticAvatar = None

import sounddevice as sd
import numpy as np

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VoiceToSignLanguageApp:
    """Main GUI application"""
    
    def __init__(self):
        """Initialize the application"""
        self.root = ctk.CTk()
        self.root.title("Voice to Sign Language - Avatar Edition")
        self.root.geometry("1200x800")
        
        # State variables
        self.is_recording = False
        self.current_audio = None
        self.current_text = ""
        self.current_pose_file = None
        self.processing_stage = "idle"
        
        # Models (lazy loaded)
        self.whisper_model = None
        self.wlasl_generator = None
        self.pose_extractor = None
        
        # Setup UI
        self.setup_ui()
        
        # Load models in background
        threading.Thread(target=self.load_models, daemon=True).start()
    
    def setup_ui(self):
        """Create the user interface"""
        
        # Main container
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_container,
            text="🎤 Voice to Sign Language Converter",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        subtitle = ctk.CTkLabel(
            main_container,
            text="Speak → Transcribe → Generate → Animate with Futuristic Avatar",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 30))
        
        # Control Panel
        control_frame = ctk.CTkFrame(main_container)
        control_frame.pack(fill="x", pady=(0, 20))
        
        # Record Button (main action)
        self.record_btn = ctk.CTkButton(
            control_frame,
            text="🎤 Click to Record",
            command=self.toggle_recording,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        self.record_btn.pack(pady=20, padx=20)
        
        # Status Display
        status_frame = ctk.CTkFrame(main_container)
        status_frame.pack(fill="both", expand=True)
        
        # Progress section
        progress_label = ctk.CTkLabel(
            status_frame,
            text="Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        progress_label.pack(pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        self.stage_label = ctk.CTkLabel(
            status_frame,
            text="Status: Ready",
            font=ctk.CTkFont(size=14),
            text_color="cyan"
        )
        self.stage_label.pack(pady=5)
        
        # Transcription Display
        transcription_frame = ctk.CTkFrame(status_frame)
        transcription_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            transcription_frame,
            text="📝 Transcription:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.transcription_text = ctk.CTkTextbox(
            transcription_frame,
            height=80,
            font=ctk.CTkFont(size=16)
        )
        self.transcription_text.pack(fill="x", padx=10, pady=(0, 10))
        self.transcription_text.insert("1.0", "Your transcribed speech will appear here...")
        self.transcription_text.configure(state="disabled")
        
        # Avatar Display Info
        avatar_frame = ctk.CTkFrame(status_frame)
        avatar_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            avatar_frame,
            text="🤖 Avatar Animation",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.avatar_info = ctk.CTkLabel(
            avatar_frame,
            text="Avatar will appear in a separate window after processing",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.avatar_info.pack(pady=10)
        
        # Action Buttons
        button_frame = ctk.CTkFrame(avatar_frame)
        button_frame.pack(pady=10)
        
        self.play_avatar_btn = ctk.CTkButton(
            button_frame,
            text="▶️  Play Avatar Animation",
            command=self.play_avatar,
            state="disabled",
            fg_color="#2b8a3e",
            hover_color="#1e6029"
        )
        self.play_avatar_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(
            button_frame,
            text="💾 Export Video",
            command=self.export_video,
            state="disabled",
            fg_color="#5c5f66",
            hover_color="#3d4046"
        )
        self.export_btn.pack(side="left", padx=5)
        
        # Settings/Info at bottom
        info_frame = ctk.CTkFrame(main_container)
        info_frame.pack(fill="x", pady=(10, 0))
        
        self.info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Loading models... Please wait",
            font=ctk.CTkFont(size=12),
            text_color="orange"
        )
        self.info_label.pack(pady=10)
    
    def load_models(self):
        """Load AI models in background"""
        try:
            self.update_stage("Loading Faster-Whisper model...")
            
            if WhisperModel:
                self.whisper_model = WhisperModel(
                    "base",
                    device="cpu",
                    compute_type="int8"
                )
                self.update_info("✅ Faster-Whisper loaded", "green")
            
            self.update_stage("Loading WLASL generator...")
            
            if WLASLGenerator:
                self.wlasl_generator = WLASLGenerator()
                self.update_info("✅ WLASL dataset ready", "green")
            
            self.update_stage("Loading pose extractor...")
            
            if PoseExtractor:
                self.pose_extractor = PoseExtractor()
                self.update_info("✅ MediaPipe pose extractor ready", "green")
            
            self.update_stage("Ready!")
            self.update_info("✅ All systems ready! Click to record.", "cyan")
            self.progress_bar.set(0)
            
        except Exception as e:
            self.update_info(f"❌ Error loading models: {e}", "red")
    
    def toggle_recording(self):
        """Start or stop recording"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start recording audio"""
        self.is_recording = True
        self.record_btn.configure(
            text="🔴 Recording... (Auto-stops)",
            fg_color="#d32f2f"
        )
        
        # Start recording in thread
        threading.Thread(target=self.record_audio_thread, daemon=True).start()
    
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        self.record_btn.configure(
            text="🎤 Click to Record",
            fg_color="#1f6aa5"
        )
    
    def record_audio_thread(self):
        """Record audio with silence detection"""
        try:
            self.update_stage("🎤 Recording... Speak now!")
            self.progress_bar.set(0.1)
            
            sample_rate = 16000
            audio_data = []
            silence_frames = 0
            silence_limit = int(3 * sample_rate / 1024)  # 3 seconds
            
            def callback(indata, frames, time_info, status):
                nonlocal silence_frames
                audio_data.append(indata.copy())
                
                volume = np.abs(indata).mean()
                if volume < 0.01:
                    silence_frames += 1
                else:
                    silence_frames = 0
            
            with sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                dtype='float32',
                callback=callback,
                blocksize=1024
            ):
                while self.is_recording:
                    if silence_frames >= silence_limit:
                        break
                    time.sleep(0.1)
            
            self.stop_recording()
            
            if audio_data:
                self.current_audio = np.concatenate(audio_data, axis=0)
                self.update_stage("✅ Recording complete!")
                self.progress_bar.set(0.25)
                
                # Process the audio
                self.process_audio()
            else:
                self.update_info("⚠️ No audio recorded", "orange")
                
        except Exception as e:
            self.update_info(f"❌ Recording error: {e}", "red")
            self.stop_recording()
    
    def process_audio(self):
        """Process recorded audio through the pipeline"""
        threading.Thread(target=self.process_pipeline, daemon=True).start()
    
    def process_pipeline(self):
        """Complete processing pipeline"""
        try:
            # Step 1: Transcribe
            self.update_stage("🔄 Transcribing speech...")
            self.progress_bar.set(0.3)
            
            if not self.whisper_model:
                raise Exception("Whisper model not loaded")
            
            segments, info = self.whisper_model.transcribe(
                self.current_audio.flatten(),
                language="en",
                beam_size=5,
                vad_filter=True
            )
            
            self.current_text = " ".join([seg.text for seg in segments]).strip()
            
            if not self.current_text:
                self.update_info("⚠️ No speech detected", "orange")
                self.progress_bar.set(0)
                return
            
            # Update transcription display
            self.transcription_text.configure(state="normal")
            self.transcription_text.delete("1.0", "end")
            self.transcription_text.insert("1.0", self.current_text)
            self.transcription_text.configure(state="disabled")
            
            self.update_stage(f"✅ Transcribed: '{self.current_text}'")
            self.progress_bar.set(0.5)
            
            # Step 2: Generate ASL video (get first word for demo)
            words = self.current_text.lower().split()
            if not words:
                self.update_info("⚠️ No words to process", "orange")
                return
            
            # Use first word for avatar demo
            target_word = words[0]
            
            self.update_stage(f"🎬 Finding ASL sign for '{target_word}'...")
            self.progress_bar.set(0.6)
            
            if not self.wlasl_generator:
                raise Exception("WLASL generator not loaded")
            
            video_path = self.wlasl_generator.find_sign(target_word)
            
            if not video_path:
                self.update_info(f"⚠️ No sign found for '{target_word}'", "orange")
                self.progress_bar.set(0)
                return
            
            # Step 3: Extract pose
            self.update_stage(f"🔍 Extracting pose data...")
            self.progress_bar.set(0.7)
            
            if not self.pose_extractor:
                raise Exception("Pose extractor not loaded")
            
            # Extract pose to temp file
            pose_dir = "pose_data"
            os.makedirs(pose_dir, exist_ok=True)
            
            import cv2
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frames_data = []
            
            frame_idx = 0
            while cap.isOpened() and frame_idx < 60:  # Limit to 2 seconds
                success, frame = cap.read()
                if not success:
                    break
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose_extractor.holistic.process(frame_rgb)
                
                frame_data = {
                    'frame_idx': frame_idx,
                    'timestamp': frame_idx / fps if fps > 0 else 0,
                    'pose': self.pose_extractor._landmarks_to_list(results.pose_landmarks),
                    'left_hand': self.pose_extractor._landmarks_to_list(results.left_hand_landmarks),
                    'right_hand': self.pose_extractor._landmarks_to_list(results.right_hand_landmarks),
                    'face': self.pose_extractor._landmarks_to_list(results.face_landmarks)
                }
                
                frames_data.append(frame_data)
                frame_idx += 1
            
            cap.release()
            
            pose_data = {
                'frames': frames_data,
                'fps': fps,
                'duration': len(frames_data) / fps if fps > 0 else 0,
                'frame_count': len(frames_data),
                'word': target_word
            }
            
            pose_file = os.path.join(pose_dir, f"{target_word}_temp.json")
            with open(pose_file, 'w') as f:
                json.dump(pose_data, f)
            
            self.current_pose_file = pose_file
            
            self.update_stage(f"✅ Pose extracted! ({len(frames_data)} frames)")
            self.progress_bar.set(0.9)
            
            # Step 4: Ready to animate
            self.update_stage(f"✅ Ready to animate '{target_word}'!")
            self.progress_bar.set(1.0)
            
            self.avatar_info.configure(
                text=f"Avatar ready for word: '{target_word}' ({len(frames_data)} frames)",
                text_color="cyan"
            )
            
            # Enable buttons
            self.play_avatar_btn.configure(state="normal")
            self.export_btn.configure(state="normal")
            
            self.update_info("✅ Processing complete! Click 'Play Avatar' to view", "green")
            
        except Exception as e:
            self.update_info(f"❌ Processing error: {e}", "red")
            self.progress_bar.set(0)
            import traceback
            traceback.print_exc()
    
    def play_avatar(self):
        """Play avatar animation in separate window"""
        if not self.current_pose_file:
            self.update_info("⚠️ No pose data available", "orange")
            return
        
        self.update_info("🎬 Opening avatar window...", "cyan")
        
        # Launch avatar in separate thread
        threading.Thread(target=self.play_avatar_thread, daemon=True).start()
    
    def play_avatar_thread(self):
        """Play avatar animation"""
        try:
            if not FuturisticAvatar:
                self.update_info("❌ Avatar renderer not available", "red")
                return
            
            avatar = FuturisticAvatar(screen_size=(1024, 768))
            avatar.animate_from_pose_file(self.current_pose_file, loop=True, fps=30)
            
        except Exception as e:
            self.update_info(f"❌ Avatar error: {e}", "red")
            import traceback
            traceback.print_exc()
    
    def export_video(self):
        """Export avatar animation as video"""
        if not self.current_pose_file:
            self.update_info("⚠️ No pose data available", "orange")
            return
        
        self.update_info("📹 Exporting video...", "cyan")
        threading.Thread(target=self.export_video_thread, daemon=True).start()
    
    def export_video_thread(self):
        """Export video in background"""
        try:
            if not FuturisticAvatar:
                self.update_info("❌ Avatar renderer not available", "red")
                return
            
            output_dir = "asl_outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = int(time.time())
            output_path = os.path.join(output_dir, f"avatar_{timestamp}.mp4")
            
            avatar = FuturisticAvatar(screen_size=(1024, 768))
            avatar.export_animation_video(self.current_pose_file, output_path, fps=30)
            
            self.update_info(f"✅ Video exported: {output_path}", "green")
            
        except Exception as e:
            self.update_info(f"❌ Export error: {e}", "red")
            import traceback
            traceback.print_exc()
    
    def update_stage(self, text):
        """Update stage label"""
        self.stage_label.configure(text=f"Status: {text}")
        self.root.update()
    
    def update_info(self, text, color="white"):
        """Update info label"""
        self.info_label.configure(text=text, text_color=color)
        self.root.update()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


# Main entry point
if __name__ == "__main__":
    print("="*70)
    print("Voice to Sign Language - GUI Application")
    print("="*70)
    print("\n🚀 Starting graphical interface...")
    print("💡 This may take a moment to load models...\n")
    
    try:
        app = VoiceToSignLanguageApp()
        app.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
