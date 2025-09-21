import logging
from datetime import datetime, timedelta
from models import db, Signal, Trade, Strategy
from oanda_trader import OANDATrader
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingStrategies:
    def __init__(self, app, oanda_trader):
        self.app = app
        self.oanda_trader = oanda_trader
        self.strategies = {
            'DISCORD_SIGNAL': self.discord_signal_strategy
        }
    
    def format_price(self, price, symbol):
        """Format price according to OANDA precision requirements"""
        return self.oanda_trader.format_price(price, symbol)
    
    
    def discord_signal_strategy(self, signal):
        """Process Discord signals with additional validation"""
        try:
            # Validate signal parameters
            if not signal.symbol or not signal.action:
                return None
            
            # Check if signal is already processed
            if signal.processed:
                return None
            
            # Add risk management - always ensure stop loss and take profit
            price_data = self.oanda_trader.get_current_price(signal.symbol)
            if price_data:
                current_price = price_data['mid']
                
                if not signal.stop_loss:
                    if signal.action == 'BUY':
                        signal.stop_loss = self.format_price(current_price * 0.995, signal.symbol)  # 0.5% stop loss
                    else:
                        signal.stop_loss = self.format_price(current_price * 1.005, signal.symbol)  # 0.5% stop loss
                
                if not signal.take_profit:
                    if signal.action == 'BUY':
                        signal.take_profit = self.format_price(current_price * 1.01, signal.symbol)  # 1% take profit
                    else:
                        signal.take_profit = self.format_price(current_price * 0.99, signal.symbol)  # 1% take profit
            
            # Mark signal as processed
            signal.processed = True
            
            with self.app.app_context():
                db.session.commit()
            
            return {
                'symbol': signal.symbol,
                'action': signal.action,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'lot_size': signal.lot_size,
                'strategy': signal.strategy,
                'confidence': signal.confidence or 0.8
            }
            
        except Exception as e:
            logger.error(f"Error processing Discord signal: {e}")
            return None
    
    def execute_strategy(self, strategy_name, symbol=None, signal=None):
        """Execute a specific strategy"""
        try:
            if strategy_name not in self.strategies:
                logger.error(f"Unknown strategy: {strategy_name}")
                return None
            
            if strategy_name == 'DISCORD_SIGNAL' and signal:
                return self.strategies[strategy_name](signal)
            elif symbol:
                return self.strategies[strategy_name](symbol)
            else:
                logger.error(f"Missing required parameters for strategy: {strategy_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing strategy {strategy_name}: {e}")
            return None
    
    def run_all_strategies(self, symbols=['EUR_USD', 'GBP_USD', 'USD_JPY']):
        """Run Discord signal strategy only"""
        signals = []
        
        try:
            with self.app.app_context():
                # Get unprocessed Discord signals
                discord_signals = Signal.query.filter_by(processed=False).all()
                
                for signal in discord_signals:
                    signal_data = self.execute_strategy('DISCORD_SIGNAL', signal=signal)
                    if signal_data:
                        signals.append(signal_data)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error running strategies: {e}")
            return []
    
    def update_strategy_performance(self):
        """Update strategy performance metrics"""
        try:
            with self.app.app_context():
                strategies = Strategy.query.all()
                
                for strategy in strategies:
                    # Get trades for this strategy
                    trades = Trade.query.filter_by(strategy=strategy.name).all()
                    
                    if trades:
                        total_trades = len(trades)
                        profitable_trades = len([t for t in trades if t.pnl > 0])
                        success_rate = (profitable_trades / total_trades) * 100
                        
                        strategy.total_trades = total_trades
                        strategy.profitable_trades = profitable_trades
                        strategy.success_rate = success_rate
                
                db.session.commit()
                logger.info("Strategy performance updated")
                
        except Exception as e:
            logger.error(f"Error updating strategy performance: {e}")
