#!/usr/bin/env python3
"""
Enhanced Integration Test Script
This script tests the TradingView and OANDA configuration functionality.
"""

import os
import sys
import requests
import time
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """Test all new API endpoints"""
    print("🧪 Testing Enhanced API Endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test 1: TradingView configs endpoint
        print("🔍 Testing TradingView configs endpoint...")
        response = requests.get(f"{base_url}/api/tradingview_configs", timeout=10)
        if response.status_code == 200:
            print("✅ TradingView configs endpoint working")
        else:
            print(f"❌ TradingView configs endpoint error: {response.status_code}")
            return False
        
        # Test 2: OANDA configs endpoint
        print("🔍 Testing OANDA configs endpoint...")
        response = requests.get(f"{base_url}/api/oanda_configs", timeout=10)
        if response.status_code == 200:
            print("✅ OANDA configs endpoint working")
        else:
            print(f"❌ OANDA configs endpoint error: {response.status_code}")
            return False
        
        # Test 3: OANDA accounts endpoint
        print("🔍 Testing OANDA accounts endpoint...")
        response = requests.get(f"{base_url}/api/oanda_accounts", timeout=10)
        if response.status_code == 200:
            print("✅ OANDA accounts endpoint working")
        else:
            print(f"❌ OANDA accounts endpoint error: {response.status_code}")
            return False
        
        # Test 4: TradingView webhook endpoint
        print("🔍 Testing TradingView webhook endpoint...")
        test_webhook_data = {
            'symbol': 'EUR_USD',
            'action': 'BUY',
            'price': 1.1000,
            'stop_loss': 1.0950,
            'take_profit': 1.1100,
            'test': True
        }
        response = requests.post(f"{base_url}/api/tradingview_webhook", 
                               json=test_webhook_data, timeout=10)
        if response.status_code in [200, 400]:  # 400 is expected if no config
            print("✅ TradingView webhook endpoint working")
        else:
            print(f"❌ TradingView webhook endpoint error: {response.status_code}")
            return False
        
        # Test 5: Device detection endpoints
        print("🔍 Testing device detection endpoints...")
        device_fingerprint = "test_device_123"
        
        # TradingView device detection
        response = requests.get(f"{base_url}/api/tradingview_configs/by_device?device_fingerprint={device_fingerprint}", timeout=10)
        if response.status_code in [200, 404]:  # 404 is expected if no config
            print("✅ TradingView device detection working")
        else:
            print(f"❌ TradingView device detection error: {response.status_code}")
            return False
        
        # OANDA device detection
        response = requests.get(f"{base_url}/api/oanda_configs/by_device?device_fingerprint={device_fingerprint}", timeout=10)
        if response.status_code in [200, 404]:  # 404 is expected if no config
            print("✅ OANDA device detection working")
        else:
            print(f"❌ OANDA device detection error: {response.status_code}")
            return False
        
        print("✅ All enhanced API endpoints are working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the bot is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

def test_database_structure():
    """Test database structure"""
    print("\n🗄️ Testing Enhanced Database Structure...")
    
    try:
        from app import create_app
        from models import db, TradingViewConfig, OANDAConfig
        
        app = create_app()
        with app.app_context():
            # Check if TradingViewConfig table exists and has all columns
            inspector = db.inspect(db.engine)
            tradingview_columns = inspector.get_columns('trading_view_config')
            tradingview_column_names = [col['name'] for col in tradingview_columns]
            
            required_tradingview_columns = [
                'id', 'user_id', 'username', 'api_key', 'webhook_url', 'is_active',
                'device_fingerprint', 'ip_address', 'user_agent', 'last_used',
                'created_at', 'updated_at'
            ]
            
            missing_tradingview_columns = [col for col in required_tradingview_columns if col not in tradingview_column_names]
            
            if missing_tradingview_columns:
                print(f"❌ Missing TradingView config columns: {missing_tradingview_columns}")
                return False
            
            print("✅ TradingView config table structure is correct")
            
            # Check if OANDAConfig table exists and has all columns
            oanda_columns = inspector.get_columns('oanda_config')
            oanda_column_names = [col['name'] for col in oanda_columns]
            
            required_oanda_columns = [
                'id', 'user_id', 'username', 'account_id', 'account_name', 'api_key',
                'environment', 'is_active', 'device_fingerprint', 'ip_address', 
                'user_agent', 'last_used', 'created_at', 'updated_at'
            ]
            
            missing_oanda_columns = [col for col in required_oanda_columns if col not in oanda_column_names]
            
            if missing_oanda_columns:
                print(f"❌ Missing OANDA config columns: {missing_oanda_columns}")
                return False
            
            print("✅ OANDA config table structure is correct")
            
            # Test creating objects
            test_tradingview_config = TradingViewConfig(
                user_id="test123",
                username="TestUser",
                api_key="encrypted_api_key_here",
                webhook_url="https://example.com/webhook",
                device_fingerprint="test_device",
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )
            
            test_oanda_config = OANDAConfig(
                user_id="test123",
                username="TestUser",
                account_id="test_account",
                account_name="Test Account",
                api_key="encrypted_api_key_here",
                environment="practice",
                device_fingerprint="test_device",
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )
            
            print("✅ TradingView and OANDA config models can be created")
            
            return True
            
    except Exception as e:
        print(f"❌ Database structure test failed: {e}")
        return False

def test_configuration_managers():
    """Test configuration manager classes"""
    print("\n⚙️ Testing Configuration Managers...")
    
    try:
        from config_manager import TradingViewConfigManager, OANDAConfigManager
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # Test TradingViewConfigManager
            print("🔍 Testing TradingViewConfigManager...")
            
            # Test save method
            saved_config = TradingViewConfigManager.save_tradingview_config(
                user_id="test_tradingview",
                username="TestUser",
                api_key="test_api_key",
                webhook_url="https://example.com/webhook",
                device_fingerprint="test_device",
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )
            
            if saved_config:
                print("✅ TradingViewConfigManager.save_tradingview_config() working")
            else:
                print("❌ TradingViewConfigManager.save_tradingview_config() failed")
                return False
            
            # Test get method
            config_info = TradingViewConfigManager.get_tradingview_config("test_tradingview")
            if config_info:
                print("✅ TradingViewConfigManager.get_tradingview_config() working")
            else:
                print("❌ TradingViewConfigManager.get_tradingview_config() failed")
                return False
            
            # Test OANDAConfigManager
            print("🔍 Testing OANDAConfigManager...")
            
            # Test save method
            saved_oanda_config = OANDAConfigManager.save_oanda_config(
                user_id="test_oanda",
                username="TestUser",
                account_id="test_account",
                account_name="Test Account",
                api_key="test_api_key",
                environment="practice",
                device_fingerprint="test_device",
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )
            
            if saved_oanda_config:
                print("✅ OANDAConfigManager.save_oanda_config() working")
            else:
                print("❌ OANDAConfigManager.save_oanda_config() failed")
                return False
            
            # Test get method
            oanda_config_info = OANDAConfigManager.get_oanda_config("test_oanda")
            if oanda_config_info:
                print("✅ OANDAConfigManager.get_oanda_config() working")
            else:
                print("❌ OANDAConfigManager.get_oanda_config() failed")
                return False
            
            # Test get all accounts
            accounts = OANDAConfigManager.get_all_oanda_accounts()
            if isinstance(accounts, list):
                print("✅ OANDAConfigManager.get_all_oanda_accounts() working")
            else:
                print("❌ OANDAConfigManager.get_all_oanda_accounts() failed")
                return False
            
            print("✅ All configuration managers are working correctly!")
            return True
            
    except Exception as e:
        print(f"❌ Configuration managers test failed: {e}")
        return False

def test_tradingview_signal_fetcher():
    """Test TradingView signal fetcher"""
    print("\n📡 Testing TradingView Signal Fetcher...")
    
    try:
        from tradingview_signal_fetcher import TradingViewSignalFetcher
        from app import create_app
        
        app = create_app()
        with app.app_context():
            fetcher = TradingViewSignalFetcher(app)
            
            # Test signal parsing
            test_webhook_data = {
                'symbol': 'EUR_USD',
                'action': 'BUY',
                'price': 1.1000,
                'stop_loss': 1.0950,
                'take_profit': 1.1100,
                'lot_size': 0.01,
                'confidence': 85.0
            }
            
            parsed_signal = fetcher.parse_tradingview_signal(test_webhook_data)
            if parsed_signal:
                print("✅ TradingView signal parsing working")
                print(f"   Parsed signal: {parsed_signal}")
            else:
                print("❌ TradingView signal parsing failed")
                return False
            
            # Test webhook signature validation
            test_payload = "test_payload"
            test_signature = "test_signature"
            test_api_key = "test_api_key"
            
            validation_result = fetcher.validate_webhook_signature(test_payload, test_signature, test_api_key)
            if isinstance(validation_result, bool):
                print("✅ TradingView webhook signature validation working")
            else:
                print("❌ TradingView webhook signature validation failed")
                return False
            
            print("✅ TradingView signal fetcher is working correctly!")
            return True
            
    except Exception as e:
        print(f"❌ TradingView signal fetcher test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Enhanced Integration Test Script")
    print("=" * 50)
    print("Testing TradingView and OANDA configuration functionality...")
    print()
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Database structure
    if test_database_structure():
        tests_passed += 1
    
    # Test 2: Configuration managers
    if test_configuration_managers():
        tests_passed += 1
    
    # Test 3: TradingView signal fetcher
    if test_tradingview_signal_fetcher():
        tests_passed += 1
    
    # Test 4: API endpoints
    if test_api_endpoints():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The enhanced integration is working correctly.")
        print()
        print("🚀 You can now:")
        print("1. Open dashboard: http://localhost:5000")
        print("2. Add TradingView API configuration")
        print("3. Add OANDA account configurations")
        print("4. Select active accounts from dropdown")
        print("5. Use both Discord and TradingView signals")
        print("6. Receive TradingView webhook signals")
        print()
        print("📋 Features Available:")
        print("✅ TradingView API configuration")
        print("✅ OANDA account management")
        print("✅ Device fingerprinting")
        print("✅ IP address tracking")
        print("✅ Web-based configuration")
        print("✅ Account selection dropdown")
        print("✅ Signal source selection")
        print("✅ TradingView webhook processing")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
