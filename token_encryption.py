#!/usr/bin/env python3
"""
Token Encryption Utility
This module provides encryption and decryption for Discord tokens stored in the database.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class TokenEncryption:
    def __init__(self, password=None):
        """
        Initialize token encryption with a password.
        If no password is provided, uses a default key from environment.
        """
        if password is None:
            password = os.getenv('ENCRYPTION_PASSWORD', 'default_trading_bot_password')
        
        # Generate key from password
        salt = b'trading_bot_salt_2024'  # Fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher_suite = Fernet(key)
    
    def encrypt_token(self, token):
        """
        Encrypt a Discord token for storage.
        
        Args:
            token (str): The Discord token to encrypt
            
        Returns:
            str: Encrypted token as base64 string
        """
        try:
            if not token:
                return None
            
            encrypted_token = self.cipher_suite.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted_token).decode()
        except Exception as e:
            logger.error(f"Error encrypting token: {e}")
            return None
    
    def decrypt_token(self, encrypted_token):
        """
        Decrypt a Discord token from storage.
        
        Args:
            encrypted_token (str): The encrypted token as base64 string
            
        Returns:
            str: Decrypted Discord token
        """
        try:
            if not encrypted_token:
                return None
            
            encrypted_data = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted_token = self.cipher_suite.decrypt(encrypted_data)
            return decrypted_token.decode()
        except Exception as e:
            logger.error(f"Error decrypting token: {e}")
            return None
    
    def is_encrypted(self, token):
        """
        Check if a token is already encrypted.
        
        Args:
            token (str): Token to check
            
        Returns:
            bool: True if token appears to be encrypted
        """
        try:
            # Try to decode as base64 and decrypt
            encrypted_data = base64.urlsafe_b64decode(token.encode())
            self.cipher_suite.decrypt(encrypted_data)
            return True
        except:
            return False

# Global instance for easy use
token_encryption = TokenEncryption()
