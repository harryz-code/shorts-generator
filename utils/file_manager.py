"""
File Manager Utility
Handles file operations, cleanup, and storage management
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

from config.settings import settings

class FileManager:
    """Manages file operations and storage"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.settings.output_dir,
            self.settings.temp_dir,
            self.settings.data_dir,
            self.settings.music_dir,
            Path(self.settings.output_dir) / "videos",
            Path(self.settings.output_dir) / "images",
            Path(self.settings.output_dir) / "thumbnails"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def save_video(self, video_path: str, metadata: Dict[str, Any]) -> str:
        """Save video to output directory with metadata"""
        try:
            source_path = Path(video_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source video not found: {video_path}")
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_hash = self._generate_content_hash(metadata)
            filename = f"video_{timestamp}_{content_hash[:8]}.mp4"
            
            # Determine output path
            output_path = Path(self.settings.output_dir) / "videos" / filename
            
            # Copy video to output directory
            shutil.copy2(source_path, output_path)
            
            # Save metadata
            metadata_path = output_path.with_suffix('.json')
            await self._save_metadata(metadata_path, metadata)
            
            self.logger.info(f"✅ Video saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error saving video: {e}")
            raise
    
    async def save_image(self, image_path: str, metadata: Dict[str, Any]) -> str:
        """Save image to output directory"""
        try:
            source_path = Path(image_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source image not found: {image_path}")
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_hash = self._generate_content_hash(metadata)
            filename = f"image_{timestamp}_{content_hash[:8]}.png"
            
            # Determine output path
            output_path = Path(self.settings.output_dir) / "images" / filename
            
            # Copy image to output directory
            shutil.copy2(source_path, output_path)
            
            self.logger.info(f"✅ Image saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error saving image: {e}")
            raise
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified age"""
        try:
            temp_dir = Path(self.settings.temp_dir)
            if not temp_dir.exists():
                return
            
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
            
            if cleaned_count > 0:
                self.logger.info(f"🧹 Cleaned up {cleaned_count} temporary files")
                
        except Exception as e:
            self.logger.error(f"❌ Error cleaning temp files: {e}")
    
    async def cleanup_old_outputs(self, max_age_days: int = 7):
        """Clean up old output files"""
        try:
            output_dir = Path(self.settings.output_dir)
            if not output_dir.exists():
                return
            
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            cleaned_count = 0
            
            for file_path in output_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.mp4', '.png', '.jpg']:
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
            
            if cleaned_count > 0:
                self.logger.info(f"🧹 Cleaned up {cleaned_count} old output files")
                
        except Exception as e:
            self.logger.error(f"❌ Error cleaning old outputs: {e}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage usage information"""
        try:
            info = {}
            
            # Check output directory
            output_dir = Path(self.settings.output_dir)
            if output_dir.exists():
                output_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
                info['output_size_mb'] = round(output_size / (1024 * 1024), 2)
                info['output_file_count'] = len(list(output_dir.rglob('*')))
            
            # Check temp directory
            temp_dir = Path(self.settings.temp_dir)
            if temp_dir.exists():
                temp_size = sum(f.stat().st_size for f in temp_dir.rglob('*') if f.is_file())
                info['temp_size_mb'] = round(temp_size / (1024 * 1024), 2)
                info['temp_file_count'] = len(list(temp_dir.rglob('*')))
            
            # Check available disk space
            total, used, free = shutil.disk_usage(self.settings.output_dir)
            info['disk_total_gb'] = round(total / (1024**3), 2)
            info['disk_used_gb'] = round(used / (1024**3), 2)
            info['disk_free_gb'] = round(free / (1024**3), 2)
            info['disk_usage_percent'] = round((used / total) * 100, 2)
            
            return info
            
        except Exception as e:
            self.logger.error(f"❌ Error getting storage info: {e}")
            return {}
    
    def _generate_content_hash(self, metadata: Dict[str, Any]) -> str:
        """Generate hash from content metadata"""
        content_string = f"{metadata.get('title', '')}{metadata.get('description', '')}{metadata.get('theme', '')}"
        return hashlib.md5(content_string.encode()).hexdigest()
    
    async def _save_metadata(self, metadata_path: Path, metadata: Dict[str, Any]):
        """Save metadata to JSON file"""
        try:
            import json
            metadata['saved_at'] = datetime.now().isoformat()
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"❌ Error saving metadata: {e}")
    
    async def backup_content(self, backup_dir: str = None):
        """Create backup of content"""
        try:
            if not backup_dir:
                backup_dir = Path(self.settings.data_dir) / "backups"
            
            backup_path = Path(backup_dir) / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup database
            db_path = Path(self.settings.data_dir) / "shorts.db"
            if db_path.exists():
                shutil.copy2(db_path, backup_path / "shorts.db")
            
            # Backup output directory
            output_dir = Path(self.settings.output_dir)
            if output_dir.exists():
                shutil.copytree(output_dir, backup_path / "output", dirs_exist_ok=True)
            
            self.logger.info(f"✅ Backup created: {backup_path}")
            
            # Clean old backups
            await self._cleanup_old_backups(backup_dir)
            
        except Exception as e:
            self.logger.error(f"❌ Error creating backup: {e}")
    
    async def _cleanup_old_backups(self, backup_dir: str, max_backups: int = None):
        """Clean up old backup files"""
        try:
            if max_backups is None:
                max_backups = self.settings.max_backup_files
            
            backup_path = Path(backup_dir)
            if not backup_path.exists():
                return
            
            # Get all backup directories
            backup_dirs = [d for d in backup_path.iterdir() if d.is_dir() and d.name.startswith('backup_')]
            backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for old_backup in backup_dirs[max_backups:]:
                shutil.rmtree(old_backup)
                self.logger.info(f"🧹 Removed old backup: {old_backup}")
                
        except Exception as e:
            self.logger.error(f"❌ Error cleaning old backups: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.cleanup_temp_files()
            await self.cleanup_old_outputs()
            self.logger.info("✅ File manager cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
