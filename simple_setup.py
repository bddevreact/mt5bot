#!/usr/bin/env python3
"""
Simple Discord Setup
This script helps you set up Discord user token and channel ID.
"""

import os

def main():
    print("🔧 Simple Discord Setup")
    print("=" * 40)
    print()
    
    print("📋 What you need:")
    print("1. Your Discord User Token")
    print("2. Discord Channel ID")
    print()
    
    print("🔑 How to get Discord User Token:")
    print("1. Open Discord in web browser (not app)")
    print("2. Press F12 (Developer Tools)")
    print("3. Go to Network tab")
    print("4. Send any message in Discord")
    print("5. Find request to 'discord.com/api'")
    print("6. Look for 'authorization' header")
    print("7. Copy the token (starts with your user ID)")
    print()
    
    print("📺 How to get Channel ID:")
    print("1. Right-click on Discord channel name")
    print("2. Select 'Copy Channel ID'")
    print("3. Paste it here")
    print()
    
    # Get user input
    print("Enter your details:")
    print("-" * 20)
    
    token = input("Discord User Token: ").strip()
    if not token:
        print("❌ No token provided!")
        return
    
    channel_id = input("Discord Channel ID: ").strip()
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
        
        print()
        print("✅ Setup completed!")
        print(f"   Token: {'*' * 20}...{token[-4:]}")
        print(f"   Channel ID: {channel_id}")
        print()
        print("🚀 Next steps:")
        print("1. Run: python discord_signal_processor.py")
        print("2. Or run: python trading_control.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
