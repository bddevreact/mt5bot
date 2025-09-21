#!/usr/bin/env python3
"""
Trading Bot Launcher
This script starts the trading bot with proper error handling and logging.
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config

def setup_logging():
    """Setup logging configuration"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'DISCORD_TOKEN',
        'DISCORD_CHANNEL_ID',
        'OANDA_API_KEY',
        'OANDA_ACCOUNT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(Config, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("See env_example.txt for reference.")
        return False
    
    return True

def main():
    """Main function to start the trading bot"""
    logger = setup_logging()
    
    print("🤖 Trading Bot Starting...")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    try:
        # Create Flask app
        app = create_app()
        
        print("✅ Environment variables loaded")
        print("✅ Database initialized")
        print("✅ Trading components initialized")
        print("✅ Discord fetcher ready")
        print("✅ OANDA trader connected")
        print("✅ Strategies loaded")
        print("\n🌐 Starting web dashboard...")
        print(f"📊 Dashboard URL: http://localhost:5000")
        print(f"🔧 Environment: {Config.OANDA_ENVIRONMENT}")
        print(f"💰 Default lot size: {Config.DEFAULT_LOT_SIZE}")
        print(f"⚠️  Max risk: {Config.MAX_RISK_PERCENT}%")
        print("\n" + "=" * 50)
        print("🚀 Trading Bot is now running!")
        print("Press Ctrl+C to stop the bot")
        print("=" * 50)
        
        # Start the Flask app
        app.run(
            debug=Config.DEBUG,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to prevent issues with background threads
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Trading Bot stopped by user")
        logger.info("Trading bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting trading bot: {e}")
        logger.error(f"Error starting trading bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
