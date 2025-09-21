#!/usr/bin/env python3
"""
Multi Signal Processor
This script processes signals from Discord, TradingView, and manual input.
"""

import os
import sys
import logging
import re
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Signal, db, TradingSettings
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_signal(signal_text, source="MANUAL"):
    """Parse trading signal from text"""
    try:
        content = signal_text.upper().strip()
        
        # Extract action
        action = None
        if 'BUY' in content or 'LONG' in content:
            action = 'BUY'
        elif 'SELL' in content or 'SHORT' in content:
            action = 'SELL'
        
        if not action:
            return None
        
        # Extract symbol
        symbols = [
            'EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD',
            'NZD_USD', 'USD_CHF', 'EUR_GBP', 'EUR_JPY', 'GBP_JPY',
            'AUD_JPY', 'CAD_JPY', 'CHF_JPY', 'EUR_AUD', 'EUR_CAD',
            'EUR_CHF', 'EUR_NZD', 'GBP_AUD', 'GBP_CAD', 'GBP_CHF',
            'GBP_NZD', 'AUD_CAD', 'AUD_CHF', 'AUD_NZD', 'CAD_CHF',
            'CAD_NZD', 'CHF_NZD', 'NZD_JPY', 'EURUSD', 'GBPUSD',
            'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF',
            'EURGBP', 'EURJPY', 'GBPJPY'
        ]
        
        symbol = None
        for s in symbols:
            if s in content:
                symbol = s
                break
        
        if not symbol:
            return None
        
        # Normalize symbol format
        if len(symbol) == 6 and '_' not in symbol:
            symbol = symbol[:3] + '_' + symbol[3:]
        
        # Extract prices
        price_pattern = r'(\d+\.?\d*)'
        prices = re.findall(price_pattern, content)
        
        if len(prices) < 1:
            return None
        
        entry_price = float(prices[0])
        stop_loss = float(prices[1]) if len(prices) > 1 else None
        take_profit = float(prices[2]) if len(prices) > 2 else None
        
        # Use defaults if not provided
        if not stop_loss:
            if action == 'BUY':
                stop_loss = entry_price * 0.995  # 0.5% stop loss
            else:
                stop_loss = entry_price * 1.005  # 0.5% stop loss
        
        if not take_profit:
            if action == 'BUY':
                take_profit = entry_price * 1.01  # 1% take profit
            else:
                take_profit = entry_price * 0.99  # 1% take profit
        
        return {
            'symbol': symbol,
            'action': action,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'lot_size': Config.DEFAULT_LOT_SIZE,
            'source': source
        }
        
    except Exception as e:
        logger.error(f'Error parsing signal: {e}')
        return None

def process_signal(signal_text, source="MANUAL"):
    """Process a signal and add it to the database"""
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Parse the signal
            signal_data = parse_signal(signal_text, source)
            if not signal_data:
                return False, "Invalid signal format"
            
            # Create signal record
            signal = Signal(
                discord_message_id=f"{source.lower()}_{datetime.now().timestamp()}",
                symbol=signal_data['symbol'],
                action=signal_data['action'],
                entry_price=signal_data['entry_price'],
                stop_loss=signal_data['stop_loss'],
                take_profit=signal_data['take_profit'],
                lot_size=signal_data['lot_size'],
                strategy=f'{source}_SIGNAL',
                raw_message=signal_text,
                processed=False,
                timestamp=datetime.utcnow()
            )
            
            # Add to database
            db.session.add(signal)
            db.session.commit()
            
            logger.info(f'{source} signal processed: {signal.action} {signal.symbol} @ {signal.entry_price}')
            
            return True, f"Signal processed: {signal.action} {signal.symbol} @ {signal.entry_price}"
            
    except Exception as e:
        logger.error(f'Error processing {source} signal: {e}')
        return False, f"Error: {e}"

def main():
    """Main function for processing signals from multiple sources"""
    print("📡 Multi Signal Processor")
    print("=" * 50)
    print("This script processes signals from:")
    print("• Discord channels")
    print("• TradingView")
    print("• Manual input")
    print()
    
    print("📝 Supported Signal Formats:")
    print("  BUY EUR_USD @ 1.1000 SL: 1.0950 TP: 1.1100")
    print("  SELL GBP_USD @ 1.2500 STOP: 1.2550 TARGET: 1.2400")
    print("  LONG EURUSD 1.1000 1.0950 1.1100")
    print("  SHORT GBPUSD 1.2500 1.2550 1.2400")
    print()
    
    try:
        while True:
            print("\n" + "="*50)
            print("Signal Sources:")
            print("1. Discord Signal")
            print("2. TradingView Signal")
            print("3. Manual Signal")
            print("4. View Recent Signals")
            print("5. Check Auto Trading Status")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                print("\n📡 Discord Signal Input:")
                print("Copy signal from your Discord channel and paste here:")
                signal_text = input("Discord Signal: ").strip()
                
                if signal_text:
                    success, message = process_signal(signal_text, "DISCORD")
                    if success:
                        print(f"✅ {message}")
                    else:
                        print(f"❌ {message}")
                else:
                    print("❌ No signal provided!")
                    
            elif choice == "2":
                print("\n📊 TradingView Signal Input:")
                print("Enter TradingView signal manually:")
                signal_text = input("TradingView Signal: ").strip()
                
                if signal_text:
                    success, message = process_signal(signal_text, "TRADINGVIEW")
                    if success:
                        print(f"✅ {message}")
                    else:
                        print(f"❌ {message}")
                else:
                    print("❌ No signal provided!")
                    
            elif choice == "3":
                print("\n✍️ Manual Signal Input:")
                print("Enter signal manually:")
                signal_text = input("Manual Signal: ").strip()
                
                if signal_text:
                    success, message = process_signal(signal_text, "MANUAL")
                    if success:
                        print(f"✅ {message}")
                    else:
                        print(f"❌ {message}")
                else:
                    print("❌ No signal provided!")
                    
            elif choice == "4":
                print("\n📊 Recent Signals:")
                app = create_app()
                with app.app_context():
                    signals = Signal.query.order_by(Signal.timestamp.desc()).limit(10).all()
                    if signals:
                        for signal in signals:
                            source = signal.strategy.replace('_SIGNAL', '')
                            print(f"   {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {source} - {signal.symbol} {signal.action} @ {signal.entry_price}")
                    else:
                        print("   No signals found")
                        
            elif choice == "5":
                print("\n🎛️ Auto Trading Status:")
                app = create_app()
                with app.app_context():
                    settings = TradingSettings.query.first()
                    auto_trading = settings.auto_trading_enabled if settings else True
                    
                    if auto_trading:
                        print("🟢 Auto trading is ENABLED - Signals will be executed automatically!")
                    else:
                        print("🔴 Auto trading is DISABLED - Enable it to execute signals")
                        print("   Run: python trading_control.py")
                        
            elif choice == "6":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice!")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

