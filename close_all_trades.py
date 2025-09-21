#!/usr/bin/env python3
"""
Close All Trades Script
This script will close all open trades immediately.
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from oanda_trader import OANDATrader
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to close all trades"""
    print("🛑 Closing All Trades Script")
    print("=" * 40)
    
    try:
        # Create Flask app context
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Initialize OANDA trader
        oanda_trader = OANDATrader(app)
        
        print("✅ OANDA trader initialized")
        print(f"🔧 Environment: {Config.OANDA_ENVIRONMENT}")
        print(f"💰 Account: {Config.OANDA_ACCOUNT_ID}")
        print("\n📊 Getting open trades...")
        
        # Get open trades
        open_trades = oanda_trader.get_open_trades()
        
        if not open_trades:
            print("✅ No open trades found. All trades are already closed.")
            return
        
        print(f"📈 Found {len(open_trades)} open trades:")
        for trade in open_trades:
            print(f"   - {trade['instrument']}: {trade['units']} units @ {trade['price']}")
        
        # Confirm before closing
        response = input(f"\n⚠️  Are you sure you want to close ALL {len(open_trades)} trades? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled by user")
            return
        
        print("\n🔄 Closing all trades...")
        
        # Close all trades
        result = oanda_trader.close_all_trades()
        
        print("\n" + "=" * 40)
        print("📊 Results:")
        print(f"✅ Successfully closed: {result['closed']} trades")
        print(f"❌ Failed to close: {result['failed']} trades")
        
        if result.get('error'):
            print(f"⚠️  Error: {result['error']}")
        
        if result['closed'] > 0:
            print("🎉 All trades closed successfully!")
        else:
            print("⚠️  No trades were closed")
        
        print("=" * 40)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Script stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Error in close all trades script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
