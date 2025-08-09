#!/usr/bin/env python3
"""
Test script for the Cute Animal Short Video Generator
Tests all major components to ensure they work correctly
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from agents.content_agent import ContentAgent
from agents.video_agent import VideoAgent
from agents.audio_agent import AudioAgent
from agents.upload_agent import UploadAgent
from utils.database import DatabaseManager
from utils.scheduler import ContentScheduler
from utils.logger import setup_logging

async def test_content_agent():
    """Test content generation agent"""
    print("🧪 Testing Content Agent...")
    
    try:
        agent = ContentAgent()
        await agent.initialize()
        
        # Test idea generation
        ideas = await agent.generate_ideas(count=2, theme="cute_animals")
        assert len(ideas) == 2, f"Expected 2 ideas, got {len(ideas)}"
        assert all('title' in idea for idea in ideas), "All ideas should have titles"
        assert all('script' in idea for idea in ideas), "All ideas should have scripts"
        
        print("✅ Content Agent: PASSED")
        await agent.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Content Agent: FAILED - {e}")
        return False

async def test_video_agent():
    """Test video generation agent"""
    print("🧪 Testing Video Agent...")
    
    try:
        agent = VideoAgent()
        await agent.initialize()
        
        # Test video generation (with fallback)
        test_prompt = "A cute puppy playing in a garden"
        video_path = await agent.generate_video(prompt=test_prompt, duration=5)
        
        assert video_path, "Video path should not be empty"
        assert Path(video_path).exists(), f"Video file should exist: {video_path}"
        
        print("✅ Video Agent: PASSED")
        await agent.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Video Agent: FAILED - {e}")
        return False

async def test_audio_agent():
    """Test audio processing agent"""
    print("🧪 Testing Audio Agent...")
    
    try:
        agent = AudioAgent()
        await agent.initialize()
        
        # Test music generation
        music_path = await agent._create_simple_music("upbeat_cute")
        assert music_path, "Music path should not be empty"
        
        # Test voice placeholder
        voice_path = await agent._create_voice_placeholder("Test script")
        assert voice_path, "Voice path should not be empty"
        
        # Test audio combination
        combined_path = await agent._combine_audio(music_path, voice_path)
        assert combined_path, "Combined audio path should not be empty"
        
        print("✅ Audio Agent: PASSED")
        await agent.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Audio Agent: FAILED - {e}")
        return False

async def test_database():
    """Test database operations"""
    print("🧪 Testing Database...")
    
    try:
        db = DatabaseManager()
        await db.initialize()
        
        # Test content saving
        test_content = {
            'id': 'test_001',
            'title': 'Test Video',
            'description': 'A test video for testing',
            'category': 'test',
            'theme': 'test',
            'script': 'This is a test script',
            'video_path': '/tmp/test.mp4',
            'tags': ['test', 'demo'],
            'created_at': '2024-01-01T00:00:00'
        }
        
        success = await db.save_content(test_content)
        assert success, "Content saving should succeed"
        
        # Test content retrieval
        retrieved = await db.get_content('test_001')
        assert retrieved, "Content should be retrievable"
        assert retrieved['title'] == 'Test Video', "Retrieved content should match"
        
        print("✅ Database: PASSED")
        await db.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Database: FAILED - {e}")
        return False

async def test_scheduler():
    """Test content scheduler"""
    print("🧪 Testing Scheduler...")
    
    try:
        scheduler = ContentScheduler()
        await scheduler.initialize()
        
        # Test content queuing
        test_content = {
            'id': 'sched_test_001',
            'title': 'Scheduled Test Video',
            'description': 'A test video for scheduling',
            'video_path': '/tmp/scheduled_test.mp4',
            'platforms': ['youtube'],
            'scheduled_time': '2024-01-01T12:00:00'
        }
        
        await scheduler.queue_content(test_content)
        
        # Test queue retrieval
        queued = await scheduler.get_queued_content()
        assert len(queued) > 0, "Should have queued content"
        
        print("✅ Scheduler: PASSED")
        await scheduler.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Scheduler: FAILED - {e}")
        return False

async def test_upload_agent():
    """Test upload agent (without actual uploads)"""
    print("🧪 Testing Upload Agent...")
    
    try:
        agent = UploadAgent()
        await agent.initialize()
        
        # Test initialization (should not fail even without API keys)
        print("✅ Upload Agent: PASSED (initialization only)")
        await agent.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Upload Agent: FAILED - {e}")
        return False

async def test_integration():
    """Test basic integration workflow"""
    print("🧪 Testing Integration Workflow...")
    
    try:
        # Initialize all components
        content_agent = ContentAgent()
        video_agent = VideoAgent()
        audio_agent = AudioAgent()
        db = DatabaseManager()
        
        await content_agent.initialize()
        await video_agent.initialize()
        await audio_agent.initialize()
        await db.initialize()
        
        # Generate a simple idea
        ideas = await content_agent.generate_ideas(count=1, theme="cute_animals")
        idea = ideas[0]
        
        # Generate video
        video_path = await video_agent.generate_video(
            prompt=idea['description'],
            duration=5
        )
        
        # Add audio
        final_video = await audio_agent.add_audio(
            video_path=video_path,
            script=idea['script'],
            music_style="upbeat_cute"
        )
        
        # Save to database
        await db.save_content({
            'id': idea['id'],
            'title': idea['title'],
            'description': idea['description'],
            'category': idea['category'],
            'theme': idea['theme'],
            'script': idea['script'],
            'video_path': final_video,
            'tags': idea['tags'],
            'created_at': idea['created_at']
        })
        
        print("✅ Integration Workflow: PASSED")
        
        # Cleanup
        await content_agent.cleanup()
        await video_agent.cleanup()
        await audio_agent.cleanup()
        await db.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Integration Workflow: FAILED - {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting System Tests...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    tests = [
        test_content_agent,
        test_video_agent,
        test_audio_agent,
        test_database,
        test_scheduler,
        test_upload_agent,
        test_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1:2d}. {test.__name__:25s} - {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
