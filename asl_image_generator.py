#!/usr/bin/env python3
"""
ASL Image Generator - Uses Kaggle dataset instead of WLASL videos
Generates image sequences or GIFs for ASL translation
"""
import os
import re
from pathlib import Path
from PIL import Image
import random

# Dataset paths
KAGGLE_ASL_DIR = "kaggle_asl_dataset/asl_dataset"
OUTPUT_DIR = "asl_outputs"

def get_asl_image(character):
    """
    Get a random ASL image for a given character (letter or number)
    
    Args:
        character: Single letter (a-z) or digit (0-9)
    
    Returns:
        Path to image file, or None if not found
    """
    char = str(character).lower().strip()
    
    # Map common words to spelling
    if len(char) > 1:
        return None
    
    char_dir = Path(KAGGLE_ASL_DIR) / char
    
    if not char_dir.exists():
        return None
    
    # Get all images for this character
    images = list(char_dir.glob("*.jpg")) + list(char_dir.glob("*.jpeg")) + list(char_dir.glob("*.png"))
    
    if not images:
        return None
    
    # Return random image for variety
    return str(random.choice(images))


def text_to_asl_images(text):
    """
    Convert text to list of ASL image paths
    
    Args:
        text: Input text to convert
    
    Returns:
        List of (character, image_path) tuples
    """
    # Clean text - only keep letters, numbers, and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text.lower())
    
    result = []
    for char in text:
        if char == ' ':
            result.append(('space', None))  # Pause between words
        else:
            img_path = get_asl_image(char)
            if img_path:
                result.append((char, img_path))
    
    return result


def create_asl_image_sequence(text, output_path, grid=False):
    """
    Create a single image showing ASL signs for the text
    
    Args:
        text: Text to convert
        output_path: Where to save the output image
        grid: If True, arrange in grid. If False, horizontal strip
    
    Returns:
        Path to generated image
    """
    images_data = text_to_asl_images(text)
    
    if not images_data:
        raise ValueError(f"No ASL images found for: {text}")
    
    # Filter out spaces for the visual output
    images_to_show = [(char, path) for char, path in images_data if path is not None]
    
    if not images_to_show:
        raise ValueError(f"No valid images to display for: {text}")
    
    # Load all images
    loaded_images = []
    labels = []
    for char, img_path in images_to_show:
        try:
            img = Image.open(img_path)
            loaded_images.append(img)
            labels.append(char.upper())
        except Exception as e:
            print(f"⚠️  Error loading image for '{char}': {e}")
    
    if not loaded_images:
        raise ValueError(f"Failed to load any images for: {text}")
    
    # Get max dimensions
    max_width = max(img.width for img in loaded_images)
    max_height = max(img.height for img in loaded_images)
    
    # Resize all to same size (square)
    size = max(max_width, max_height)
    resized = []
    for img in loaded_images:
        # Create white background
        new_img = Image.new('RGB', (size, size), 'white')
        # Paste original centered
        offset = ((size - img.width) // 2, (size - img.height) // 2)
        new_img.paste(img, offset)
        resized.append(new_img)
    
    if grid:
        # Arrange in grid (max 10 per row)
        cols = min(10, len(resized))
        rows = (len(resized) + cols - 1) // cols
        
        result = Image.new('RGB', (size * cols, size * rows), 'white')
        
        for idx, img in enumerate(resized):
            row = idx // cols
            col = idx % cols
            result.paste(img, (col * size, row * size))
    else:
        # Horizontal strip
        result = Image.new('RGB', (size * len(resized), size), 'white')
        
        for idx, img in enumerate(resized):
            result.paste(img, (idx * size, 0))
    
    # Save
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    result.save(output_path)
    
    return output_path


def create_asl_gif(text, output_path, duration=800):
    """
    Create an animated GIF showing ASL signs one by one
    
    Args:
        text: Text to convert
        output_path: Where to save the GIF
        duration: Milliseconds per frame
    
    Returns:
        Path to generated GIF
    """
    images_data = text_to_asl_images(text)
    
    if not images_data:
        raise ValueError(f"No ASL images found for: {text}")
    
    # Load images
    frames = []
    for char, img_path in images_data:
        if img_path:  # Skip spaces
            try:
                img = Image.open(img_path)
                # Resize to consistent size
                img = img.resize((400, 400), Image.Resampling.LANCZOS)
                frames.append(img)
            except Exception as e:
                print(f"⚠️  Error loading '{char}': {e}")
    
    if not frames:
        raise ValueError(f"No valid frames for: {text}")
    
    # Save as GIF
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0
    )
    
    return output_path


def generate_asl_output(text, output_type='gif'):
    """
    Main function to generate ASL output from text
    
    Args:
        text: Text to convert to ASL
        output_type: 'gif', 'image', or 'grid'
    
    Returns:
        Path to generated file
    """
    # Clean filename
    safe_text = re.sub(r'[^a-z0-9]', '_', text.lower())[:30]
    timestamp = int(__import__('time').time())
    
    if output_type == 'gif':
        output_path = os.path.join(OUTPUT_DIR, f"asl_{safe_text}_{timestamp}.gif")
        return create_asl_gif(text, output_path)
    elif output_type == 'grid':
        output_path = os.path.join(OUTPUT_DIR, f"asl_{safe_text}_{timestamp}.png")
        return create_asl_image_sequence(text, output_path, grid=True)
    else:  # image strip
        output_path = os.path.join(OUTPUT_DIR, f"asl_{safe_text}_{timestamp}.png")
        return create_asl_image_sequence(text, output_path, grid=False)


# Test function
if __name__ == "__main__":
    import sys
    
    test_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hello world"
    
    print(f"Converting to ASL: '{test_text}'")
    print()
    
    try:
        # Try all three formats
        gif_path = generate_asl_output(test_text, 'gif')
        print(f"✅ GIF created: {gif_path}")
        
        img_path = generate_asl_output(test_text, 'image')
        print(f"✅ Image strip created: {img_path}")
        
        grid_path = generate_asl_output(test_text, 'grid')
        print(f"✅ Grid image created: {grid_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
