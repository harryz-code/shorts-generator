"""
Notifications Utility
Handles system notifications, alerts, and status updates
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

from config.settings import settings

class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SYSTEM = "system"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """Notification delivery channels"""
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"
    CONSOLE = "console"

class Notification:
    """Represents a single notification"""
    
    def __init__(self, 
                 message: str, 
                 notification_type: NotificationType = NotificationType.INFO,
                 priority: NotificationPriority = NotificationPriority.NORMAL,
                 channels: List[NotificationChannel] = None,
                 metadata: Dict[str, Any] = None,
                 expires_at: Optional[datetime] = None):
        
        self.id = self._generate_id()
        self.message = message
        self.notification_type = notification_type
        self.priority = priority
        self.channels = channels or [NotificationChannel.LOG, NotificationChannel.DASHBOARD]
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.expires_at = expires_at
        self.delivered = False
        self.delivery_attempts = 0
    
    def _generate_id(self) -> str:
        """Generate unique notification ID"""
        import uuid
        return str(uuid.uuid4())
    
    def is_expired(self) -> bool:
        """Check if notification has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'message': self.message,
            'type': self.notification_type.value,
            'priority': self.priority.value,
            'channels': [ch.value for ch in self.channels],
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'delivered': self.delivered,
            'delivery_attempts': self.delivery_attempts
        }
    
    def __str__(self) -> str:
        return f"[{self.notification_type.value.upper()}] {self.message}"

class NotificationManager:
    """Manages system notifications and alerts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # Notification storage
        self.notifications: List[Notification] = []
        self.notification_history: List[Notification] = []
        
        # Channel handlers
        self.channel_handlers = {
            NotificationChannel.LOG: self._send_to_log,
            NotificationChannel.CONSOLE: self._send_to_console,
            NotificationChannel.DASHBOARD: self._send_to_dashboard,
            NotificationChannel.EMAIL: self._send_to_email,
            NotificationChannel.WEBHOOK: self._send_to_webhook
        }
        
        # Notification templates
        self.templates = self._load_notification_templates()
        
        # Rate limiting
        self.rate_limits = {
            NotificationType.INFO: {'max_per_hour': 100, 'max_per_day': 1000},
            NotificationType.SUCCESS: {'max_per_hour': 50, 'max_per_day': 500},
            NotificationType.WARNING: {'max_per_hour': 20, 'max_per_day': 200},
            NotificationType.ERROR: {'max_per_hour': 10, 'max_per_day': 100},
            NotificationType.SYSTEM: {'max_per_hour': 5, 'max_per_day': 50}
        }
    
    def _load_notification_templates(self) -> Dict[str, str]:
        """Load notification message templates"""
        return {
            'content_generated': "🎬 Content generated successfully: {title}",
            'content_uploaded': "📤 Content uploaded to {platform}: {title}",
            'upload_failed': "❌ Upload failed to {platform}: {title} - {error}",
            'system_startup': "🚀 System started successfully",
            'system_shutdown': "🛑 System shutting down",
            'daily_generation': "📅 Starting daily content generation ({count} videos)",
            'backup_created': "💾 Backup created successfully: {backup_path}",
            'storage_warning': "⚠️ Storage usage high: {usage_percent}% used",
            'rate_limit_warning': "⏳ Rate limit approaching for {platform}: {current}/{limit}",
            'validation_error': "🔍 Content validation failed: {title} - {errors}",
            'ai_model_error': "🤖 AI model error: {model} - {error}",
            'database_error': "🗄️ Database error: {operation} - {error}",
            'network_error': "🌐 Network error: {operation} - {error}"
        }
    
    async def send_notification(self, 
                               message: str, 
                               notification_type: NotificationType = NotificationType.INFO,
                               priority: NotificationPriority = NotificationPriority.NORMAL,
                               channels: List[NotificationChannel] = None,
                               metadata: Dict[str, Any] = None,
                               template: str = None,
                               template_data: Dict[str, Any] = None,
                               expires_in_hours: Optional[int] = None) -> str:
        """Send a notification through specified channels"""
        try:
            # Check rate limits
            if not await self._check_rate_limit(notification_type):
                self.logger.warning(f"⚠️ Rate limit exceeded for {notification_type.value} notifications")
                return ""
            
            # Use template if specified
            if template and template in self.templates:
                if template_data:
                    message = self.templates[template].format(**template_data)
                else:
                    message = self.templates[template]
            
            # Set expiration
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            
            # Create notification
            notification = Notification(
                message=message,
                notification_type=notification_type,
                priority=priority,
                channels=channels,
                metadata=metadata,
                expires_at=expires_at
            )
            
            # Add to notifications list
            self.notifications.append(notification)
            
            # Send through channels
            await self._deliver_notification(notification)
            
            self.logger.info(f"📢 Notification sent: {notification}")
            return notification.id
            
        except Exception as e:
            self.logger.error(f"❌ Error sending notification: {e}")
            return ""
    
    async def send_system_notification(self, message: str, priority: NotificationPriority = NotificationPriority.NORMAL):
        """Send a system notification"""
        return await self.send_notification(
            message=message,
            notification_type=NotificationType.SYSTEM,
            priority=priority,
            channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE]
        )
    
    async def send_success_notification(self, message: str, metadata: Dict[str, Any] = None):
        """Send a success notification"""
        return await self.send_notification(
            message=message,
            notification_type=NotificationType.SUCCESS,
            priority=NotificationPriority.NORMAL,
            metadata=metadata
        )
    
    async def send_warning_notification(self, message: str, metadata: Dict[str, Any] = None):
        """Send a warning notification"""
        return await self.send_notification(
            message=message,
            notification_type=NotificationType.WARNING,
            priority=NotificationPriority.HIGH,
            metadata=metadata
        )
    
    async def send_error_notification(self, message: str, metadata: Dict[str, Any] = None):
        """Send an error notification"""
        return await self.send_notification(
            message=message,
            notification_type=NotificationType.ERROR,
            priority=NotificationPriority.CRITICAL,
            metadata=metadata
        )
    
    async def _deliver_notification(self, notification: Notification):
        """Deliver notification through all specified channels"""
        try:
            for channel in notification.channels:
                if channel in self.channel_handlers:
                    try:
                        await self.channel_handlers[channel](notification)
                        notification.delivery_attempts += 1
                    except Exception as e:
                        self.logger.error(f"❌ Error delivering to {channel.value}: {e}")
            
            notification.delivered = True
            
        except Exception as e:
            self.logger.error(f"❌ Error delivering notification: {e}")
    
    async def _send_to_log(self, notification: Notification):
        """Send notification to log system"""
        log_level = {
            NotificationType.INFO: logging.INFO,
            NotificationType.SUCCESS: logging.INFO,
            NotificationType.WARNING: logging.WARNING,
            NotificationType.ERROR: logging.ERROR,
            NotificationType.SYSTEM: logging.INFO
        }.get(notification.notification_type, logging.INFO)
        
        self.logger.log(log_level, f"📢 {notification.message}")
    
    async def _send_to_console(self, notification: Notification):
        """Send notification to console"""
        # Console output is handled by logging system
        pass
    
    async def _send_to_dashboard(self, notification: Notification):
        """Send notification to web dashboard"""
        # This would integrate with the web dashboard
        # For now, just store for dashboard retrieval
        pass
    
    async def _send_to_email(self, notification: Notification):
        """Send notification via email"""
        # Email functionality would be implemented here
        # Requires SMTP configuration
        pass
    
    async def _send_to_webhook(self, notification: Notification):
        """Send notification via webhook"""
        # Webhook functionality would be implemented here
        # Requires webhook URL configuration
        pass
    
    async def _check_rate_limit(self, notification_type: NotificationType) -> bool:
        """Check if notification rate limit is exceeded"""
        try:
            limits = self.rate_limits.get(notification_type, {})
            if not limits:
                return True
            
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)
            
            # Count recent notifications
            hourly_count = sum(1 for n in self.notifications 
                             if n.notification_type == notification_type and n.created_at > hour_ago)
            daily_count = sum(1 for n in self.notifications 
                            if n.notification_type == notification_type and n.created_at > day_ago)
            
            # Check limits
            if hourly_count >= limits.get('max_per_hour', float('inf')):
                return False
            if daily_count >= limits.get('max_per_day', float('inf')):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error checking rate limit: {e}")
            return True  # Allow if check fails
    
    async def get_notifications(self, 
                               notification_type: Optional[NotificationType] = None,
                               priority: Optional[NotificationPriority] = None,
                               limit: int = 100,
                               include_expired: bool = False) -> List[Notification]:
        """Get notifications with optional filtering"""
        try:
            notifications = self.notifications.copy()
            
            # Apply filters
            if notification_type:
                notifications = [n for n in notifications if n.notification_type == notification_type]
            
            if priority:
                notifications = [n for n in notifications if n.priority == priority]
            
            if not include_expired:
                notifications = [n for n in notifications if not n.is_expired()]
            
            # Sort by priority and creation time
            priority_order = {NotificationPriority.CRITICAL: 0, NotificationPriority.HIGH: 1, 
                            NotificationPriority.NORMAL: 2, NotificationPriority.LOW: 3}
            
            notifications.sort(key=lambda n: (priority_order.get(n.priority, 4), n.created_at))
            
            return notifications[:limit]
            
        except Exception as e:
            self.logger.error(f"❌ Error getting notifications: {e}")
            return []
    
    async def get_notification_count(self, notification_type: Optional[NotificationType] = None) -> int:
        """Get count of notifications"""
        try:
            if notification_type:
                return sum(1 for n in self.notifications if n.notification_type == notification_type)
            return len(self.notifications)
        except Exception as e:
            self.logger.error(f"❌ Error getting notification count: {e}")
            return 0
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            for notification in self.notifications:
                if notification.id == notification_id:
                    notification.delivered = True
                    return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Error marking notification as read: {e}")
            return False
    
    async def clear_notifications(self, notification_type: Optional[NotificationType] = None):
        """Clear notifications, optionally by type"""
        try:
            if notification_type:
                # Move to history
                to_remove = [n for n in self.notifications if n.notification_type == notification_type]
                self.notification_history.extend(to_remove)
                self.notifications = [n for n in self.notifications if n.notification_type != notification_type]
            else:
                # Move all to history
                self.notification_history.extend(self.notifications)
                self.notifications.clear()
            
            self.logger.info(f"🧹 Cleared notifications: {len(to_remove) if notification_type else 'all'}")
            
        except Exception as e:
            self.logger.error(f"❌ Error clearing notifications: {e}")
    
    async def cleanup_expired_notifications(self):
        """Remove expired notifications"""
        try:
            expired = [n for n in self.notifications if n.is_expired()]
            self.notifications = [n for n in self.notifications if not n.is_expired()]
            
            if expired:
                self.logger.info(f"🧹 Cleaned up {len(expired)} expired notifications")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up expired notifications: {e}")
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            stats = {
                'total_notifications': len(self.notifications),
                'total_history': len(self.notification_history),
                'by_type': {},
                'by_priority': {},
                'delivery_rate': 0
            }
            
            # Count by type
            for notification_type in NotificationType:
                count = sum(1 for n in self.notifications if n.notification_type == notification_type)
                stats['by_type'][notification_type.value] = count
            
            # Count by priority
            for priority in NotificationPriority:
                count = sum(1 for n in self.notifications if n.priority == priority)
                stats['by_priority'][priority.value] = count
            
            # Calculate delivery rate
            if self.notifications:
                delivered = sum(1 for n in self.notifications if n.delivered)
                stats['delivery_rate'] = (delivered / len(self.notifications)) * 100
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Error getting notification stats: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.cleanup_expired_notifications()
            self.logger.info("✅ Notification manager cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
