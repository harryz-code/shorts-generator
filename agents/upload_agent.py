"""
Upload Agent
Handles uploading videos to multiple social media platforms
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import os

from config.settings import settings

class UploadAgent:
    """Handles video uploads to social media platforms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # Platform clients
        self.youtube_client = None
        self.instagram_client = None
        self.tiktok_client = None
        
        # Upload status tracking
        self.upload_history = []
    
    async def initialize(self):
        """Initialize platform clients"""
        try:
            self.logger.info("📤 Initializing Upload Agent...")
            
            # Initialize YouTube client
            if self.settings.is_youtube_enabled:
                await self._init_youtube()
            
            # Initialize Instagram client
            if self.settings.is_instagram_enabled:
                await self._init_instagram()
            
            # Initialize TikTok client
            if self.settings.is_tiktok_enabled:
                await self._init_tiktok()
            
            self.logger.info("✅ Upload Agent initialized!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize: {e}")
    
    async def _init_youtube(self):
        """Initialize YouTube API client"""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            
            # YouTube API setup
            SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
            
            creds = None
            token_file = 'token.json'
            
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secrets.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.youtube_client = build('youtube', 'v3', credentials=creds)
            self.logger.info("✅ YouTube client initialized")
            
        except Exception as e:
            self.logger.error(f"❌ YouTube init failed: {e}")
    
    async def _init_instagram(self):
        """Initialize Instagram client"""
        try:
            from instagram_private_api import Client
            
            self.instagram_client = Client(
                self.settings.instagram_username,
                self.settings.instagram_password
            )
            self.logger.info("✅ Instagram client initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Instagram init failed: {e}")
    
    async def _init_tiktok(self):
        """Initialize TikTok client"""
        try:
            # TikTok API is limited, using basic setup
            self.tiktok_client = {
                'access_token': self.settings.tiktok_access_token,
                'client_key': self.settings.tiktok_client_key,
                'client_secret': self.settings.tiktok_client_secret
            }
            self.logger.info("✅ TikTok client initialized")
            
        except Exception as e:
            self.logger.error(f"❌ TikTok init failed: {e}")
    
    async def upload_to_all_platforms(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to all enabled platforms"""
        try:
            self.logger.info(f"📤 Uploading to all platforms: {content['title']}")
            
            results = {}
            
            # Upload to YouTube
            if self.settings.is_youtube_enabled:
                try:
                    youtube_result = await self._upload_to_youtube(content)
                    results['youtube'] = youtube_result
                except Exception as e:
                    self.logger.error(f"❌ YouTube upload failed: {e}")
                    results['youtube'] = {'success': False, 'error': str(e)}
            
            # Upload to Instagram
            if self.settings.is_instagram_enabled:
                try:
                    instagram_result = await self._upload_to_instagram(content)
                    results['instagram'] = instagram_result
                except Exception as e:
                    self.logger.error(f"❌ Instagram upload failed: {e}")
                    results['instagram'] = {'success': False, 'error': str(e)}
            
            # Upload to TikTok
            if self.settings.is_tiktok_enabled:
                try:
                    tiktok_result = await self._upload_to_tiktok(content)
                    results['tiktok'] = tiktok_result
                except Exception as e:
                    self.logger.error(f"❌ TikTok upload failed: {e}")
                    results['tiktok'] = {'success': False, 'error': str(e)}
            
            # Record upload
            self._record_upload(content, results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Upload failed: {e}")
            return {'error': str(e)}
    
    async def _upload_to_youtube(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Upload video to YouTube"""
        try:
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': content['title'],
                    'description': content['description'],
                    'tags': content.get('tags', []),
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video
            media = MediaFileUpload(
                content['video_path'],
                mimetype='video/mp4',
                resumable=True
            )
            
            request = self.youtube_client.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            return {
                'success': True,
                'video_id': response['id'],
                'url': f"https://youtu.be/{response['id']}",
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ YouTube upload error: {e}")
            raise
    
    async def _upload_to_instagram(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Upload video to Instagram"""
        try:
            if not self.instagram_client:
                raise Exception("Instagram client not initialized")
            
            # Instagram Reels upload
            result = self.instagram_client.post_video(
                video_path=content['video_path'],
                caption=content['description'],
                extra_data={
                    'custom_accessibility_caption': content['title'],
                    'like_and_view_counts_disabled': False,
                    'disable_comments': False
                }
            )
            
            return {
                'success': True,
                'media_id': result['media']['id'],
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Instagram upload error: {e}")
            raise
    
    async def _upload_to_tiktok(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Upload video to TikTok"""
        try:
            if not self.tiktok_client:
                raise Exception("TikTok client not initialized")
            
            # TikTok upload (simplified - would need proper API integration)
            # For now, return success status
            return {
                'success': True,
                'uploaded_at': datetime.now().isoformat(),
                'note': 'TikTok upload simulated - requires proper API integration'
            }
            
        except Exception as e:
            self.logger.error(f"❌ TikTok upload error: {e}")
            raise
    
    def _record_upload(self, content: Dict[str, Any], results: Dict[str, Any]):
        """Record upload history"""
        upload_record = {
            'content_id': content['id'],
            'title': content['title'],
            'uploaded_at': datetime.now().isoformat(),
            'results': results,
            'video_path': content['video_path']
        }
        
        self.upload_history.append(upload_record)
        
        # Keep only last 100 uploads
        if len(self.upload_history) > 100:
            self.upload_history = self.upload_history[-100:]
    
    async def get_upload_status(self, content_id: str) -> Dict[str, Any]:
        """Get upload status for specific content"""
        for record in self.upload_history:
            if record['content_id'] == content_id:
                return record
        return {'error': 'Content not found'}
    
    async def get_upload_history(self) -> List[Dict[str, Any]]:
        """Get upload history"""
        return self.upload_history
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Clear clients
            self.youtube_client = None
            self.instagram_client = None
            self.tiktok_client = None
            
            self.logger.info("🧹 Upload Agent cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
