#!/usr/bin/env python3
"""
Simple launcher for the web dashboard
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from web.dashboard import start_dashboard

if __name__ == "__main__":
    print("🚀 Starting Short Video Generator Dashboard...")
    print("📍 Dashboard will be available at: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        asyncio.run(start_dashboard())
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)
