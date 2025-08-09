"""
Database Manager
Handles data persistence for content and uploads
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from config.settings import settings

class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        self.db_path = self.settings.data_dir / "shorts.db"
        self.connection = None
    
    async def initialize(self):
        """Initialize database"""
        try:
            self.logger.info("🗄️ Initializing Database...")
            
            # Ensure data directory exists
            self.settings.data_dir.mkdir(exist_ok=True, parents=True)
            
            # Connect to database
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_tables()
            
            self.logger.info("✅ Database initialized!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        try:
            cursor = self.connection.cursor()
            
            # Content table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    theme TEXT,
                    script TEXT,
                    video_path TEXT,
                    tags TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Uploads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    uploaded_at TEXT,
                    FOREIGN KEY (content_id) REFERENCES content (id)
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """)
            
            # Commit changes
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"❌ Error creating tables: {e}")
            raise
    
    async def save_content(self, content: Dict[str, Any]) -> bool:
        """Save content to database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO content 
                (id, title, description, category, theme, script, video_path, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content['id'],
                content['title'],
                content['description'],
                content.get('category'),
                content.get('theme'),
                content.get('script'),
                content.get('video_path'),
                json.dumps(content.get('tags', [])),
                content.get('created_at'),
                datetime.now().isoformat()
            ))
            
            self.connection.commit()
            self.logger.info(f"💾 Saved content: {content['id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error saving content: {e}")
            return False
    
    async def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT * FROM content WHERE id = ?", (content_id,))
            row = cursor.fetchone()
            
            if row:
                content = dict(row)
                # Parse tags
                if content.get('tags'):
                    content['tags'] = json.loads(content['tags'])
                return content
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting content: {e}")
            return None
    
    async def get_all_content(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all content with limit"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM content 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            content_list = []
            
            for row in rows:
                content = dict(row)
                if content.get('tags'):
                    content['tags'] = json.loads(content['tags'])
                content_list.append(content)
            
            return content_list
            
        except Exception as e:
            self.logger.error(f"❌ Error getting all content: {e}")
            return []
    
    async def save_upload_result(self, content_id: str, platform: str, result: Dict[str, Any]) -> bool:
        """Save upload result"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO uploads (content_id, platform, status, result, uploaded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                content_id,
                platform,
                'success' if result.get('success') else 'failed',
                json.dumps(result),
                datetime.now().isoformat()
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error saving upload result: {e}")
            return False
    
    async def get_upload_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get upload history"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT u.*, c.title, c.description
                FROM uploads u
                JOIN content c ON u.content_id = c.id
                ORDER BY u.uploaded_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            uploads = []
            
            for row in rows:
                upload = dict(row)
                if upload.get('result'):
                    upload['result'] = json.loads(upload['result'])
                uploads.append(upload)
            
            return uploads
            
        except Exception as e:
            self.logger.error(f"❌ Error getting upload history: {e}")
            return []
    
    async def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform upload statistics"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT platform, 
                       COUNT(*) as total_uploads,
                       SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_uploads
                FROM uploads
                GROUP BY platform
            """)
            
            rows = cursor.fetchall()
            stats = {}
            
            for row in rows:
                platform = row['platform']
                stats[platform] = {
                    'total_uploads': row['total_uploads'],
                    'successful_uploads': row['successful_uploads'],
                    'success_rate': (row['successful_uploads'] / row['total_uploads']) * 100
                }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Error getting platform stats: {e}")
            return {}
    
    async def save_setting(self, key: str, value: Any) -> bool:
        """Save application setting"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), datetime.now().isoformat()))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error saving setting: {e}")
            return False
    
    async def get_setting(self, key: str, default: Any = None) -> Any:
        """Get application setting"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row['value'])
            
            return default
            
        except Exception as e:
            self.logger.error(f"❌ Error getting setting: {e}")
            return default
    
    async def cleanup(self):
        """Cleanup database connection"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            
            self.logger.info("🧹 Database cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
