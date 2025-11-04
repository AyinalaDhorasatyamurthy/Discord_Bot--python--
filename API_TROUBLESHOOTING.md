# API Troubleshooting Guide

## 🔴 **OpenAI API Rate Limit Issues**

### Error: "Rate limit exceeded"

**What it means:**
- Your OpenAI API account has hit its usage limits
- Free tier accounts have strict rate limits
- You've made too many requests too quickly

### Solutions:

1. **Wait and Retry:**
   - Wait 30-60 seconds between requests
   - The bot now has a 30-second cooldown between AI commands

2. **Check Your Usage:**
   - Visit: https://platform.openai.com/usage
   - Check your remaining credits/quota
   - Free tier has limited usage

3. **Check Your Account:**
   - Visit: https://platform.openai.com/account/billing
   - Ensure you have credits/balance
   - Free tier may have expired

4. **Reduce Token Usage:**
   - The bot now uses fewer tokens per request
   - Commands are limited to 30 seconds apart

5. **Upgrade if Needed:**
   - If you need more usage, upgrade your OpenAI plan
   - Visit: https://platform.openai.com/account/billing

---

## 🌤️ **Weather API Issues**

### Error: "Invalid API key"

**What it means:**
- API key needs activation time
- Key might be incorrect
- Account might not be verified

### Solutions:

1. **Wait for Activation:**
   - New API keys need **10 minutes to 2 hours** to activate
   - Check your email for verification

2. **Verify Your Key:**
   - Visit: https://home.openweathermap.org/api_keys
   - Make sure your key matches exactly
   - Copy it again if needed

3. **Check Email:**
   - OpenWeatherMap sends verification emails
   - Click the verification link

4. **Test Your Key:**
   - Visit: https://openweathermap.org/api
   - Try the API key in their documentation
   - If it works there, wait for activation in your bot

5. **Common Issues:**
   - Extra spaces in the key → Remove them
   - Key copied incorrectly → Re-copy from dashboard
   - Account not verified → Check email

---

## 📊 **Current Bot Cooldowns**

- **AI Commands (`!ask`, `!chat`)**: 30 seconds between uses
- **Weather Command**: 10 seconds between uses
- **Meme Command**: 5 seconds between uses

These cooldowns help prevent rate limiting.

---

## 💡 **Best Practices**

1. **Wait Between Requests:**
   - Don't spam commands
   - Respect the cooldown timers

2. **Monitor Usage:**
   - Check your API usage regularly
   - OpenAI: https://platform.openweathermap.org/usage
   - Weather: https://home.openweathermap.org/api_keys (shows usage)

3. **Free Tier Limits:**
   - OpenAI free tier: Very limited (usually $5 credit that expires)
   - Weather free tier: 1,000 calls/day (more than enough)

4. **If Rate Limited:**
   - Wait at least 1 minute before trying again
   - Check your account balance/usage
   - Consider upgrading if you need more

---

## 🔧 **Quick Fixes**

### For OpenAI Rate Limits:
```bash
# Wait 60 seconds, then try again
# Check your balance at: https://platform.openai.com/account/billing
```

### For Weather API:
```bash
# Wait 1-2 hours for key activation
# Verify your key at: https://home.openweathermap.org/api_keys
```

---

## 📞 **Need Help?**

- **OpenAI Support**: https://help.openai.com/
- **Weather Support**: https://openweathermap.org/appid
- Check the bot logs: `bot.log` file

