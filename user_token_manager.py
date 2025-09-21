#!/usr/bin/env python3
"""
User Token Manager
This module provides functions to manage Discord user tokens in the database.
"""

import logging
from datetime import datetime
from models import db, UserToken
from token_encryption import token_encryption

logger = logging.getLogger(__name__)

class UserTokenManager:
    """Manager class for Discord user tokens"""
    
    @staticmethod
    def save_user_token(user_id, username, token, channel_id=None, channel_name=None, device_fingerprint=None, ip_address=None, user_agent=None):
        """
        Save or update a Discord user token in the database.
        
        Args:
            user_id (str): Discord user ID
            username (str): Discord username
            token (str): Discord token (will be encrypted)
            channel_id (str, optional): Channel ID to monitor
            channel_name (str, optional): Channel name for display
            device_fingerprint (str, optional): Device fingerprint for tracking
            ip_address (str, optional): IP address for tracking
            user_agent (str, optional): Browser user agent
            
        Returns:
            UserToken: The saved token object
        """
        try:
            # Encrypt the token
            encrypted_token = token_encryption.encrypt_token(token)
            if not encrypted_token:
                raise ValueError("Failed to encrypt token")
            
            # Check if token already exists
            existing_token = UserToken.query.filter_by(user_id=user_id).first()
            
            if existing_token:
                # Update existing token
                existing_token.username = username
                existing_token.token = encrypted_token
                existing_token.channel_id = channel_id
                existing_token.channel_name = channel_name
                existing_token.device_fingerprint = device_fingerprint
                existing_token.ip_address = ip_address
                existing_token.user_agent = user_agent
                existing_token.is_active = True
                existing_token.updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Updated token for user {username} ({user_id})")
                return existing_token
            else:
                # Create new token
                new_token = UserToken(
                    user_id=user_id,
                    username=username,
                    token=encrypted_token,
                    channel_id=channel_id,
                    channel_name=channel_name,
                    device_fingerprint=device_fingerprint,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_token)
                db.session.commit()
                logger.info(f"Saved new token for user {username} ({user_id})")
                return new_token
                
        except Exception as e:
            logger.error(f"Error saving user token: {e}")
            db.session.rollback()
            raise
    
    @staticmethod
    def get_user_token(user_id):
        """
        Get a Discord user token from the database.
        
        Args:
            user_id (str): Discord user ID
            
        Returns:
            dict: Token information with decrypted token, or None if not found
        """
        try:
            token_obj = UserToken.query.filter_by(user_id=user_id, is_active=True).first()
            if not token_obj:
                return None
            
            # Decrypt the token
            decrypted_token = token_encryption.decrypt_token(token_obj.token)
            if not decrypted_token:
                logger.error(f"Failed to decrypt token for user {user_id}")
                return None
            
            # Update last used timestamp
            token_obj.last_used = datetime.utcnow()
            db.session.commit()
            
            return {
                'user_id': token_obj.user_id,
                'username': token_obj.username,
                'token': decrypted_token,
                'channel_id': token_obj.channel_id,
                'channel_name': token_obj.channel_name,
                'is_active': token_obj.is_active,
                'last_used': token_obj.last_used,
                'created_at': token_obj.created_at,
                'updated_at': token_obj.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting user token: {e}")
            return None
    
    @staticmethod
    def get_active_tokens():
        """
        Get all active user tokens.
        
        Returns:
            list: List of token information (without decrypted tokens for security)
        """
        try:
            tokens = UserToken.query.filter_by(is_active=True).all()
            return [token.to_dict() for token in tokens]
        except Exception as e:
            logger.error(f"Error getting active tokens: {e}")
            return []
    
    @staticmethod
    def deactivate_token(user_id):
        """
        Deactivate a user token.
        
        Args:
            user_id (str): Discord user ID
            
        Returns:
            bool: True if successfully deactivated
        """
        try:
            token_obj = UserToken.query.filter_by(user_id=user_id).first()
            if token_obj:
                token_obj.is_active = False
                token_obj.updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Deactivated token for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating token: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def delete_token(user_id):
        """
        Permanently delete a user token from the database.
        
        Args:
            user_id (str): Discord user ID
            
        Returns:
            bool: True if successfully deleted
        """
        try:
            token_obj = UserToken.query.filter_by(user_id=user_id).first()
            if token_obj:
                db.session.delete(token_obj)
                db.session.commit()
                logger.info(f"Deleted token for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting token: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def update_channel_info(user_id, channel_id, channel_name):
        """
        Update channel information for a user token.
        
        Args:
            user_id (str): Discord user ID
            channel_id (str): Channel ID to monitor
            channel_name (str): Channel name for display
            
        Returns:
            bool: True if successfully updated
        """
        try:
            token_obj = UserToken.query.filter_by(user_id=user_id).first()
            if token_obj:
                token_obj.channel_id = channel_id
                token_obj.channel_name = channel_name
                token_obj.updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Updated channel info for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating channel info: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_token_by_device_info(device_fingerprint=None, ip_address=None):
        """
        Get user token based on device fingerprint or IP address.
        
        Args:
            device_fingerprint (str): Device fingerprint
            ip_address (str): IP address
            
        Returns:
            dict: Token information with decrypted token, or None if not found
        """
        try:
            query = UserToken.query.filter_by(is_active=True)
            
            if device_fingerprint:
                token_obj = query.filter_by(device_fingerprint=device_fingerprint).first()
            elif ip_address:
                token_obj = query.filter_by(ip_address=ip_address).first()
            else:
                return None
            
            if not token_obj:
                return None
            
            # Decrypt the token
            decrypted_token = token_encryption.decrypt_token(token_obj.token)
            if not decrypted_token:
                logger.error(f"Failed to decrypt token for device {device_fingerprint} or IP {ip_address}")
                return None
            
            # Update last used timestamp
            token_obj.last_used = datetime.utcnow()
            db.session.commit()
            
            return {
                'user_id': token_obj.user_id,
                'username': token_obj.username,
                'token': decrypted_token,
                'channel_id': token_obj.channel_id,
                'channel_name': token_obj.channel_name,
                'is_active': token_obj.is_active,
                'device_fingerprint': token_obj.device_fingerprint,
                'ip_address': token_obj.ip_address,
                'user_agent': token_obj.user_agent,
                'last_used': token_obj.last_used,
                'created_at': token_obj.created_at,
                'updated_at': token_obj.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting token by device info: {e}")
            return None
    
    @staticmethod
    def update_token_info(user_id, username=None, channel_id=None, channel_name=None):
        """
        Update token information without changing the token itself.
        
        Args:
            user_id (str): Discord user ID
            username (str, optional): New username
            channel_id (str, optional): New channel ID
            channel_name (str, optional): New channel name
            
        Returns:
            bool: True if successfully updated
        """
        try:
            token_obj = UserToken.query.filter_by(user_id=user_id).first()
            if token_obj:
                if username is not None:
                    token_obj.username = username
                if channel_id is not None:
                    token_obj.channel_id = channel_id
                if channel_name is not None:
                    token_obj.channel_name = channel_name
                
                token_obj.updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Updated token info for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating token info: {e}")
            db.session.rollback()
            return False
