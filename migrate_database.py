#!/usr/bin/env python3
"""
Database Migration Script
This script migrates the existing database to include new columns for device tracking.
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
    """Migrate database to add new columns"""
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
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(user_token)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = ['device_fingerprint', 'ip_address', 'user_agent']
        missing_columns = [col for col in new_columns if col not in columns]
        
        if not missing_columns:
            print("✅ All new columns already exist. No migration needed.")
            conn.close()
            return True
        
        print(f"🔄 Adding missing columns: {missing_columns}")
        
        # Add missing columns
        for column in missing_columns:
            if column == 'device_fingerprint':
                cursor.execute("ALTER TABLE user_token ADD COLUMN device_fingerprint VARCHAR(255)")
            elif column == 'ip_address':
                cursor.execute("ALTER TABLE user_token ADD COLUMN ip_address VARCHAR(45)")
            elif column == 'user_agent':
                cursor.execute("ALTER TABLE user_token ADD COLUMN user_agent TEXT")
            
            print(f"✅ Added column: {column}")
        
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
        cursor.execute("PRAGMA table_info(user_token)")
        columns = [column[1] for column in cursor.fetchall()]
        
        required_columns = [
            'id', 'user_id', 'username', 'token', 'channel_id', 'channel_name',
            'is_active', 'last_used', 'device_fingerprint', 'ip_address', 
            'user_agent', 'created_at', 'updated_at'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Missing columns after migration: {missing_columns}")
            return False
        
        print("✅ All required columns present in database")
        
        # Check if we can query the new columns
        cursor.execute("SELECT COUNT(*) FROM user_token")
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} existing user tokens")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def main():
    """Main migration function"""
    print("🔄 Database Migration Script")
    print("=" * 50)
    print("Migrating database to include device tracking columns...")
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
    print("🎉 Database migration completed successfully!")
    print()
    print("📋 What was added:")
    print("✅ device_fingerprint column")
    print("✅ ip_address column") 
    print("✅ user_agent column")
    print()
    print("🚀 You can now:")
    print("1. Start the bot: python run_bot.py")
    print("2. Open dashboard: http://localhost:5000")
    print("3. Add Discord tokens with device tracking")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
