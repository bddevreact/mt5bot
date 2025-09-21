#!/usr/bin/env python3
"""
Configuration Manager
This module provides functions to manage TradingView and OANDA configurations in the database.
"""

import logging
from datetime import datetime
from models import db, TradingViewConfig, OANDAConfig
from token_encryption import token_encryption

logger = logging.getLogger(__name__)

class TradingViewConfigManager:
    """Manager class for TradingView configurations"""
    
    @staticmethod
    def save_tradingview_config(user_id, username, api_key, webhook_url=None, device_fingerprint=None, ip_address=None, user_agent=None):
        """
        Save or update a TradingView configuration in the database.
        
        Args:
            user_id (str): User identifier
            username (str): Display name
            api_key (str): TradingView API key (will be encrypted)
            webhook_url (str, optional): TradingView webhook URL
            device_fingerprint (str, optional): Device fingerprint
            ip_address (str, optional): IP address
            user_agent (str, optional): Browser user agent
            
        Returns:
            TradingViewConfig: The saved config object
        """
        try:
            # Encrypt the API key
            encrypted_api_key = token_encryption.encrypt_token(api_key)
            if not encrypted_api_key:
                raise ValueError("Failed to encrypt API key")
            
            # Check if config already exists
            existing_config = TradingViewConfig.query.filter_by(user_id=user_id).first()
            
            if existing_config:
                # Update existing config
                existing_config.username = username
                existing_config.api_key = encrypted_api_key
                existing_config.webhook_url = webhook_url
                existing_config.device_fingerprint = device_fingerprint
                existing_config.ip_address = ip_address
                existing_config.user_agent = user_agent
                existing_config.is_active = True
                existing_config.updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Updated TradingView config for user {username} ({user_id})")
                return existing_config
            else:
                # Create new config
                new_config = TradingViewConfig(
                    user_id=user_id,
                    username=username,
                    api_key=encrypted_api_key,
                    webhook_url=webhook_url,
                    device_fingerprint=device_fingerprint,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_config)
                db.session.commit()
                logger.info(f"Saved new TradingView config for user {username} ({user_id})")
                return new_config
                
        except Exception as e:
            logger.error(f"Error saving TradingView config: {e}")
            db.session.rollback()
            raise
    
    @staticmethod
    def get_tradingview_config(user_id):
        """
        Get a TradingView configuration from the database.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            dict: Config information with decrypted API key, or None if not found
        """
        try:
            config_obj = TradingViewConfig.query.filter_by(user_id=user_id, is_active=True).first()
            if not config_obj:
                return None
            
            # Decrypt the API key
            decrypted_api_key = token_encryption.decrypt_token(config_obj.api_key)
            if not decrypted_api_key:
                logger.error(f"Failed to decrypt API key for user {user_id}")
                return None
            
            # Update last used timestamp
            config_obj.last_used = datetime.utcnow()
            db.session.commit()
            
            return {
                'user_id': config_obj.user_id,
                'username': config_obj.username,
                'api_key': decrypted_api_key,
                'webhook_url': config_obj.webhook_url,
                'is_active': config_obj.is_active,
                'device_fingerprint': config_obj.device_fingerprint,
                'ip_address': config_obj.ip_address,
                'user_agent': config_obj.user_agent,
                'last_used': config_obj.last_used,
                'created_at': config_obj.created_at,
                'updated_at': config_obj.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting TradingView config: {e}")
            return None
    
    @staticmethod
    def get_active_configs():
        """
        Get all active TradingView configurations.
        
        Returns:
            list: List of config information (without decrypted API keys for security)
        """
        try:
            configs = TradingViewConfig.query.filter_by(is_active=True).all()
            return [config.to_dict() for config in configs]
        except Exception as e:
            logger.error(f"Error getting active TradingView configs: {e}")
            return []

class OANDAConfigManager:
    """Manager class for OANDA configurations"""
    
    @staticmethod
    def save_oanda_config(user_id, username, account_id, account_name, api_key, environment='practice', device_fingerprint=None, ip_address=None, user_agent=None):
        """
        Save or update an OANDA configuration in the database.
        
        Args:
            user_id (str): User identifier
            username (str): Display name
            account_id (str): OANDA account ID
            account_name (str): Display name for account
            api_key (str): OANDA API key (will be encrypted)
            environment (str): practice or live
            device_fingerprint (str, optional): Device fingerprint
            ip_address (str, optional): IP address
            user_agent (str, optional): Browser user agent
            
        Returns:
            OANDAConfig: The saved config object
        """
        try:
            # Encrypt the API key
            encrypted_api_key = token_encryption.encrypt_token(api_key)
            if not encrypted_api_key:
                raise ValueError("Failed to encrypt API key")
            
            # Check if config already exists
            existing_config = OANDAConfig.query.filter_by(user_id=user_id).first()
            
            if existing_config:
                # Update existing config
                existing_config.username = username
                existing_config.account_id = account_id
                existing_config.account_name = account_name
                existing_config.api_key = encrypted_api_key
                existing_config.environment = environment
                existing_config.device_fingerprint = device_fingerprint
                existing_config.ip_address = ip_address
                existing_config.user_agent = user_agent
                existing_config.is_active = True
                existing_config.updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Updated OANDA config for user {username} ({user_id})")
                return existing_config
            else:
                # Create new config
                new_config = OANDAConfig(
                    user_id=user_id,
                    username=username,
                    account_id=account_id,
                    account_name=account_name,
                    api_key=encrypted_api_key,
                    environment=environment,
                    device_fingerprint=device_fingerprint,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_config)
                db.session.commit()
                logger.info(f"Saved new OANDA config for user {username} ({user_id})")
                return new_config
                
        except Exception as e:
            logger.error(f"Error saving OANDA config: {e}")
            db.session.rollback()
            raise
    
    @staticmethod
    def get_oanda_config(user_id):
        """
        Get an OANDA configuration from the database.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            dict: Config information with decrypted API key, or None if not found
        """
        try:
            config_obj = OANDAConfig.query.filter_by(user_id=user_id, is_active=True).first()
            if not config_obj:
                return None
            
            # Decrypt the API key
            decrypted_api_key = token_encryption.decrypt_token(config_obj.api_key)
            if not decrypted_api_key:
                logger.error(f"Failed to decrypt API key for user {user_id}")
                return None
            
            # Update last used timestamp
            config_obj.last_used = datetime.utcnow()
            db.session.commit()
            
            return {
                'user_id': config_obj.user_id,
                'username': config_obj.username,
                'account_id': config_obj.account_id,
                'account_name': config_obj.account_name,
                'api_key': decrypted_api_key,
                'environment': config_obj.environment,
                'is_active': config_obj.is_active,
                'device_fingerprint': config_obj.device_fingerprint,
                'ip_address': config_obj.ip_address,
                'user_agent': config_obj.user_agent,
                'last_used': config_obj.last_used,
                'created_at': config_obj.created_at,
                'updated_at': config_obj.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting OANDA config: {e}")
            return None
    
    @staticmethod
    def get_all_oanda_accounts():
        """
        Get all OANDA account configurations for dropdown.
        
        Returns:
            list: List of account configurations
        """
        try:
            configs = OANDAConfig.query.filter_by(is_active=True).all()
            return [config.to_dict() for config in configs]
        except Exception as e:
            logger.error(f"Error getting OANDA accounts: {e}")
            return []
    
    @staticmethod
    def get_oanda_config_by_account(account_id):
        """
        Get OANDA configuration by account ID.
        
        Args:
            account_id (str): OANDA account ID
            
        Returns:
            dict: Config information with decrypted API key, or None if not found
        """
        try:
            config_obj = OANDAConfig.query.filter_by(account_id=account_id, is_active=True).first()
            if not config_obj:
                return None
            
            # Decrypt the API key
            decrypted_api_key = token_encryption.decrypt_token(config_obj.api_key)
            if not decrypted_api_key:
                logger.error(f"Failed to decrypt API key for account {account_id}")
                return None
            
            # Update last used timestamp
            config_obj.last_used = datetime.utcnow()
            db.session.commit()
            
            return {
                'user_id': config_obj.user_id,
                'username': config_obj.username,
                'account_id': config_obj.account_id,
                'account_name': config_obj.account_name,
                'api_key': decrypted_api_key,
                'environment': config_obj.environment,
                'is_active': config_obj.is_active,
                'device_fingerprint': config_obj.device_fingerprint,
                'ip_address': config_obj.ip_address,
                'user_agent': config_obj.user_agent,
                'last_used': config_obj.last_used,
                'created_at': config_obj.created_at,
                'updated_at': config_obj.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting OANDA config by account: {e}")
            return None
