#!/usr/bin/env python3
"""
Simple, standalone dashboard for the Short Video Generator
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class SimpleDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self._get_dashboard_html()
            self.wfile.write(html.encode())
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                'status': 'online',
                'timestamp': datetime.now().isoformat(),
                'system': 'Short Video Generator',
                'version': '1.0.0'
            }
            self.wfile.write(json.dumps(status).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def _get_dashboard_html(self):
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Short Video Generator Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 3em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .status-card {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #4CAF50;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .metric {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .metric h3 {{
            margin: 0 0 10px 0;
            font-size: 1.5em;
        }}
        .metric .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .btn {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
        }}
        .btn:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Short Video Generator</h1>
            <p>AI-Powered Content Creation System</p>
        </div>
        
        <div class="status-card">
            <h2><span class="status-indicator"></span>System Status</h2>
            <p>Your Short Video Generator is running successfully!</p>
            <div class="grid">
                <div class="metric">
                    <h3>Status</h3>
                    <div class="value">🟢 Online</div>
                </div>
                <div class="metric">
                    <h3>Version</h3>
                    <div class="value">1.0.0</div>
                </div>
                <div class="metric">
                    <h3>Platform</h3>
                    <div class="value">macOS</div>
                </div>
            </div>
        </div>
        
        <div class="status-card">
            <h2>🚀 Quick Actions</h2>
            <div style="text-align: center;">
                <button class="btn" onclick="testCLI()">Test CLI</button>
                <button class="btn" onclick="checkSystem()">Check System</button>
                <button class="btn" onclick="refreshStatus()">Refresh Status</button>
            </div>
        </div>
        
        <div class="status-card">
            <h2>📊 System Information</h2>
            <div class="grid">
                <div class="metric">
                    <h3>Database</h3>
                    <div class="value">✅ Ready</div>
                </div>
                <div class="metric">
                    <h3>Audio Agent</h3>
                    <div class="value">✅ Ready</div>
                </div>
                <div class="metric">
                    <h3>Upload Agent</h3>
                    <div class="value">✅ Ready</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Built with ❤️ using Python, FastAPI, and AI/ML technologies</p>
            <p>Dashboard loaded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        function testCLI() {{
            alert('CLI testing would be done from the terminal. Try: python cli.py status');
        }}
        
        function checkSystem() {{
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {{
                    alert('System Status: ' + JSON.stringify(data, null, 2));
                }})
                .catch(error => {{
                    alert('Error checking system: ' + error);
                }});
        }}
        
        function refreshStatus() {{
            location.reload();
        }}
    </script>
</body>
</html>
        """

def run_dashboard(port=8000):
    """Run the simple dashboard server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleDashboardHandler)
    
    print(f"🚀 Starting Simple Dashboard...")
    print(f"📍 Dashboard available at: http://localhost:{port}")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        httpd.shutdown()

if __name__ == "__main__":
    run_dashboard()
