import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments as instruments
import logging
from datetime import datetime, timedelta
from models import db, Trade, Position, Account
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OANDATrader:
    def __init__(self, app):
        self.app = app
        self.client = oandapyV20.API(
            access_token=Config.OANDA_API_KEY,
            environment=Config.OANDA_ENVIRONMENT
        )
        self.account_id = Config.OANDA_ACCOUNT_ID
        
        # Price precision for different currency pairs
        self.price_precision = {
            'EUR_USD': 5,  # 5 decimal places
            'GBP_USD': 5,  # 5 decimal places
            'USD_JPY': 3,  # 3 decimal places
            'AUD_USD': 5,  # 5 decimal places
            'USD_CAD': 5,  # 5 decimal places
            'NZD_USD': 5,  # 5 decimal places
            'USD_CHF': 5,  # 5 decimal places
            'EUR_GBP': 5,  # 5 decimal places
            'EUR_JPY': 3,  # 3 decimal places
            'GBP_JPY': 3,  # 3 decimal places
        }
    
    def format_price(self, price, symbol):
        """Format price according to OANDA precision requirements"""
        precision = self.price_precision.get(symbol, 5)  # Default to 5 decimal places
        return round(float(price), precision)
    
    def get_account_info(self):
        """Get account information from OANDA"""
        try:
            r = accounts.AccountDetails(accountID=self.account_id)
            response = self.client.request(r)
            
            account_data = response['account']
            
            # Update or create account record
            with self.app.app_context():
                account = Account.query.filter_by(oanda_account_id=self.account_id).first()
                if not account:
                    account = Account(oanda_account_id=self.account_id)
                    db.session.add(account)
                
                account.balance = float(account_data['balance'])
                account.unrealized_pnl = float(account_data.get('unrealizedPL', 0))
                account.realized_pnl = float(account_data.get('realizedPL', 0))
                account.margin_used = float(account_data.get('marginUsed', 0))
                account.margin_available = float(account_data.get('marginAvailable', 0))
                account.currency = account_data.get('currency', 'USD')
                
                db.session.commit()
                
                return account.to_dict()
                
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            params = {"instruments": symbol}
            r = pricing.PricingInfo(accountID=self.account_id, params=params)
            response = self.client.request(r)
            
            price_data = response['prices'][0]
            if price_data['tradeable']:
                bid = float(price_data['bids'][0]['price'])
                ask = float(price_data['asks'][0]['price'])
                return {'bid': bid, 'ask': ask, 'mid': (bid + ask) / 2}
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def place_order(self, signal):
        """Place order based on signal"""
        try:
            symbol = signal.symbol
            action = signal.action
            units = int(signal.lot_size * 100000)  # Convert lot size to units
            
            if action == 'SELL':
                units = -units
            
            # Get current price
            price_data = self.get_current_price(symbol)
            if not price_data:
                logger.error(f"Could not get price for {symbol}")
                return None
            
            # Create order data
            order_data = {
                "order": {
                    "type": "MARKET",
                    "instrument": symbol,
                    "units": str(units),
                    "timeInForce": "FOK",
                    "positionFill": "DEFAULT"
                }
            }
            
            # Always add stop loss and take profit
            current_price = price_data['mid']
            
            # Calculate stop loss
            if signal.stop_loss:
                sl_price = self.format_price(signal.stop_loss, symbol)
            else:
                # Use default stop loss based on action and current price
                if action == 'BUY':
                    sl_price = self.format_price(current_price * (1 - Config.STOP_LOSS_PIPS / 10000), symbol)
                else:
                    sl_price = self.format_price(current_price * (1 + Config.STOP_LOSS_PIPS / 10000), symbol)
            
            order_data["order"]["stopLossOnFill"] = {
                "price": str(sl_price)
            }
            
            # Calculate take profit
            if signal.take_profit:
                tp_price = self.format_price(signal.take_profit, symbol)
            else:
                # Use default take profit based on action and current price
                if action == 'BUY':
                    tp_price = self.format_price(current_price * (1 + Config.TAKE_PROFIT_PIPS / 10000), symbol)
                else:
                    tp_price = self.format_price(current_price * (1 - Config.TAKE_PROFIT_PIPS / 10000), symbol)
            
            order_data["order"]["takeProfitOnFill"] = {
                "price": str(tp_price)
            }
            
            # Place order
            r = orders.OrderCreate(accountID=self.account_id, data=order_data)
            response = self.client.request(r)
            
            if response['orderFillTransaction']:
                fill_transaction = response['orderFillTransaction']
                trade_id = fill_transaction['id']
                fill_price = float(fill_transaction['price'])
                
                # Create trade record
                with self.app.app_context():
                    trade = Trade(
                        oanda_trade_id=trade_id,
                        signal_id=signal.id,
                        symbol=symbol,
                        action=action,
                        units=units,
                        entry_price=fill_price,
                        stop_loss=signal.stop_loss,
                        take_profit=signal.take_profit,
                        strategy=signal.strategy
                    )
                    
                    db.session.add(trade)
                    db.session.commit()
                    
                    logger.info(f"Order placed successfully: {action} {symbol} @ {fill_price}")
                    return trade
            else:
                logger.error(f"Order failed: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def close_trade(self, trade_id):
        """Close a specific trade"""
        try:
            data = {"units": "ALL"}
            r = trades.TradeClose(accountID=self.account_id, tradeID=trade_id, data=data)
            response = self.client.request(r)
            
            if response['orderFillTransaction']:
                fill_transaction = response['orderFillTransaction']
                close_price = float(fill_transaction['price'])
                
                # Update trade record
                with self.app.app_context():
                    trade = Trade.query.filter_by(oanda_trade_id=trade_id).first()
                    if trade:
                        trade.status = 'CLOSED'
                        trade.close_timestamp = datetime.utcnow()
                        trade.close_price = close_price
                        trade.pnl = float(fill_transaction['pl'])
                        
                        db.session.commit()
                        
                        logger.info(f"Trade closed: {trade_id} @ {close_price}")
                        return True
                
        except Exception as e:
            logger.error(f"Error closing trade {trade_id}: {e}")
            return False
    
    def close_all_trades(self):
        """Close all open trades"""
        try:
            open_trades = self.get_open_trades()
            closed_count = 0
            failed_count = 0
            
            for trade in open_trades:
                try:
                    data = {"units": "ALL"}
                    r = trades.TradeClose(accountID=self.account_id, tradeID=trade['id'], data=data)
                    response = self.client.request(r)
                    
                    if response.get('orderFillTransaction'):
                        fill_transaction = response['orderFillTransaction']
                        close_price = float(fill_transaction['price'])
                        
                        # Update trade record
                        with self.app.app_context():
                            db_trade = Trade.query.filter_by(oanda_trade_id=trade['id']).first()
                            if db_trade:
                                db_trade.status = 'CLOSED'
                                db_trade.close_timestamp = datetime.utcnow()
                                db_trade.close_price = close_price
                                db_trade.pnl = float(fill_transaction['pl'])
                        
                        closed_count += 1
                        logger.info(f"Trade closed: {trade['id']} @ {close_price}")
                    else:
                        failed_count += 1
                        logger.warning(f"Failed to close trade: {trade['id']}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error closing trade {trade['id']}: {e}")
            
            with self.app.app_context():
                db.session.commit()
            
            logger.info(f"Closed {closed_count} trades, {failed_count} failed")
            return {'closed': closed_count, 'failed': failed_count}
            
        except Exception as e:
            logger.error(f"Error closing all trades: {e}")
            return {'closed': 0, 'failed': 0, 'error': str(e)}
    
    def get_open_trades(self):
        """Get all open trades from OANDA"""
        try:
            r = trades.OpenTrades(accountID=self.account_id)
            response = self.client.request(r)
            
            open_trades = []
            for trade_data in response['trades']:
                trade_info = {
                    'id': trade_data['id'],
                    'instrument': trade_data['instrument'],
                    'units': int(trade_data['currentUnits']),
                    'price': float(trade_data['price']),
                    'unrealizedPL': float(trade_data['unrealizedPL']),
                    'openTime': trade_data['openTime']
                }
                open_trades.append(trade_info)
            
            return open_trades
            
        except Exception as e:
            logger.error(f"Error getting open trades: {e}")
            return []
    
    def get_positions(self):
        """Get all positions from OANDA"""
        try:
            r = positions.OpenPositions(accountID=self.account_id)
            response = self.client.request(r)
            
            positions_list = []
            for position_data in response['positions']:
                if float(position_data['long']['units']) != 0 or float(position_data['short']['units']) != 0:
                    position_info = {
                        'instrument': position_data['instrument'],
                        'long_units': int(position_data['long']['units']),
                        'short_units': int(position_data['short']['units']),
                        'long_avg_price': float(position_data['long']['averagePrice']) if position_data['long']['units'] != '0' else None,
                        'short_avg_price': float(position_data['short']['averagePrice']) if position_data['short']['units'] != '0' else None,
                        'unrealizedPL': float(position_data['unrealizedPL']),
                        'marginUsed': float(position_data['marginUsed'])
                    }
                    positions_list.append(position_info)
            
            return positions_list
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def update_trade_prices(self):
        """Update current prices and PnL for all open trades"""
        try:
            with self.app.app_context():
                open_trades = Trade.query.filter_by(status='OPEN').all()
                
                for trade in open_trades:
                    price_data = self.get_current_price(trade.symbol)
                    if price_data:
                        trade.current_price = price_data['mid']
                        
                        # Calculate PnL
                        if trade.action == 'BUY':
                            trade.pnl = (price_data['mid'] - trade.entry_price) * abs(trade.units)
                        else:
                            trade.pnl = (trade.entry_price - price_data['mid']) * abs(trade.units)
                        
                        trade.pnl_percentage = (trade.pnl / (trade.entry_price * abs(trade.units))) * 100
                
                db.session.commit()
                logger.info(f"Updated prices for {len(open_trades)} trades")
                
        except Exception as e:
            logger.error(f"Error updating trade prices: {e}")
    
    def add_stop_loss_take_profit_to_trades(self):
        """Add stop loss and take profit to trades that don't have them"""
        try:
            with self.app.app_context():
                # Get open trades without stop loss or take profit
                open_trades = Trade.query.filter_by(status='OPEN').all()
                
                for trade in open_trades:
                    if not trade.stop_loss or not trade.take_profit:
                        # Get current price
                        price_data = self.get_current_price(trade.symbol)
                        if price_data:
                            current_price = price_data['mid']
                            
                            # Calculate stop loss and take profit
                            if not trade.stop_loss:
                                if trade.action == 'BUY':
                                    trade.stop_loss = self.format_price(current_price * 0.995, trade.symbol)
                                else:
                                    trade.stop_loss = self.format_price(current_price * 1.005, trade.symbol)
                            
                            if not trade.take_profit:
                                if trade.action == 'BUY':
                                    trade.take_profit = self.format_price(current_price * 1.01, trade.symbol)
                                else:
                                    trade.take_profit = self.format_price(current_price * 0.99, trade.symbol)
                
                db.session.commit()
                logger.info(f"Updated stop loss and take profit for {len(open_trades)} trades")
                
        except Exception as e:
            logger.error(f"Error adding stop loss/take profit to trades: {e}")
    
    def sync_positions(self):
        """Sync positions with database"""
        try:
            positions_data = self.get_positions()
            
            with self.app.app_context():
                # Clear existing positions
                Position.query.delete()
                
                for pos_data in positions_data:
                    position = Position(
                        oanda_position_id=f"{pos_data['instrument']}_{datetime.now().timestamp()}",
                        symbol=pos_data['instrument'],
                        long_units=pos_data['long_units'],
                        short_units=pos_data['short_units'],
                        long_avg_price=pos_data['long_avg_price'],
                        short_avg_price=pos_data['short_avg_price'],
                        unrealized_pnl=pos_data['unrealizedPL'],
                        margin_used=pos_data['marginUsed']
                    )
                    
                    db.session.add(position)
                
                db.session.commit()
                logger.info(f"Synced {len(positions_data)} positions")
                
        except Exception as e:
            logger.error(f"Error syncing positions: {e}")
