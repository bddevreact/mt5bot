#!/usr/bin/env python3
"""
TradingView Signal Fetcher
This module fetches trading signals from TradingView webhooks and processes them.
"""

import os
import sys
import logging
import requests
import json
from datetime import datetime
from flask import request

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, Signal
from config_manager import TradingViewConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingViewSignalFetcher:
    def __init__(self, app):
        self.app = app
    
    def process_webhook_signal(self, webhook_data):
        """
        Process incoming TradingView webhook signal.
        
        Args:
            webhook_data (dict): TradingView webhook payload
            
        Returns:
            Signal: Created signal object, or None if failed
        """
        try:
            with self.app.app_context():
                # Parse TradingView signal format
                signal_data = self.parse_tradingview_signal(webhook_data)
                if not signal_data:
                    logger.warning("Failed to parse TradingView signal")
                    return None
                
                # Create signal record
                signal = Signal(
                    discord_message_id=f"tradingview_{datetime.utcnow().timestamp()}",
                    symbol=signal_data.get('symbol'),
                    action=signal_data.get('action'),
                    entry_price=signal_data.get('entry_price'),
                    stop_loss=signal_data.get('stop_loss'),
                    take_profit=signal_data.get('take_profit'),
                    lot_size=signal_data.get('lot_size', 0.01),
                    strategy='TRADINGVIEW_SIGNAL',
                    confidence=signal_data.get('confidence', 100.0),
                    raw_message=json.dumps(webhook_data),
                    processed=False,
                    timestamp=datetime.utcnow()
                )
                
                db.session.add(signal)
                db.session.commit()
                
                logger.info(f"TradingView signal processed: {signal.action} {signal.symbol} @ {signal.entry_price}")
                return signal
                
        except Exception as e:
            logger.error(f"Error processing TradingView signal: {e}")
            return None
    
    def parse_tradingview_signal(self, webhook_data):
        """
        Parse TradingView webhook signal data.
        
        Args:
            webhook_data (dict): TradingView webhook payload
            
        Returns:
            dict: Parsed signal data, or None if invalid
        """
        try:
            # Common TradingView webhook formats
            if isinstance(webhook_data, str):
                webhook_data = json.loads(webhook_data)
            
            # Extract signal information
            symbol = webhook_data.get('symbol') or webhook_data.get('ticker') or webhook_data.get('pair')
            action = webhook_data.get('action') or webhook_data.get('side') or webhook_data.get('order')
            entry_price = webhook_data.get('price') or webhook_data.get('entry') or webhook_data.get('close')
            stop_loss = webhook_data.get('stop_loss') or webhook_data.get('sl') or webhook_data.get('stop')
            take_profit = webhook_data.get('take_profit') or webhook_data.get('tp') or webhook_data.get('target')
            lot_size = webhook_data.get('lot_size') or webhook_data.get('quantity') or webhook_data.get('size')
            confidence = webhook_data.get('confidence') or webhook_data.get('strength')
            
            # Validate required fields
            if not symbol or not action:
                logger.warning("Missing required fields: symbol or action")
                return None
            
            # Normalize action
            action = action.upper()
            if action in ['BUY', 'LONG', 'CALL']:
                action = 'BUY'
            elif action in ['SELL', 'SHORT', 'PUT']:
                action = 'SELL'
            else:
                logger.warning(f"Invalid action: {action}")
                return None
            
            # Normalize symbol format
            symbol = symbol.upper().replace('/', '_')
            
            # Convert prices to float
            try:
                entry_price = float(entry_price) if entry_price else None
                stop_loss = float(stop_loss) if stop_loss else None
                take_profit = float(take_profit) if take_profit else None
                lot_size = float(lot_size) if lot_size else 0.01
                confidence = float(confidence) if confidence else 100.0
            except (ValueError, TypeError):
                logger.warning("Invalid numeric values in signal")
                return None
            
            return {
                'symbol': symbol,
                'action': action,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'lot_size': lot_size,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error parsing TradingView signal: {e}")
            return None
    
    def validate_webhook_signature(self, payload, signature, api_key):
        """
        Validate TradingView webhook signature.
        
        Args:
            payload (str): Webhook payload
            signature (str): Webhook signature
            api_key (str): TradingView API key
            
        Returns:
            bool: True if signature is valid
        """
        try:
            import hmac
            import hashlib
            
            # Create expected signature
            expected_signature = hmac.new(
                api_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False
    
    def get_recent_signals(self, limit=10):
        """
        Get recent TradingView signals.
        
        Args:
            limit (int): Number of signals to return
            
        Returns:
            list: List of recent signals
        """
        try:
            with self.app.app_context():
                signals = Signal.query.filter_by(strategy='TRADINGVIEW_SIGNAL')\
                    .order_by(Signal.timestamp.desc())\
                    .limit(limit)\
                    .all()
                
                return [signal.to_dict() for signal in signals]
                
        except Exception as e:
            logger.error(f"Error getting recent TradingView signals: {e}")
            return []
    
    def test_webhook_connection(self, webhook_url, api_key):
        """
        Test TradingView webhook connection.
        
        Args:
            webhook_url (str): TradingView webhook URL
            api_key (str): TradingView API key
            
        Returns:
            dict: Test result
        """
        try:
            # Create test payload
            test_payload = {
                'symbol': 'EUR_USD',
                'action': 'BUY',
                'price': 1.1000,
                'stop_loss': 1.0950,
                'take_profit': 1.1100,
                'test': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send test request
            response = requests.post(
                webhook_url,
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Webhook connection successful',
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'message': f'Webhook failed with status {response.status_code}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Webhook test failed: {str(e)}',
                'status_code': None
            }

def create_tradingview_webhook_handler(app):
    """
    Create TradingView webhook handler for Flask app.
    
    Args:
        app: Flask app instance
        
    Returns:
        function: Webhook handler function
    """
    def tradingview_webhook():
        """Handle TradingView webhook requests"""
        try:
            # Get request data
            if request.is_json:
                webhook_data = request.get_json()
            else:
                webhook_data = request.form.to_dict()
            
            # Get signature for validation
            signature = request.headers.get('X-Signature') or request.headers.get('Signature')
            
            # Log webhook request
            logger.info(f"Received TradingView webhook: {webhook_data}")
            
            # Process signal
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
    
    return tradingview_webhook