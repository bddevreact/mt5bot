import discord
import asyncio
import re
import logging
from datetime import datetime
from models import db, Signal
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscordSignalFetcher:
    def __init__(self, app):
        self.app = app
        # Use basic intents only (no privileged intents required)
        intents = discord.Intents.default()
        intents.message_content = False  # Don't require message content intent
        self.client = discord.Client(intents=intents)
        self.channel_id = int(Config.DISCORD_CHANNEL_ID)
        self.setup_events()
    
    def setup_events(self):
        @self.client.event
        async def on_ready():
            logger.info(f'Discord bot logged in as {self.client.user}')
            logger.info(f'Monitoring channel ID: {self.channel_id}')
        
        @self.client.event
        async def on_message(message):
            if message.channel.id == self.channel_id and not message.author.bot:
                await self.process_signal(message)
    
    async def process_signal(self, message):
        """Process incoming Discord messages for trading signals"""
        try:
            with self.app.app_context():
                # Check if message already processed
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
                        lot_size=signal_data.get('lot_size'),
                        strategy=signal_data.get('strategy'),
                        confidence=signal_data.get('confidence'),
                        raw_message=message.content
                    )
                    
                    db.session.add(signal)
                    db.session.commit()
                    
                    logger.info(f"New signal processed: {signal_data['symbol']} {signal_data['action']}")
                    
        except Exception as e:
            logger.error(f"Error processing signal: {e}")
    
    def parse_signal(self, message_content):
        """Parse trading signal from Discord message"""
        try:
            # Common signal patterns
            patterns = {
                'buy_pattern': r'(?:BUY|LONG|BUYING)\s+([A-Z]{6})\s+(?:@|at)\s*([\d.]+)',
                'sell_pattern': r'(?:SELL|SHORT|SELLING)\s+([A-Z]{6})\s+(?:@|at)\s*([\d.]+)',
                'sl_pattern': r'(?:SL|STOP\s*LOSS|STOP)\s*:?\s*([\d.]+)',
                'tp_pattern': r'(?:TP|TAKE\s*PROFIT|TARGET)\s*:?\s*([\d.]+)',
                'lot_pattern': r'(?:LOT|SIZE|UNITS)\s*:?\s*([\d.]+)',
                'confidence_pattern': r'(?:CONFIDENCE|CONF)\s*:?\s*([\d.]+)%?'
            }
            
            signal_data = {}
            message_upper = message_content.upper()
            
            # Check for BUY signal
            buy_match = re.search(patterns['buy_pattern'], message_upper)
            if buy_match:
                signal_data['action'] = 'BUY'
                signal_data['symbol'] = buy_match.group(1)
                signal_data['entry_price'] = float(buy_match.group(2))
            
            # Check for SELL signal
            sell_match = re.search(patterns['sell_pattern'], message_upper)
            if sell_match:
                signal_data['action'] = 'SELL'
                signal_data['symbol'] = sell_match.group(1)
                signal_data['entry_price'] = float(sell_match.group(2))
            
            # Extract stop loss
            sl_match = re.search(patterns['sl_pattern'], message_upper)
            if sl_match:
                signal_data['stop_loss'] = float(sl_match.group(1))
            
            # Extract take profit
            tp_match = re.search(patterns['tp_pattern'], message_upper)
            if tp_match:
                signal_data['take_profit'] = float(tp_match.group(1))
            
            # Extract lot size
            lot_match = re.search(patterns['lot_pattern'], message_upper)
            if lot_match:
                signal_data['lot_size'] = float(lot_match.group(1))
            else:
                signal_data['lot_size'] = Config.DEFAULT_LOT_SIZE
            
            # Extract confidence
            conf_match = re.search(patterns['confidence_pattern'], message_upper)
            if conf_match:
                signal_data['confidence'] = float(conf_match.group(1)) / 100
            
            # Determine strategy based on message content
            if 'DISCORD' in message_upper:
                signal_data['strategy'] = 'DISCORD_SIGNAL'
            else:
                signal_data['strategy'] = 'DISCORD_SIGNAL'  # All signals are treated as Discord signals
            
            # Return signal data only if we have at least action and symbol
            if 'action' in signal_data and 'symbol' in signal_data:
                return signal_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing signal: {e}")
            return None
    
    async def start(self):
        """Start the Discord bot"""
        try:
            await self.client.start(Config.DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Error starting Discord bot: {e}")
    
    async def stop(self):
        """Stop the Discord bot"""
        await self.client.close()

# Alternative simple signal fetcher for testing without Discord bot
class SimpleSignalFetcher:
    def __init__(self, app):
        self.app = app
    
    def add_test_signal(self, symbol, action, entry_price, stop_loss=None, take_profit=None):
        """Add a test signal for development"""
        with self.app.app_context():
            signal = Signal(
                discord_message_id=f"test_{datetime.now().timestamp()}",
                symbol=symbol,
                action=action,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                lot_size=Config.DEFAULT_LOT_SIZE,
                strategy='TEST',
                confidence=0.8,
                raw_message=f"Test signal: {action} {symbol} @ {entry_price}"
            )
            
            db.session.add(signal)
            db.session.commit()
            
            logger.info(f"Test signal added: {action} {symbol} @ {entry_price}")
            return signal
