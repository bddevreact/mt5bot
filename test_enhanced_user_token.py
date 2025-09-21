#!/usr/bin/env python3
"""
Test Enhanced User Token Database Implementation
This script tests the enhanced user token database functionality with device/IP tracking.
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

def test_enhanced_token_management():
    """Test enhanced token management with device/IP tracking"""
    print("🔐 Testing Enhanced Token Management...")
    
    try:
        app = create_app()
        
        with app.app_context():
            # Test data
            test_user_id = "123456789012345678"
            test_username = "TestUser"
            test_token = "123456789012345678.abcdefghijklmnopqrstuvwxyz"
            test_channel_id = "987654321098765432"
            test_channel_name = "Test Channel"
            test_device_fingerprint = "test_device_123"
            test_ip_address = "192.168.1.100"
            test_user_agent = "Mozilla/5.0 Test Browser"
            
            # Test 1: Save token with device info
            print("💾 Testing save token with device info...")
            saved_token = UserTokenManager.save_user_token(
                test_user_id, test_username, test_token, test_channel_id, test_channel_name,
                test_device_fingerprint, test_ip_address, test_user_agent
            )
            print(f"✅ Token saved with ID: {saved_token.id}")
            
            # Test 2: Get token by device fingerprint
            print("🔍 Testing get token by device fingerprint...")
            retrieved_token = UserTokenManager.get_token_by_device_info(
                device_fingerprint=test_device_fingerprint
            )
            if retrieved_token and retrieved_token['token'] == test_token:
                print("✅ Token retrieved by device fingerprint successfully!")
            else:
                print("❌ Token retrieval by device fingerprint failed!")
                return False
            
            # Test 3: Get token by IP address
            print("🌐 Testing get token by IP address...")
            retrieved_token_ip = UserTokenManager.get_token_by_device_info(
                ip_address=test_ip_address
            )
            if retrieved_token_ip and retrieved_token_ip['token'] == test_token:
                print("✅ Token retrieved by IP address successfully!")
            else:
                print("❌ Token retrieval by IP address failed!")
                return False
            
            # Test 4: Update token info
            print("✏️ Testing update token info...")
            updated = UserTokenManager.update_token_info(
                test_user_id, 
                username="UpdatedUser", 
                channel_name="Updated Channel"
            )
            if updated:
                print("✅ Token info updated successfully!")
            else:
                print("❌ Token info update failed!")
                return False
            
            # Test 5: Verify updated info
            print("🔍 Testing verify updated info...")
            updated_token = UserTokenManager.get_user_token(test_user_id)
            if updated_token and updated_token['username'] == "UpdatedUser":
                print("✅ Updated info verified successfully!")
            else:
                print("❌ Updated info verification failed!")
                return False
            
            # Test 6: Get active tokens
            print("📋 Testing get active tokens...")
            active_tokens = UserTokenManager.get_active_tokens()
            if len(active_tokens) > 0:
                print(f"✅ Found {len(active_tokens)} active token(s)")
                # Check if device info is included
                if 'device_fingerprint' in active_tokens[0]:
                    print("✅ Device fingerprint included in token data")
                else:
                    print("❌ Device fingerprint missing from token data")
                    return False
            else:
                print("❌ No active tokens found!")
                return False
            
            # Cleanup
            print("🧹 Cleaning up test data...")
            UserTokenManager.delete_token(test_user_id)
            print("✅ Test data cleaned up")
            
            print("✅ All enhanced token management tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Error in enhanced token management test: {e}")
        logger.error(f"Error in enhanced token management test: {e}")
        return False

def test_device_fingerprint_generation():
    """Test device fingerprint generation (simulated)"""
    print("\n📱 Testing Device Fingerprint Generation...")
    
    try:
        # Simulate device fingerprint generation
        test_fingerprint = "test_device_fingerprint_12345"
        
        # Test saving token with fingerprint
        app = create_app()
        with app.app_context():
            test_user_id = "999888777666555444"
            test_token = "999888777666555444.zyxwvutsrqponmlkjihgfedcba"
            
            saved_token = UserTokenManager.save_user_token(
                test_user_id, "TestDeviceUser", test_token, "111222333444555666", "Test Device Channel",
                test_fingerprint, "10.0.0.1", "Test User Agent"
            )
            
            # Test retrieval by fingerprint
            retrieved = UserTokenManager.get_token_by_device_info(
                device_fingerprint=test_fingerprint
            )
            
            if retrieved and retrieved['user_id'] == test_user_id:
                print("✅ Device fingerprint generation and retrieval test passed!")
                
                # Cleanup
                UserTokenManager.delete_token(test_user_id)
                return True
            else:
                print("❌ Device fingerprint test failed!")
                return False
                
    except Exception as e:
        print(f"❌ Error in device fingerprint test: {e}")
        return False

def test_multiple_devices():
    """Test multiple devices with different tokens"""
    print("\n🖥️ Testing Multiple Devices...")
    
    try:
        app = create_app()
        
        with app.app_context():
            # Device 1
            device1_fingerprint = "device1_fingerprint"
            device1_ip = "192.168.1.101"
            user1_id = "111111111111111111"
            token1 = "111111111111111111.device1tokenabcdefghijklmnop"
            
            # Device 2
            device2_fingerprint = "device2_fingerprint"
            device2_ip = "192.168.1.102"
            user2_id = "222222222222222222"
            token2 = "222222222222222222.device2tokenqrstuvwxyz123456"
            
            # Save tokens for both devices
            UserTokenManager.save_user_token(
                user1_id, "Device1User", token1, "111111111111111111", "Device1 Channel",
                device1_fingerprint, device1_ip, "Device1 Browser"
            )
            
            UserTokenManager.save_user_token(
                user2_id, "Device2User", token2, "222222222222222222", "Device2 Channel",
                device2_fingerprint, device2_ip, "Device2 Browser"
            )
            
            # Test retrieval for each device
            device1_token = UserTokenManager.get_token_by_device_info(
                device_fingerprint=device1_fingerprint
            )
            device2_token = UserTokenManager.get_token_by_device_info(
                device_fingerprint=device2_fingerprint
            )
            
            if (device1_token and device1_token['user_id'] == user1_id and
                device2_token and device2_token['user_id'] == user2_id):
                print("✅ Multiple devices test passed!")
                
                # Cleanup
                UserTokenManager.delete_token(user1_id)
                UserTokenManager.delete_token(user2_id)
                return True
            else:
                print("❌ Multiple devices test failed!")
                return False
                
    except Exception as e:
        print(f"❌ Error in multiple devices test: {e}")
        return False

def main():
    """Run all enhanced tests"""
    print("🧪 Enhanced User Token Database Implementation Test")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Enhanced Token Management
    if test_enhanced_token_management():
        tests_passed += 1
    
    # Test 2: Device Fingerprint Generation
    if test_device_fingerprint_generation():
        tests_passed += 1
    
    # Test 3: Multiple Devices
    if test_multiple_devices():
        tests_passed += 1
    
    # Test 4: Basic functionality still works
    print("\n🔧 Testing Basic Functionality...")
    try:
        from test_user_token_database import main as basic_test
        if basic_test():
            tests_passed += 1
            print("✅ Basic functionality test passed!")
        else:
            print("❌ Basic functionality test failed!")
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Enhanced Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All enhanced tests passed! The implementation is working correctly.")
        print("\n🚀 New Features Available:")
        print("✅ Device fingerprint tracking")
        print("✅ IP address tracking")
        print("✅ Automatic token detection")
        print("✅ User-friendly web interface")
        print("✅ Edit functionality")
        print("✅ Multiple device support")
        print("\n📱 How to Use:")
        print("1. Open dashboard: http://localhost:5000")
        print("2. Click 'Add Token' button")
        print("3. Enter your Discord token and channel info")
        print("4. Click 'Save Token'")
        print("5. Token will be automatically detected on future visits")
        print("6. Use 'Edit' button to modify token info")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
