#!/usr/bin/env python3
"""
Setup script for the Trading Bot
This script helps with initial setup and configuration.
"""

import os
import sys
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_example = "env_example.txt"
    env_file = ".env"
    
    if os.path.exists(env_file):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env file creation")
            return
    
    if os.path.exists(env_example):
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys and configuration")
    else:
        print("❌ env_example.txt not found")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data', 'backups']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ Error installing dependencies:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 Trading Bot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Create .env file
    print("\n🔧 Setting up configuration...")
    if not create_env_file():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Dependencies installation failed. Please install manually:")
        print("   pip install -r requirements.txt")
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Configure Discord bot and get channel ID")
    print("3. Set up OANDA account and get API key")
    print("4. Run: python run_bot.py")
    print("\n📖 See README.md for detailed instructions")
    print("=" * 40)

if __name__ == "__main__":
    main()
