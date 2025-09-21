#!/usr/bin/env python3
"""
User Discord Bot
This bot logs in with your Discord account and fetches signals from channels.
"""

import os
import sys
import asyncio
import logging
import re
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Signal, db
from config import Config
from user_token_manager import UserTokenManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserDiscordBot:
    def __init__(self, app):
        self.app = app
        self.channel_id = None
        self.user_token = None
        self.username = None
        self.processed_messages = set()
        
    def load_token_from_database(self):
        """Load user token from database"""
        try:
            with self.app.app_context():
                # Get the first active token
                tokens = UserTokenManager.get_active_tokens()
                if not tokens:
                    logger.error("No active user tokens found in database")
                    return False
                
                # Use the first token (you can modify this logic to select specific token)
                token_info = UserTokenManager.get_user_token(tokens[0]['user_id'])
                if not token_info:
                    logger.error("Failed to load user token from database")
                    return False
                
                self.user_token = token_info['token']
                self.username = token_info['username']
                self.channel_id = int(token_info['channel_id'])
                
                logger.info(f"Loaded token for user: {self.username}")
                logger.info(f"Monitoring channel ID: {self.channel_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error loading token from database: {e}")
            return False
        
    async def start(self):
        """Start the user bot"""
        try:
            # Load token from database first
            if not self.load_token_from_database():
                logger.error("Failed to load user token from database")
                return
            
            import discord
            from discord.ext import commands
            
            # Create bot with your user token (no privileged intents)
            intents = discord.Intents.default()
            intents.message_content = False  # Don't require privileged intents
            intents.guilds = True
            intents.messages = True
            
            # Use your user token (not bot token)
            bot = commands.Bot(command_prefix='!', intents=intents, self_bot=True)
            
            @bot.event
            async def on_ready():
                logger.info(f'User bot logged in as {bot.user}')
                logger.info(f'Monitoring channel ID: {self.channel_id}')
                
                # Check if we can access the channel
                channel = bot.get_channel(self.channel_id)
                if channel:
                    logger.info(f'Monitoring channel: #{channel.name} in {channel.guild.name}')
                else:
                    logger.error(f'Cannot access channel ID: {self.channel_id}')
            
            @bot.event
            async def on_message(message):
                if message.channel.id == self.channel_id and not message.author.bot:
                    await self.process_signal(message)
            
            # Start the bot
            await bot.start(self.user_token)
            
        except Exception as e:
            logger.error(f'Error starting user bot: {e}')
    
    async def process_signal(self, message):
        """Process incoming Discord messages for trading signals"""
        try:
            # Skip if already processed
            if message.id in self.processed_messages:
                return
            
            self.processed_messages.add(message.id)
            
            with self.app.app_context():
                # Check if message already processed in database
                existing_signal = Signal.query.filter_by(discord_message_id=str(message.id)).first()
                if existing_signal:
                    return
                
                # Parse signal from message
                signal_data = self.parse_signal(message.content)
                if signal_data:
                    signal = Signal(
                        discord_message_id=str(message.id),
                        symbol=signal_data.get('symbol'),
                        action=signal_data.get('action'),
                        entry_price=signal_data.get('entry_price'),
                        stop_loss=signal_data.get('stop_loss'),
                        take_profit=signal_data.get('take_profit'),
                        lot_size=signal_data.get('lot_size', Config.DEFAULT_LOT_SIZE),
                        strategy='DISCORD_SIGNAL',
                        raw_message=message.content,
                        processed=False,
                        timestamp=datetime.utcnow()
                    )
                    
                    db.session.add(signal)
                    db.session.commit()
                    
                    logger.info(f'New signal received: {signal.action} {signal.symbol} @ {signal.entry_price}')
                    print(f'📡 New Signal: {signal.action} {signal.symbol} @ {signal.entry_price}')
                    print(f'   Stop Loss: {signal.stop_loss}')
                    print(f'   Take Profit: {signal.take_profit}')
                    print(f'   From: {message.author.name}')
                    print(f'   Time: {signal.timestamp}')
                    print()
                
        except Exception as e:
            logger.error(f'Error processing signal: {e}')
    
    def parse_signal(self, message_content):
        """Parse trading signal from message content"""
        try:
            content = message_content.upper().strip()
            
            # Skip if not a trading signal
            if not any(word in content for word in ['BUY', 'SELL', 'LONG', 'SHORT']):
                return None
            
            # Extract action
            action = None
            if 'BUY' in content or 'LONG' in content:
                action = 'BUY'
            elif 'SELL' in content or 'SHORT' in content:
                action = 'SELL'
            
            if not action:
                return None
            
            # Extract symbol (common forex pairs)
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
            
            # If no stop loss/take profit provided, use defaults
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

async def start_user_bot():
    """Start the user Discord bot"""
    print("🤖 Starting User Discord Bot (Database Version)")
    print("=" * 60)
    print("This bot will log in with your Discord account")
    print("and fetch signals from the specified channel.")
    print("Token will be loaded from the SQLite database.")
    print()
    
    try:
        # Create Flask app
        app = create_app()
        
        # Create user bot
        user_bot = UserDiscordBot(app)
        
        print("🔄 Loading token from database...")
        
        # Check if token exists in database
        with app.app_context():
            tokens = UserTokenManager.get_active_tokens()
            if not tokens:
                print("❌ No active user tokens found in database!")
                print("Please run: python setup_user_bot.py")
                return
            
            print(f"✅ Found {len(tokens)} active token(s)")
            for token in tokens:
                print(f"   - User: {token['username']} (ID: {token['user_id']})")
                print(f"   - Channel: {token['channel_name']} (ID: {token['channel_id']})")
        
        print("\n🔄 Starting user bot...")
        print("📝 Bot will process trading signals automatically")
        print("⏰ Bot will run continuously. Press Ctrl+C to stop.")
        print()
        
        # Start the bot
        await user_bot.start()
        
    except KeyboardInterrupt:
        print("\n🛑 User bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error starting user bot: {e}")

def main():
    """Main function"""
    try:
        asyncio.run(start_user_bot())
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
