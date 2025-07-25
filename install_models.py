#!/usr/bin/env python3
"""
AI Model Installation Script for Short Video Generator
Downloads and sets up required AI models
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 Running: {description}")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            if result.stdout:
                print("Output:", result.stdout.strip())
            return True
        else:
            print(f"❌ {description} failed!")
            if result.stderr:
                print("Error:", result.stderr.strip())
            return False
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 AI Model Installation for Short Video Generator")
    print("=" * 60)
    print()
    
    # Check disk space
    print("💾 Checking disk space...")
    try:
        result = subprocess.run("df -h .", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
        print()
    except:
        print("⚠️ Could not check disk space")
    
    # Install Stable Diffusion model for image generation
    print("🖼️ Installing Stable Diffusion model for image generation...")
    print("📥 This will download ~4GB of data...")
    
    sd_script = """
import torch
from diffusers import StableDiffusionPipeline
import os

print("Downloading Stable Diffusion model...")
model_id = "runwayml/stable-diffusion-v1-5"

# Use CPU if CUDA not available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

print("🔄 Downloading model files (this may take several minutes)...")
# Download and cache the model
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map=device if device == "cuda" else None
)

if device == "cpu":
    pipe = pipe.to(device)

print("✅ Stable Diffusion model installed successfully!")
try:
    print(f"Model location: {pipe.config.name_or_path}")
except:
    print(f"Model location: {model_id}")
"""
    
    with open("temp_sd_install.py", "w") as f:
        f.write(sd_script)
    
    if run_command("python3 temp_sd_install.py", "Stable Diffusion installation"):
        print("✅ Stable Diffusion model installed!")
    else:
        print("⚠️ Stable Diffusion installation failed, but continuing...")
    
    # Clean up temp file
    try:
        os.remove("temp_sd_install.py")
    except:
        pass
    
    # Install Stable Video Diffusion model
    print("🎬 Installing Stable Video Diffusion model...")
    print("📥 This will download ~6GB of data...")
    
    svd_script = """
import torch
from diffusers import DiffusionPipeline
import os

print("Downloading Stable Video Diffusion model...")
model_id = "stabilityai/stable-video-diffusion-img2vid-xt"

# Use CPU if CUDA not available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

print("🔄 Downloading model files (this may take 10+ minutes)...")
print("📊 Progress will be shown as files download...")

# Download and cache the model
pipe = DiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map=device if device == "cuda" else None
)

if device == "cpu":
    pipe = pipe.to(device)

print("✅ Stable Video Diffusion model installed successfully!")
try:
    print(f"Model location: {pipe.config.name_or_path}")
except:
    print(f"Model location: {model_id}")

# Check the actual downloaded size
model_path = pipe.config.name_or_path
if os.path.exists(model_path):
    import subprocess
    try:
        result = subprocess.run(f"du -sh {model_path}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"📁 Downloaded model size: {result.stdout.strip()}")
    except:
        pass
"""
    
    with open("temp_svd_install.py", "w") as f:
        f.write(svd_script)
    
    if run_command("python3 temp_svd_install.py", "Stable Video Diffusion installation"):
        print("✅ Stable Video Diffusion model installed!")
    else:
        print("⚠️ Stable Video Diffusion installation failed, but continuing...")
    
    # Clean up temp file
    try:
        os.remove("temp_svd_install.py")
    except:
        pass
    
    print()
    print("🎉 AI Model Installation Complete!")
    print()
    print("Next steps:")
    print("1. Test the system: python3 cli.py status")
    print("2. Generate a video: python3 cli.py generate --theme cute_pets")
    print("3. Check the output: open output/videos/")
    print()
    print("Note: If you're using CPU, video generation will be slower but still functional.")
    print("For best performance, ensure CUDA is available and properly configured.")

if __name__ == "__main__":
    main()
