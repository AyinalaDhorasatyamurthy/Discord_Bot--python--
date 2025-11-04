# Music Player Usage Guide

## 🎵 **How to Use Music Commands**

### **Prerequisites:**
1. **Join a Voice Channel** - You MUST be in a voice channel first!
2. **Bot Permissions** - Bot needs "Connect" and "Speak" permissions
3. **ffmpeg** - Must be installed (see below)

---

## 🎮 **Step-by-Step Usage:**

### **1. Join a Voice Channel:**
- In Discord, join any voice channel (General, Music, etc.)
- You must be IN the voice channel before using music commands

### **2. Play Music:**

#### **Option A: By Song Name**
```
!play Never Gonna Give You Up
!play Bohemian Rhapsody
!play Imagine Dragons Believer
```

#### **Option B: By YouTube URL**
```
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
!play https://youtu.be/dQw4w9WgXcQ
```

#### **Option C: By YouTube Playlist**
```
!play https://www.youtube.com/playlist?list=PLxxxxxx
```

### **3. Control Playback:**

```
!pause      # Pause the current song
!resume     # Resume playback
!skip       # Skip to next song
!stop       # Stop and disconnect bot
```

### **4. View Queue:**

```
!queue      # See what's playing and what's next
```

---

## 📋 **Complete Command List:**

| Command | Usage | Description |
|---------|-------|-------------|
| `!play [song/URL]` | `!play song name` | Play music from YouTube |
| `!pause` | `!pause` | Pause current song |
| `!resume` | `!resume` | Resume playback |
| `!stop` | `!stop` | Stop and disconnect |
| `!skip` | `!skip` | Skip current song |
| `!queue` | `!queue` | View music queue |

---

## ⚙️ **Setup Required:**

### **Install ffmpeg (Required for Audio):**

#### **Windows:**
1. Download: https://www.gyan.dev/ffmpeg/builds/
2. Download "ffmpeg-release-essentials.zip"
3. Extract to `C:\ffmpeg` (or any folder)
4. Add to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" system variable
   - Add: `C:\ffmpeg\bin`
   - Restart terminal/bot

#### **Alternative (Easier):**
- Place `ffmpeg.exe` in your project folder: `discord_prj\ffmpeg.exe`
- Bot will find it automatically

### **Verify ffmpeg Installation:**
```bash
ffmpeg -version
```
If you see version info, it's installed correctly!

---

## 🎯 **Example Usage:**

### **Scenario 1: Play a Song**
```
1. You join "General" voice channel
2. You type: !play Never Gonna Give You Up
3. Bot joins channel and plays the song
4. Everyone in voice channel hears the music!
```

### **Scenario 2: Create a Queue**
```
1. !play Song 1
2. !play Song 2
3. !play Song 3
4. !queue (to see all 3 songs)
```

### **Scenario 3: Control Playback**
```
1. !play music
2. !pause (music pauses)
3. !resume (music continues)
4. !skip (next song plays)
5. !stop (bot leaves voice channel)
```

---

## ❌ **Common Issues:**

### **"You need to be in a voice channel"**
- **Solution:** Join a voice channel first, then use `!play`

### **"I don't have permission"**
- **Solution:** Bot needs "Connect" and "Speak" permissions
- Re-invite bot with proper permissions

### **"ffmpeg not found"**
- **Solution:** Install ffmpeg (see setup above)
- Make sure it's in PATH or project folder

### **Music Doesn't Play**
- Check bot is in voice channel (green icon)
- Check bot has "Speak" permission
- Verify ffmpeg is installed

---

## 💡 **Tips:**

1. **Queue Management:**
   - Add multiple songs with `!play` multiple times
   - They'll play in order
   - Use `!queue` to see what's coming

2. **Voice Channel:**
   - Bot must be in SAME voice channel as you
   - If you move channels, use `!stop` then `!play` again

3. **Multiple Users:**
   - Anyone in the voice channel can control playback
   - Use `!skip` if you don't like a song

4. **Stopping Music:**
   - `!stop` - Stops music and disconnects bot
   - `!pause` - Just pauses (can resume)

---

## 🎶 **Where to Use It:**

### **Best Places:**
- 🔊 **Voice Channels** (General, Music, Gaming)
- 🎮 **Gaming Servers** (background music)
- 🎵 **Music Servers** (dedicated music channel)
- 🎉 **Party Channels** (play music during events)

### **How It Works:**
1. Bot joins voice channel
2. Plays audio through voice channel
3. Everyone in that channel hears the music
4. Like a DJ in your Discord server!

---

## 📝 **Quick Reference:**

```
# Start playing
!play song name

# Control
!pause
!resume  
!skip
!stop

# Info
!queue
```

**Remember: You MUST be in a voice channel first!**

