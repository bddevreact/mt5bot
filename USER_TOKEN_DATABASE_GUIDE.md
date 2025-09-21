# User Token Database Implementation

## Overview

This implementation adds SQLite database support for storing Discord user tokens securely. Instead of storing tokens in `.env` files, tokens are now encrypted and stored in the SQLite database with proper management capabilities.

## Features

### 🔐 **Secure Token Storage**
- Tokens are encrypted using AES encryption before storage
- Uses PBKDF2 key derivation for enhanced security
- Tokens are never stored in plain text

### 📊 **Database Management**
- SQLite database integration with existing trading bot
- UserToken model with comprehensive fields
- Automatic database table creation

### 🎛️ **Management Interface**
- Web dashboard integration for token management
- Command-line tools for token operations
- API endpoints for programmatic access

### 🔄 **Seamless Integration**
- Backward compatibility with existing bot functionality
- Automatic token loading from database
- Fallback mechanisms for error handling

## Database Schema

### UserToken Table
```sql
CREATE TABLE user_token (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,     -- Discord user ID
    username VARCHAR(100),                   -- Discord username
    token TEXT NOT NULL,                     -- Encrypted Discord token
    channel_id VARCHAR(50),                  -- Monitored channel ID
    channel_name VARCHAR(100),              -- Channel name for display
    is_active BOOLEAN DEFAULT TRUE,          -- Whether token is active
    last_used DATETIME,                      -- Last time token was used
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Files Added/Modified

### New Files
- `token_encryption.py` - Token encryption/decryption utilities
- `user_token_manager.py` - Database operations for user tokens
- `view_user_tokens.py` - Command-line token viewer
- `manage_user_tokens.py` - Interactive token management
- `test_user_token_database.py` - Test suite for the implementation

### Modified Files
- `models.py` - Added UserToken model
- `app.py` - Added API endpoints and database initialization
- `setup_user_bot.py` - Updated to use database instead of .env
- `user_discord_bot.py` - Updated to load tokens from database
- `templates/dashboard.html` - Added token management interface
- `requirements.txt` - Added cryptography dependency

## API Endpoints

### User Token Management
- `GET /api/user_tokens` - Get all active tokens
- `POST /api/user_tokens` - Save new token
- `GET /api/user_tokens/<user_id>` - Get specific token
- `POST /api/user_tokens/<user_id>/deactivate` - Deactivate token
- `DELETE /api/user_tokens/<user_id>` - Delete token permanently

## Usage

### 1. Setup User Token
```bash
python setup_user_bot.py
```
- Interactive setup process
- Token validation and encryption
- Database storage

### 2. View Tokens
```bash
python view_user_tokens.py
```
- Display all saved tokens
- Show token status and usage

### 3. Manage Tokens
```bash
python manage_user_tokens.py
```
- Interactive token management
- Add, deactivate, delete tokens
- Update channel information

### 4. Start Bot
```bash
python user_discord_bot.py
```
- Loads token from database
- Automatic token decryption
- Channel monitoring

### 5. Web Dashboard
- Access `http://localhost:5000`
- View and manage tokens in browser
- Real-time token status

## Security Features

### Encryption
- **Algorithm**: AES-256-GCM
- **Key Derivation**: PBKDF2 with SHA-256
- **Salt**: Fixed salt for consistency
- **Iterations**: 100,000 iterations

### Token Masking
- Tokens are masked in API responses
- Only last 4 characters shown
- Full tokens only available during decryption

### Access Control
- Database-level access control
- Token deactivation capabilities
- Permanent deletion option

## Configuration

### Environment Variables
```env
# Optional: Custom encryption password
ENCRYPTION_PASSWORD=your_custom_password

# Database configuration (existing)
DATABASE_URL=sqlite:///trading_bot.db
```

### Default Settings
- Encryption password: `default_trading_bot_password`
- Database: `trading_bot.db` (SQLite)
- Token masking: Last 4 characters visible

## Migration from .env

### Before (Old Method)
```env
DISCORD_TOKEN=your_token_here
DISCORD_CHANNEL_ID=channel_id_here
```

### After (New Method)
- Tokens stored in database
- Encrypted with AES-256
- Managed through web interface or CLI tools

## Error Handling

### Common Issues
1. **No tokens found**: Run `setup_user_bot.py`
2. **Decryption failed**: Check encryption password
3. **Database locked**: Ensure no other processes are using the database
4. **Invalid token format**: Verify Discord token format

### Troubleshooting
```bash
# Test the implementation
python test_user_token_database.py

# Check database
python view_user_tokens.py

# Reset tokens
python manage_user_tokens.py
```

## Benefits

### ✅ **Enhanced Security**
- Encrypted token storage
- No plain text tokens in files
- Secure key derivation

### ✅ **Better Management**
- Multiple token support
- Web-based management
- Command-line tools

### ✅ **Improved Reliability**
- Database transactions
- Error handling
- Fallback mechanisms

### ✅ **User Experience**
- Interactive setup
- Visual dashboard
- Real-time status

## Testing

### Run Test Suite
```bash
python test_user_token_database.py
```

### Test Coverage
- Token encryption/decryption
- Database operations
- User token manager
- API endpoints
- Error handling

## Future Enhancements

### Planned Features
- Multiple token support per user
- Token rotation capabilities
- Audit logging
- Backup/restore functionality
- Token expiration handling

### Integration Opportunities
- Discord bot token management
- OANDA API key storage
- General credential management

## Support

### Documentation
- This file: Complete implementation guide
- Code comments: Inline documentation
- API docs: Endpoint documentation

### Help Commands
```bash
python setup_user_bot.py --help
python manage_user_tokens.py --help
python view_user_tokens.py --help
```

## Conclusion

The user token database implementation provides a secure, manageable, and user-friendly way to store Discord tokens. It integrates seamlessly with the existing trading bot while providing enhanced security and management capabilities.

**Key Benefits:**
- 🔐 Secure encrypted storage
- 🎛️ Easy management interface
- 🔄 Seamless integration
- 📊 Comprehensive monitoring
- 🛠️ Multiple management tools
