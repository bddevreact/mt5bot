#!/usr/bin/env python3
"""
Easy Discord Setup
This script makes Discord setup super easy without copy-paste.
"""

import os
import sys
import webbrowser
import time

def main():
    print("🎯 Easy Discord Setup")
    print("=" * 40)
    print()
    
    print("📋 This will make Discord setup super easy!")
    print("No copy-paste needed!")
    print()
    
    print("🚀 Method 1: Browser Extension (Easiest)")
    print("-" * 40)
    print("1. Install 'Discord Token Extractor' browser extension")
    print("2. Login to Discord")
    print("3. Click extension icon")
    print("4. Token automatically copied!")
    print()
    
    print("🌐 Method 2: Simple Browser Steps")
    print("-" * 40)
    print("1. Open Discord in browser")
    print("2. Login with your username/password")
    print("3. Press F12")
    print("4. Go to Application tab")
    print("5. Local Storage → discord.com")
    print("6. Find 'token' key")
    print("7. Double-click to select all")
    print("8. Right-click → Copy")
    print()
    
    print("📱 Method 3: Mobile App")
    print("-" * 40)
    print("1. Use Discord mobile app")
    print("2. Go to Settings")
    print("3. Look for 'Token' or 'API Key'")
    print("4. Copy it")
    print()
    
    # Ask user which method they prefer
    print("🎯 Which method do you want to try?")
    print("1. Browser Extension (Recommended)")
    print("2. Browser Application Tab")
    print("3. Mobile App")
    print("4. I'll do it manually")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🌐 Opening Discord in your browser...")
        webbrowser.open("https://discord.com/app")
        print("\n📋 Instructions:")
        print("1. Login to Discord")
        print("2. Install 'Discord Token Extractor' extension")
        print("3. Click the extension icon")
        print("4. Token will be copied automatically")
        
    elif choice == "2":
        print("\n🌐 Opening Discord in your browser...")
        webbrowser.open("https://discord.com/app")
        print("\n📋 Instructions:")
        print("1. Login to Discord")
        print("2. Press F12")
        print("3. Go to Application tab")
        print("4. Local Storage → discord.com")
        print("5. Find 'token' key")
        print("6. Double-click to select all")
        print("7. Right-click → Copy")
        
    elif choice == "3":
        print("\n📱 Mobile App Method:")
        print("1. Open Discord mobile app")
        print("2. Go to Settings")
        print("3. Look for 'Token' or 'API Key'")
        print("4. Copy it")
        
    elif choice == "4":
        print("\n📋 Manual Method:")
        print("1. Open Discord in web browser")
        print("2. Login with username/password")
        print("3. Press F12")
        print("4. Go to Network tab")
        print("5. Send any message")
        print("6. Find 'discord.com/api' request")
        print("7. Look for 'authorization' header")
        print("8. Copy the token value")
        
    else:
        print("❌ Invalid choice!")
        return
    
    print("\n" + "="*50)
    print("🔧 After getting your token:")
    print("1. Run: python simple_setup.py")
    print("2. Type your token (no copy-paste needed)")
    print("3. Enter channel ID")
    print("4. Setup complete!")
    print()
    
    # Ask if they want to continue with setup
    continue_setup = input("Do you want to continue with setup now? (y/n): ").strip().lower()
    
    if continue_setup == 'y':
        print("\n🔧 Starting setup...")
        print("You can type your token manually (no copy-paste needed)")
        
        # Get token manually
        print("\n🔑 Enter your Discord token:")
        print("(Type it manually - no copy-paste needed)")
        token = input("Token: ").strip()
        
        if not token:
            print("❌ No token provided!")
            return
        
        # Get channel ID
        print("\n📺 Enter Discord Channel ID:")
        print("(Right-click on channel name → Copy Channel ID)")
        channel_id = input("Channel ID: ").strip()
        
        if not channel_id:
            print("❌ No channel ID provided!")
            return
        
        # Update .env file
        try:
            # Read current .env
            env_lines = []
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add lines
            updated = False
            for i, line in enumerate(env_lines):
                if line.startswith('DISCORD_TOKEN='):
                    env_lines[i] = f'DISCORD_TOKEN={token}\n'
                    updated = True
                elif line.startswith('DISCORD_CHANNEL_ID='):
                    env_lines[i] = f'DISCORD_CHANNEL_ID={channel_id}\n'
                    updated = True
            
            # Add if not found
            if not any(line.startswith('DISCORD_TOKEN=') for line in env_lines):
                env_lines.append(f'DISCORD_TOKEN={token}\n')
            if not any(line.startswith('DISCORD_CHANNEL_ID=') for line in env_lines):
                env_lines.append(f'DISCORD_CHANNEL_ID={channel_id}\n')
            
            # Write back
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            
            print("\n✅ Setup completed successfully!")
            print(f"   Token: {'*' * 20}...{token[-4:]}")
            print(f"   Channel ID: {channel_id}")
            print()
            print("🚀 Next steps:")
            print("1. Run: python discord_signal_processor.py")
            print("2. Or run: python trading_control.py")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    else:
        print("\n👋 Setup cancelled. Run 'python easy_discord_setup.py' when ready!")

if __name__ == "__main__":
    main()
