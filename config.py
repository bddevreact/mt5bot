import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
    
    # OANDA Configuration
    OANDA_API_KEY = os.getenv('OANDA_API_KEY')
    OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID')
    OANDA_ENVIRONMENT = os.getenv('OANDA_ENVIRONMENT', 'practice')  # 'practice' or 'live'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///trading_bot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Trading Configuration
    DEFAULT_LOT_SIZE = float(os.getenv('DEFAULT_LOT_SIZE', '0.01'))
    MAX_RISK_PERCENT = float(os.getenv('MAX_RISK_PERCENT', '2.0'))
    STOP_LOSS_PIPS = int(os.getenv('STOP_LOSS_PIPS', '50'))  # 0.5% stop loss
    TAKE_PROFIT_PIPS = int(os.getenv('TAKE_PROFIT_PIPS', '100'))  # 1% take profit
    
    # Web App Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Strategy Configuration - Only Discord signals are executed
