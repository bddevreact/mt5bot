#!/usr/bin/env python3
"""
Enhanced Database Migration Script
This script migrates the existing database to include new tables for TradingView and OANDA configurations.
"""

import os
import sys
import sqlite3
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrate database to add new tables"""
    try:
        # Database file path
        db_path = 'instance/trading_bot.db'
        
        if not os.path.exists(db_path):
            print("❌ Database file not found. Creating new database...")
            from app import create_app
            from models import db
            app = create_app()
            with app.app_context():
                db.create_all()
            print("✅ New database created successfully!")
            return True
        
        # Connect to existing database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if new tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        new_tables = ['trading_view_config', 'oanda_config']
        missing_tables = [table for table in new_tables if table not in existing_tables]
        
        if not missing_tables:
            print("✅ All new tables already exist. No migration needed.")
            conn.close()
            return True
        
        print(f"🔄 Adding missing tables: {missing_tables}")
        
        # Create TradingView config table
        if 'trading_view_config' not in existing_tables:
            cursor.execute("""
                CREATE TABLE trading_view_config (
                    id INTEGER PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    username VARCHAR(100),
                    api_key TEXT NOT NULL,
                    webhook_url VARCHAR(500),
                    is_active BOOLEAN DEFAULT TRUE,
                    device_fingerprint VARCHAR(255),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    last_used DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created trading_view_config table")
        
        # Create OANDA config table
        if 'oanda_config' not in existing_tables:
            cursor.execute("""
                CREATE TABLE oanda_config (
                    id INTEGER PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    username VARCHAR(100),
                    account_id VARCHAR(50) NOT NULL,
                    account_name VARCHAR(100),
                    api_key TEXT NOT NULL,
                    environment VARCHAR(20) DEFAULT 'practice',
                    is_active BOOLEAN DEFAULT TRUE,
                    device_fingerprint VARCHAR(255),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    last_used DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created oanda_config table")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        logger.error(f"Database migration error: {e}")
        return False

def verify_migration():
    """Verify that migration was successful"""
    try:
        db_path = 'instance/trading_bot.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        required_tables = [
            'signal', 'trade', 'position', 'account', 'strategy', 
            'trading_settings', 'user_token', 'trading_view_config', 'oanda_config'
        ]
        
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables after migration: {missing_tables}")
            return False
        
        print("✅ All required tables present in database")
        
        # Check TradingView config table structure
        cursor.execute("PRAGMA table_info(trading_view_config)")
        tradingview_columns = [column[1] for column in cursor.fetchall()]
        
        required_tradingview_columns = [
            'id', 'user_id', 'username', 'api_key', 'webhook_url', 'is_active',
            'device_fingerprint', 'ip_address', 'user_agent', 'last_used',
            'created_at', 'updated_at'
        ]
        
        missing_tradingview_columns = [col for col in required_tradingview_columns if col not in tradingview_columns]
        
        if missing_tradingview_columns:
            print(f"❌ Missing TradingView config columns: {missing_tradingview_columns}")
            return False
        
        print("✅ TradingView config table structure is correct")
        
        # Check OANDA config table structure
        cursor.execute("PRAGMA table_info(oanda_config)")
        oanda_columns = [column[1] for column in cursor.fetchall()]
        
        required_oanda_columns = [
            'id', 'user_id', 'username', 'account_id', 'account_name', 'api_key',
            'environment', 'is_active', 'device_fingerprint', 'ip_address', 
            'user_agent', 'last_used', 'created_at', 'updated_at'
        ]
        
        missing_oanda_columns = [col for col in required_oanda_columns if col not in oanda_columns]
        
        if missing_oanda_columns:
            print(f"❌ Missing OANDA config columns: {missing_oanda_columns}")
            return False
        
        print("✅ OANDA config table structure is correct")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def main():
    """Main migration function"""
    print("🔄 Enhanced Database Migration Script")
    print("=" * 50)
    print("Migrating database to include TradingView and OANDA configuration tables...")
    print()
    
    # Step 1: Migrate database
    if not migrate_database():
        print("❌ Migration failed!")
        return False
    
    # Step 2: Verify migration
    if not verify_migration():
        print("❌ Migration verification failed!")
        return False
    
    print()
    print("🎉 Enhanced database migration completed successfully!")
    print()
    print("📋 What was added:")
    print("✅ trading_view_config table")
    print("✅ oanda_config table")
    print("✅ Device fingerprinting support")
    print("✅ IP address tracking")
    print("✅ User agent storage")
    print()
    print("🚀 You can now:")
    print("1. Start the bot: python run_bot.py")
    print("2. Open dashboard: http://localhost:5000")
    print("3. Add TradingView API configuration")
    print("4. Add OANDA account configurations")
    print("5. Select active accounts from dropdown")
    print("6. Use both Discord and TradingView signals")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
