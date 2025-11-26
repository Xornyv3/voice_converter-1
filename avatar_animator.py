#!/usr/bin/env python3
"""
Avatar Animator - Create a blue futuristic 3D avatar that mimics ASL poses
Uses extracted pose data to animate a virtual character
"""
import os
import json
import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time

class FuturisticAvatar:
    """Blue futuristic 3D avatar for ASL animation"""
    
    def __init__(self, screen_size=(800, 600)):
        """Initialize PyGame and OpenGL for 3D rendering"""
        print("🎨 Initializing 3D Avatar Renderer...")
        
        pygame.init()
        self.screen_size = screen_size
        
        # Create OpenGL display
        self.display = pygame.display.set_mode(
            screen_size,
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption("ASL Avatar - Futuristic Mode")
        
        # Setup OpenGL viewport
        glViewport(0, 0, *screen_size)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (screen_size[0] / screen_size[1]), 0.1, 50.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Enable depth testing for 3D
        glEnable(GL_DEPTH_TEST)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Blue futuristic color scheme
        self.colors = {
            'primary': (0.0, 0.6, 1.0, 1.0),      # Bright blue
            'secondary': (0.0, 0.9, 1.0, 1.0),    # Cyan
            'glow': (0.4, 0.8, 1.0, 0.6),         # Light blue glow
            'joints': (1.0, 1.0, 1.0, 1.0),       # White joints
            'background': (0.05, 0.05, 0.15, 1.0) # Dark blue background
        }
        
        # Camera position
        self.camera_distance = 3.0
        self.camera_rotation = [0, 0]
        
        print("✅ Avatar renderer ready!")
    
    def draw_sphere(self, position, radius, color):
        """Draw a sphere at given position"""
        glPushMatrix()
        glTranslatef(*position)
        glColor4f(*color)
        
        # Create quadric for sphere
        quad = gluNewQuadric()
        gluSphere(quad, radius, 16, 16)
        gluDeleteQuadric(quad)
        
        glPopMatrix()
    
    def draw_cylinder(self, start, end, radius, color):
        """Draw a cylinder between two points (for limbs)"""
        glPushMatrix()
        
        # Calculate direction vector
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = np.sqrt(dx**2 + dy**2 + dz**2)
        
        if length < 0.001:
            glPopMatrix()
            return
        
        # Move to start position
        glTranslatef(*start)
        
        # Rotate to point towards end
        if abs(dy) > 0.999:
            glRotatef(90 if dy > 0 else -90, 1, 0, 0)
        else:
            angle = np.degrees(np.arccos(dy / length))
            axis_x = -dz
            axis_z = dx
            axis_length = np.sqrt(axis_x**2 + axis_z**2)
            if axis_length > 0.001:
                glRotatef(angle, axis_x/axis_length, 0, axis_z/axis_length)
        
        # Draw cylinder
        glColor4f(*color)
        quad = gluNewQuadric()
        gluCylinder(quad, radius, radius, length, 16, 4)
        gluDeleteQuadric(quad)
        
        glPopMatrix()
    
    def draw_hand(self, hand_landmarks, is_left=True):
        """Draw a hand with all finger joints"""
        if not hand_landmarks:
            return
        
        # Hand connections (MediaPipe hand landmark indices)
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20)
        ]
        
        # Convert normalized coordinates to 3D
        points_3d = []
        for lm in hand_landmarks:
            # Scale and center hand
            x = (lm['x'] - 0.5) * 0.4
            y = -(lm['y'] - 0.5) * 0.4
            z = lm['z'] * 0.2
            
            # Offset left/right hand
            if is_left:
                x -= 0.3
            else:
                x += 0.3
            
            points_3d.append((x, y, z))
        
        # Draw connections (bones)
        for start_idx, end_idx in connections:
            if start_idx < len(points_3d) and end_idx < len(points_3d):
                self.draw_cylinder(
                    points_3d[start_idx],
                    points_3d[end_idx],
                    0.008,
                    self.colors['primary']
                )
        
        # Draw joints (spheres)
        for point in points_3d:
            self.draw_sphere(point, 0.015, self.colors['secondary'])
    
    def draw_pose(self, pose_landmarks):
        """Draw body pose"""
        if not pose_landmarks:
            return
        
        # Key body connections
        connections = [
            # Torso
            (11, 12),  # Shoulders
            (11, 23), (12, 24),  # Shoulders to hips
            (23, 24),  # Hips
            # Arms
            (11, 13), (13, 15),  # Left arm
            (12, 14), (14, 16),  # Right arm
            # Legs
            (23, 25), (25, 27),  # Left leg
            (24, 26), (26, 28),  # Right leg
        ]
        
        # Convert landmarks to 3D
        points_3d = []
        for lm in pose_landmarks:
            x = (lm['x'] - 0.5) * 1.0
            y = -(lm['y'] - 0.5) * 1.0
            z = lm['z'] * 0.3
            points_3d.append((x, y, z))
        
        # Draw connections
        for start_idx, end_idx in connections:
            if start_idx < len(points_3d) and end_idx < len(points_3d):
                # Make torso/shoulders thicker
                radius = 0.025 if start_idx in [11, 12, 23, 24] else 0.015
                self.draw_cylinder(
                    points_3d[start_idx],
                    points_3d[end_idx],
                    radius,
                    self.colors['primary']
                )
        
        # Draw joints
        for i, point in enumerate(points_3d):
            # Make key joints bigger
            radius = 0.03 if i in [11, 12, 23, 24] else 0.02
            self.draw_sphere(point, radius, self.colors['joints'])
    
    def render_frame(self, pose_data):
        """
        Render a single frame of avatar animation
        
        Args:
            pose_data: Dict with 'pose', 'left_hand', 'right_hand', 'face'
        """
        # Clear screen
        glClearColor(*self.colors['background'])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glLoadIdentity()
        
        # Position camera
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_rotation[0], 1, 0, 0)
        glRotatef(self.camera_rotation[1], 0, 1, 0)
        
        # Draw avatar components
        if pose_data.get('pose'):
            self.draw_pose(pose_data['pose'])
        
        if pose_data.get('left_hand'):
            self.draw_hand(pose_data['left_hand'], is_left=True)
        
        if pose_data.get('right_hand'):
            self.draw_hand(pose_data['right_hand'], is_left=False)
        
        # Update display
        pygame.display.flip()
    
    def animate_from_pose_file(self, pose_json_path, loop=False, fps=30):
        """
        Animate avatar from extracted pose data
        
        Args:
            pose_json_path: Path to JSON file with pose data
            loop: Whether to loop animation
            fps: Playback frame rate
        """
        print(f"\n🎬 Loading animation: {os.path.basename(pose_json_path)}")
        
        with open(pose_json_path, 'r') as f:
            data = json.load(f)
        
        frames = data['frames']
        original_fps = data.get('fps', 30)
        
        print(f"   Frames: {len(frames)} | FPS: {original_fps:.1f}")
        print("   Controls: ESC=Exit, Space=Pause, R=Restart")
        
        clock = pygame.time.Clock()
        frame_idx = 0
        paused = False
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        frame_idx = 0
                    # Camera controls
                    elif event.key == pygame.K_UP:
                        self.camera_rotation[0] += 5
                    elif event.key == pygame.K_DOWN:
                        self.camera_rotation[0] -= 5
                    elif event.key == pygame.K_LEFT:
                        self.camera_rotation[1] -= 5
                    elif event.key == pygame.K_RIGHT:
                        self.camera_rotation[1] += 5
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.camera_distance = max(1.5, self.camera_distance - 0.2)
                    elif event.key == pygame.K_MINUS:
                        self.camera_distance = min(6.0, self.camera_distance + 0.2)
            
            if not paused:
                # Render current frame
                if frames:
                    self.render_frame(frames[frame_idx])
                
                # Advance frame
                frame_idx += 1
                if frame_idx >= len(frames):
                    if loop:
                        frame_idx = 0
                    else:
                        print("\n✅ Animation complete!")
                        running = False
            
            clock.tick(fps)
        
        print("👋 Exiting...")
    
    def export_animation_video(self, pose_json_path, output_path, fps=30):
        """
        Export avatar animation as MP4 video
        
        Args:
            pose_json_path: Path to pose data JSON
            output_path: Output video file path
            fps: Frame rate for output
        """
        print(f"\n📹 Exporting animation to video...")
        print(f"   Output: {output_path}")
        
        import cv2
        
        with open(pose_json_path, 'r') as f:
            data = json.load(f)
        
        frames = data['frames']
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, self.screen_size)
        
        for i, frame_data in enumerate(frames):
            # Render frame
            self.render_frame(frame_data)
            
            # Read pixels from OpenGL
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            pixels = glReadPixels(0, 0, *self.screen_size, GL_RGB, GL_UNSIGNED_BYTE)
            
            # Convert to numpy array and flip
            image = np.frombuffer(pixels, dtype=np.uint8).reshape(
                self.screen_size[1], self.screen_size[0], 3
            )
            image = cv2.flip(image, 0)  # OpenGL bottom-left origin
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            writer.write(image)
            
            if (i + 1) % 30 == 0:
                print(f"   Rendered {i+1}/{len(frames)} frames...", end='\r')
        
        writer.release()
        print(f"\n✅ Video exported: {output_path}")
    
    def __del__(self):
        """Cleanup"""
        pygame.quit()


# CLI usage
if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("Futuristic 3D Avatar Animator for ASL")
    print("="*70)
    
    # Check if pose data exists
    if len(sys.argv) < 2:
        print("\n💡 Usage: python avatar_animator.py <pose_data.json>")
        print("\n🔍 Looking for existing pose data...")
        
        pose_dir = "pose_data"
        if os.path.exists(pose_dir):
            files = [f for f in os.listdir(pose_dir) if f.endswith('.json')]
            if files:
                print(f"\n📁 Found {len(files)} pose files:")
                for f in files[:5]:
                    print(f"   - {f}")
                
                # Use first file
                pose_file = os.path.join(pose_dir, files[0])
                print(f"\n🎯 Using: {files[0]}")
            else:
                print("\n❌ No pose data files found.")
                print("💡 Run: python pose_extractor.py <word>")
                sys.exit(1)
        else:
            print("\n❌ No pose_data directory found.")
            print("💡 Run: python pose_extractor.py <word>")
            sys.exit(1)
    else:
        pose_file = sys.argv[1]
    
    if not os.path.exists(pose_file):
        print(f"❌ File not found: {pose_file}")
        sys.exit(1)
    
    try:
        # Create avatar and animate
        avatar = FuturisticAvatar(screen_size=(1024, 768))
        avatar.animate_from_pose_file(pose_file, loop=True, fps=30)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
