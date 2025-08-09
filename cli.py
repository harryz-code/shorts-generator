#!/usr/bin/env python3
"""
Command Line Interface for the Short Video Generator
Provides easy access to all system functions
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from agents.content_agent import ContentAgent
from agents.video_agent import VideoAgent
from agents.audio_agent import AudioAgent
from agents.upload_agent import UploadAgent
from utils.scheduler import ContentScheduler
from utils.database import DatabaseManager
from utils.logger import setup_logging, get_logger

class ShortGeneratorCLI:
    """Command line interface for the video generation system"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings = settings
        
        # Initialize components
        self.db = DatabaseManager()
        self.content_agent = ContentAgent()
        self.video_agent = VideoAgent()
        self.audio_agent = AudioAgent()
        self.upload_agent = UploadAgent()
        self.scheduler = ContentScheduler()
        
        # Initialize state
        self.initialized = False
    
    async def initialize(self):
        """Initialize all system components"""
        if self.initialized:
            return
            
        try:
            self.logger.info("▶️ Initializing system components...")
            
            # Setup database
            await self.db.initialize()
            
            # Initialize agents
            await self.content_agent.initialize()
            await self.video_agent.initialize()
            await self.audio_agent.initialize()
            await self.upload_agent.initialize()
            
            # Setup scheduler
            await self.scheduler.initialize()
            
            self.initialized = True
            self.logger.info("✅ System initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize system: {e}")
            raise
    
    async def generate_content(self, count: int = 3, theme: str = "cute_animals"):
        """Generate content using the content agent"""
        try:
            await self.initialize()
            
            self.logger.info(f"🎬 Generating {count} videos with theme: {theme}")
            
            # Generate content ideas
            ideas = await self.content_agent.generate_ideas(count=count, theme=theme)
            
            for idea in ideas:
                self.logger.info(f"📝 Processing: {idea['title']}")
                
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
                
                # Save to database
                idea['video_path'] = final_video
                await self.db.save_content(idea)
                
                # Queue for upload
                await self.scheduler.queue_content(idea)
                
                self.logger.info(f"✅ Completed: {idea['title']}")
            
            self.logger.info(f"🎉 Successfully generated {count} videos!")
            
        except Exception as e:
            self.logger.error(f"❌ Error generating content: {e}")
            raise
    
    async def list_content(self, limit: int = 20):
        """List all generated content"""
        try:
            await self.initialize()
            
            content = await self.db.get_all_content(limit=limit)
            
            if not content:
                print("📭 No content found")
                return
            
            print(f"📋 Found {len(content)} content items:")
            print("-" * 80)
            
            for item in content:
                print(f"ID: {item['id']}")
                print(f"Title: {item['title']}")
                print(f"Category: {item.get('category', 'N/A')}")
                print(f"Created: {item.get('created_at', 'N/A')}")
                if item.get('video_path'):
                    print(f"Video: {item['video_path']}")
                print("-" * 40)
            
        except Exception as e:
            self.logger.error(f"❌ Error listing content: {e}")
            raise
    
    async def upload_content(self, content_id: Optional[str] = None):
        """Upload content to social media platforms"""
        try:
            await self.initialize()
            
            if content_id:
                # Upload specific content
                content = await self.db.get_content(content_id)
                if not content:
                    self.logger.error(f"❌ Content not found: {content_id}")
                    return
                
                self.logger.info(f"📤 Uploading content: {content['title']}")
                results = await self.upload_agent.upload_to_all_platforms(content)
                
                # Save results
                for platform, result in results.items():
                    await self.db.save_upload_result(content_id, platform, result)
                
                self.logger.info(f"✅ Upload completed for: {content['title']}")
                
            else:
                # Upload all queued content
                queued_content = await self.scheduler.get_queued_content()
                
                if not queued_content:
                    self.logger.info("📭 No content queued for upload")
                    return
                
                self.logger.info(f"📤 Uploading {len(queued_content)} queued items...")
                
                for content in queued_content:
                    if await self.scheduler.should_upload(content):
                        self.logger.info(f"📤 Uploading: {content['title']}")
                        
                        results = await self.upload_agent.upload_to_all_platforms(content)
                        
                        # Save results
                        for platform, result in results.items():
                            await self.db.save_upload_result(content['id'], platform, result)
                        
                        # Mark as uploaded
                        await self.scheduler.mark_uploaded(content['id'])
                        
                        self.logger.info(f"✅ Uploaded: {content['title']}")
                
                self.logger.info("🎉 Upload cycle completed!")
            
        except Exception as e:
            self.logger.error(f"❌ Error uploading content: {e}")
            raise
    
    async def show_status(self):
        """Show system status"""
        try:
            await self.initialize()
            
            # Get system status
            queued_content = await self.scheduler.get_queued_content()
            daily_stats = await self.scheduler.get_daily_stats()
            platform_stats = await self.db.get_platform_stats()
            
            print("📊 System Status")
            print("=" * 50)
            print(f"Status: 🟢 Online")
            print(f"Queue Size: {len(queued_content)}")
            print(f"Daily Generated: {daily_stats.get('content_generated', 0)}")
            print(f"Daily Uploaded: {daily_stats.get('content_uploaded', 0)}")
            
            if daily_stats.get('next_upload'):
                print(f"Next Upload: {daily_stats['next_upload']}")
            
            print("\n📈 Platform Statistics")
            print("-" * 30)
            for platform, stats in platform_stats.items():
                print(f"{platform.title()}:")
                print(f"  Total: {stats['total_uploads']}")
                print(f"  Success: {stats['successful_uploads']}")
                print(f"  Rate: {stats['success_rate']:.1f}%")
            
            print("\n🔧 Configuration")
            print("-" * 20)
            print(f"Daily Video Count: {self.settings.daily_video_count}")
            print(f"Video Duration: {self.settings.video_duration}s")
            print(f"Video Resolution: {self.settings.video_resolution}")
            print(f"Enabled Platforms: {', '.join(self.settings.get_platforms())}")
            
        except Exception as e:
            self.logger.error(f"❌ Error getting status: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup system resources"""
        try:
            if self.initialized:
                await self.content_agent.cleanup()
                await self.video_agent.cleanup()
                await self.audio_agent.cleanup()
                await self.upload_agent.cleanup()
                await self.db.cleanup()
                await self.scheduler.cleanup()
                
                self.initialized = False
                self.logger.info("🧹 System cleaned up")
                
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Short Video Generator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --count 5 --theme funny_pets
  %(prog)s list --limit 10
  %(prog)s upload --content-id idea_123
  %(prog)s status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate new content')
    gen_parser.add_argument('--count', type=int, default=3, help='Number of videos to generate')
    gen_parser.add_argument('--theme', default='cute_animals', help='Content theme')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List generated content')
    list_parser.add_argument('--limit', type=int, default=20, help='Maximum number of items to show')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload content to social media')
    upload_parser.add_argument('--content-id', help='Specific content ID to upload')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    async def run_command():
        cli = ShortGeneratorCLI()
        
        try:
            if args.command == 'generate':
                await cli.generate_content(args.count, args.theme)
            elif args.command == 'list':
                await cli.list_content(args.limit)
            elif args.command == 'upload':
                await cli.upload_content(args.content_id)
            elif args.command == 'status':
                await cli.show_status()
            
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")
            sys.exit(1)
        finally:
            await cli.cleanup()
    
    # Run the command
    asyncio.run(run_command())

if __name__ == "__main__":
    main()
