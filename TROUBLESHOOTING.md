# Troubleshooting Bot Not Responding

## Issue: Bot Online But Not Responding to Messages

If your bot shows as online and loaded all cogs, but doesn't respond to messages:

### ✅ **Quick Fixes:**

1. **Use Command Prefix:**
   - Type `!hello` instead of just `hi`
   - The bot responds to commands starting with `!`
   - Commands: `!help`, `!hello`, `!ping`, etc.

2. **Check Bot Permissions in Channel:**
   - Bot needs "View Channels" permission
   - Bot needs "Send Messages" permission  
   - Bot needs "Read Message History" permission
   - Check channel permissions: Server Settings → Roles → Your Bot Role → Permissions

3. **Verify Message Content Intent:**
   - Go to: https://discord.com/developers/applications
   - Select your application → Bot
   - Scroll to "Privileged Gateway Intents"
   - ✅ **MESSAGE CONTENT INTENT** must be ENABLED
   - Click "Save Changes"
   - **RESTART the bot** after enabling

4. **Check Bot Role Position:**
   - Bot role must be high enough in hierarchy
   - Go to: Server Settings → Roles
   - Drag bot role above member roles
   - Bot role should have same or higher position than members

5. **Verify Bot Can See the Channel:**
   - Make sure bot role has access to the channel
   - Check channel permissions: Right-click channel → Edit Channel → Permissions
   - Ensure bot role can "View Channel"

### 🔍 **Debug Steps:**

1. **Check Bot Logs:**
   ```bash
   # After sending a message, check bot.log
   Get-Content bot.log -Tail 20
   ```
   - Look for "Received message from..." entries
   - If you see them → Bot is receiving messages
   - If not → Bot can't see messages (permissions/intent issue)

2. **Test with Commands:**
   - Type: `!help` - Should show command list
   - Type: `!ping` - Should respond with latency
   - Type: `!hello` - Should greet you

3. **Test Greetings:**
   - Type: `hi` or `hello` (lowercase)
   - Bot should respond (new feature added)

### 🐛 **Common Issues:**

#### Issue 1: "Bot online but no response"
**Solution:** 
- Enable MESSAGE CONTENT INTENT
- Restart bot
- Use `!` prefix for commands

#### Issue 2: "Bot responds to commands but not greetings"
**Solution:**
- Make sure MESSAGE CONTENT INTENT is enabled
- Check bot.log for error messages

#### Issue 3: "Forbidden error in logs"
**Solution:**
- Bot lacks permissions in that channel
- Check channel permissions for bot role
- Verify bot can send messages

### 📋 **Verification Checklist:**

- [ ] Bot shows as online in Discord
- [ ] All cogs loaded successfully (check bot.py output)
- [ ] MESSAGE CONTENT INTENT enabled in Developer Portal
- [ ] Bot has proper permissions in server
- [ ] Bot role has access to the channel
- [ ] Using correct command prefix (`!` by default)
- [ ] Bot role position is high enough
- [ ] Restarted bot after enabling intents

### 🔄 **After Making Changes:**

**ALWAYS restart the bot:**
1. Stop bot (Ctrl+C in terminal)
2. Start again: `python bot.py`
3. Wait for "Bot is ready!" message
4. Test in Discord

### 💡 **Still Not Working?**

1. **Check bot.log for errors:**
   ```bash
   Get-Content bot.log
   ```

2. **Try in different channel:**
   - Sometimes channel-specific permissions block the bot

3. **Verify token is correct:**
   - Check .env file has correct DISCORD_TOKEN

4. **Re-invite bot with all permissions:**
   - Use OAuth2 URL Generator again
   - Select all required permissions
   - Re-invite to server

