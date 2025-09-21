#!/usr/bin/env python3
"""
Quick Test Script
This script quickly tests if the database migration was successful.
"""

import os
import sys
import requests
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """Test API endpoints to verify everything is working"""
    print("🧪 Testing API Endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test 1: Check if server is running
        print("🔍 Testing server connection...")
        response = requests.get(f"{base_url}/api/user_tokens", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running and responding")
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
        
        # Test 2: Check user tokens endpoint
        print("🔍 Testing user tokens endpoint...")
        tokens = response.json()
        print(f"✅ Found {len(tokens)} user tokens")
        
        # Test 3: Test device detection endpoint
        print("🔍 Testing device detection endpoint...")
        device_response = requests.get(
            f"{base_url}/api/user_tokens/by_device?device_fingerprint=test123",
            timeout=10
        )
        if device_response.status_code in [200, 404]:  # 404 is expected if no token found
            print("✅ Device detection endpoint working")
        else:
            print(f"❌ Device detection endpoint error: {device_response.status_code}")
            return False
        
        # Test 4: Test dashboard
        print("🔍 Testing dashboard...")
        dashboard_response = requests.get(f"{base_url}/", timeout=10)
        if dashboard_response.status_code == 200:
            print("✅ Dashboard is accessible")
        else:
            print(f"❌ Dashboard error: {dashboard_response.status_code}")
            return False
        
        print("✅ All API endpoints are working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the bot is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

def test_database_structure():
    """Test database structure"""
    print("\n🗄️ Testing Database Structure...")
    
    try:
        from app import create_app
        from models import db, UserToken
        
        app = create_app()
        with app.app_context():
            # Check if UserToken table exists and has all columns
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('user_token')
            column_names = [col['name'] for col in columns]
            
            required_columns = [
                'id', 'user_id', 'username', 'token', 'channel_id', 'channel_name',
                'is_active', 'last_used', 'device_fingerprint', 'ip_address', 
                'user_agent', 'created_at', 'updated_at'
            ]
            
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            
            print("✅ All required columns present in database")
            
            # Test creating a UserToken object
            test_token = UserToken(
                user_id="test123",
                username="TestUser",
                token="encrypted_token_here",
                channel_id="test_channel",
                channel_name="Test Channel",
                device_fingerprint="test_device",
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )
            
            print("✅ UserToken model can be created with new fields")
            
            return True
            
    except Exception as e:
        print(f"❌ Database structure test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Quick Test Script")
    print("=" * 40)
    print("Testing if the database migration was successful...")
    print()
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Database structure
    if test_database_structure():
        tests_passed += 1
    
    # Test 2: API endpoints
    if test_api_endpoints():
        tests_passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The migration was successful.")
        print()
        print("🚀 You can now:")
        print("1. Open dashboard: http://localhost:5000")
        print("2. Click 'Add Token' to set up Discord token")
        print("3. Token will be automatically detected on future visits")
        print("4. Use device tracking features")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
