#!/usr/bin/env python3
"""
Test User Token Database Implementation
This script tests the user token database functionality.
"""

import os
import sys
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from user_token_manager import UserTokenManager
from token_encryption import token_encryption

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_token_encryption():
    """Test token encryption and decryption"""
    print("🔐 Testing Token Encryption...")
    
    test_token = "1234567890.abcdefghijklmnopqrstuvwxyz"
    
    # Encrypt token
    encrypted = token_encryption.encrypt_token(test_token)
    print(f"✅ Token encrypted: {encrypted[:20]}...")
    
    # Decrypt token
    decrypted = token_encryption.decrypt_token(encrypted)
    print(f"✅ Token decrypted: {decrypted[:20]}...")
    
    # Verify
    if decrypted == test_token:
        print("✅ Encryption/Decryption test passed!")
        return True
    else:
        print("❌ Encryption/Decryption test failed!")
        return False

def test_user_token_manager():
    """Test user token manager functionality"""
    print("\n👤 Testing User Token Manager...")
    
    try:
        app = create_app()
        
        with app.app_context():
            # Test data
            test_user_id = "123456789012345678"
            test_username = "TestUser"
            test_token = "123456789012345678.abcdefghijklmnopqrstuvwxyz"
            test_channel_id = "987654321098765432"
            test_channel_name = "Test Channel"
            
            # Test save token
            print("💾 Testing save token...")
            saved_token = UserTokenManager.save_user_token(
                test_user_id, test_username, test_token, test_channel_id, test_channel_name
            )
            print(f"✅ Token saved with ID: {saved_token.id}")
            
            # Test get token
            print("🔍 Testing get token...")
            retrieved_token = UserTokenManager.get_user_token(test_user_id)
            if retrieved_token and retrieved_token['token'] == test_token:
                print("✅ Token retrieved successfully!")
            else:
                print("❌ Token retrieval failed!")
                return False
            
            # Test get active tokens
            print("📋 Testing get active tokens...")
            active_tokens = UserTokenManager.get_active_tokens()
            if len(active_tokens) > 0:
                print(f"✅ Found {len(active_tokens)} active token(s)")
            else:
                print("❌ No active tokens found!")
                return False
            
            # Test deactivate token
            print("🚫 Testing deactivate token...")
            deactivated = UserTokenManager.deactivate_token(test_user_id)
            if deactivated:
                print("✅ Token deactivated successfully!")
            else:
                print("❌ Token deactivation failed!")
                return False
            
            # Test delete token
            print("🗑️ Testing delete token...")
            deleted = UserTokenManager.delete_token(test_user_id)
            if deleted:
                print("✅ Token deleted successfully!")
            else:
                print("❌ Token deletion failed!")
                return False
            
            print("✅ All User Token Manager tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Error in User Token Manager test: {e}")
        logger.error(f"Error in User Token Manager test: {e}")
        return False

def test_database_models():
    """Test database models"""
    print("\n🗄️ Testing Database Models...")
    
    try:
        app = create_app()
        
        with app.app_context():
            from models import UserToken, db
            
            # Test UserToken model
            print("📊 Testing UserToken model...")
            
            # Check if table exists
            result = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_token'")
            table_exists = result.fetchone() is not None
            
            if table_exists:
                print("✅ UserToken table exists!")
            else:
                print("❌ UserToken table not found!")
                return False
            
            print("✅ Database models test passed!")
            return True
            
    except Exception as e:
        print(f"❌ Error in database models test: {e}")
        logger.error(f"Error in database models test: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 User Token Database Implementation Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Token Encryption
    if test_token_encryption():
        tests_passed += 1
    
    # Test 2: Database Models
    if test_database_models():
        tests_passed += 1
    
    # Test 3: User Token Manager
    if test_user_token_manager():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! User token database implementation is working correctly.")
        print("\n🚀 Next Steps:")
        print("1. Run: python setup_user_bot.py")
        print("2. Add your Discord user token")
        print("3. Run: python user_discord_bot.py")
        print("4. Access dashboard at: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
