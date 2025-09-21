# 🚂 Railway Deployment Guide

এই guide টি আপনাকে Railway platform এ MT5 Bot deploy করতে সাহায্য করবে।

## 📋 Prerequisites

1. **Railway Account**: [railway.app](https://railway.app) এ account তৈরি করুন
2. **GitHub Repository**: আপনার code GitHub এ push করা থাকতে হবে
3. **API Keys**: OANDA, Discord, TradingView API keys প্রস্তুত রাখুন

## 🚀 Step-by-Step Deployment

### Step 1: Railway Account Setup
1. [railway.app](https://railway.app) এ যান
2. "Login" ক্লিক করুন
3. GitHub account দিয়ে login করুন
4. Railway dashboard এ যান

### Step 2: New Project Create
1. Railway dashboard এ "New Project" ক্লিক করুন
2. "Deploy from GitHub repo" select করুন
3. আপনার `mt5bot` repository select করুন
4. "Deploy Now" ক্লিক করুন

### Step 3: Environment Variables Setup
Railway dashboard এ আপনার project এ যান এবং "Variables" tab এ যান। নিচের variables add করুন:

#### Required Variables:
```
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=sqlite:///instance/trading_bot.db
```

#### OANDA Configuration:
```
OANDA_ACCOUNT_ID=your-oanda-account-id
OANDA_API_KEY=your-oanda-api-key
OANDA_ENVIRONMENT=practice
```

#### Discord Configuration (Optional):
```
DISCORD_TOKEN=your-discord-bot-token
DISCORD_CHANNEL_ID=your-discord-channel-id
```

#### TradingView Configuration (Optional):
```
TRADINGVIEW_WEBHOOK_SECRET=your-webhook-secret
```

#### Trading Settings:
```
AUTO_TRADING_ENABLED=true
MAX_CONCURRENT_TRADES=5
RISK_PER_TRADE=2.0
```

#### Security:
```
ENCRYPTION_KEY=your-32-character-encryption-key-here
```

### Step 4: Database Setup
1. Railway dashboard এ "Add Service" ক্লিক করুন
2. "Database" select করুন
3. "PostgreSQL" select করুন (recommended)
4. Database service add করুন
5. Database URL copy করুন
6. Environment variables এ `DATABASE_URL` update করুন

**Note**: SQLite production environment এ recommended নয়। PostgreSQL ব্যবহার করুন।

### Step 5: Deploy
1. Railway automatically আপনার code deploy করবে
2. "Deployments" tab এ progress monitor করুন
3. Deployment complete হলে "View Logs" ক্লিক করুন
4. Logs check করুন যে সব কিছু ঠিক আছে

### Step 6: Domain Setup
1. Railway automatically একটি domain provide করবে
2. "Settings" tab এ যান
3. "Domains" section এ custom domain add করতে পারেন
4. Domain copy করুন এবং browser এ test করুন

## 🔧 Configuration Tips

### Database Configuration
- Railway এ PostgreSQL বা MySQL ব্যবহার করুন
- SQLite production environment এ recommended নয়
- Database URL format: `postgresql://username:password@host:port/database`

### Security Configuration
- Strong SECRET_KEY ব্যবহার করুন
- API keys secure রাখুন
- Environment variables এ sensitive data store করুন

### Performance Optimization
- `AUTO_TRADING_ENABLED=true` set করুন
- `MAX_CONCURRENT_TRADES` limit করুন
- Log level `INFO` রাখুন

## 📊 Monitoring

### Railway Dashboard
- **Deployments**: Deployment status check করুন
- **Logs**: Real-time logs দেখুন
- **Metrics**: CPU, Memory usage monitor করুন
- **Variables**: Environment variables manage করুন

### Application Monitoring
- Web dashboard: `https://your-app.railway.app`
- Health check: `https://your-app.railway.app/api/account`
- Trading status: Dashboard এ check করুন

## 🚨 Troubleshooting

### Common Issues:

1. **Pandas Installation Error**
   - **Solution**: Pandas dependency removed from requirements.txt
   - **Reason**: Python 3.13 এর সাথে pandas 2.1.1 compatible নয়
   - **Status**: ✅ Fixed - pandas not used in the application

2. **Six Module Missing Error**
   - **Solution**: Added `six==1.16.0` to requirements.txt
   - **Reason**: oandapyV20 requires six module
   - **Status**: ✅ Fixed - six dependency added

3. **Deployment Failed**
   - Logs check করুন
   - Environment variables verify করুন
   - Requirements.txt check করুন

4. **Database Connection Error**
   - DATABASE_URL check করুন
   - Database service running আছে কিনা check করুন
   - PostgreSQL URL format: `postgresql://user:pass@host:port/db`

5. **API Keys Not Working**
   - Environment variables এ correct keys আছে কিনা check করুন
   - API keys valid আছে কিনা verify করুন

6. **Trading Not Working**
   - OANDA credentials check করুন
   - AUTO_TRADING_ENABLED=true আছে কিনা check করুন

### Debug Commands:
```bash
# Logs check করুন
railway logs

# Environment variables check করুন
railway variables

# Database connect করুন
railway connect
```

## 🔄 Updates

### Code Update:
1. GitHub এ code push করুন
2. Railway automatically redeploy করবে
3. New deployment check করুন

### Configuration Update:
1. Railway dashboard এ variables update করুন
2. Service restart করুন
3. Changes verify করুন

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: আপনার repository এ issue create করুন

## ✅ Success Checklist

- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] Environment variables set
- [ ] Database configured
- [ ] Application deployed
- [ ] Domain accessible
- [ ] Trading bot working
- [ ] Dashboard accessible

---

**Happy Deploying! 🚂🚀**
