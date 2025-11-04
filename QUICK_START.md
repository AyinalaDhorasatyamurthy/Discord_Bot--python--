# Quick Start Guide - OAuth2 Permissions

## 🔐 **SECURITY WARNING**
⚠️ **You've shared your bot token publicly!** After testing:
1. Go to Discord Developer Portal[https://discord.com/developers/applications](https://discord.com/developers/applications) → Bot → Reset Token
2. Update `.env` with the new token
3. Never share tokens publicly!

---

## 📋 OAuth2 Permissions Checklist

### **Go to:** [Discord Developer Portal](https://discord.com/developers/applications) → Your Application → OAuth2 → URL Generator

### **STEP 1: Select SCOPES**
- ✅ Check **`bot`**
- ✅ Check **`applications.commands`**

### **STEP 2: Select BOT PERMISSIONS**

Copy and check each of these:

#### **📝 TEXT PERMISSIONS (Required for basic commands):**
```
☑ Send Messages
☑ Manage Messages
☑ Embed Links
☑ Attach Files
☑ Read Message History
```

#### **🔊 VOICE PERMISSIONS (Required for music commands):**
```
☑ Connect
☑ Speak
☑ Use Voice Activity
```

#### **🛡️ MODERATION PERMISSIONS (Required for moderation commands):**
```
☑ Kick Members
☑ Ban Members
☑ Moderate Members
```

#### **👁️ GENERAL PERMISSIONS (Required for bot to function):**
```
☑ View Channels
```

### **STEP 3: Copy the Generated URL**

The URL at the bottom will look like:
```
https://discord.com/api/oauth2/authorize?client_id=...
```

### **STEP 4: Open URL & Authorize**

1. Paste URL in browser
2. Select your server
3. Click "Authorize"
4. Complete CAPTCHA if needed

---

## ✅ **Also Enable These Intents:**

**Go to:** [Discord Developer Portal](https://discord.com/developers/applications) → Your Application → Bot → Scroll to "Privileged Gateway Intents"

- ✅ **SERVER MEMBERS INTENT** (Enable this!)
- ✅ **MESSAGE CONTENT INTENT** (Enable this!)
- ⚪ PRESENCE INTENT (Optional)

---

## 🚀 **After Inviting:**

1. **Run the bot:**
   ```bash
   python bot.py
   ```

2. **Test it:**
   - Type `!hello` in Discord
   - Bot should respond!

3. **See all commands:**
   - Type `!help`

---

## 📊 **Permission Summary:**

**Minimum for basic bot:** 8 permissions
**Full functionality:** 12 permissions (as listed above)

**All features will work with these permissions selected!**

