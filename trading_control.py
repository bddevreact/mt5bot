#!/usr/bin/env python3
"""
Trading Control Script
This script provides comprehensive control over the trading bot.
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
from models import db, TradingSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_menu():
    """Display the main menu"""
    print("\n" + "=" * 50)
    print("🤖 TRADING BOT CONTROL CENTER")
    print("=" * 50)
    print("1. 📊 Show Account Status")
    print("2. 📈 Show Open Trades")
    print("3. 🛑 Close All Trades")
    print("4. ⚡ Emergency Close All Trades")
    print("5. 🔄 Toggle Auto Trading")
    print("6. 🛡️  Add Stop Loss & Take Profit")
    print("7. 📋 Show Trading Settings")
    print("8. 🚪 Exit")
    print("=" * 50)

def show_account_status(oanda_trader):
    """Show account status"""
    print("\n📊 ACCOUNT STATUS")
    print("-" * 30)
    
    try:
        account_info = oanda_trader.get_account_info()
        if account_info:
            print(f"💰 Balance: ${account_info['balance']:.2f}")
            print(f"📈 Unrealized P&L: ${account_info['unrealized_pnl']:.2f}")
            print(f"📉 Realized P&L: ${account_info['realized_pnl']:.2f}")
            print(f"💳 Margin Used: ${account_info['margin_used']:.2f}")
            print(f"💳 Margin Available: ${account_info['margin_available']:.2f}")
            print(f"💱 Currency: {account_info['currency']}")
        else:
            print("❌ Could not retrieve account information")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_open_trades(oanda_trader):
    """Show open trades"""
    print("\n📈 OPEN TRADES")
    print("-" * 30)
    
    try:
        open_trades = oanda_trader.get_open_trades()
        if not open_trades:
            print("✅ No open trades")
            return
        
        print(f"Found {len(open_trades)} open trades:")
        for i, trade in enumerate(open_trades, 1):
            pnl_color = "🟢" if trade['unrealizedPL'] >= 0 else "🔴"
            print(f"{i}. {trade['instrument']}: {trade['units']} units @ {trade['price']} {pnl_color} ${trade['unrealizedPL']:.2f}")
    except Exception as e:
        print(f"❌ Error: {e}")

def close_all_trades(oanda_trader):
    """Close all trades with confirmation"""
    print("\n🛑 CLOSE ALL TRADES")
    print("-" * 30)
    
    try:
        open_trades = oanda_trader.get_open_trades()
        if not open_trades:
            print("✅ No open trades to close")
            return
        
        print(f"Found {len(open_trades)} open trades")
        response = input("Are you sure you want to close ALL trades? (yes/no): ")
        
        if response.lower() == 'yes':
            result = oanda_trader.close_all_trades()
            print(f"✅ Closed {result['closed']} trades")
            print(f"❌ Failed to close {result['failed']} trades")
        else:
            print("❌ Operation cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")

def emergency_close_all_trades(oanda_trader):
    """Emergency close all trades without confirmation"""
    print("\n🚨 EMERGENCY CLOSE ALL TRADES")
    print("-" * 30)
    print("⚠️  WARNING: This will close ALL trades immediately!")
    
    try:
        result = oanda_trader.close_all_trades()
        print(f"✅ Emergency closed {result['closed']} trades")
        print(f"❌ Failed to close {result['failed']} trades")
    except Exception as e:
        print(f"❌ Error: {e}")

def toggle_auto_trading(app):
    """Toggle auto trading"""
    print("\n🔄 TOGGLE AUTO TRADING")
    print("-" * 30)
    
    try:
        with app.app_context():
            settings = TradingSettings.query.first()
            if not settings:
                settings = TradingSettings()
                db.session.add(settings)
            
            current_status = settings.auto_trading_enabled
            settings.auto_trading_enabled = not current_status
            db.session.commit()
            
            new_status = "ENABLED" if settings.auto_trading_enabled else "DISABLED"
            print(f"✅ Auto trading is now {new_status}")
    except Exception as e:
        print(f"❌ Error: {e}")

def add_stop_loss_take_profit(oanda_trader):
    """Add stop loss and take profit to all trades"""
    print("\n🛡️  ADD STOP LOSS & TAKE PROFIT")
    print("-" * 30)
    
    try:
        oanda_trader.add_stop_loss_take_profit_to_trades()
        print("✅ Stop loss and take profit added to all trades")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_trading_settings(app):
    """Show trading settings"""
    print("\n📋 TRADING SETTINGS")
    print("-" * 30)
    
    try:
        with app.app_context():
            settings = TradingSettings.query.first()
            if settings:
                status = "ENABLED" if settings.auto_trading_enabled else "DISABLED"
                print(f"🔄 Auto Trading: {status}")
                print(f"📊 Max Concurrent Trades: {settings.max_concurrent_trades}")
                print(f"⚠️  Risk Per Trade: {settings.risk_per_trade}%")
                print(f"🕒 Last Updated: {settings.updated_at}")
            else:
                print("❌ No trading settings found")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🤖 Trading Bot Control Center")
    print("Initializing...")
    
    try:
        # Create Flask app context
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Initialize OANDA trader
        oanda_trader = OANDATrader(app)
        
        print("✅ OANDA trader initialized")
        print(f"🔧 Environment: {Config.OANDA_ENVIRONMENT}")
        print(f"💰 Account: {Config.OANDA_ACCOUNT_ID}")
        
        while True:
            show_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                show_account_status(oanda_trader)
            elif choice == '2':
                show_open_trades(oanda_trader)
            elif choice == '3':
                close_all_trades(oanda_trader)
            elif choice == '4':
                emergency_close_all_trades(oanda_trader)
            elif choice == '5':
                toggle_auto_trading(app)
            elif choice == '6':
                add_stop_loss_take_profit(oanda_trader)
            elif choice == '7':
                show_trading_settings(app)
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-8.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Error in trading control script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
