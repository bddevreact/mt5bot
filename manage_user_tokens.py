#!/usr/bin/env python3
"""
Manage User Tokens
This script provides interactive management of Discord user tokens.
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

def show_menu():
    """Display the main menu"""
    print("\n🔧 User Token Manager")
    print("=" * 40)
    print("1. View all tokens")
    print("2. Add new token")
    print("3. Deactivate token")
    print("4. Delete token")
    print("5. Update channel info")
    print("6. Exit")
    print()

def view_tokens():
    """View all tokens"""
    try:
        with app.app_context():
            tokens = UserTokenManager.get_active_tokens()
            
            if not tokens:
                print("❌ No tokens found")
                return
            
            print(f"\n📊 Found {len(tokens)} token(s):")
            for i, token in enumerate(tokens, 1):
                print(f"\n🔑 Token #{i}")
                print(f"   User ID: {token['user_id']}")
                print(f"   Username: {token['username']}")
                print(f"   Token: {token['token']}")
                print(f"   Channel: {token['channel_name']} (ID: {token['channel_id']})")
                print(f"   Active: {'✅ Yes' if token['is_active'] else '❌ No'}")
                print(f"   Last Used: {token['last_used'] or 'Never'}")
                
    except Exception as e:
        print(f"❌ Error viewing tokens: {e}")

def add_token():
    """Add a new token"""
    print("\n➕ Add New Token")
    print("-" * 30)
    
    try:
        import getpass
        
        # Get user token
        print("🔑 Enter Discord User Token:")
        user_token = getpass.getpass("Token: ").strip()
        
        if not user_token:
            print("❌ No token provided")
            return
        
        # Extract user ID
        if '.' in user_token:
            user_id = user_token.split('.')[0]
        else:
            print("❌ Invalid token format")
            return
        
        # Get username
        username = input("👤 Username (optional): ").strip()
        if not username:
            username = f"User_{user_id}"
        
        # Get channel info
        channel_id = input("📺 Channel ID: ").strip()
        if not channel_id:
            print("❌ Channel ID required")
            return
        
        channel_name = input("📺 Channel Name (optional): ").strip()
        if not channel_name:
            channel_name = f"Channel_{channel_id}"
        
        # Save token
        with app.app_context():
            saved_token = UserTokenManager.save_user_token(
                user_id, username, user_token, channel_id, channel_name
            )
            print("✅ Token saved successfully!")
            
    except Exception as e:
        print(f"❌ Error adding token: {e}")

def deactivate_token():
    """Deactivate a token"""
    print("\n🚫 Deactivate Token")
    print("-" * 30)
    
    try:
        with app.app_context():
            tokens = UserTokenManager.get_active_tokens()
            
            if not tokens:
                print("❌ No active tokens found")
                return
            
            print("Active tokens:")
            for i, token in enumerate(tokens, 1):
                print(f"{i}. {token['username']} ({token['user_id']})")
            
            choice = input("\nEnter token number to deactivate: ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(tokens):
                    user_id = tokens[index]['user_id']
                    success = UserTokenManager.deactivate_token(user_id)
                    if success:
                        print("✅ Token deactivated successfully!")
                    else:
                        print("❌ Failed to deactivate token")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
                
    except Exception as e:
        print(f"❌ Error deactivating token: {e}")

def delete_token():
    """Delete a token permanently"""
    print("\n🗑️  Delete Token")
    print("-" * 30)
    
    try:
        with app.app_context():
            tokens = UserTokenManager.get_active_tokens()
            
            if not tokens:
                print("❌ No tokens found")
                return
            
            print("Available tokens:")
            for i, token in enumerate(tokens, 1):
                print(f"{i}. {token['username']} ({token['user_id']})")
            
            choice = input("\nEnter token number to delete: ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(tokens):
                    user_id = tokens[index]['user_id']
                    confirm = input(f"⚠️  Are you sure you want to delete token for {tokens[index]['username']}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        success = UserTokenManager.delete_token(user_id)
                        if success:
                            print("✅ Token deleted successfully!")
                        else:
                            print("❌ Failed to delete token")
                    else:
                        print("❌ Deletion cancelled")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
                
    except Exception as e:
        print(f"❌ Error deleting token: {e}")

def update_channel():
    """Update channel information"""
    print("\n📺 Update Channel Info")
    print("-" * 30)
    
    try:
        with app.app_context():
            tokens = UserTokenManager.get_active_tokens()
            
            if not tokens:
                print("❌ No tokens found")
                return
            
            print("Available tokens:")
            for i, token in enumerate(tokens, 1):
                print(f"{i}. {token['username']} - {token['channel_name']}")
            
            choice = input("\nEnter token number to update: ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(tokens):
                    user_id = tokens[index]['user_id']
                    
                    new_channel_id = input("New Channel ID: ").strip()
                    new_channel_name = input("New Channel Name: ").strip()
                    
                    if new_channel_id and new_channel_name:
                        success = UserTokenManager.update_channel_info(
                            user_id, new_channel_id, new_channel_name
                        )
                        if success:
                            print("✅ Channel info updated successfully!")
                        else:
                            print("❌ Failed to update channel info")
                    else:
                        print("❌ Both channel ID and name are required")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
                
    except Exception as e:
        print(f"❌ Error updating channel info: {e}")

def main():
    """Main function"""
    global app
    
    print("🔧 User Token Manager")
    print("=" * 50)
    print("Manage Discord user tokens stored in the database")
    
    try:
        # Create Flask app context
        app = create_app()
        
        while True:
            show_menu()
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == '1':
                view_tokens()
            elif choice == '2':
                add_token()
            elif choice == '3':
                deactivate_token()
            elif choice == '4':
                delete_token()
            elif choice == '5':
                update_channel()
            elif choice == '6':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error in token manager: {e}")

if __name__ == "__main__":
    main()
