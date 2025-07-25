"""
Content Validator Utility
Validates video content, checks quality, and ensures platform compliance
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import json
from datetime import datetime

from config.settings import settings

class ContentValidator:
    """Validates content quality and platform compliance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # Platform requirements
        self.platform_requirements = {
            'youtube': {
                'min_resolution': (1280, 720),
                'max_duration': 60,
                'min_duration': 1,
                'max_file_size_mb': 128,
                'allowed_formats': ['.mp4', '.avi', '.mov'],
                'aspect_ratio': '16:9'  # or '9:16' for shorts
            },
            'instagram': {
                'min_resolution': (1080, 1080),
                'max_duration': 60,
                'min_duration': 1,
                'max_file_size_mb': 100,
                'allowed_formats': ['.mp4'],
                'aspect_ratio': '1:1'  # square for posts, 9:16 for reels
            },
            'tiktok': {
                'min_resolution': (1080, 1920),
                'max_duration': 60,
                'min_duration': 1,
                'max_file_size_mb': 287,
                'allowed_formats': ['.mp4'],
                'aspect_ratio': '9:16'  # vertical format
            }
        }
    
    async def validate_video(self, video_path: str, platform: str = None) -> Dict[str, Any]:
        """Validate video content for quality and platform compliance"""
        try:
            self.logger.info(f"🔍 Validating video: {video_path}")
            
            if not os.path.exists(video_path):
                return {
                    'valid': False,
                    'errors': ['Video file does not exist'],
                    'warnings': []
                }
            
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'metadata': {},
                'platform_compliance': {}
            }
            
            # Basic video validation
            basic_validation = await self._validate_basic_video(video_path)
            validation_result['metadata'] = basic_validation
            
            if not basic_validation.get('valid', False):
                validation_result['valid'] = False
                validation_result['errors'].extend(basic_validation.get('errors', []))
                return validation_result
            
            # Quality validation
            quality_validation = await self._validate_video_quality(video_path)
            validation_result['warnings'].extend(quality_validation.get('warnings', []))
            
            # Platform-specific validation
            if platform:
                platform_validation = await self._validate_platform_requirements(
                    video_path, platform, basic_validation
                )
                validation_result['platform_compliance'][platform] = platform_validation
                
                if not platform_validation.get('compliant', False):
                    validation_result['warnings'].extend(platform_validation.get('warnings', []))
            
            self.logger.info(f"✅ Video validation completed: {len(validation_result['errors'])} errors, {len(validation_result['warnings'])} warnings")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"❌ Error validating video: {e}")
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}'],
                'warnings': []
            }
    
    async def _validate_basic_video(self, video_path: str) -> Dict[str, Any]:
        """Validate basic video properties"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {
                    'valid': False,
                    'errors': ['Cannot open video file']
                }
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Check file size
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            
            cap.release()
            
            # Basic validation
            errors = []
            if duration <= 0:
                errors.append('Invalid video duration')
            if width <= 0 or height <= 0:
                errors.append('Invalid video dimensions')
            if fps <= 0:
                errors.append('Invalid frame rate')
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration,
                'file_size_mb': file_size_mb,
                'aspect_ratio': f"{width}:{height}"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in basic video validation: {e}")
            return {
                'valid': False,
                'errors': [f'Basic validation error: {str(e)}']
            }
    
    async def _validate_video_quality(self, video_path: str) -> Dict[str, Any]:
        """Validate video quality metrics"""
        try:
            warnings = []
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {'warnings': ['Cannot analyze video quality']}
            
            # Sample frames for quality analysis
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_indices = [0, frame_count // 4, frame_count // 2, 3 * frame_count // 4, frame_count - 1]
            
            brightness_values = []
            contrast_values = []
            
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Convert to grayscale for analysis
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Brightness (mean pixel value)
                    brightness = np.mean(gray)
                    brightness_values.append(brightness)
                    
                    # Contrast (standard deviation)
                    contrast = np.std(gray)
                    contrast_values.append(contrast)
            
            cap.release()
            
            # Analyze quality metrics
            if brightness_values:
                avg_brightness = np.mean(brightness_values)
                if avg_brightness < 30:
                    warnings.append('Video may be too dark')
                elif avg_brightness > 225:
                    warnings.append('Video may be too bright')
            
            if contrast_values:
                avg_contrast = np.mean(contrast_values)
                if avg_contrast < 20:
                    warnings.append('Video may have low contrast')
            
            return {'warnings': warnings}
            
        except Exception as e:
            self.logger.error(f"❌ Error in quality validation: {e}")
            return {'warnings': [f'Quality validation error: {str(e)}']}
    
    async def _validate_platform_requirements(self, video_path: str, platform: str, video_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate video against platform-specific requirements"""
        try:
            if platform not in self.platform_requirements:
                return {
                    'compliant': False,
                    'warnings': [f'Unknown platform: {platform}']
                }
            
            requirements = self.platform_requirements[platform]
            warnings = []
            
            # Check resolution
            width = video_metadata.get('width', 0)
            height = video_metadata.get('height', 0)
            min_width, min_height = requirements['min_resolution']
            
            if width < min_width or height < min_height:
                warnings.append(f'Resolution {width}x{height} below minimum {min_width}x{min_height}')
            
            # Check duration
            duration = video_metadata.get('duration', 0)
            if duration < requirements['min_duration']:
                warnings.append(f'Duration {duration:.1f}s below minimum {requirements["min_duration"]}s')
            elif duration > requirements['max_duration']:
                warnings.append(f'Duration {duration:.1f}s above maximum {requirements["max_duration"]}s')
            
            # Check file size
            file_size_mb = video_metadata.get('file_size_mb', 0)
            if file_size_mb > requirements['max_file_size_mb']:
                warnings.append(f'File size {file_size_mb:.1f}MB above maximum {requirements["max_file_size_mb"]}MB')
            
            # Check format
            video_ext = Path(video_path).suffix.lower()
            if video_ext not in requirements['allowed_formats']:
                warnings.append(f'Format {video_ext} not allowed for {platform}')
            
            # Check aspect ratio
            if width > 0 and height > 0:
                aspect_ratio = width / height
                expected_ratio = self._parse_aspect_ratio(requirements['aspect_ratio'])
                if expected_ratio and abs(aspect_ratio - expected_ratio) > 0.1:
                    warnings.append(f'Aspect ratio {width}:{height} differs from expected {requirements["aspect_ratio"]}')
            
            return {
                'compliant': len(warnings) == 0,
                'warnings': warnings,
                'requirements': requirements
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in platform validation: {e}")
            return {
                'compliant': False,
                'warnings': [f'Platform validation error: {str(e)}']
            }
    
    def _parse_aspect_ratio(self, ratio_str: str) -> Optional[float]:
        """Parse aspect ratio string to float value"""
        try:
            if ':' in ratio_str:
                width, height = map(int, ratio_str.split(':'))
                return width / height
            return None
        except:
            return None
    
    async def validate_content_metadata(self, metadata: Dict[str, Any], platform: str = None) -> Dict[str, Any]:
        """Validate content metadata for platform compliance"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check required fields
            required_fields = ['title', 'description']
            for field in required_fields:
                if field not in metadata or not metadata[field]:
                    validation_result['errors'].append(f'Missing required field: {field}')
                    validation_result['valid'] = False
            
            # Check title length
            if 'title' in metadata:
                title = metadata['title']
                if len(title) < 5:
                    validation_result['warnings'].append('Title may be too short')
                elif len(title) > 100:
                    validation_result['warnings'].append('Title may be too long')
            
            # Check description length
            if 'description' in metadata:
                desc = metadata['description']
                if len(desc) < 10:
                    validation_result['warnings'].append('Description may be too short')
                elif len(desc) > 5000:
                    validation_result['warnings'].append('Description may be too long')
            
            # Platform-specific metadata validation
            if platform:
                platform_validation = await self._validate_platform_metadata(metadata, platform)
                validation_result['warnings'].extend(platform_validation.get('warnings', []))
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"❌ Error validating metadata: {e}")
            return {
                'valid': False,
                'errors': [f'Metadata validation error: {str(e)}'],
                'warnings': []
            }
    
    async def _validate_platform_metadata(self, metadata: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Validate metadata against platform-specific requirements"""
        try:
            warnings = []
            
            if platform == 'youtube':
                # YouTube-specific validation
                if 'tags' in metadata:
                    tags = metadata['tags']
                    if isinstance(tags, str):
                        tags = [tag.strip() for tag in tags.split(',')]
                    
                    if len(tags) > 500:
                        warnings.append('YouTube allows maximum 500 tags')
                    elif len(tags) < 3:
                        warnings.append('Consider adding more tags for better discoverability')
            
            elif platform == 'instagram':
                # Instagram-specific validation
                if 'hashtags' in metadata:
                    hashtags = metadata['hashtags']
                    if isinstance(hashtags, str):
                        hashtags = [tag.strip() for tag in hashtags.split(',')]
                    
                    if len(hashtags) > 30:
                        warnings.append('Instagram allows maximum 30 hashtags')
                    elif len(hashtags) < 5:
                        warnings.append('Consider adding more hashtags for better reach')
            
            elif platform == 'tiktok':
                # TikTok-specific validation
                if 'hashtags' in metadata:
                    hashtags = metadata['hashtags']
                    if isinstance(hashtags, str):
                        hashtags = [tag.strip() for tag in hashtags.split(',')]
                    
                    if len(hashtags) > 100:
                        warnings.append('TikTok allows maximum 100 hashtags')
                    elif len(hashtags) < 3:
                        warnings.append('Consider adding more hashtags for better discoverability')
            
            return {'warnings': warnings}
            
        except Exception as e:
            self.logger.error(f"❌ Error in platform metadata validation: {e}")
            return {'warnings': [f'Platform metadata validation error: {str(e)}']}
    
    async def generate_validation_report(self, video_path: str, metadata: Dict[str, Any] = None, platforms: List[str] = None) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        try:
            if platforms is None:
                platforms = list(self.platform_requirements.keys())
            
            report = {
                'video_path': video_path,
                'timestamp': str(datetime.now()),
                'video_validation': await self.validate_video(video_path),
                'platform_compliance': {},
                'overall_score': 0
            }
            
            # Validate for each platform
            for platform in platforms:
                platform_validation = await self.validate_video(video_path, platform)
                report['platform_compliance'][platform] = platform_validation
            
            # Validate metadata if provided
            if metadata:
                report['metadata_validation'] = await self.validate_content_metadata(metadata)
            
            # Calculate overall score
            report['overall_score'] = self._calculate_validation_score(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating validation report: {e}")
            return {
                'error': f'Failed to generate report: {str(e)}',
                'timestamp': str(datetime.now())
            }
    
    def _calculate_validation_score(self, report: Dict[str, Any]) -> int:
        """Calculate overall validation score (0-100)"""
        try:
            score = 100
            
            # Deduct points for errors
            video_errors = len(report.get('video_validation', {}).get('errors', []))
            score -= video_errors * 20
            
            # Deduct points for warnings
            video_warnings = len(report.get('video_validation', {}).get('warnings', []))
            score -= video_warnings * 5
            
            # Check platform compliance
            for platform, compliance in report.get('platform_compliance', {}).items():
                if not compliance.get('valid', True):
                    score -= 10
                platform_warnings = len(compliance.get('warnings', []))
                score -= platform_warnings * 2
            
            return max(0, score)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating validation score: {e}")
            return 0
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            self.logger.info("✅ Content validator cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
