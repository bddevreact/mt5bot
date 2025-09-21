# User Discord Bot Guide

## 🤖 What is a User Discord Bot?

A User Discord Bot logs in with **YOUR Discord account** (not a separate bot account) and fetches signals from channels you have access to. This solves the problem when you can't invite a regular bot to a channel.

## ⚠️ Important Warnings

- **Using self-bots is against Discord Terms of Service**
- **Use at your own risk**
- **Never share your user token with anyone**
- **Only use for personal trading signals**

## 🔧 Setup Instructions

### Step 1: Get Your Discord User Token

1. Open Discord in your web browser (not the app)
2. Press `F12` to open Developer Tools
3. Go to the `Network` tab
4. Send any message in Discord
5. Look for a request to `discord.com/api`
6. In the request headers, find `authorization`
7. Copy the token (it starts with your user ID)

### Step 2: Get Channel ID

1. Right-click on the Discord channel name
2. Select "Copy Channel ID"
3. Paste it when prompted

### Step 3: Run Setup

```bash
python setup_user_bot.py
```

### Step 4: Start the Bot

```bash
python user_discord_bot.py
```

Or double-click: `start_user_bot.bat`

## 📝 Supported Signal Formats

The bot can parse these signal formats:

```
BUY EUR_USD @ 1.1000 SL: 1.0950 TP: 1.1100
SELL GBP_USD @ 1.2500 STOP: 1.2550 TARGET: 1.2400
LONG EUR_USD 1.1000 1.0950 1.1100
SHORT GBP_USD 1.2500 1.2550 1.2400
```

## 🎯 How It Works

1. **Bot logs in with your Discord account**
2. **Monitors the specified channel**
3. **Detects trading signals automatically**
4. **Parses signal data (symbol, action, prices)**
5. **Saves signals to database**
6. **Executes trades when auto-trading is enabled**

## 🔄 Integration with Trading Bot

The user bot works with your existing trading bot:

1. **User bot fetches signals** → Database
2. **Trading bot processes signals** → OANDA
3. **Trades are executed** → Your account

## 🛠️ Files Created

- `user_discord_bot.py` - Main user bot script
- `setup_user_bot.py` - Setup configuration
- `start_user_bot.bat` - Windows batch file
- `USER_BOT_GUIDE.md` - This guide

## 🚀 Quick Start

1. Run: `python setup_user_bot.py`
2. Enter your Discord user token
3. Enter the channel ID
4. Run: `python user_discord_bot.py`
5. Enable auto-trading: `python trading_control.py`

## 🔍 Troubleshooting

### Bot can't connect
- Check your user token is correct
- Make sure you're using web browser token, not app token

### No signals detected
- Check channel ID is correct
- Make sure you're a member of that channel
- Verify signal format matches examples

### Signals not executing
- Check auto-trading is enabled
- Verify OANDA credentials are correct
- Check bot logs for errors

## 📊 Monitoring

Use these scripts to monitor the bot:

- `python view_pending_signals.py` - See pending signals
- `python bot_status.py` - Check overall bot status
- `python check_signals.py` - View all signals

## 🎉 Benefits

✅ **Works with any Discord channel you have access to**
✅ **No need to invite bots to servers**
✅ **Automatic signal detection and parsing**
✅ **Integrates with existing trading bot**
✅ **Real-time signal processing**

## ⚖️ Legal Notice

This tool is for educational and personal use only. Users are responsible for complying with Discord's Terms of Service and applicable laws. The developers are not responsible for any misuse of this software.
