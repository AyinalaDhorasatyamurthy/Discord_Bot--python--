# Discord Bot Permissions Guide

## ⚠️ IMPORTANT SECURITY NOTE
**You've shared your bot token publicly. After testing, you should:**
1. Go to Discord Developer Portal → Your Bot → Reset Token
2. Generate a new token
3. Update your `.env` file with the new token
4. Never share tokens publicly again!

---

## Required Permissions for OAuth2 URL Generator

### Step-by-Step Instructions:

1. **Go to Discord Developer Portal:**
   - Visit: https://discord.com/developers/applications
   - Select your application

2. **Navigate to OAuth2 → URL Generator**

3. **Select Scopes:**
   - ✅ **bot** (Required - allows bot to join server)
   - ✅ **applications.commands** (Recommended - for slash commands support)

4. **Select Bot Permissions (Check these boxes):**

   **Text Permissions:**
   - ✅ **Send Messages** (Required - bot needs to respond)
   - ✅ **Manage Messages** (Required - for purge command, deleting messages)
   - ✅ **Embed Links** (Required - for rich embeds in responses)
   - ✅ **Attach Files** (Required - for file attachments)
   - ✅ **Read Message History** (Required - to read commands and messages)
   - ✅ **Use External Emojis** (Optional - for better emoji support)
   - ✅ **Add Reactions** (Optional - for reaction features)

   **Voice Permissions (for music commands):**
   - ✅ **Connect** (Required - join voice channels)
   - ✅ **Speak** (Required - play music/audio)
   - ✅ **Use Voice Activity** (Required - for voice features)
   - ⚪ **Priority Speaker** (Optional - not required)

   **Moderation Permissions:**
   - ✅ **Kick Members** (Required - for !kick command)
   - ✅ **Ban Members** (Required - for !ban command)
   - ✅ **Moderate Members** (Required - for !timeout command)
   - ⚪ **Manage Roles** (Optional - for role management)
   - ⚪ **Manage Channels** (Optional - for channel management)
   - ⚪ **Manage Server** (Optional - for advanced server management)

   **General Permissions:**
   - ✅ **View Channels** (Required - bot needs to see channels)
   - ⚪ **Manage Events** (Optional - for event management)

5. **Copy the Generated URL:**
   - The URL will look like: `https://discord.com/api/oauth2/authorize?client_id=...&permissions=...&scope=bot%20applications.commands`
   - Copy this entire URL

6. **Open the URL in Your Browser:**
   - Paste the URL in your browser
   - Select the server where you want to add the bot
   - Click "Authorize"
   - Complete any CAPTCHA if prompted

---

## Permission Summary (Quick Checklist)

### ✅ **ESSENTIAL PERMISSIONS (Minimum Required):**
- [ ] bot (scope)
- [ ] applications.commands (scope)
- [ ] Send Messages
- [ ] Embed Links
- [ ] Read Message History
- [ ] View Channels

### ✅ **FOR MUSIC COMMANDS:**
- [ ] Connect
- [ ] Speak
- [ ] Use Voice Activity

### ✅ **FOR MODERATION COMMANDS:**
- [ ] Manage Messages
- [ ] Kick Members
- [ ] Ban Members
- [ ] Moderate Members

### ⚪ **OPTIONAL (Nice to Have):**
- [ ] Attach Files
- [ ] Add Reactions
- [ ] Use External Emojis
- [ ] Manage Roles
- [ ] Manage Channels

---

## Permission Value Explanation

When you select all required permissions, you'll see a permission number at the bottom (like `294879126592`). This is the calculated permission value.

**For a fully functional bot with all features, you need:**
- **Permission Integer:** `294879127040` (approximate)
- **Or select individual permissions as listed above**

---

## After Inviting the Bot

1. **Check Bot Intents in Developer Portal:**
   - Go to Bot section
   - Scroll down to "Privileged Gateway Intents"
   - Enable:
     - ✅ **SERVER MEMBERS INTENT** (Required - for member tracking)
     - ✅ **MESSAGE CONTENT INTENT** (Required - to read message content)
     - ⚪ **PRESENCE INTENT** (Optional - for presence tracking)

2. **Verify Bot Joined:**
   - Check your Discord server member list
   - The bot should appear offline initially

3. **Run the Bot:**
   ```bash
   python bot.py
   ```
   - The bot should come online
   - Try `!hello` in a channel the bot can see

---

## Troubleshooting Permission Issues

### Bot doesn't respond to commands:
- ✅ Check "Message Content Intent" is enabled
- ✅ Verify bot has "Read Message History" permission
- ✅ Check bot role position (should be high enough to interact)

### Music commands don't work:
- ✅ Verify "Connect" and "Speak" permissions
- ✅ Check bot has access to voice channel
- ✅ Ensure bot role can see the voice channel

### Moderation commands fail:
- ✅ Verify kick/ban/moderate permissions
- ✅ Check bot role is higher than member roles
- ✅ Ensure bot has proper channel permissions

### Can't see bot in server:
- ✅ Verify bot was successfully invited
- ✅ Check bot has "View Channels" permission
- ✅ Verify bot role has access to channels

---

## Quick Permission URL Generator Alternative

You can also use this format manually (replace `YOUR_BOT_ID` with your actual bot ID):

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=294879127040&scope=bot%20applications.commands
```

To find your Bot ID:
1. Go to Developer Portal → Your Application → General Information
2. Copy the "Application ID"
3. Or check the "Bot" section for "User ID"

---

## Need Help?

If permissions aren't working:
1. Re-invite the bot with updated permissions
2. Check bot role hierarchy in server settings
3. Verify intents are enabled in Developer Portal
4. Check bot logs for error messages

