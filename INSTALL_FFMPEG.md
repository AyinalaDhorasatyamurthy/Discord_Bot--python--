# How to Install ffmpeg (Required for Music)

## ❌ **Error: ffmpeg Not Found**

Your system doesn't have ffmpeg installed. Music commands won't work without it.

---

## 🔽 **Quick Installation (Windows):**

### **Option 1: Download Pre-built Binary (Easiest)**

1. **Download:**
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download: **"ffmpeg-release-essentials.zip"**
   - (Direct link: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)

2. **Extract:**
   - Extract the zip file
   - You'll get a folder like `ffmpeg-6.x.x-essentials_build`

3. **Option A: Add to PATH (Recommended)**
   - Copy the path to `bin` folder (e.g., `C:\ffmpeg-6.x.x-essentials_build\bin`)
   - Search Windows for "Environment Variables"
   - Click "Environment Variables" button
   - Under "System variables", find "Path" → Click "Edit"
   - Click "New" → Paste the `bin` folder path
   - Click OK on all dialogs
   - **Restart your terminal/bot**

4. **Option B: Place in Project Folder (Easier)**
   - Copy `ffmpeg.exe` from the `bin` folder
   - Paste it in your project folder: `C:\Users\ASUS\OneDrive\Documents\discord_prj\`
   - Rename to exactly: `ffmpeg.exe`
   - **Restart your bot**

### **Option 2: Using Chocolatey (If You Have It)**

```powershell
choco install ffmpeg
```

### **Option 3: Using Scoop (If You Have It)**

```powershell
scoop install ffmpeg
```

---

## ✅ **Verify Installation:**

After installation, run in terminal:

```bash
ffmpeg -version
```

You should see version information. If you get an error, ffmpeg is not installed correctly.

---

## 🎵 **After Installing:**

1. **Restart your bot:**
   ```bash
   python bot.py
   ```

2. **Test music:**
   ```
   !play Never Gonna Give You Up
   ```
   or
   ```
   !play https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

---

## 📝 **Quick Steps Summary:**

1. Download: https://www.gyan.dev/ffmpeg/builds/
2. Extract zip
3. Copy `ffmpeg.exe` to project folder OR add to PATH
4. Restart bot
5. Test with `!play song name`

---

## ⚠️ **Note:**

- Without ffmpeg, music commands will always fail
- ffmpeg is required for audio processing
- It's free and safe to download
- Takes ~30 seconds to install

