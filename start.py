#!/usr/bin/env python3
"""
Startup script for the Short Video Generator
Provides an interactive menu for starting different system components
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("🎬" + "="*50 + "🎬")
    print("        SHORT VIDEO GENERATOR")
    print("           Startup Menu")
    print("🎬" + "="*50 + "🎬")
    print()

def print_menu():
    """Print the main menu"""
    print("Available options:")
    print("1. 🚀 Start Full System (Main + Dashboard)")
    print("2. 🌐 Start Web Dashboard Only")
    print("3. 🎬 Start Main System Only")
    print("4. 💻 Open CLI Interface")
    print("5. 🧪 Run System Test")
    print("6. 📊 Show System Status")
    print("7. ⚙️  Open Configuration")
    print("8. 📚 View Documentation")
    print("9. 🚪 Exit")
    print()

def check_environment():
    """Check if environment is properly configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("   Run 'python install.py' to set up the environment")
        print()
        return False
    
    print("✅ Environment configuration found")
    return True

def start_full_system():
    """Start the full system with dashboard"""
    print("🚀 Starting full system...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ Error starting system: {e}")

def start_dashboard():
    """Start only the web dashboard"""
    print("🌐 Starting web dashboard...")
    try:
        subprocess.run([sys.executable, "web/dashboard.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def start_main_system():
    """Start only the main system"""
    print("🎬 Starting main system...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ Error starting system: {e}")

def open_cli():
    """Open the CLI interface"""
    print("💻 Opening CLI interface...")
    print("Type 'help' for available commands")
    try:
        subprocess.run([sys.executable, "cli.py", "--help"], check=True)
    except Exception as e:
        print(f"❌ Error opening CLI: {e}")

def run_test():
    """Run system test"""
    print("🧪 Running system test...")
    try:
        result = subprocess.run([sys.executable, "test_system.py"], check=True)
        if result.returncode == 0:
            print("✅ System test passed!")
        else:
            print("❌ System test failed!")
    except Exception as e:
        print(f"❌ Error running test: {e}")

def show_status():
    """Show system status"""
    print("📊 Getting system status...")
    try:
        subprocess.run([sys.executable, "cli.py", "status"], check=True)
    except Exception as e:
        print(f"❌ Error getting status: {e}")

def open_config():
    """Open configuration files"""
    print("⚙️  Opening configuration...")
    
    # Check for common editors
    editors = ['code', 'nano', 'vim', 'notepad']
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found. Run 'python install.py' first.")
        return
    
    for editor in editors:
        try:
            if editor == 'code':
                subprocess.run(['code', '.env'], check=True)
                print("✅ Opened .env in VS Code")
                break
            elif editor == 'nano':
                subprocess.run(['nano', '.env'], check=True)
                break
            elif editor == 'vim':
                subprocess.run(['vim', '.env'], check=True)
                break
            elif editor == 'notepad':
                subprocess.run(['notepad', '.env'], check=True)
                break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    else:
        print("📄 .env file location: .env")
        print("   Open it manually with your preferred editor")

def view_docs():
    """View documentation"""
    print("📚 Documentation:")
    print("   • README.md - Complete system documentation")
    print("   • config.env.example - Configuration examples")
    print("   • cli.py --help - Command line interface help")
    print()
    print("📖 Quick Commands:")
    print("   • python cli.py generate --count 3")
    print("   • python cli.py status")
    print("   • python cli.py upload")
    print()
    print("🌐 Web Dashboard: http://localhost:8000")

def main():
    """Main startup function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        print("Please run 'python install.py' to set up the system first.")
        print()
        input("Press Enter to continue anyway...")
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == '1':
                start_full_system()
            elif choice == '2':
                start_dashboard()
            elif choice == '3':
                start_main_system()
            elif choice == '4':
                open_cli()
            elif choice == '5':
                run_test()
            elif choice == '6':
                show_status()
            elif choice == '7':
                open_config()
            elif choice == '8':
                view_docs()
            elif choice == '9':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-9.")
            
            print()
            input("Press Enter to continue...")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    main()
