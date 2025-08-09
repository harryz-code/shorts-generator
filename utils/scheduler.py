"""
Content Scheduler
Manages content generation and upload timing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import schedule
import time

from config.settings import settings

class ContentScheduler:
    """Manages content scheduling and timing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # Scheduling state
        self.last_generation = None
        self.last_upload = None
        self.content_queue = []
        self.upload_schedule = []
        
        # Daily schedule
        self.daily_generation_time = "06:00"  # 6 AM
        self.upload_times = ["09:00", "12:00", "15:00", "18:00"]  # Spread throughout day
    
    async def initialize(self):
        """Initialize scheduler"""
        try:
            self.logger.info("⏰ Initializing Content Scheduler...")
            
            # Setup daily schedule
            schedule.every().day.at(self.daily_generation_time).do(self._mark_daily_generation_needed)
            
            # Setup upload schedule
            for upload_time in self.upload_times:
                schedule.every().day.at(upload_time).do(self._mark_upload_time)
            
            self.logger.info("✅ Content Scheduler initialized!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize: {e}")
    
    async def should_generate_daily(self) -> bool:
        """Check if daily content generation is needed"""
        now = datetime.now()
        
        # Check if we haven't generated today
        if not self.last_generation:
            return True
        
        # Check if it's a new day
        if self.last_generation.date() < now.date():
            return True
        
        # Check if we need more content
        if len(self.content_queue) < self.settings.daily_video_count:
            return True
        
        return False
    
    async def should_upload(self, content: Dict[str, Any]) -> bool:
        """Check if content should be uploaded now"""
        now = datetime.now()
        
        # Check if content is scheduled for upload
        scheduled_time = content.get('scheduled_time')
        if scheduled_time and isinstance(scheduled_time, str):
            try:
                scheduled_time = datetime.fromisoformat(scheduled_time)
            except:
                scheduled_time = None
        
        if scheduled_time:
            # Check if it's time to upload
            if now >= scheduled_time:
                return True
        
        # Check if content has been queued long enough
        created_at = content.get('created_at')
        if created_at and isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
                # Upload if content is older than 2 hours
                if now - created_at > timedelta(hours=2):
                    return True
            except:
                pass
        
        return False
    
    async def queue_content(self, content: Dict[str, Any]):
        """Add content to upload queue"""
        try:
            # Add to queue
            self.content_queue.append(content)
            
            # Sort by priority (scheduled time first, then creation time)
            self.content_queue.sort(key=lambda x: (
                x.get('scheduled_time', datetime.max),
                x.get('created_at', datetime.max)
            ))
            
            self.logger.info(f"📋 Queued content: {content['title']}")
            
        except Exception as e:
            self.logger.error(f"❌ Error queuing content: {e}")
    
    async def get_queued_content(self) -> List[Dict[str, Any]]:
        """Get list of queued content"""
        return self.content_queue.copy()
    
    async def mark_uploaded(self, content_id: str):
        """Mark content as uploaded and remove from queue"""
        try:
            # Find and remove content from queue
            self.content_queue = [c for c in self.content_queue if c['id'] != content_id]
            
            # Update last upload time
            self.last_upload = datetime.now()
            
            self.logger.info(f"✅ Marked content as uploaded: {content_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error marking content uploaded: {e}")
    
    async def get_next_upload_time(self) -> Optional[datetime]:
        """Get next scheduled upload time"""
        now = datetime.now()
        
        for upload_time_str in self.upload_times:
            try:
                # Parse time
                time_parts = upload_time_str.split(':')
                hour, minute = int(time_parts[0]), int(time_parts[1])
                
                # Create datetime for today
                upload_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time has passed today, get tomorrow's time
                if upload_time <= now:
                    upload_time += timedelta(days=1)
                
                return upload_time
                
            except Exception as e:
                self.logger.error(f"❌ Error parsing upload time {upload_time_str}: {e}")
        
        return None
    
    async def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily statistics"""
        now = datetime.now()
        
        # Count content generated today
        today_content = [
            c for c in self.content_queue 
            if c.get('created_at') and 
            datetime.fromisoformat(c['created_at']).date() == now.date()
        ]
        
        # Count content uploaded today
        today_uploads = 0
        if self.last_upload and self.last_upload.date() == now.date():
            today_uploads = len([c for c in self.content_queue if c.get('uploaded_at')])
        
        return {
            'date': now.date().isoformat(),
            'content_generated': len(today_content),
            'content_uploaded': today_uploads,
            'queue_length': len(self.content_queue),
            'next_upload': await self.get_next_upload_time()
        }
    
    def _mark_daily_generation_needed(self):
        """Mark that daily generation is needed"""
        self.last_generation = None
        self.logger.info("🔄 Daily generation marked as needed")
    
    def _mark_upload_time(self):
        """Mark that it's time to upload"""
        self.logger.info("📤 Upload time reached")
    
    async def run_scheduler_loop(self):
        """Run the scheduler loop"""
        while True:
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def cleanup(self):
        """Cleanup scheduler"""
        try:
            # Clear all scheduled jobs
            schedule.clear()
            
            self.logger.info("🧹 Content Scheduler cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
