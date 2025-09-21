#!/usr/bin/env python3
"""
Check Recent Signals
This script shows recent signals received by the bot.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Check recent signals"""
    print("📊 Checking Recent Signals")
    print("=" * 50)
    
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Get all signals
            all_signals = Signal.query.order_by(Signal.timestamp.desc()).all()
            
            print(f"📈 Total signals in database: {len(all_signals)}")
            
            if not all_signals:
                print("❌ No signals found in database")
                return
            
            # Show recent signals (last 10)
            print(f"\n📋 Recent Signals (Last 10):")
            print("-" * 80)
            print(f"{'#':<3} {'Time':<20} {'Symbol':<10} {'Action':<6} {'Price':<10} {'Strategy':<12} {'Source'}")
            print("-" * 80)
            
            for i, signal in enumerate(all_signals[:10], 1):
                time_str = signal.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                source = "Discord" if signal.discord_message_id.startswith("strategy_") == False else "Strategy"
                price_str = f"{signal.entry_price:.4f}" if signal.entry_price else "N/A"
                
                print(f"{i:<3} {time_str:<20} {signal.symbol:<10} {signal.action:<6} {price_str:<10} {signal.strategy:<12} {source}")
            
            # Show signals by source
            discord_signals = [s for s in all_signals if not s.discord_message_id.startswith("strategy_")]
            strategy_signals = [s for s in all_signals if s.discord_message_id.startswith("strategy_")]
            
            print(f"\n📊 Signal Sources:")
            print(f"   📡 Discord Signals: {len(discord_signals)}")
            print(f"   🤖 Strategy Signals: {len(strategy_signals)}")
            
            # Show signals by strategy
            strategies = {}
            for signal in all_signals:
                strategy = signal.strategy or "Unknown"
                strategies[strategy] = strategies.get(strategy, 0) + 1
            
            print(f"\n📈 Signals by Strategy:")
            for strategy, count in strategies.items():
                print(f"   {strategy}: {count}")
            
            # Show recent Discord signals
            if discord_signals:
                print(f"\n📡 Recent Discord Signals:")
                print("-" * 60)
                for signal in discord_signals[:5]:
                    time_str = signal.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"   {time_str}: {signal.symbol} {signal.action} @ {signal.entry_price}")
                    print(f"   Message: {signal.raw_message[:100]}...")
                    print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error checking signals: {e}")

if __name__ == "__main__":
    main()
