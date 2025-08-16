#!/usr/bin/env python3
"""
Advanced puppy video test with proper fallback handling
"""

import asyncio
import sys
from pathlib import Path
import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ffmpeg_mac():
    """Try to install ffmpeg on macOS using homebrew"""
    try:
        logger.info("🔧 Attempting to install ffmpeg via homebrew...")
        result = subprocess.run(['brew', 'install', 'ffmpeg'], capture_output=True, text=True, timeout=300)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

async def test_stable_video_diffusion():
    """Test if we can actually use Stable Video Diffusion"""
    logger.info("🧪 Testing Stable Video Diffusion availability...")
    
    try:
        # Try to import required libraries
        import torch
        from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline
        from PIL import Image
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🖥️ Device: {device}")
        
        if device == "cpu":
            logger.warning("⚠️ Using CPU - this will be very slow!")
        
        # Test loading models (this might fail due to dependency issues)
        logger.info("🔄 Testing model loading...")
        
        # Try to load a small model first
        try:
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            logger.info("✅ Stable Diffusion model loaded successfully!")
            del pipe  # Free memory
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load Stable Diffusion: {e}")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

async def generate_with_stable_diffusion():
    """Try to generate with actual Stable Video Diffusion"""
    logger.info("🎬 Attempting Stable Video Diffusion generation...")
    
    try:
        import torch
        from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline
        from PIL import Image
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Create output directories
        output_dir = Path("output")
        images_dir = output_dir / "images"
        videos_dir = output_dir / "videos"
        images_dir.mkdir(parents=True, exist_ok=True)
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Generate input image
        logger.info("🖼️ Generating input image...")
        image_pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        ).to(device)
        
        prompt = "a cute golden retriever puppy, high quality, detailed, adorable, sitting, happy expression"
        image = image_pipe(
            prompt=prompt,
            num_inference_steps=20,
            guidance_scale=7.5,
            height=576,
            width=1024
        ).images[0]
        
        # Save input image
        image_path = images_dir / "puppy_input_advanced.png"
        image.save(image_path)
        logger.info(f"✅ Input image saved: {image_path}")
        
        # Clear memory
        del image_pipe
        if device == "cuda":
            torch.cuda.empty_cache()
        
        # Step 2: Generate video
        logger.info("🎬 Loading Stable Video Diffusion...")
        video_pipe = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            variant="fp16" if device == "cuda" else None
        ).to(device)
        
        logger.info("🎬 Generating video frames...")
        video_frames = video_pipe(
            image,
            num_frames=25,
            num_inference_steps=10,
            min_guidance_scale=1.0,
            max_guidance_scale=3.0,
            decode_chunk_size=4
        ).frames[0]
        
        logger.info(f"✅ Generated {len(video_frames)} frames")
        
        # Save as GIF
        gif_path = videos_dir / "puppy_advanced_svd.gif"
        video_frames[0].save(
            gif_path,
            save_all=True,
            append_images=video_frames[1:],
            duration=200,  # 5 FPS
            loop=0,
            optimize=True
        )
        
        logger.info(f"✅ Advanced puppy video saved: {gif_path}")
        
        # Try to save as MP4 if ffmpeg is available
        if check_ffmpeg():
            mp4_path = await save_as_mp4(video_frames, videos_dir / "puppy_advanced_svd.mp4")
            if mp4_path:
                logger.info(f"✅ MP4 version saved: {mp4_path}")
        
        return str(gif_path)
        
    except Exception as e:
        logger.error(f"❌ Stable Video Diffusion failed: {e}")
        raise

async def save_as_mp4(frames, output_path, fps=5):
    """Save frames as MP4 using ffmpeg"""
    try:
        temp_dir = output_path.parent / "temp_frames"
        temp_dir.mkdir(exist_ok=True)
        
        # Save individual frames
        for i, frame in enumerate(frames):
            frame_path = temp_dir / f"frame_{i:04d}.png"
            frame.save(frame_path)
        
        # Use ffmpeg to create MP4
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', str(temp_dir / 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-crf', '23',
            str(output_path)
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Clean up temp files
            import shutil
            shutil.rmtree(temp_dir)
            return str(output_path)
        else:
            logger.error(f"FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"MP4 conversion failed: {e}")
        return None

async def fallback_generation():
    """Use the simple animation fallback"""
    logger.info("🎨 Using fallback animation generation...")
    
    # Import and run our simple generator
    sys.path.append(str(Path(__file__).parent))
    from simple_puppy_test import create_puppy_frames, save_as_gif, create_output_dirs
    
    videos_dir = create_output_dirs()
    frames = create_puppy_frames(width=640, height=480, duration=5, fps=10)
    
    output_path = videos_dir / "puppy_fallback.gif"
    if save_as_gif(frames, output_path, fps=10):
        return str(output_path)
    return None

async def main():
    """Main test function"""
    logger.info("🐶 Starting advanced puppy video generation test...")
    
    # Check ffmpeg availability
    if not check_ffmpeg():
        logger.warning("⚠️ FFmpeg not found - will only generate GIF")
        if sys.platform == "darwin":  # macOS
            logger.info("💡 You can install ffmpeg with: brew install ffmpeg")
    
    # Test if we can use Stable Video Diffusion
    can_use_svd = await test_stable_video_diffusion()
    
    if can_use_svd:
        try:
            result = await generate_with_stable_diffusion()
            logger.info(f"🎉 SUCCESS with Stable Video Diffusion: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Stable Video Diffusion failed: {e}")
            logger.info("🔄 Falling back to simple animation...")
    else:
        logger.info("🔄 Stable Video Diffusion not available, using fallback...")
    
    # Use fallback
    result = await fallback_generation()
    if result:
        logger.info(f"🎉 SUCCESS with fallback generation: {result}")
        return result
    else:
        logger.error("❌ All generation methods failed")
        return None

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            print(f"\n🎉 SUCCESS! Puppy video saved at: {result}")
            print(f"You can open it with: open '{result}'")
        else:
            print("\n❌ FAILED: No video was generated")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)
