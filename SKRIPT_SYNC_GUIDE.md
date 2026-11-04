# Skript Firebase Sync Guide

Complete guide for syncing Minecraft player data to Firebase using Skript + SkBee.

## 🎯 Overview

Three different approaches are provided:

1. **firebase_sync.sk** - Basic sync (requires HTTP addon)
2. **firebase_sync_webhook.sk** - Webhook-based sync
3. **firebase_sync_file.sk + watch_and_sync.py** - File-based sync (RECOMMENDED)

## 📦 Requirements

### Server-Side (Minecraft):
- Skript (latest version)
- SkBee (for NBT and features)
- Vault (for economy integration)
- Optional: TuSKe or skUtilities (for HTTP requests)

### Local Machine (for file-based sync):
- Python 3.x
- Firebase Admin SDK
- Service account key

## 🚀 Method 1: File-Based Sync (RECOMMENDED) ⭐

This is the easiest and most reliable method. Skript writes to a file, Python watches it and syncs to Firebase.

### Step 1: Install Skript on Your Server

1. Download Skript: https://github.com/SkriptLang/Skript/releases
2. Download SkBee: https://github.com/bastos-org/skbee/releases
3. Download Vault: https://github.com/MilkBowl/Vault/releases
4. Place JAR files in `plugins/` folder
5. Restart server

### Step 2: Install Skript File

1. Copy `firebase_sync_file.sk` to `plugins/Skript/scripts/`
2. Rename to `firebase_sync.sk` (or keep as is)
3. Type `/sk reload firebase_sync` in-game or reload server

### Step 3: Configure Options

Edit the options in the Skript:
```skript
options:
    sync::file: plugins/FirebaseSync/data.json
    sync::on-join: true        # Sync when player joins
    sync::on-quit: true        # Sync when player quits
    sync::interval: 5          # Auto-sync every 5 minutes
    sync::enable: true         # Enable/disable sync
```

### Step 4: Set Up Python Watcher

1. Get Firebase service account key:
   - Firebase Console → Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Download JSON file
   - Rename to `service-account.json`
   - Place in same folder as `watch_and_sync.py`

2. Install Python dependencies:
```bash
pip install firebase-admin
```

3. Run the watcher:
```bash
python watch_and_sync.py
```

### Step 5: Test

1. Join your Minecraft server
2. Check the Python console - it should show sync messages
3. Check Firebase Console → Firestore → players collection
4. Player data should appear!

### Commands (In-Game):

- `/firebase-sync` - Sync your data
- `/firebase-sync-all` - Sync all online players (Admin)
- `/firebase-toggle` - Enable/disable sync (Admin)
- `/firebase-status` - View sync status

## 🔧 Method 2: Webhook-Based Sync

Requires a webhook endpoint to receive data and sync to Firebase.

### Setup:

1. Copy `firebase_sync_webhook.sk` to `plugins/Skript/scripts/`
2. Set up a webhook endpoint (Firebase Cloud Function or simple server)
3. Configure `webhook::url` option
4. Requires HTTP addon (TuSKe or skUtilities)

### Note:
This method is more complex but allows for server-side processing of data before syncing.

## 🌐 Method 3: Direct HTTP Sync

Requires an HTTP addon for Skript.

### Setup:

1. Copy `firebase_sync.sk` to `plugins/Skript/scripts/`
2. Install TuSKe or skUtilities for HTTP support
3. Configure Firebase API options
4. Skript sends HTTP requests directly to Firebase

### Note:
Firebase API requires authentication which is complex to implement in Skript. Not recommended unless you have HTTP addon experience.

## 📊 Data Being Synced

The Skript syncs the following data:

- **Player Name**: Minecraft username
- **UUID**: Player UUID
- **Playtime**: Total playtime in minutes
- **Money**: Economy balance (requires Vault)
- **Rank**: Player rank (requires permission plugin)
- **Joined**: First join date
- **Last Seen**: Last login/quit time
- **Online**: Current online status

## 🔒 Security Considerations

1. **Never commit service account keys** to public repositories
2. **Limit who can use sync commands** (set permissions)
3. **Use rate limiting** if using webhook approach
4. **Validate data** before syncing to Firebase
5. **Monitor sync logs** for errors

## 🛠️ Troubleshooting

### "File not found" error
- Make sure `plugins/FirebaseSync/` directory exists
- The Python script will create it automatically
- Check file path in options

### "Firebase not initialized" error
- Verify service account key is present
- Check key is named `service-account.json`
- Ensure Python Firebase Admin SDK is installed

### "Skript not syncing"
- Check if sync is enabled: `/firebase-status`
- Verify Skript reloaded: `/sk reload firebase_sync`
- Check console for errors
- Ensure Vault is installed for economy data

### "Python watcher not syncing"
- Verify file path is correct
- Check Firebase credentials
- Ensure service account key is valid
- Check Python console for errors

## 📈 Automation

### Keep Python Watcher Running

**Windows:**
```bash
python watch_and_sync.py
```

**Linux (with nohup):**
```bash
nohup python watch_and_sync.py > sync.log 2>&1 &
```

**Linux (with screen/tmux):**
```bash
screen -S firebase-sync
python watch_and_sync.py
# Press Ctrl+A then D to detach
```

### Auto-start on Boot

**Windows (Task Scheduler):**
- Create task to run Python script on startup
- Set action to: `python watch_and_sync.py`
- Set working directory to script location

**Linux (systemd):**
Create `/etc/systemd/system/firebase-sync.service`:
```ini
[Unit]
Description=Firebase Sync Watcher
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/script
ExecStart=/usr/bin/python3 /path/to/watch_and_sync.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable firebase-sync
sudo systemctl start firebase-sync
```

## 🎯 Recommended Setup

For CoconutSMP, I recommend:

1. **Use Method 1 (File-based sync)** - Most reliable
2. **Run Python watcher** on your hosting machine or local PC
3. **Enable sync on join/quit** for immediate updates
4. **Set interval to 5 minutes** for periodic sync
5. **Monitor logs** occasionally for errors

## 📝 Customization

### Add More Data Fields

Edit the Skript to sync additional data:
```skript
# Add these to the JSON
set {_kills} to %stat_player_kills% of player
set {_deaths} to %stat_player_deaths% of player
set {_level} to %player's level%
```

### Sync Plugin-Specific Data

For plugins like EssentialsX, LuckPerms, etc.:

```skript
# EssentialsX playtime
set {_essentials-playtime} to {essentials::%player's uuid%::playtime}

# LuckPerms rank
set {_luckperms-rank} to luckperms rank of player
```

## 🔗 Integration with Dashboard

Once data is syncing:
1. Open dashboard.html
2. Player search will show real data
3. Stats will be accurate
4. Graphs will populate with historical data

## ✅ Checklist

- [ ] Install Skript and SkBee on server
- [ ] Install Vault for economy
- [ ] Copy firebase_sync_file.sk to server
- [ ] Configure sync options
- [ ] Get Firebase service account key
- [ ] Install Python Firebase Admin SDK
- [ ] Run watch_and_sync.py
- [ ] Test with player join/quit
- [ ] Verify data in Firebase Console
- [ ] Check dashboard displays data
- [ ] Set up auto-start for Python watcher

## 📞 Help

- **Skript Docs**: https://docs.skriptlang.org/
- **SkBee Docs**: https://docs.skbee.net/
- **Firebase Admin SDK**: https://firebase.google.com/docs/admin/setup
- **Vault Docs**: https://github.com/MilkBowl/Vault/wiki

## 🎉 Summary

The file-based sync method (Method 1) is:
- ✅ Easy to set up
- ✅ Reliable
- ✅ No HTTP complications
- ✅ Works with any Skript setup
- ✅ Easy to debug
- ✅ Can run on any machine

Start with Method 1, and if you need more advanced features, consider the webhook approach later!
