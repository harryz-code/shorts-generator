#!/usr/bin/env python3
"""
Installation script for the Short Video Generator
Sets up the system, creates directories, and installs dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json

def print_banner():
    """Print installation banner"""
    print("=" * 60)
    print("🎬 Short Video Generator - Installation")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "models",
        "output",
        "output/videos",
        "output/images",
        "temp",
        "data",
        "logs",
        "assets",
        "assets/music",
        "assets/sounds",
        "web/static",
        "web/templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")
    
    print()

def create_env_file():
    """Create .env file from example"""
    env_example = Path("config.env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("📄 .env file already exists, skipping creation")
        return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("📄 Created .env file from config.env.example")
        print("⚠️  Please edit .env file with your actual configuration values")
    else:
        print("⚠️  config.env.example not found, creating basic .env file")
        
        basic_env = """# Basic configuration for Short Video Generator
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=shorts_generator.log

# Paths
MODEL_PATH=./models
OUTPUT_DIR=./output
TEMP_DIR=./temp
DATA_DIR=./data

# AI Model Settings
USE_GPU=false
SD_MODEL=runwayml/stable-diffusion-v1-5
VIDEO_MODEL=damo-vilab/text-to-video-zero

# Content Generation
DAILY_VIDEO_COUNT=3
VIDEO_DURATION=15
VIDEO_RESOLUTION=1080x1920
VIDEO_FPS=30

# Database
DATABASE_URL=sqlite:///./data/shorts.db

# Web Dashboard
WEB_HOST=0.0.0.0
WEB_PORT=8000
WEB_SECRET_KEY=change-this-secret-key
"""
        
        with open(env_file, 'w') as f:
            f.write(basic_env)
        
        print("📄 Created basic .env file")
    
    print()

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip not found. Please install pip first.")
        sys.exit(1)
    
    # Install requirements
    if Path("requirements.txt").exists():
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("⚠️  You may need to install some dependencies manually")
    else:
        print("⚠️  requirements.txt not found, installing basic dependencies")
        
        basic_deps = [
            "fastapi",
            "uvicorn",
            "python-dotenv",
            "schedule",
            "requests",
            "pillow",
            "opencv-python",
            "numpy",
            "pydub"
        ]
        
        for dep in basic_deps:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], check=True)
                print(f"  ✅ Installed: {dep}")
            except subprocess.CalledProcessError:
                print(f"  ⚠️  Failed to install: {dep}")
    
    print()

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check for FFmpeg (required for video processing)
    ffmpeg_available = shutil.which("ffmpeg") is not None
    if ffmpeg_available:
        print("✅ FFmpeg found")
    else:
        print("⚠️  FFmpeg not found")
        print("   FFmpeg is required for video processing")
        print("   Install from: https://ffmpeg.org/download.html")
    
    # Check for CUDA (optional, for GPU acceleration)
    try:
        import torch
        if torch.cuda.is_available():
            print("✅ CUDA available for GPU acceleration")
        else:
            print("ℹ️  CUDA not available, will use CPU")
    except ImportError:
        print("ℹ️  PyTorch not installed, GPU check skipped")
    
    print()

def create_config_files():
    """Create additional configuration files"""
    print("⚙️  Creating configuration files...")
    
    # Create basic config file
    config_file = Path("config.py")
    if not config_file.exists():
        basic_config = """# Basic configuration file
# This file can be used to override default settings

from config.settings import settings

# Override settings here if needed
# settings.daily_video_count = 5
# settings.video_duration = 20
"""
        
        with open(config_file, 'w') as f:
            f.write(basic_config)
        
        print("  ✅ Created: config.py")
    
    # Create basic test file
    test_file = Path("test_system.py")
    if not test_file.exists():
        basic_test = """#!/usr/bin/env python3
\"\"\"
Basic system test
Run this to verify your installation
\"\"\"

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

async def test_system():
    \"\"\"Test basic system functionality\"\"\"
    try:
        from config.settings import settings
        print(f"✅ Settings loaded: {settings.app_name}")
        
        from utils.logger import setup_logging
        setup_logging()
        print("✅ Logging system initialized")
        
        from utils.database import DatabaseManager
        db = DatabaseManager()
        await db.initialize()
        print("✅ Database initialized")
        await db.cleanup()
        
        print("\\n🎉 All tests passed! System is ready to use.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_system())
    sys.exit(0 if success else 1)
"""
        
        with open(test_file, 'w') as f:
            f.write(basic_test)
        
        # Make executable
        test_file.chmod(0o755)
        
        print("  ✅ Created: test_system.py")
    
    print()

def print_next_steps():
    """Print next steps for the user"""
    print("🎯 Next Steps:")
    print("=" * 40)
    print("1. Edit .env file with your configuration")
    print("2. Set up social media API credentials")
    print("3. Run test: python test_system.py")
    print("4. Start the system: python main.py")
    print("5. Use CLI: python cli.py --help")
    print("6. Access dashboard: http://localhost:8000")
    print()
    print("📚 Documentation:")
    print("- README.md - System overview and usage")
    print("- config.env.example - Configuration options")
    print("- cli.py --help - Command line interface")
    print()

def main():
    """Main installation function"""
    print_banner()
    
    try:
        check_python_version()
        create_directories()
        create_env_file()
        install_dependencies()
        check_system_requirements()
        create_config_files()
        
        print("🎉 Installation completed successfully!")
        print()
        print_next_steps()
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
