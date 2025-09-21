#!/usr/bin/env python3
"""
View User Tokens
This script displays all saved Discord user tokens from the database.
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from user_token_manager import UserTokenManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """View all user tokens"""
    print("🔍 User Tokens Viewer")
    print("=" * 50)
    print("Displaying all saved Discord user tokens from database")
    print()
    
    try:
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            tokens = UserTokenManager.get_active_tokens()
            
            if not tokens:
                print("❌ No user tokens found in database")
                print("Run: python setup_user_bot.py")
                return
            
            print(f"📊 Found {len(tokens)} user token(s):")
            print()
            
            for i, token in enumerate(tokens, 1):
                print(f"🔑 Token #{i}")
                print(f"   User ID: {token['user_id']}")
                print(f"   Username: {token['username']}")
                print(f"   Token: {token['token']}")  # Already masked in to_dict()
                print(f"   Channel ID: {token['channel_id']}")
                print(f"   Channel Name: {token['channel_name']}")
                print(f"   Active: {'✅ Yes' if token['is_active'] else '❌ No'}")
                print(f"   Last Used: {token['last_used'] or 'Never'}")
                print(f"   Created: {token['created_at']}")
                print(f"   Updated: {token['updated_at']}")
                print()
            
            print("🔧 Management Commands:")
            print("   python manage_user_tokens.py  # Manage tokens")
            print("   python user_discord_bot.py    # Start bot")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error viewing tokens: {e}")

if __name__ == "__main__":
    main()
