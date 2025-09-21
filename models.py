from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Signal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_message_id = db.Column(db.String(50), unique=True, nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # BUY, SELL
    entry_price = db.Column(db.Float, nullable=True)
    stop_loss = db.Column(db.Float, nullable=True)
    take_profit = db.Column(db.Float, nullable=True)
    lot_size = db.Column(db.Float, nullable=True)
    strategy = db.Column(db.String(50), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    raw_message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'action': self.action,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'lot_size': self.lot_size,
            'strategy': self.strategy,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'processed': self.processed
        }

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oanda_trade_id = db.Column(db.String(50), unique=True, nullable=False)
    signal_id = db.Column(db.Integer, db.ForeignKey('signal.id'), nullable=True)
    symbol = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # BUY, SELL
    units = db.Column(db.Integer, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, nullable=True)
    take_profit = db.Column(db.Float, nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    pnl = db.Column(db.Float, default=0.0)
    pnl_percentage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='OPEN')  # OPEN, CLOSED, CANCELLED
    strategy = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    close_timestamp = db.Column(db.DateTime, nullable=True)
    close_price = db.Column(db.Float, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'oanda_trade_id': self.oanda_trade_id,
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'action': self.action,
            'units': self.units,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'current_price': self.current_price,
            'pnl': self.pnl,
            'pnl_percentage': self.pnl_percentage,
            'status': self.status,
            'strategy': self.strategy,
            'timestamp': self.timestamp.isoformat(),
            'close_timestamp': self.close_timestamp.isoformat() if self.close_timestamp else None,
            'close_price': self.close_price
        }

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oanda_position_id = db.Column(db.String(50), unique=True, nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    long_units = db.Column(db.Integer, default=0)
    short_units = db.Column(db.Integer, default=0)
    long_avg_price = db.Column(db.Float, nullable=True)
    short_avg_price = db.Column(db.Float, nullable=True)
    unrealized_pnl = db.Column(db.Float, default=0.0)
    realized_pnl = db.Column(db.Float, default=0.0)
    margin_used = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'long_units': self.long_units,
            'short_units': self.short_units,
            'long_avg_price': self.long_avg_price,
            'short_avg_price': self.short_avg_price,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'margin_used': self.margin_used,
            'timestamp': self.timestamp.isoformat()
        }

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oanda_account_id = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    unrealized_pnl = db.Column(db.Float, default=0.0)
    realized_pnl = db.Column(db.Float, default=0.0)
    margin_used = db.Column(db.Float, default=0.0)
    margin_available = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'balance': self.balance,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'margin_used': self.margin_used,
            'margin_available': self.margin_available,
            'currency': self.currency,
            'timestamp': self.timestamp.isoformat()
        }

class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    parameters = db.Column(db.Text, nullable=True)  # JSON string
    enabled = db.Column(db.Boolean, default=True)
    success_rate = db.Column(db.Float, default=0.0)
    total_trades = db.Column(db.Integer, default=0)
    profitable_trades = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parameters': json.loads(self.parameters) if self.parameters else {},
            'enabled': self.enabled,
            'success_rate': self.success_rate,
            'total_trades': self.total_trades,
            'profitable_trades': self.profitable_trades,
            'created_at': self.created_at.isoformat()
        }

class TradingSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auto_trading_enabled = db.Column(db.Boolean, default=True)
    max_concurrent_trades = db.Column(db.Integer, default=5)
    risk_per_trade = db.Column(db.Float, default=2.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'auto_trading_enabled': self.auto_trading_enabled,
            'max_concurrent_trades': self.max_concurrent_trades,
            'risk_per_trade': self.risk_per_trade,
            'updated_at': self.updated_at.isoformat()
        }

class UserToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)  # Discord user ID
    username = db.Column(db.String(100), nullable=True)  # Discord username
    token = db.Column(db.Text, nullable=False)  # Encrypted Discord token
    channel_id = db.Column(db.String(50), nullable=True)  # Monitored channel ID
    channel_name = db.Column(db.String(100), nullable=True)  # Channel name for display
    is_active = db.Column(db.Boolean, default=True)  # Whether this token is currently active
    last_used = db.Column(db.DateTime, nullable=True)  # Last time token was used
    device_fingerprint = db.Column(db.String(255), nullable=True)  # Device fingerprint for tracking
    ip_address = db.Column(db.String(45), nullable=True)  # IP address for tracking
    user_agent = db.Column(db.Text, nullable=True)  # Browser user agent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'token': '***' + self.token[-4:] if self.token else None,  # Mask token for security
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'is_active': self.is_active,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'device_fingerprint': self.device_fingerprint,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class TradingViewConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)  # User identifier
    username = db.Column(db.String(100), nullable=True)  # Display name
    api_key = db.Column(db.Text, nullable=False)  # Encrypted TradingView API key
    webhook_url = db.Column(db.String(500), nullable=True)  # TradingView webhook URL
    is_active = db.Column(db.Boolean, default=True)  # Whether this config is active
    device_fingerprint = db.Column(db.String(255), nullable=True)  # Device fingerprint
    ip_address = db.Column(db.String(45), nullable=True)  # IP address
    user_agent = db.Column(db.Text, nullable=True)  # Browser user agent
    last_used = db.Column(db.DateTime, nullable=True)  # Last time used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'api_key': '***' + self.api_key[-4:] if self.api_key else None,  # Mask API key
            'webhook_url': self.webhook_url,
            'is_active': self.is_active,
            'device_fingerprint': self.device_fingerprint,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class OANDAConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)  # User identifier
    username = db.Column(db.String(100), nullable=True)  # Display name
    account_id = db.Column(db.String(50), nullable=False)  # OANDA account ID
    account_name = db.Column(db.String(100), nullable=True)  # Display name for account
    api_key = db.Column(db.Text, nullable=False)  # Encrypted OANDA API key
    environment = db.Column(db.String(20), default='practice')  # practice or live
    is_active = db.Column(db.Boolean, default=True)  # Whether this config is active
    device_fingerprint = db.Column(db.String(255), nullable=True)  # Device fingerprint
    ip_address = db.Column(db.String(45), nullable=True)  # IP address
    user_agent = db.Column(db.Text, nullable=True)  # Browser user agent
    last_used = db.Column(db.DateTime, nullable=True)  # Last time used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'account_id': self.account_id,
            'account_name': self.account_name,
            'api_key': '***' + self.api_key[-4:] if self.api_key else None,  # Mask API key
            'environment': self.environment,
            'is_active': self.is_active,
            'device_fingerprint': self.device_fingerprint,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }