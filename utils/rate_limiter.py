"""
Rate Limiter Utility
Handles API rate limiting for social media platforms
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

from config.settings import settings

class RateLimiter:
    """Manages API rate limiting for different platforms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # Rate limit tracking per platform
        self.request_counts = defaultdict(lambda: deque())
        self.last_request_times = defaultdict(float)
        
        # Platform-specific rate limits
        self.rate_limits = {
            'youtube': {
                'requests_per_hour': 1000,
                'requests_per_day': 10000,
                'min_interval': 0.1  # seconds between requests
            },
            'instagram': {
                'requests_per_hour': 200,
                'requests_per_day': 1000,
                'min_interval': 1.0  # seconds between requests
            },
            'tiktok': {
                'requests_per_hour': 100,
                'requests_per_day': 1000,
                'min_interval': 2.0  # seconds between requests
            }
        }
    
    async def wait_if_needed(self, platform: str) -> bool:
        """Wait if rate limit would be exceeded"""
        try:
            if platform not in self.rate_limits:
                self.logger.warning(f"⚠️ Unknown platform: {platform}")
                return True
            
            limits = self.rate_limits[platform]
            now = time.time()
            
            # Check minimum interval between requests
            time_since_last = now - self.last_request_times[platform]
            if time_since_last < limits['min_interval']:
                wait_time = limits['min_interval'] - time_since_last
                self.logger.info(f"⏳ Waiting {wait_time:.2f}s for {platform} rate limit")
                await asyncio.sleep(wait_time)
            
            # Check hourly limit
            if not await self._check_hourly_limit(platform, limits['requests_per_hour']):
                return False
            
            # Check daily limit
            if not await self._check_daily_limit(platform, limits['requests_per_day']):
                return False
            
            # Record request
            self._record_request(platform, now)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error in rate limiter: {e}")
            return False
    
    async def _check_hourly_limit(self, platform: str, max_requests: int) -> bool:
        """Check if hourly rate limit would be exceeded"""
        try:
            now = time.time()
            hour_ago = now - 3600
            
            # Remove old requests from tracking
            requests = self.request_counts[platform]
            while requests and requests[0] < hour_ago:
                requests.popleft()
            
            # Check if adding this request would exceed limit
            if len(requests) >= max_requests:
                oldest_request = requests[0] if requests else 0
                wait_time = hour_ago - oldest_request + 1
                
                if wait_time > 0:
                    self.logger.warning(f"⏳ Hourly rate limit reached for {platform}, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    return await self._check_hourly_limit(platform, max_requests)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error checking hourly limit: {e}")
            return False
    
    async def _check_daily_limit(self, platform: str, max_requests: int) -> bool:
        """Check if daily rate limit would be exceeded"""
        try:
            now = time.time()
            day_ago = now - 86400
            
            # Count requests in last 24 hours
            daily_count = sum(1 for req_time in self.request_counts[platform] if req_time > day_ago)
            
            if daily_count >= max_requests:
                self.logger.error(f"❌ Daily rate limit exceeded for {platform}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error checking daily limit: {e}")
            return False
    
    def _record_request(self, platform: str, timestamp: float):
        """Record a request for rate limiting"""
        self.request_counts[platform].append(timestamp)
        self.last_request_times[platform] = timestamp
    
    def get_platform_status(self, platform: str) -> Dict[str, Any]:
        """Get current rate limit status for a platform"""
        try:
            if platform not in self.rate_limits:
                return {'error': f'Unknown platform: {platform}'}
            
            limits = self.rate_limits[platform]
            now = time.time()
            hour_ago = now - 3600
            day_ago = now - 86400
            
            requests = self.request_counts[platform]
            
            # Count recent requests
            hourly_count = sum(1 for req_time in requests if req_time > hour_ago)
            daily_count = sum(1 for req_time in requests if req_time > day_ago)
            
            # Calculate time until next available slot
            time_since_last = now - self.last_request_times[platform]
            next_available = max(0, limits['min_interval'] - time_since_last)
            
            return {
                'platform': platform,
                'hourly_requests': hourly_count,
                'hourly_limit': limits['requests_per_hour'],
                'daily_requests': daily_count,
                'daily_limit': limits['requests_per_day'],
                'min_interval': limits['min_interval'],
                'time_since_last': time_since_last,
                'next_available_in': next_available,
                'can_make_request': hourly_count < limits['requests_per_hour'] and daily_count < limits['requests_per_day']
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting platform status: {e}")
            return {'error': str(e)}
    
    def get_all_platforms_status(self) -> Dict[str, Dict[str, Any]]:
        """Get rate limit status for all platforms"""
        return {
            platform: self.get_platform_status(platform)
            for platform in self.rate_limits.keys()
        }
    
    async def reset_platform_limits(self, platform: str):
        """Reset rate limit tracking for a platform"""
        try:
            if platform in self.request_counts:
                self.request_counts[platform].clear()
            if platform in self.last_request_times:
                self.last_request_times[platform] = 0
            
            self.logger.info(f"✅ Reset rate limits for {platform}")
            
        except Exception as e:
            self.logger.error(f"❌ Error resetting rate limits: {e}")
    
    async def cleanup(self):
        """Clean up old rate limit data"""
        try:
            now = time.time()
            day_ago = now - 86400
            
            # Remove old request timestamps
            for platform in self.request_counts:
                requests = self.request_counts[platform]
                while requests and requests[0] < day_ago:
                    requests.popleft()
            
            self.logger.info("✅ Rate limiter cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
    
    def update_rate_limits(self, platform: str, new_limits: Dict[str, Any]):
        """Update rate limits for a platform"""
        try:
            if platform in self.rate_limits:
                self.rate_limits[platform].update(new_limits)
                self.logger.info(f"✅ Updated rate limits for {platform}: {new_limits}")
            else:
                self.rate_limits[platform] = new_limits
                self.logger.info(f"✅ Added new platform {platform} with limits: {new_limits}")
                
        except Exception as e:
            self.logger.error(f"❌ Error updating rate limits: {e}")
    
    async def simulate_request(self, platform: str) -> bool:
        """Simulate a request to test rate limiting"""
        try:
            self.logger.info(f"🧪 Simulating request to {platform}")
            return await self.wait_if_needed(platform)
            
        except Exception as e:
            self.logger.error(f"❌ Error simulating request: {e}")
            return False
