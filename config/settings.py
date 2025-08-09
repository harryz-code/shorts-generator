"""
Configuration settings for the Short Video Generator
Manages environment variables, defaults, and system configuration
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Cute Animal Short Generator"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    models_dir: Path = Field(default="./models", env="MODEL_PATH")
    output_dir: Path = Field(default="./output", env="OUTPUT_DIR")
    temp_dir: Path = Field(default="./temp", env="TEMP_DIR")
    data_dir: Path = Field(default="./data", env="DATA_DIR")
    
    # AI Models
    use_gpu: bool = Field(default=True, env="USE_GPU")
    model_device: str = Field(default="cuda" if os.environ.get("USE_GPU", "true").lower() == "true" else "cpu")
    
    # Content Generation
    daily_video_count: int = Field(default=3, env="DAILY_VIDEO_COUNT")
    video_duration: int = Field(default=15, env="VIDEO_DURATION")  # seconds
    video_resolution: str = Field(default="1080x1920", env="VIDEO_RESOLUTION")  # vertical for shorts
    video_fps: int = Field(default=30, env="VIDEO_FPS")
    
    # Content Themes
    content_themes: List[str] = [
        "cute_animals",
        "funny_pets", 
        "heartwarming_stories",
        "educational_facts",
        "seasonal_content"
    ]
    
    # Video Generation
    stable_diffusion_model: str = Field(default="runwayml/stable-diffusion-v1-5", env="SD_MODEL")
    video_model: str = Field(default="damo-vilab/text-to-video-zero", env="VIDEO_MODEL")
    max_video_length: int = Field(default=60, env="MAX_VIDEO_LENGTH")
    
    # Audio Settings
    audio_sample_rate: int = Field(default=44100, env="AUDIO_SAMPLE_RATE")
    background_music_dir: Path = Field(default="./assets/music", env="MUSIC_DIR")
    sound_effects_dir: Path = Field(default="./assets/sounds", env="SOUNDS_DIR")
    
    # Social Media Settings
    upload_time: str = Field(default="09:00", env="UPLOAD_TIME")
    timezone: str = Field(default="UTC", env="TIMEZONE")
    
    # YouTube Settings
    youtube_api_key: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")
    youtube_client_id: Optional[str] = Field(default=None, env="YOUTUBE_CLIENT_ID")
    youtube_client_secret: Optional[str] = Field(default=None, env="YOUTUBE_CLIENT_SECRET")
    youtube_channel_id: Optional[str] = Field(default=None, env="YOUTUBE_CHANNEL_ID")
    
    # Instagram Settings
    instagram_username: Optional[str] = Field(default=None, env="INSTAGRAM_USERNAME")
    instagram_password: Optional[str] = Field(default=None, env="INSTAGRAM_PASSWORD")
    instagram_session_file: Optional[str] = Field(default=None, env="INSTAGRAM_SESSION_FILE")
    
    # TikTok Settings
    tiktok_access_token: Optional[str] = Field(default=None, env="TIKTOK_ACCESS_TOKEN")
    tiktok_client_key: Optional[str] = Field(default=None, env="TIKTOK_CLIENT_KEY")
    tiktok_client_secret: Optional[str] = Field(default=None, env="TIKTOK_CLIENT_SECRET")
    
    # Database
    database_url: str = Field(default="sqlite:///./data/shorts.db", env="DATABASE_URL")
    
    # Web Dashboard
    web_host: str = Field(default="0.0.0.0", env="WEB_HOST")
    web_port: int = Field(default=8000, env="WEB_PORT")
    web_secret_key: str = Field(default="your-secret-key-here", env="WEB_SECRET_KEY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Rate Limiting
    max_requests_per_hour: int = Field(default=100, env="MAX_REQUESTS_PER_HOUR")
    request_delay: float = Field(default=1.0, env="REQUEST_DELAY")  # seconds
    
    # Quality Settings
    min_video_quality: str = Field(default="720p", env="MIN_VIDEO_QUALITY")
    enable_watermark: bool = Field(default=False, env="ENABLE_WATERMARK")
    watermark_text: str = Field(default="", env="WATERMARK_TEXT")
    
    # Backup Settings
    enable_backup: bool = Field(default=True, env="ENABLE_BACKUP")
    backup_interval_hours: int = Field(default=24, env="BACKUP_INTERVAL_HOURS")
    max_backup_files: int = Field(default=7, env="MAX_BACKUP_FILES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Create necessary directories
        self.models_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.background_music_dir.mkdir(exist_ok=True, parents=True)
        self.sound_effects_dir.mkdir(exist_ok=True, parents=True)
    
    @property
    def is_youtube_enabled(self) -> bool:
        """Check if YouTube integration is enabled"""
        return all([
            self.youtube_api_key,
            self.youtube_client_id,
            self.youtube_client_secret
        ])
    
    @property
    def is_instagram_enabled(self) -> bool:
        """Check if Instagram integration is enabled"""
        return all([
            self.instagram_username,
            self.instagram_password
        ])
    
    @property
    def is_tiktok_enabled(self) -> bool:
        """Check if TikTok integration is enabled"""
        return all([
            self.tiktok_access_token,
            self.tiktok_client_key,
            self.tiktok_client_secret
        ])
    
    def get_platforms(self) -> List[str]:
        """Get list of enabled platforms"""
        platforms = []
        if self.is_youtube_enabled:
            platforms.append("youtube")
        if self.is_instagram_enabled:
            platforms.append("instagram")
        if self.is_tiktok_enabled:
            platforms.append("tiktok")
        return platforms
    
    def validate(self) -> bool:
        """Validate critical settings"""
        errors = []
        
        if not self.get_platforms():
            errors.append("At least one social media platform must be configured")
        
        if self.daily_video_count <= 0:
            errors.append("Daily video count must be positive")
        
        if self.video_duration <= 0 or self.video_duration > self.max_video_length:
            errors.append(f"Video duration must be between 1 and {self.max_video_length} seconds")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True

# Global settings instance
settings = Settings()
