from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import threading
import time
import logging

from config import Config
from models import db, Signal, Trade, Position, Account, Strategy, TradingSettings, UserToken, TradingViewConfig, OANDAConfig
from discord_fetcher import DiscordSignalFetcher, SimpleSignalFetcher
from oanda_trader import OANDATrader
from strategies import TradingStrategies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Initialize trading components
    oanda_trader = OANDATrader(app)
    strategies = TradingStrategies(app, oanda_trader)
    
    # Initialize Discord fetcher
    if Config.DISCORD_TOKEN and Config.DISCORD_CHANNEL_ID:
        discord_fetcher = DiscordSignalFetcher(app)
        logger.info("Discord signal fetcher initialized")
    else:
        discord_fetcher = SimpleSignalFetcher(app)
        logger.info("Using test signal fetcher (Discord not configured)")
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Initialize default strategies
        default_strategies = [
            {'name': 'DISCORD_SIGNAL', 'description': 'Discord signal processing'}
        ]
        
        for strategy_data in default_strategies:
            existing = Strategy.query.filter_by(name=strategy_data['name']).first()
            if not existing:
                strategy = Strategy(
                    name=strategy_data['name'],
                    description=strategy_data['description'],
                    parameters='{}'
                )
                db.session.add(strategy)
        
        # Initialize trading settings
        settings = TradingSettings.query.first()
        if not settings:
            settings = TradingSettings(
                auto_trading_enabled=True,
                max_concurrent_trades=5,
                risk_per_trade=2.0
            )
            db.session.add(settings)
        
        db.session.commit()
    
    # Trading bot thread
    def trading_bot_loop():
        while True:
            try:
                with app.app_context():
                    # Check if auto trading is enabled
                    settings = TradingSettings.query.first()
                    auto_trading_enabled = settings.auto_trading_enabled if settings else True
                    
                    if auto_trading_enabled:
                        # Only process Discord signals (no internal strategies)
                        unprocessed_discord_signals = Signal.query.filter(
                            Signal.discord_message_id.notlike('strategy_%'),
                            Signal.processed == False
                        ).all()
                        
                        # Process Discord signals and place trades
                        for signal in unprocessed_discord_signals:
                            # Place order
                            trade = oanda_trader.place_order(signal)
                            if trade:
                                signal.processed = True
                                db.session.commit()
                                logger.info(f"Discord trade placed: {signal.action} {signal.symbol}")
                            else:
                                logger.warning(f"Failed to place Discord trade: {signal.action} {signal.symbol}")
                    else:
                        logger.info("Auto trading is disabled - skipping signal processing")
                    
                    # Always update trade prices and sync data (even when auto trading is off)
                    oanda_trader.update_trade_prices()
                    
                    # Add stop loss and take profit to trades that don't have them
                    oanda_trader.add_stop_loss_take_profit_to_trades()
                    
                    # Sync positions
                    oanda_trader.sync_positions()
                    
                    # Update account info
                    oanda_trader.get_account_info()
                    
                    # Update strategy performance
                    strategies.update_strategy_performance()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in trading bot loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    # Start trading bot in background thread
    trading_thread = threading.Thread(target=trading_bot_loop, daemon=True)
    trading_thread.start()
    
    # Routes
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/api/account')
    def get_account():
        try:
            account = Account.query.order_by(Account.timestamp.desc()).first()
            if account:
                return jsonify(account.to_dict())
            else:
                # Get fresh account data
                account_data = oanda_trader.get_account_info()
                return jsonify(account_data or {})
        except Exception as e:
            logger.error(f"Error getting account data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/trades')
    def get_trades():
        try:
            status = request.args.get('status', 'all')
            limit = request.args.get('limit', 50, type=int)
            
            query = Trade.query
            if status != 'all':
                query = query.filter_by(status=status.upper())
            
            trades = query.order_by(Trade.timestamp.desc()).limit(limit).all()
            return jsonify([trade.to_dict() for trade in trades])
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/positions')
    def get_positions():
        try:
            positions = Position.query.all()
            return jsonify([position.to_dict() for position in positions])
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/signals')
    def get_signals():
        try:
            limit = request.args.get('limit', 50, type=int)
            signals = Signal.query.order_by(Signal.timestamp.desc()).limit(limit).all()
            return jsonify([signal.to_dict() for signal in signals])
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/strategies')
    def get_strategies():
        try:
            strategies = Strategy.query.all()
            return jsonify([strategy.to_dict() for strategy in strategies])
        except Exception as e:
            logger.error(f"Error getting strategies: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/close_trade/<trade_id>', methods=['POST'])
    def close_trade(trade_id):
        try:
            success = oanda_trader.close_trade(trade_id)
            if success:
                return jsonify({'message': 'Trade closed successfully'})
            else:
                return jsonify({'error': 'Failed to close trade'}), 400
        except Exception as e:
            logger.error(f"Error closing trade: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test_signal', methods=['POST'])
    def add_test_signal():
        try:
            data = request.get_json()
            signal = discord_fetcher.add_test_signal(
                symbol=data.get('symbol', 'EUR_USD'),
                action=data.get('action', 'BUY'),
                entry_price=data.get('entry_price', 1.1000),
                stop_loss=data.get('stop_loss'),
                take_profit=data.get('take_profit')
            )
            return jsonify(signal.to_dict())
        except Exception as e:
            logger.error(f"Error adding test signal: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/refresh_data', methods=['POST'])
    def refresh_data():
        try:
            with app.app_context():
                # Update all data
                oanda_trader.update_trade_prices()
                oanda_trader.add_stop_loss_take_profit_to_trades()
                oanda_trader.sync_positions()
                oanda_trader.get_account_info()
                strategies.update_strategy_performance()
            
            return jsonify({'message': 'Data refreshed successfully'})
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/add_sl_tp', methods=['POST'])
    def add_stop_loss_take_profit():
        try:
            with app.app_context():
                oanda_trader.add_stop_loss_take_profit_to_trades()
            
            return jsonify({'message': 'Stop loss and take profit added to all trades'})
        except Exception as e:
            logger.error(f"Error adding stop loss/take profit: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/close_all_trades', methods=['POST'])
    def close_all_trades():
        try:
            with app.app_context():
                result = oanda_trader.close_all_trades()
            
            return jsonify({
                'message': f"Closed {result['closed']} trades, {result['failed']} failed",
                'closed': result['closed'],
                'failed': result['failed']
            })
        except Exception as e:
            logger.error(f"Error closing all trades: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/trading_settings', methods=['GET'])
    def get_trading_settings():
        try:
            with app.app_context():
                settings = TradingSettings.query.first()
                if settings:
                    return jsonify(settings.to_dict())
                else:
                    return jsonify({'auto_trading_enabled': True, 'max_concurrent_trades': 5, 'risk_per_trade': 2.0})
        except Exception as e:
            logger.error(f"Error getting trading settings: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/toggle_auto_trading', methods=['POST'])
    def toggle_auto_trading():
        try:
            with app.app_context():
                settings = TradingSettings.query.first()
                if not settings:
                    settings = TradingSettings()
                    db.session.add(settings)
                
                settings.auto_trading_enabled = not settings.auto_trading_enabled
                settings.updated_at = datetime.utcnow()
                db.session.commit()
                
                status = "enabled" if settings.auto_trading_enabled else "disabled"
                return jsonify({
                    'message': f'Auto trading {status}',
                    'auto_trading_enabled': settings.auto_trading_enabled
                })
        except Exception as e:
            logger.error(f"Error toggling auto trading: {e}")
            return jsonify({'error': str(e)}), 500
    
    # User Token Management Endpoints
    @app.route('/api/user_tokens', methods=['GET'])
    def get_user_tokens():
        try:
            with app.app_context():
                from user_token_manager import UserTokenManager
                tokens = UserTokenManager.get_active_tokens()
                return jsonify(tokens)
        except Exception as e:
            logger.error(f"Error getting user tokens: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user_tokens', methods=['POST'])
    def save_user_token():
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            username = data.get('username')
            token = data.get('token')
            channel_id = data.get('channel_id')
            channel_name = data.get('channel_name')
            
            # Get device and IP information
            device_fingerprint = data.get('device_fingerprint')
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            if not user_id or not token:
                return jsonify({'error': 'user_id and token are required'}), 400
            
            with app.app_context():
                from user_token_manager import UserTokenManager
                saved_token = UserTokenManager.save_user_token(
                    user_id, username, token, channel_id, channel_name,
                    device_fingerprint, ip_address, user_agent
                )
                return jsonify(saved_token.to_dict())
        except Exception as e:
            logger.error(f"Error saving user token: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user_tokens/by_device', methods=['GET'])
    def get_token_by_device():
        try:
            device_fingerprint = request.args.get('device_fingerprint')
            ip_address = request.remote_addr
            
            with app.app_context():
                from user_token_manager import UserTokenManager
                token_info = UserTokenManager.get_token_by_device_info(device_fingerprint, ip_address)
                if token_info:
                    # Don't return the actual token for security
                    token_info['token'] = '***' + token_info['token'][-4:] if token_info['token'] else None
                    return jsonify(token_info)
                else:
                    return jsonify({'error': 'No token found for this device/IP'}), 404
        except Exception as e:
            logger.error(f"Error getting token by device: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user_tokens/<user_id>/update', methods=['POST'])
    def update_token_info(user_id):
        try:
            data = request.get_json()
            username = data.get('username')
            channel_id = data.get('channel_id')
            channel_name = data.get('channel_name')
            
            with app.app_context():
                from user_token_manager import UserTokenManager
                success = UserTokenManager.update_token_info(
                    user_id, username, channel_id, channel_name
                )
                if success:
                    return jsonify({'message': 'Token info updated successfully'})
                else:
                    return jsonify({'error': 'Token not found'}), 404
        except Exception as e:
            logger.error(f"Error updating token info: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user_tokens/<user_id>', methods=['GET'])
    def get_user_token(user_id):
        try:
            with app.app_context():
                from user_token_manager import UserTokenManager
                token_info = UserTokenManager.get_user_token(user_id)
                if token_info:
                    # Don't return the actual token for security
                    token_info['token'] = '***' + token_info['token'][-4:] if token_info['token'] else None
                    return jsonify(token_info)
                else:
                    return jsonify({'error': 'Token not found'}), 404
        except Exception as e:
            logger.error(f"Error getting user token: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user_tokens/<user_id>/deactivate', methods=['POST'])
    def deactivate_user_token(user_id):
        try:
            with app.app_context():
                from user_token_manager import UserTokenManager
                success = UserTokenManager.deactivate_token(user_id)
                if success:
                    return jsonify({'message': 'Token deactivated successfully'})
                else:
                    return jsonify({'error': 'Token not found'}), 404
        except Exception as e:
            logger.error(f"Error deactivating user token: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user_tokens/<user_id>', methods=['DELETE'])
    def delete_user_token(user_id):
        try:
            with app.app_context():
                from user_token_manager import UserTokenManager
                success = UserTokenManager.delete_token(user_id)
                if success:
                    return jsonify({'message': 'Token deleted successfully'})
                else:
                    return jsonify({'error': 'Token not found'}), 404
        except Exception as e:
            logger.error(f"Error deleting user token: {e}")
            return jsonify({'error': str(e)}), 500
    
    # TradingView Configuration Endpoints
    @app.route('/api/tradingview_configs', methods=['GET'])
    def get_tradingview_configs():
        try:
            with app.app_context():
                from config_manager import TradingViewConfigManager
                configs = TradingViewConfigManager.get_active_configs()
                return jsonify(configs)
        except Exception as e:
            logger.error(f"Error getting TradingView configs: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tradingview_configs', methods=['POST'])
    def save_tradingview_config():
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            username = data.get('username')
            api_key = data.get('api_key')
            webhook_url = data.get('webhook_url')
            
            # Get device and IP information
            device_fingerprint = data.get('device_fingerprint')
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            if not user_id or not api_key:
                return jsonify({'error': 'user_id and api_key are required'}), 400
            
            with app.app_context():
                from config_manager import TradingViewConfigManager
                saved_config = TradingViewConfigManager.save_tradingview_config(
                    user_id, username, api_key, webhook_url,
                    device_fingerprint, ip_address, user_agent
                )
                return jsonify(saved_config.to_dict())
        except Exception as e:
            logger.error(f"Error saving TradingView config: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tradingview_configs/by_device', methods=['GET'])
    def get_tradingview_config_by_device():
        try:
            device_fingerprint = request.args.get('device_fingerprint')
            ip_address = request.remote_addr
            
            with app.app_context():
                from config_manager import TradingViewConfigManager
                config_info = TradingViewConfigManager.get_tradingview_config(device_fingerprint)
                if config_info:
                    # Don't return the actual API key for security
                    config_info['api_key'] = '***' + config_info['api_key'][-4:] if config_info['api_key'] else None
                    return jsonify(config_info)
                else:
                    return jsonify({'error': 'No TradingView config found for this device/IP'}), 404
        except Exception as e:
            logger.error(f"Error getting TradingView config by device: {e}")
            return jsonify({'error': str(e)}), 500
    
    # OANDA Configuration Endpoints
    @app.route('/api/oanda_configs', methods=['GET'])
    def get_oanda_configs():
        try:
            with app.app_context():
                from config_manager import OANDAConfigManager
                configs = OANDAConfigManager.get_all_oanda_accounts()
                return jsonify(configs)
        except Exception as e:
            logger.error(f"Error getting OANDA configs: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/oanda_configs', methods=['POST'])
    def save_oanda_config():
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            username = data.get('username')
            account_id = data.get('account_id')
            account_name = data.get('account_name')
            api_key = data.get('api_key')
            environment = data.get('environment', 'practice')
            
            # Get device and IP information
            device_fingerprint = data.get('device_fingerprint')
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            if not user_id or not account_id or not api_key:
                return jsonify({'error': 'user_id, account_id and api_key are required'}), 400
            
            with app.app_context():
                from config_manager import OANDAConfigManager
                saved_config = OANDAConfigManager.save_oanda_config(
                    user_id, username, account_id, account_name, api_key, environment,
                    device_fingerprint, ip_address, user_agent
                )
                return jsonify(saved_config.to_dict())
        except Exception as e:
            logger.error(f"Error saving OANDA config: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/oanda_configs/by_device', methods=['GET'])
    def get_oanda_config_by_device():
        try:
            device_fingerprint = request.args.get('device_fingerprint')
            ip_address = request.remote_addr
            
            with app.app_context():
                from config_manager import OANDAConfigManager
                config_info = OANDAConfigManager.get_oanda_config(device_fingerprint)
                if config_info:
                    # Don't return the actual API key for security
                    config_info['api_key'] = '***' + config_info['api_key'][-4:] if config_info['api_key'] else None
                    return jsonify(config_info)
                else:
                    return jsonify({'error': 'No OANDA config found for this device/IP'}), 404
        except Exception as e:
            logger.error(f"Error getting OANDA config by device: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/oanda_accounts', methods=['GET'])
    def get_oanda_accounts():
        try:
            with app.app_context():
                from config_manager import OANDAConfigManager
                accounts = OANDAConfigManager.get_all_oanda_accounts()
                return jsonify(accounts)
        except Exception as e:
            logger.error(f"Error getting OANDA accounts: {e}")
            return jsonify({'error': str(e)}), 500
    
    # TradingView Webhook Endpoint
    @app.route('/api/tradingview_webhook', methods=['POST'])
    def tradingview_webhook():
        try:
            # Get request data
            if request.is_json:
                webhook_data = request.get_json()
            else:
                webhook_data = request.form.to_dict()
            
            logger.info(f"Received TradingView webhook: {webhook_data}")
            
            # Process signal
            from tradingview_signal_fetcher import TradingViewSignalFetcher
            fetcher = TradingViewSignalFetcher(app)
            signal = fetcher.process_webhook_signal(webhook_data)
            
            if signal:
                return jsonify({
                    'success': True,
                    'message': 'Signal processed successfully',
                    'signal_id': signal.id
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to process signal'
                }), 400
                
        except Exception as e:
            logger.error(f"Error handling TradingView webhook: {e}")
            return jsonify({
                'success': False,
                'message': f'Webhook error: {str(e)}'
            }), 500
    
    return app

def start_discord_bot():
    """Start Discord bot in a separate thread"""
    try:
        if Config.DISCORD_TOKEN and Config.DISCORD_CHANNEL_ID:
            import asyncio
            from discord_fetcher import DiscordSignalFetcher
            
            app = create_app()
            discord_fetcher = DiscordSignalFetcher(app)
            
            # Run Discord bot
            asyncio.run(discord_fetcher.start())
    except Exception as e:
        logger.error(f"Error starting Discord bot: {e}")

if __name__ == '__main__':
    app = create_app()
    
    # Start Discord bot in a separate thread
    if Config.DISCORD_TOKEN and Config.DISCORD_CHANNEL_ID:
        import threading
        discord_thread = threading.Thread(target=start_discord_bot, daemon=True)
        discord_thread.start()
        logger.info("Discord bot started in background thread")
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
