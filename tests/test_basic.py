"""
Basic tests for the Short Video Generator system
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import Settings
from utils.logger import setup_logging

class TestBasicFunctionality:
    """Test basic system functionality"""
    
    def test_settings_loading(self):
        """Test that settings can be loaded"""
        settings = Settings()
        assert settings.app_name == "Short Video Generator"
        assert settings.app_version == "1.0.0"
        assert isinstance(settings.daily_video_count, int)
        assert isinstance(settings.video_duration, int)
    
    def test_logger_setup(self):
        """Test that logger can be set up"""
        setup_logging()
        # If no exception is raised, the test passes
        assert True
    
    def test_project_structure(self):
        """Test that essential project files exist"""
        project_root = Path(__file__).parent.parent
        
        essential_files = [
            "main.py",
            "cli.py",
            "requirements.txt",
            "README.md",
            "config/settings.py",
            "agents/content_agent.py",
            "agents/video_agent.py",
            "agents/audio_agent.py",
            "agents/upload_agent.py",
            "utils/database.py",
            "utils/scheduler.py",
            "web/dashboard.py"
        ]
        
        for file_path in essential_files:
            assert (project_root / file_path).exists(), f"Missing file: {file_path}"

class TestConfiguration:
    """Test configuration system"""
    
    def test_environment_variables(self):
        """Test environment variable handling"""
        settings = Settings()
        
        # Test that required fields have defaults
        assert settings.host is not None
        assert settings.port is not None
        assert settings.web_host is not None
        assert settings.web_port is not None
        
        # Test that paths are valid
        assert isinstance(settings.output_dir, str)
        assert isinstance(settings.temp_dir, str)
        assert isinstance(settings.data_dir, str)

@pytest.mark.asyncio
async def test_async_functionality():
    """Test that async functionality works"""
    await asyncio.sleep(0.1)
    assert True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
