"""
Configuration settings for the Short Video Generator system.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # Application settings
    app_name: str = "Short Video Generator"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_file: Optional[str] = Field(default="shorts_generator.log", description="Log file path")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    web_host: str = Field(default="0.0.0.0", description="Web dashboard host")
    web_port: int = Field(default=8000, description="Web dashboard port")
    web_secret_key: str = Field(default="your-secret-key-here-change-this", description="Web secret key")
    
    # Paths
    model_path: str = Field(default="./models", description="Models directory")
    output_dir: str = Field(default="./output", description="Output directory for videos")
    temp_dir: str = Field(default="./temp", description="Temporary directory")
    data_dir: str = Field(default="./data", description="Data directory")
    music_dir: str = Field(default="./assets/music", description="Music directory")
    sounds_dir: str = Field(default="./assets/sounds", description="Sound effects directory")
    background_music_dir: str = Field(default="./assets/music", description="Background music directory")
    
    # Database settings
    database_url: str = Field(
        default="sqlite:///./data/shorts.db",
        description="Database connection URL"
    )
    
    # AI/ML settings
    use_gpu: bool = Field(default=True, description="Use GPU for AI models")
    model_device: str = Field(default="cuda", description="Model device (cuda/cpu)")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    sd_model: str = Field(default="runwayml/stable-diffusion-v1-5", description="Stable Diffusion model")
    stable_diffusion_model: str = Field(default="runwayml/stable-diffusion-v1-5", description="Stable Diffusion model")
    video_model: str = Field(default="stabilityai/stable-video-diffusion-img2vid-xt", description="Stable Video Diffusion model")
    
    # Content generation settings
    daily_video_count: int = Field(default=3, description="Number of videos to generate per day")
    video_duration: int = Field(default=15, description="Video duration in seconds")
    video_resolution: str = Field(default="1080x1920", description="Video resolution")
    video_fps: int = Field(default=30, description="Video FPS")
    max_video_length: int = Field(default=60, description="Maximum video length in seconds")
    content_themes: str = Field(default="cute_animals,funny_pets,heartwarming_stories,educational_facts,seasonal_content", description="Content themes")
    
    # Video processing settings
    max_video_duration: int = Field(default=60, description="Maximum video duration in seconds")
    min_video_quality: str = Field(default="720p", description="Minimum video quality")
    enable_watermark: bool = Field(default=False, description="Enable watermark")
    watermark_text: str = Field(default="", description="Watermark text")
    
    # Audio settings
    audio_sample_rate: int = Field(default=44100, description="Audio sample rate")
    
    # Social media settings
    youtube_api_key: Optional[str] = Field(default=None, description="YouTube API key")
    youtube_client_id: Optional[str] = Field(default=None, description="YouTube client ID")
    youtube_client_secret: Optional[str] = Field(default=None, description="YouTube client secret")
    youtube_channel_id: Optional[str] = Field(default=None, description="YouTube channel ID")
    tiktok_access_token: Optional[str] = Field(default=None, description="TikTok access token")
    tiktok_client_key: Optional[str] = Field(default=None, description="TikTok client key")
    tiktok_client_secret: Optional[str] = Field(default=None, description="TikTok client secret")
    instagram_access_token: Optional[str] = Field(default=None, description="Instagram access token")
    instagram_username: Optional[str] = Field(default=None, description="Instagram username")
    instagram_password: Optional[str] = Field(default=None, description="Instagram password")
    instagram_session_file: Optional[str] = Field(default=None, description="Instagram session file")
    
    # Scheduling settings
    auto_publish: bool = Field(default=False, description="Enable automatic publishing")
    publish_schedule: str = Field(default="0 9 * * *", description="Cron schedule for publishing")
    upload_time: str = Field(default="09:00", description="Upload time")
    timezone: str = Field(default="UTC", description="Timezone")
    
    # Rate limiting
    max_requests_per_hour: int = Field(default=100, description="Maximum requests per hour")
    request_delay: float = Field(default=1.0, description="Delay between requests in seconds")
    
    # Storage settings
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Maximum file size in bytes")
    allowed_extensions: List[str] = Field(
        default=[".mp4", ".avi", ".mov", ".mkv", ".jpg", ".png", ".mp3", ".wav"],
        description="Allowed file extensions"
    )
    
    # Backup settings
    enable_backup: bool = Field(default=True, description="Enable backup")
    backup_interval_hours: int = Field(default=24, description="Backup interval in hours")
    max_backup_files: int = Field(default=7, description="Maximum backup files to keep")
    
    # Computed properties
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
        """Get list of enabled social media platforms"""
        platforms = []
        if self.is_youtube_enabled:
            platforms.append("YouTube")
        if self.is_instagram_enabled:
            platforms.append("Instagram")
        if self.is_tiktok_enabled:
            platforms.append("TikTok")
        return platforms

# Global settings instance
settings = Settings()
