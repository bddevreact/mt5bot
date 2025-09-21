#!/usr/bin/env python3
"""
Discord Signal Processor
This script processes Discord signals and sends them to the trading bot.
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Signal, db, TradingSettings
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_discord_signal(signal_text):
    """Process a Discord signal and add it to the database"""
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Parse the signal
            signal_data = parse_signal(signal_text)
            if not signal_data:
                return False, "Invalid signal format"
            
            # Create signal record
            signal = Signal(
                discord_message_id=f"manual_{datetime.now().timestamp()}",
                symbol=signal_data['symbol'],
                action=signal_data['action'],
                entry_price=signal_data['entry_price'],
                stop_loss=signal_data['stop_loss'],
                take_profit=signal_data['take_profit'],
                lot_size=signal_data.get('lot_size', Config.DEFAULT_LOT_SIZE),
                strategy='DISCORD_SIGNAL',
                raw_message=signal_text,
                processed=False,
                timestamp=datetime.utcnow()
            )
            
            # Add to database
            db.session.add(signal)
            db.session.commit()
            
            logger.info(f'Discord signal processed: {signal.action} {signal.symbol} @ {signal.entry_price}')
            
            return True, f"Signal processed: {signal.action} {signal.symbol} @ {signal.entry_price}"
            
    except Exception as e:
        logger.error(f'Error processing Discord signal: {e}')
        return False, f"Error: {e}"

def parse_signal(signal_text):
    """Parse trading signal from text"""
    try:
        import re
        
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
            'CAD_NZD', 'CHF_NZD', 'NZD_JPY'
        ]
        
        symbol = None
        for s in symbols:
            if s in content:
                symbol = s
                break
        
        if not symbol:
            return None
        
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
            'lot_size': Config.DEFAULT_LOT_SIZE
        }
        
    except Exception as e:
        logger.error(f'Error parsing signal: {e}')
        return None

def main():
    """Main function for processing Discord signals"""
    print("📡 Discord Signal Processor")
    print("=" * 50)
    print("This script processes Discord signals and sends them to the trading bot.")
    print()
    print("Supported formats:")
    print("  BUY EUR_USD @ 1.1000 SL: 1.0950 TP: 1.1100")
    print("  SELL GBP_USD @ 1.2500 STOP: 1.2550 TARGET: 1.2400")
    print("  LONG EUR_USD 1.1000 1.0950 1.1100")
    print()
    
    try:
        while True:
            print("\n" + "="*50)
            signal_text = input("Enter Discord signal (or 'quit' to exit): ").strip()
            
            if signal_text.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not signal_text:
                continue
            
            # Process the signal
            success, message = process_discord_signal(signal_text)
            
            if success:
                print(f"✅ {message}")
                
                # Check auto trading status
                app = create_app()
                with app.app_context():
                    settings = TradingSettings.query.first()
                    auto_trading = settings.auto_trading_enabled if settings else True
                    
                    if auto_trading:
                        print("🟢 Auto trading is ENABLED - Signal will be executed automatically!")
                    else:
                        print("🔴 Auto trading is DISABLED - Enable it to execute the signal")
                        print("   Run: python trading_control.py")
            else:
                print(f"❌ {message}")
                print("   Please check the signal format and try again")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
