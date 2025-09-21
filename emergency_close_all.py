#!/usr/bin/env python3
"""
Emergency Close All Trades Script
This script will immediately close all open trades without confirmation.
Use this for emergency situations.
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
    """Emergency close all trades"""
    print("🚨 EMERGENCY CLOSE ALL TRADES")
    print("=" * 40)
    print("⚠️  WARNING: This will close ALL trades immediately!")
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
        
        # Get open trades
        open_trades = oanda_trader.get_open_trades()
        
        if not open_trades:
            print("✅ No open trades found. All trades are already closed.")
            return
        
        print(f"📈 Found {len(open_trades)} open trades - CLOSING NOW...")
        
        # Close all trades immediately
        result = oanda_trader.close_all_trades()
        
        print("\n" + "=" * 40)
        print("📊 EMERGENCY CLOSE RESULTS:")
        print(f"✅ Successfully closed: {result['closed']} trades")
        print(f"❌ Failed to close: {result['failed']} trades")
        
        if result.get('error'):
            print(f"⚠️  Error: {result['error']}")
        
        if result['closed'] > 0:
            print("🎉 Emergency close completed!")
        else:
            print("⚠️  No trades were closed")
        
        print("=" * 40)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        logger.error(f"Critical error in emergency close script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
