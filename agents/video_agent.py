"""
Video Generation Agent
Creates videos using open-source AI models like Stable Diffusion
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
import cv2
import numpy as np
from PIL import Image
import torch

from diffusers import StableDiffusionPipeline, DiffusionPipeline
from config.settings import settings

class VideoAgent:
    """AI agent for generating videos from text prompts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # AI models
        self.image_generator = None
        self.video_generator = None
        
        # Video processing
        self.fps = self.settings.video_fps
        try:
            self.resolution = tuple(map(int, self.settings.video_resolution.split('x')))
        except (ValueError, AttributeError):
            # Fallback to default resolution
            self.resolution = (1080, 1920)
            self.logger.warning(f"⚠️ Invalid resolution format: {self.settings.video_resolution}, using default: {self.resolution}")
        
    async def initialize(self):
        """Initialize AI models"""
        try:
            self.logger.info("🎬 Initializing Video Agent...")
            
            # Initialize Stable Diffusion for image generation
            self.image_generator = StableDiffusionPipeline.from_pretrained(
                self.settings.stable_diffusion_model,
                torch_dtype=torch.float16 if self.settings.use_gpu else torch.float32,
                device_map=self.settings.model_device
            )
            
            # Initialize video generation model
            self.video_generator = DiffusionPipeline.from_pretrained(
                self.settings.video_model,
                torch_dtype=torch.float16 if self.settings.use_gpu else torch.float32,
                device_map=self.settings.model_device
            )
            
            self.logger.info("✅ Video Agent initialized!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize: {e}")
            # Fallback to basic image generation
    
    async def generate_video(self, prompt: str, duration: int = 15) -> str:
        """Generate video from text prompt"""
        try:
            self.logger.info(f"🎬 Generating video: {prompt[:50]}...")
            
            # Generate keyframes
            keyframes = await self._generate_keyframes(prompt, duration)
            
            # Create video from keyframes
            video_path = await self._create_video_from_frames(keyframes, prompt, duration)
            
            self.logger.info(f"✅ Video generated: {video_path}")
            return video_path
            
        except Exception as e:
            self.logger.error(f"❌ Error generating video: {e}")
            # Fallback to simple animation
            return await self._create_fallback_video(prompt, duration)
    
    async def _generate_keyframes(self, prompt: str, duration: int) -> list:
        """Generate keyframes for the video"""
        try:
            if self.image_generator:
                # Generate multiple images with slight variations
                num_frames = min(duration * 2, 30)  # Max 30 frames
                
                keyframes = []
                for i in range(num_frames):
                    # Add variation to prompt
                    varied_prompt = f"{prompt}, frame {i+1}, cute animal video"
                    
                    # Generate image
                    image = self.image_generator(
                        prompt=varied_prompt,
                        num_inference_steps=20,
                        guidance_scale=7.5
                    ).images[0]
                    
                    keyframes.append(image)
                    
                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.1)
                
                return keyframes
            else:
                # Fallback: create simple colored frames
                return self._create_simple_frames(prompt, duration)
                
        except Exception as e:
            self.logger.error(f"❌ Error generating keyframes: {e}")
            return self._create_simple_frames(prompt, duration)
    
    def _create_simple_frames(self, prompt: str, duration: int) -> list:
        """Create simple colored frames as fallback"""
        frames = []
        colors = [(255, 182, 193), (173, 216, 230), (144, 238, 144), (255, 218, 185)]
        
        for i in range(duration * self.fps):
            # Create colored frame with text
            frame = np.ones((*self.resolution, 3), dtype=np.uint8)
            color = colors[i % len(colors)]
            frame[:] = color
            
            # Add text overlay
            frame_pil = Image.fromarray(frame)
            # Note: In production, you'd add proper text rendering here
            
            frames.append(frame_pil)
        
        return frames
    
    async def _create_video_from_frames(self, frames: list, prompt: str, duration: int) -> str:
        """Create video file from generated frames"""
        try:
            # Ensure output directory exists
            output_dir = Path(self.settings.output_dir) / "videos"
            output_dir.mkdir(exist_ok=True, parents=True)
            
            # Generate filename
            safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_prompt[:30]}_{duration}s.mp4"
            output_path = output_dir / filename
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, self.fps, self.resolution)
            
            # Write frames
            for frame in frames:
                # Convert PIL to OpenCV format
                frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                frame_cv = cv2.resize(frame_cv, self.resolution)
                
                # Write frame multiple times to achieve desired duration
                for _ in range(self.fps // len(frames) * duration):
                    out.write(frame_cv)
            
            out.release()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error creating video: {e}")
            raise
    
    async def _create_fallback_video(self, prompt: str, duration: int) -> str:
        """Create a simple fallback video"""
        try:
            # Create a simple animated video
            output_dir = Path(self.settings.output_dir) / "videos"
            output_dir.mkdir(exist_ok=True, parents=True)
            
            filename = f"fallback_{duration}s.mp4"
            output_path = output_dir / filename
            
            # Create simple animation
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, self.fps, self.resolution)
            
            for i in range(duration * self.fps):
                # Create frame with moving circle
                frame = np.zeros((*self.resolution, 3), dtype=np.uint8)
                
                # Draw moving circle
                center_x = int(self.resolution[0] * 0.5 + 100 * np.sin(i * 0.1))
                center_y = int(self.resolution[1] * 0.5 + 100 * np.cos(i * 0.1))
                cv2.circle(frame, (center_x, center_y), 50, (255, 255, 255), -1)
                
                # Add text
                cv2.putText(frame, prompt[:20], (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                out.write(frame)
            
            out.release()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error creating fallback video: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.image_generator:
                del self.image_generator
            if self.video_generator:
                del self.video_generator
            
            self.image_generator = None
            self.video_generator = None
            
            self.logger.info("🧹 Video Agent cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
