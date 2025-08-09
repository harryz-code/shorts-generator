#!/usr/bin/env python3
"""
Main application for the Cute Animal Short Video Generator
Coordinates all agents, models, and platform integrations
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import Settings
from agents.content_agent import ContentAgent
from agents.video_agent import VideoAgent
from agents.audio_agent import AudioAgent
from agents.upload_agent import UploadAgent
from utils.scheduler import ContentScheduler
from utils.database import DatabaseManager
from web.dashboard import start_dashboard
from utils.logger import setup_logging

class ShortVideoGenerator:
    """Main orchestrator for the video generation system"""
    
    def __init__(self):
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db = DatabaseManager()
        self.content_agent = ContentAgent()
        self.video_agent = VideoAgent()
        self.audio_agent = AudioAgent()
        self.upload_agent = UploadAgent()
        self.scheduler = ContentScheduler()
        
        # State tracking
        self.is_running = False
        self.current_tasks: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize all system components"""
        try:
            self.logger.info("🚀 Initializing Short Video Generator...")
            
            # Setup database
            await self.db.initialize()
            
            # Initialize agents
            await self.content_agent.initialize()
            await self.video_agent.initialize()
            await self.audio_agent.initialize()
            await self.upload_agent.initialize()
            
            # Setup scheduler
            await self.scheduler.initialize()
            
            self.logger.info("✅ System initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize system: {e}")
            raise
    
    async def generate_daily_content(self):
        """Generate the daily batch of videos"""
        try:
            self.logger.info("🎬 Starting daily content generation...")
            
            # Generate content ideas
            ideas = await self.content_agent.generate_ideas(
                count=self.settings.daily_video_count,
                theme="cute_animals"
            )
            
            for idea in ideas:
                self.logger.info(f"📝 Processing idea: {idea['title']}")
                
                # Generate video
                video_path = await self.video_agent.generate_video(
                    prompt=idea['description'],
                    duration=self.settings.video_duration
                )
                
                # Add audio
                final_video = await self.audio_agent.add_audio(
                    video_path=video_path,
                    script=idea['script'],
                    music_style="upbeat_cute"
                )
                
                # Queue for upload
                await self.scheduler.queue_content({
                    'id': idea['id'],
                    'title': idea['title'],
                    'description': idea['description'],
                    'video_path': final_video,
                    'platforms': ['youtube', 'instagram', 'tiktok'],
                    'scheduled_time': idea['optimal_time']
                })
                
                self.logger.info(f"✅ Completed: {idea['title']}")
                
        except Exception as e:
            self.logger.error(f"❌ Error in daily content generation: {e}")
    
    async def run_upload_cycle(self):
        """Run the upload cycle for queued content"""
        try:
            self.logger.info("📤 Starting upload cycle...")
            
            # Get queued content
            queued_content = await self.scheduler.get_queued_content()
            
            for content in queued_content:
                if await self.scheduler.should_upload(content):
                    self.logger.info(f"📤 Uploading: {content['title']}")
                    
                    # Upload to all platforms
                    results = await self.upload_agent.upload_to_all_platforms(content)
                    
                    # Update database with results
                    await self.db.update_upload_status(content['id'], results)
                    
                    # Mark as uploaded
                    await self.scheduler.mark_uploaded(content['id'])
                    
                    self.logger.info(f"✅ Uploaded: {content['title']}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error in upload cycle: {e}")
    
    async def run_main_loop(self):
        """Main application loop"""
        self.is_running = True
        
        while self.is_running:
            try:
                # Check if it's time for daily generation
                if await self.scheduler.should_generate_daily():
                    await self.generate_daily_content()
                
                # Run upload cycle
                await self.run_upload_cycle()
                
                # Wait before next cycle
                await asyncio.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Shutdown requested...")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def shutdown(self):
        """Clean shutdown of the system"""
        self.logger.info("🔄 Shutting down...")
        self.is_running = False
        
        # Cleanup
        await self.content_agent.cleanup()
        await self.video_agent.cleanup()
        await self.audio_agent.cleanup()
        await self.upload_agent.cleanup()
        await self.db.cleanup()
        
        self.logger.info("👋 Goodbye!")

async def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create and initialize generator
    generator = ShortVideoGenerator()
    
    try:
        # Initialize system
        await generator.initialize()
        
        # Start web dashboard in background
        dashboard_task = asyncio.create_task(start_dashboard())
        
        # Run main loop
        await generator.run_main_loop()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
    finally:
        # Cleanup
        await generator.shutdown()

if __name__ == "__main__":
    # Run the application
    asyncio.run(main())
