#!/usr/bin/env python3
"""
Ultra-simple puppy video generator using only PIL and basic libraries
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_output_dirs():
    """Create output directories"""
    output_dir = Path("output")
    videos_dir = output_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)
    return videos_dir

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB"""
    h = h / 360.0
    s = s / 100.0
    v = v / 100.0
    
    if s == 0.0:
        return int(v * 255), int(v * 255), int(v * 255)
    
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    
    if i == 0:
        return int(v * 255), int(t * 255), int(p * 255)
    elif i == 1:
        return int(q * 255), int(v * 255), int(p * 255)
    elif i == 2:
        return int(p * 255), int(v * 255), int(t * 255)
    elif i == 3:
        return int(p * 255), int(q * 255), int(v * 255)
    elif i == 4:
        return int(t * 255), int(p * 255), int(v * 255)
    else:
        return int(v * 255), int(p * 255), int(q * 255)

def create_puppy_frames(width=640, height=480, duration=5, fps=10):
    """Create animated frames for a cute puppy-themed video"""
    frames = []
    total_frames = duration * fps
    
    logger.info(f"Creating {total_frames} frames ({duration}s at {fps}fps)")
    
    for frame_num in range(total_frames):
        # Create frame
        frame = Image.new('RGB', (width, height), (135, 206, 235))  # Sky blue background
        draw = ImageDraw.Draw(frame)
        
        # Animation time factor
        t = frame_num / fps
        
        # Draw animated background elements
        # Clouds
        cloud_x = int(-50 + (t * 20) % (width + 100))
        draw.ellipse([cloud_x, 50, cloud_x + 80, 90], fill=(255, 255, 255))
        draw.ellipse([cloud_x + 20, 40, cloud_x + 70, 80], fill=(255, 255, 255))
        
        cloud_x2 = int(-30 + (t * 15) % (width + 80))
        draw.ellipse([cloud_x2, 120, cloud_x2 + 60, 150], fill=(255, 255, 255))
        
        # Ground
        ground_y = height - 100
        draw.rectangle([0, ground_y, width, height], fill=(34, 139, 34))  # Forest green
        
        # Animated puppy (simple shapes)
        puppy_center_x = width // 2 + int(30 * math.sin(t * 2))  # Gentle swaying
        puppy_center_y = ground_y - 50
        
        # Puppy body (golden color)
        body_color = (255, 215, 0)  # Golden
        draw.ellipse([puppy_center_x - 30, puppy_center_y - 20, 
                     puppy_center_x + 30, puppy_center_y + 20], fill=body_color)
        
        # Puppy head
        head_bounce = int(5 * math.sin(t * 4))  # Bouncing head
        head_y = puppy_center_y - 35 + head_bounce
        draw.ellipse([puppy_center_x - 20, head_y - 15, 
                     puppy_center_x + 20, head_y + 15], fill=body_color)
        
        # Ears (flopping)
        ear_flop = int(3 * math.sin(t * 3))
        draw.ellipse([puppy_center_x - 25, head_y - 10 + ear_flop, 
                     puppy_center_x - 15, head_y + 5 + ear_flop], fill=(218, 165, 32))
        draw.ellipse([puppy_center_x + 15, head_y - 10 + ear_flop, 
                     puppy_center_x + 25, head_y + 5 + ear_flop], fill=(218, 165, 32))
        
        # Eyes
        draw.ellipse([puppy_center_x - 12, head_y - 5, 
                     puppy_center_x - 8, head_y - 1], fill=(0, 0, 0))
        draw.ellipse([puppy_center_x + 8, head_y - 5, 
                     puppy_center_x + 12, head_y - 1], fill=(0, 0, 0))
        
        # Nose
        draw.ellipse([puppy_center_x - 2, head_y + 2, 
                     puppy_center_x + 2, head_y + 6], fill=(0, 0, 0))
        
        # Tail (wagging)
        tail_angle = math.sin(t * 6) * 0.5  # Fast wagging
        tail_end_x = puppy_center_x + 35 + int(15 * math.cos(tail_angle))
        tail_end_y = puppy_center_y - 10 + int(15 * math.sin(tail_angle))
        draw.line([puppy_center_x + 25, puppy_center_y - 5, 
                  tail_end_x, tail_end_y], fill=body_color, width=5)
        
        # Legs (simple lines)
        leg_offset = int(2 * math.sin(t * 4))  # Walking motion
        draw.line([puppy_center_x - 15, puppy_center_y + 15, 
                  puppy_center_x - 15 + leg_offset, ground_y - 5], fill=body_color, width=4)
        draw.line([puppy_center_x - 5, puppy_center_y + 15, 
                  puppy_center_x - 5 - leg_offset, ground_y - 5], fill=body_color, width=4)
        draw.line([puppy_center_x + 5, puppy_center_y + 15, 
                  puppy_center_x + 5 + leg_offset, ground_y - 5], fill=body_color, width=4)
        draw.line([puppy_center_x + 15, puppy_center_y + 15, 
                  puppy_center_x + 15 - leg_offset, ground_y - 5], fill=body_color, width=4)
        
        # Add some flowers in the grass
        flower_positions = [(100, ground_y - 10), (200, ground_y - 15), (400, ground_y - 8), (500, ground_y - 12)]
        for fx, fy in flower_positions:
            # Flower petals
            petal_color = hsv_to_rgb((frame_num * 10 + fx) % 360, 80, 90)
            draw.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=petal_color)
            draw.ellipse([fx - 5, fy - 1, fx - 1, fy + 3], fill=petal_color)
            draw.ellipse([fx + 1, fy - 1, fx + 5, fy + 3], fill=petal_color)
            draw.ellipse([fx - 1, fy - 5, fx + 3, fy - 1], fill=petal_color)
            draw.ellipse([fx - 1, fy + 1, fx + 3, fy + 5], fill=petal_color)
            # Center
            draw.ellipse([fx - 1, fy - 1, fx + 1, fy + 1], fill=(255, 255, 0))
        
        # Add title text
        try:
            # Try to use a default font
            font_size = 24
            title_text = "🐶 Cute Puppy Video! 🐶"
            
            # Calculate text position (centered at top)
            text_bbox = draw.textbbox((0, 0), title_text)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (width - text_width) // 2
            text_y = 10
            
            # Draw text with outline for better visibility
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, text_y + dy), title_text, fill=(0, 0, 0))
            draw.text((text_x, text_y), title_text, fill=(255, 255, 255))
            
        except Exception:
            # If font loading fails, skip text
            pass
        
        frames.append(frame)
        
        if frame_num % 10 == 0:
            logger.info(f"Generated frame {frame_num + 1}/{total_frames}")
    
    return frames

def save_as_gif(frames, output_path, fps=10):
    """Save frames as animated GIF"""
    try:
        duration = int(1000 / fps)  # Duration in milliseconds
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save GIF: {e}")
        return False

def main():
    """Main function to generate puppy video"""
    logger.info("🐶 Starting simple puppy video generation...")
    
    try:
        # Create output directory
        videos_dir = create_output_dirs()
        
        # Generate frames
        frames = create_puppy_frames(width=640, height=480, duration=5, fps=10)
        
        # Save as GIF
        output_path = videos_dir / "cute_puppy_simple.gif"
        logger.info(f"💾 Saving video to: {output_path}")
        
        if save_as_gif(frames, output_path, fps=10):
            file_size = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ SUCCESS! Video saved: {output_path}")
            logger.info(f"📊 File size: {file_size:.1f} MB")
            logger.info(f"📊 Frames: {len(frames)}")
            logger.info(f"📊 Duration: 5 seconds")
            
            print(f"\n🎉 SUCCESS! Puppy video saved at: {output_path}")
            print(f"You can open it with: open '{output_path}'")
            return str(output_path)
        else:
            logger.error("❌ Failed to save video")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    try:
        result = main()
        if not result:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)
