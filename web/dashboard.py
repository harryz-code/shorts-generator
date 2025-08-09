"""
Web Dashboard
Provides a web interface for monitoring and controlling the video generation system
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.settings import settings
from utils.database import DatabaseManager
from utils.scheduler import ContentScheduler

class WebDashboard:
    """Web dashboard for the video generation system"""
    
    def __init__(self):
        self.app = FastAPI(
            title=settings.app_name,
            version=settings.app_version,
            description="Web dashboard for the Cute Animal Short Video Generator"
        )
        
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseManager()
        self.scheduler = ContentScheduler()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Setup static files and templates
        self._setup_static_files()
    
    def _setup_middleware(self):
        """Setup middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_static_files(self):
        """Setup static files and templates"""
        # Create static directory if it doesn't exist
        static_dir = Path("web/static")
        static_dir.mkdir(exist_ok=True, parents=True)
        
        # Create templates directory if it doesn't exist
        templates_dir = Path("web/templates")
        templates_dir.mkdir(exist_ok=True, parents=True)
        
        # Mount static files
        self.app.mount("/static", StaticFiles(directory="web/static"), name="static")
        
        # Setup templates
        self.templates = Jinja2Templates(directory="web/templates")
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Main dashboard page"""
            return self._render_dashboard()
        
        @self.app.get("/api/status")
        async def get_system_status():
            """Get system status"""
            try:
                status = await self._get_system_status()
                return JSONResponse(content=status)
            except Exception as e:
                self.logger.error(f"Error getting status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/content")
        async def get_content():
            """Get all content"""
            try:
                content = await self.db.get_all_content()
                return JSONResponse(content=content)
            except Exception as e:
                self.logger.error(f"Error getting content: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/upload-history")
        async def get_upload_history():
            """Get upload history"""
            try:
                history = await self.db.get_upload_history()
                return JSONResponse(content=history)
            except Exception as e:
                self.logger.error(f"Error getting upload history: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/generate-content")
        async def generate_content(background_tasks: BackgroundTasks):
            """Trigger content generation"""
            try:
                # Add to background tasks
                background_tasks.add_task(self._generate_content_background)
                return JSONResponse(content={"message": "Content generation started"})
            except Exception as e:
                self.logger.error(f"Error starting content generation: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/stats")
        async def get_stats():
            """Get system statistics"""
            try:
                stats = await self._get_system_stats()
                return JSONResponse(content=stats)
            except Exception as e:
                self.logger.error(f"Error getting stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _render_dashboard(self) -> str:
        """Render the main dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cute Animal Short Generator - Dashboard</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header h1 { color: #333; margin-bottom: 10px; }
                .header p { color: #666; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
                .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .card h3 { color: #333; margin-bottom: 15px; }
                .stat { display: flex; justify-content: space-between; margin-bottom: 10px; }
                .stat-value { font-weight: bold; color: #007bff; }
                .btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
                .btn:hover { background: #0056b3; }
                .btn-success { background: #28a745; }
                .btn-success:hover { background: #1e7e34; }
                .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                .status.online { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .status.offline { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                .content-list { max-height: 400px; overflow-y: auto; }
                .content-item { padding: 10px; border-bottom: 1px solid #eee; }
                .content-item:last-child { border-bottom: none; }
                .loading { text-align: center; padding: 20px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐾 Cute Animal Short Generator</h1>
                    <p>Automated video generation and social media management</p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>System Status</h3>
                        <div id="system-status" class="loading">Loading...</div>
                        <button class="btn" onclick="refreshStatus()">Refresh</button>
                    </div>
                    
                    <div class="card">
                        <h3>Quick Actions</h3>
                        <button class="btn btn-success" onclick="generateContent()">Generate Content</button>
                        <button class="btn" onclick="refreshData()">Refresh Data</button>
                    </div>
                    
                    <div class="card">
                        <h3>Statistics</h3>
                        <div id="stats" class="loading">Loading...</div>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>Recent Content</h3>
                        <div id="content-list" class="content-list loading">Loading...</div>
                    </div>
                    
                    <div class="card">
                        <h3>Upload History</h3>
                        <div id="upload-history" class="content-list loading">Loading...</div>
                    </div>
                </div>
            </div>
            
            <script>
                // Load data on page load
                document.addEventListener('DOMContentLoaded', function() {
                    loadAllData();
                });
                
                async function loadAllData() {
                    await Promise.all([
                        loadSystemStatus(),
                        loadStats(),
                        loadContent(),
                        loadUploadHistory()
                    ]);
                }
                
                async function loadSystemStatus() {
                    try {
                        const response = await fetch('/api/status');
                        const status = await response.json();
                        displaySystemStatus(status);
                    } catch (error) {
                        console.error('Error loading status:', error);
                        document.getElementById('system-status').innerHTML = '<div class="status offline">Error loading status</div>';
                    }
                }
                
                async function loadStats() {
                    try {
                        const response = await fetch('/api/stats');
                        const stats = await response.json();
                        displayStats(stats);
                    } catch (error) {
                        console.error('Error loading stats:', error);
                        document.getElementById('stats').innerHTML = '<div class="status offline">Error loading stats</div>';
                    }
                }
                
                async function loadContent() {
                    try {
                        const response = await fetch('/api/content');
                        const content = await response.json();
                        displayContent(content);
                    } catch (error) {
                        console.error('Error loading content:', error);
                        document.getElementById('content-list').innerHTML = '<div class="status offline">Error loading content</div>';
                    }
                }
                
                async function loadUploadHistory() {
                    try {
                        const response = await fetch('/api/upload-history');
                        const history = await response.json();
                        displayUploadHistory(history);
                    } catch (error) {
                        console.error('Error loading upload history:', error);
                        document.getElementById('upload-history').innerHTML = '<div class="status offline">Error loading upload history</div>';
                    }
                }
                
                function displaySystemStatus(status) {
                    const statusDiv = document.getElementById('system-status');
                    statusDiv.innerHTML = `
                        <div class="status ${status.status === 'online' ? 'online' : 'offline'}">
                            ${status.status === 'online' ? '🟢 Online' : '🔴 Offline'}
                        </div>
                        <div class="stat">
                            <span>Last Activity:</span>
                            <span class="stat-value">${status.last_activity || 'N/A'}</span>
                        </div>
                        <div class="stat">
                            <span>Queue Size:</span>
                            <span class="stat-value">${status.queue_size || 0}</span>
                        </div>
                    `;
                }
                
                function displayStats(stats) {
                    const statsDiv = document.getElementById('stats');
                    statsDiv.innerHTML = `
                        <div class="stat">
                            <span>Total Content:</span>
                            <span class="stat-value">${stats.total_content || 0}</span>
                        </div>
                        <div class="stat">
                            <span>Total Uploads:</span>
                            <span class="stat-value">${stats.total_uploads || 0}</span>
                        </div>
                        <div class="stat">
                            <span>Success Rate:</span>
                            <span class="stat-value">${stats.success_rate || '0%'}</span>
                        </div>
                    `;
                }
                
                function displayContent(content) {
                    const contentDiv = document.getElementById('content-list');
                    if (!content || content.length === 0) {
                        contentDiv.innerHTML = '<div class="content-item">No content available</div>';
                        return;
                    }
                    
                    const contentHtml = content.slice(0, 10).map(item => `
                        <div class="content-item">
                            <strong>${item.title}</strong><br>
                            <small>${item.category} • ${item.created_at}</small>
                        </div>
                    `).join('');
                    
                    contentDiv.innerHTML = contentHtml;
                }
                
                function displayUploadHistory(history) {
                    const historyDiv = document.getElementById('upload-history');
                    if (!history || history.length === 0) {
                        historyDiv.innerHTML = '<div class="content-item">No upload history</div>';
                        return;
                    }
                    
                    const historyHtml = history.slice(0, 10).map(item => `
                        <div class="content-item">
                            <strong>${item.platform}</strong><br>
                            <small>${item.status} • ${item.uploaded_at}</small>
                        </div>
                    `).join('');
                    
                    historyDiv.innerHTML = historyHtml;
                }
                
                async function generateContent() {
                    try {
                        const response = await fetch('/api/generate-content', { method: 'POST' });
                        const result = await response.json();
                        alert(result.message);
                        // Refresh data after generation
                        setTimeout(loadAllData, 2000);
                    } catch (error) {
                        console.error('Error generating content:', error);
                        alert('Error generating content');
                    }
                }
                
                function refreshStatus() { loadSystemStatus(); }
                function refreshData() { loadAllData(); }
                
                // Auto-refresh every 30 seconds
                setInterval(loadAllData, 30000);
            </script>
        </body>
        </html>
        """
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            # Get queue size
            queued_content = await self.scheduler.get_queued_content()
            
            # Get last activity from database
            last_content = await self.db.get_all_content(limit=1)
            last_activity = last_content[0]['created_at'] if last_content else None
            
            return {
                'status': 'online',
                'last_activity': last_activity,
                'queue_size': len(queued_content),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            # Get content stats
            all_content = await self.db.get_all_content()
            upload_history = await self.db.get_upload_history()
            
            # Calculate success rate
            successful_uploads = len([u for u in upload_history if u.get('status') == 'success'])
            total_uploads = len(upload_history)
            success_rate = f"{(successful_uploads / total_uploads * 100):.1f}%" if total_uploads > 0 else "0%"
            
            return {
                'total_content': len(all_content),
                'total_uploads': total_uploads,
                'success_rate': success_rate,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _generate_content_background(self):
        """Background task for content generation"""
        try:
            self.logger.info("🎬 Starting background content generation...")
            # This would integrate with the main content generation system
            # For now, just log the action
            self.logger.info("✅ Background content generation completed")
        except Exception as e:
            self.logger.error(f"❌ Error in background content generation: {e}")

async def start_dashboard():
    """Start the web dashboard"""
    try:
        dashboard = WebDashboard()
        
        # Initialize database connection
        await dashboard.db.initialize()
        
        # Start the server
        config = uvicorn.Config(
            dashboard.app,
            host=settings.web_host,
            port=settings.web_port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logging.error(f"❌ Failed to start dashboard: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(start_dashboard())
