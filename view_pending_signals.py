#!/usr/bin/env python3
"""
View Pending Signals
This script shows all pending signals waiting to be executed.
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Signal, TradingSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """View pending signals"""
    print("📋 Pending Signals Viewer")
    print("=" * 50)
    
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Check auto trading status
            settings = TradingSettings.query.first()
            auto_trading = settings.auto_trading_enabled if settings else True
            
            print(f"🎛️  Auto Trading: {'🟢 ENABLED' if auto_trading else '🔴 DISABLED'}")
            print()
            
            # Get all unprocessed Discord signals
            pending_signals = Signal.query.filter(
                Signal.discord_message_id.notlike('strategy_%'),
                Signal.processed == False
            ).order_by(Signal.timestamp.desc()).all()
            
            if not pending_signals:
                print("📭 No pending signals found")
                print("   All Discord signals have been processed")
                return
            
            print(f"📊 Pending Signals: {len(pending_signals)}")
            print("-" * 50)
            
            for i, signal in enumerate(pending_signals, 1):
                print(f"{i}. {signal.symbol} {signal.action}")
                print(f"   Entry Price: {signal.entry_price}")
                print(f"   Stop Loss: {signal.stop_loss}")
                print(f"   Take Profit: {signal.take_profit}")
                print(f"   Timestamp: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Message: {signal.raw_message[:100]}...")
                print()
            
            # Show total signals
            total_discord_signals = Signal.query.filter(Signal.discord_message_id.notlike('strategy_%')).count()
            processed_discord_signals = Signal.query.filter(
                Signal.discord_message_id.notlike('strategy_%'),
                Signal.processed == True
            ).count()
            
            print(f"📈 Signal Statistics:")
            print(f"   Total Discord Signals: {total_discord_signals}")
            print(f"   Processed: {processed_discord_signals}")
            print(f"   Pending: {len(pending_signals)}")
            
            if auto_trading:
                print(f"\n🟢 Auto trading is ENABLED")
                print(f"   Pending signals will be executed automatically")
            else:
                print(f"\n🔴 Auto trading is DISABLED")
                print(f"   Enable auto trading to execute pending signals:")
                print(f"   Run: python trading_control.py")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error viewing pending signals: {e}")

if __name__ == "__main__":
    main()
