#!/usr/bin/env python3
"""
Trading Bot Status Report
This script provides a comprehensive status of the trading bot.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Signal, Trade, TradingSettings
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Generate comprehensive bot status report"""
    print("🤖 Trading Bot Status Report")
    print("=" * 60)
    print(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # 1. Configuration Status
            print("⚙️  CONFIGURATION STATUS")
            print("-" * 30)
            print(f"OANDA Token: {'✅ Set' if Config.OANDA_API_KEY else '❌ Not Set'}")
            print(f"OANDA Account: {Config.OANDA_ACCOUNT_ID}")
            print(f"Discord Token: {'✅ Set' if Config.DISCORD_TOKEN else '❌ Not Set'}")
            print(f"Discord Channel: {Config.DISCORD_CHANNEL_ID}")
            print(f"Environment: {Config.OANDA_ENVIRONMENT}")
            print()
            
            # 2. Trading Settings
            print("🎛️  TRADING SETTINGS")
            print("-" * 30)
            settings = TradingSettings.query.first()
            if settings:
                print(f"Auto Trading: {'🟢 ENABLED' if settings.auto_trading_enabled else '🔴 DISABLED'}")
                print(f"Max Concurrent Trades: {settings.max_concurrent_trades}")
                print(f"Risk Per Trade: {settings.risk_per_trade}%")
            else:
                print("Auto Trading: 🟢 ENABLED (Default)")
                print("Max Concurrent Trades: 5 (Default)")
                print("Risk Per Trade: 2.0% (Default)")
            print()
            
            # 3. Signal Statistics
            print("📊 SIGNAL STATISTICS")
            print("-" * 30)
            total_signals = Signal.query.count()
            discord_signals = Signal.query.filter(Signal.discord_message_id.notlike('strategy_%')).count()
            strategy_signals = total_signals - discord_signals
            
            print(f"Total Signals: {total_signals}")
            print(f"Discord Signals: {discord_signals}")
            print(f"Strategy Signals: {strategy_signals}")
            
            # Recent signals (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_signals = Signal.query.filter(Signal.timestamp >= yesterday).count()
            print(f"Recent Signals (24h): {recent_signals}")
            print()
            
            # 4. Trade Statistics
            print("💼 TRADE STATISTICS")
            print("-" * 30)
            total_trades = Trade.query.count()
            open_trades = Trade.query.filter_by(status='OPEN').count()
            closed_trades = Trade.query.filter_by(status='CLOSED').count()
            
            print(f"Total Trades: {total_trades}")
            print(f"Open Trades: {open_trades}")
            print(f"Closed Trades: {closed_trades}")
            
            # Recent trades
            recent_trades = Trade.query.filter(Trade.timestamp >= yesterday).count()
            print(f"Recent Trades (24h): {recent_trades}")
            print()
            
            # 5. Strategy Performance
            print("📈 STRATEGY PERFORMANCE")
            print("-" * 30)
            strategies = {}
            for signal in Signal.query.all():
                strategy = signal.strategy or "Unknown"
                strategies[strategy] = strategies.get(strategy, 0) + 1
            
            for strategy, count in sorted(strategies.items(), key=lambda x: x[1], reverse=True):
                print(f"{strategy}: {count} signals")
            print()
            
            # 6. Discord Bot Status
            print("📡 DISCORD BOT STATUS")
            print("-" * 30)
            if Config.DISCORD_TOKEN and Config.DISCORD_CHANNEL_ID:
                print("✅ Discord Bot: Configured")
                print(f"📡 Channel ID: {Config.DISCORD_CHANNEL_ID}")
                print(f"📨 Discord Signals Received: {discord_signals}")
                
                if discord_signals > 0:
                    latest_discord = Signal.query.filter(Signal.discord_message_id.notlike('strategy_%')).order_by(Signal.timestamp.desc()).first()
                    if latest_discord:
                        print(f"🕒 Latest Discord Signal: {latest_discord.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("❌ Discord Bot: Not Configured")
            print()
            
            # 7. Recommendations
            print("💡 RECOMMENDATIONS")
            print("-" * 30)
            
            if not settings or settings.auto_trading_enabled:
                print("🟢 Auto trading is ENABLED - Bot will execute trades")
            else:
                print("🔴 Auto trading is DISABLED - Bot will only monitor")
            
            if discord_signals == 0:
                print("📡 No Discord signals received - Check Discord bot connection")
            
            if open_trades == 0:
                print("💼 No open trades - Bot is ready for new signals")
            else:
                print(f"💼 {open_trades} open trades - Monitor positions")
            
            print()
            print("🎯 Bot is ready to receive and process trading signals!")
            
    except Exception as e:
        print(f"❌ Error generating status report: {e}")
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
