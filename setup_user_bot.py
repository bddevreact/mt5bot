#!/usr/bin/env python3
"""
Setup User Discord Bot
This script helps you set up the user Discord bot with your account.
Now uses SQLite database to store tokens securely.
"""

import os
import sys
import logging
import re

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from user_token_manager import UserTokenManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_user_id_from_token(token):
    """
    Extract Discord user ID from token.
    Discord tokens are in format: user_id.encrypted_data
    """
    try:
        if '.' in token:
            return token.split('.')[0]
        return None
    except:
        return None

def validate_discord_token(token):
    """
    Basic validation of Discord token format.
    """
    try:
        # Discord tokens typically have 2 parts separated by a dot
        parts = token.split('.')
        if len(parts) != 2:
            return False
        
        # First part should be numeric (user ID)
        if not parts[0].isdigit():
            return False
        
        # Second part should be base64-like
        if len(parts[1]) < 20:  # Minimum length check
            return False
        
        return True
    except:
        return False

def main():
    """Setup user Discord bot"""
    print("🔧 User Discord Bot Setup (Database Version)")
    print("=" * 60)
    print("This bot will log in with YOUR Discord account")
    print("and fetch signals from channels you have access to.")
    print("Your token will be stored securely in the SQLite database.")
    print()
    
    print("📋 Requirements:")
    print("1. Your Discord User Token (not bot token)")
    print("2. Channel ID where signals are posted")
    print("3. You must be a member of that channel")
    print()
    
    print("🔑 How to get your Discord User Token:")
    print("1. Open Discord in your web browser")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to Network tab")
    print("4. Send any message in Discord")
    print("5. Look for a request to 'discord.com/api'")
    print("6. In the request headers, find 'authorization'")
    print("7. Copy the token (it starts with your user ID)")
    print()
    
    print("⚠️  IMPORTANT WARNINGS:")
    print("- Never share your user token with anyone")
    print("- Using self-bots is against Discord ToS")
    print("- Use at your own risk")
    print("- Only use for personal trading signals")
    print("- Your token will be encrypted and stored in the database")
    print()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Get user token
        print("🔑 Enter your Discord User Token:")
        print("(The token will be hidden for security)")
        import getpass
        user_token = getpass.getpass("Token: ").strip()
        
        if not user_token:
            print("❌ No token provided. Exiting.")
            return
        
        # Validate token format
        if not validate_discord_token(user_token):
            print("❌ Invalid token format. Please check your token.")
            return
        
        # Extract user ID from token
        user_id = extract_user_id_from_token(user_token)
        if not user_id:
            print("❌ Could not extract user ID from token.")
            return
        
        print(f"✅ Detected User ID: {user_id}")
        
        # Get username
        print("\n👤 Enter your Discord Username (optional, for display):")
        username = input("Username: ").strip()
        if not username:
            username = f"User_{user_id}"
        
        # Get channel ID
        print("\n📺 Enter the Discord Channel ID:")
        print("(Right-click on channel name > Copy Channel ID)")
        channel_id = input("Channel ID: ").strip()
        
        if not channel_id:
            print("❌ No channel ID provided. Exiting.")
            return
        
        # Validate channel ID format
        if not channel_id.isdigit():
            print("❌ Invalid channel ID format. Channel ID should be numeric.")
            return
        
        # Get channel name (optional)
        print("\n📺 Enter Channel Name (optional, for display):")
        channel_name = input("Channel Name: ").strip()
        if not channel_name:
            channel_name = f"Channel_{channel_id}"
        
        try:
            # Save token to database
            print("\n💾 Saving token to database...")
            saved_token = UserTokenManager.save_user_token(
                user_id=user_id,
                username=username,
                token=user_token,
                channel_id=channel_id,
                channel_name=channel_name
            )
            
            print("✅ Configuration saved successfully!")
            print(f"   User ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Channel ID: {channel_id}")
            print(f"   Channel Name: {channel_name}")
            print(f"   Token: {'*' * 20}...{user_token[-4:]}")
            print()
            
            print("🚀 Next Steps:")
            print("1. Run: python user_discord_bot.py")
            print("2. Or double-click: start_user_bot.bat")
            print("3. The bot will log in with your account")
            print("4. It will monitor the channel for trading signals")
            print()
            
            print("📝 Signal Format Examples:")
            print("   BUY EUR_USD @ 1.1000 SL: 1.0950 TP: 1.1100")
            print("   SELL GBP_USD @ 1.2500 STOP: 1.2550 TARGET: 1.2400")
            print("   LONG EUR_USD 1.1000 1.0950 1.1100")
            print()
            
            print("🔧 Management Commands:")
            print("   python view_user_tokens.py    # View saved tokens")
            print("   python manage_user_tokens.py  # Manage tokens")
            print()
            
            print("⚠️  Remember:")
            print("- Keep your token secure")
            print("- Don't share it with anyone")
            print("- Use responsibly")
            print("- Your token is encrypted in the database")
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            logger.error(f"Error saving user token: {e}")

if __name__ == "__main__":
    main()
