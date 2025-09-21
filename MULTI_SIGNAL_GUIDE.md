# 📡 Multi Signal Trading Bot Guide

## 🎯 **Complete Solution: Discord + TradingView + Manual Signals**

Your trading bot now supports signals from **multiple sources**:

### ✅ **Supported Signal Sources:**
- **Discord Channels** 📡
- **TradingView** 📊
- **Manual Input** ✍️

## 🚀 **Quick Start:**

### **Method 1: Multi Signal Processor (Recommended)**
```bash
python multi_signal_processor.py
```
Or double-click: `multi_signals.bat`

### **Method 2: TradingView Only**
```bash
python tradingview_signal_fetcher.py
```
Or double-click: `tradingview_signals.bat`

## 📝 **Supported Signal Formats:**

### **Discord Signals:**
```
BUY EUR_USD @ 1.1000 SL: 1.0950 TP: 1.1100
SELL GBP_USD @ 1.2500 STOP: 1.2550 TARGET: 1.2400
LONG EURUSD 1.1000 1.0950 1.1100
SHORT GBPUSD 1.2500 1.2550 1.2400
```

### **TradingView Signals:**
```
BUY EURUSD @ 1.1000 SL: 1.0950 TP: 1.1100
SELL GBPUSD @ 1.2500 STOP: 1.2550 TARGET: 1.2400
LONG EURUSD 1.1000 1.0950 1.1100
SHORT GBPUSD 1.2500 1.2550 1.2400
```

### **Manual Signals:**
```
BUY EUR_USD @ 1.1000 SL: 1.0950 TP: 1.1100
SELL GBP_USD @ 1.2500 STOP: 1.2550 TARGET: 1.2400
```

## 🔄 **How It Works:**

```
Discord Channel → Multi Signal Processor → Database → Trading Bot → OANDA
TradingView → Multi Signal Processor → Database → Trading Bot → OANDA
Manual Input → Multi Signal Processor → Database → Trading Bot → OANDA
```

## 🎯 **Workflow:**

1. **Get Signal** from any source (Discord/TradingView/Manual)
2. **Run**: `python multi_signal_processor.py`
3. **Choose source** (Discord/TradingView/Manual)
4. **Paste/Type signal**
5. **Bot processes** and saves to database
6. **Auto trading executes** (if enabled)

## 🛠️ **Available Tools:**

| Tool | Purpose |
|------|---------|
| `multi_signal_processor.py` | Process signals from all sources |
| `tradingview_signal_fetcher.py` | TradingView specific signals |
| `trading_control.py` | Enable/disable auto trading |
| `view_pending_signals.py` | See pending signals |
| `bot_status.py` | Check overall status |

## 📊 **Signal Processing:**

### **Automatic Features:**
- ✅ **Signal parsing** (symbol, action, prices)
- ✅ **Stop loss/Take profit** (auto-calculated if not provided)
- ✅ **Database storage**
- ✅ **Source tracking** (Discord/TradingView/Manual)
- ✅ **Auto trading integration**

### **Supported Symbols:**
- **Major Pairs**: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD
- **Minor Pairs**: EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, CAD_JPY
- **Exotic Pairs**: EUR_AUD, EUR_CAD, EUR_CHF, EUR_NZD
- **All formats**: EUR_USD, EURUSD (both supported)

## 🎛️ **Control Options:**

### **Enable Auto Trading:**
```bash
python trading_control.py
```

### **View Recent Signals:**
```bash
python view_pending_signals.py
```

### **Check Bot Status:**
```bash
python bot_status.py
```

## 🔍 **Example Usage:**

### **Discord Signal:**
1. Copy signal from Discord: `BUY EUR_USD @ 1.1000 SL: 1.0950 TP: 1.1100`
2. Run: `python multi_signal_processor.py`
3. Choose: `1. Discord Signal`
4. Paste signal
5. Bot processes and executes

### **TradingView Signal:**
1. Get signal from TradingView: `SELL GBPUSD @ 1.2500 STOP: 1.2550 TARGET: 1.2400`
2. Run: `python multi_signal_processor.py`
3. Choose: `2. TradingView Signal`
4. Paste signal
5. Bot processes and executes

### **Manual Signal:**
1. Run: `python multi_signal_processor.py`
2. Choose: `3. Manual Signal`
3. Type signal: `LONG EURUSD 1.1000 1.0950 1.1100`
4. Bot processes and executes

## 🎉 **Benefits:**

✅ **Multiple signal sources**
✅ **No token setup needed**
✅ **Automatic signal parsing**
✅ **Source tracking**
✅ **Auto trading integration**
✅ **Risk management** (SL/TP)
✅ **Real-time execution**

## 🚀 **Ready to Use:**

Your trading bot is now ready to process signals from:
- **Discord channels** (copy-paste)
- **TradingView** (copy-paste or webhook)
- **Manual input** (type directly)

**Start trading with multiple signal sources!** 🎯



