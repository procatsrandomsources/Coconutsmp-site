# Minecraft to Firebase Data Sync Guide

This guide explains how to transfer player data from your Minecraft server to Firebase for the CoconutSMP dashboard.

## 🎯 What Can Be Synced

- ✅ Player names and UUIDs
- ✅ Playtime (hours/minutes)
- ✅ Economy money
- ✅ Player ranks
- ✅ Last seen timestamp
- ✅ Join date
- ✅ Server statistics (player count, uptime)

## 🔧 Setup Methods

### Method 1: RCON Sync (Simplest)

**Best for:** Basic player list and online status

**Requirements:**
- RCON enabled on your server
- RCON password
- Python installed

**Setup:**

1. **Enable RCON on your server:**
   - Edit `server.properties`:
     ```
     enable-rcon=true
     rcon.port=25575
     rcon.password=your_password
     broadcast-rcon-to-ops=true
     ```

2. **Configure the sync script:**
   - Edit `sync_mc_to_firebase.py`
   - Update `MC_SERVER` with your RCON credentials
   - Get Firebase service account key (see below)

3. **Get Firebase Service Account Key:**
   - Go to Firebase Console → Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Download JSON file
   - Update `FIREBASE_CONFIG` in the script

4. **Run the sync:**
   ```bash
   python sync_mc_to_firebase.py
   ```

**Limitations:**
- ❌ Can't get economy data (unless your RCON plugin supports it)
- ❌ Can't get playtime history
- ❌ Only works when server is online

---

### Method 2: Database Export (Most Complete)

**Best for:** One-time migration of all player data

**Requirements:**
- Access to server database (SQLite or MySQL)
- Database credentials
- Python installed

**Setup:**

1. **Locate your server database:**
   - SQLite: Usually in `world/` folder as `world.db` or similar
   - MySQL: Need host, user, password, database name

2. **Identify your database schema:**
   - Common plugins store data in different tables
   - Examples:
     - EssentialsX: `essentials_userdata`, `essentials_economy`
     - Vault: `vault_data`
     - Custom plugins: Check documentation

3. **Configure the sync script:**
   - Edit `sync_mc_to_firebase.py`
   - Update `DB_CONFIG` with your database settings
   - Update the SQL query to match your schema

4. **Run the sync:**
   ```bash
   python sync_mc_to_firebase.py
   ```

**Example SQL Queries for Common Plugins:**

**EssentialsX:**
```sql
SELECT 
    uuid as uuid,
    'lastlogin' as lastSeen,
    'totalplaytime' as playtime,
    money as money
FROM essentials_userdata
JOIN essentials_economy ON essentials_userdata.uuid = essentials_economy.uuid
```

**LuckPerms (Ranks):**
```sql
SELECT 
    uuid,
    permission as rank
FROM luckperms_permissions
WHERE permission LIKE '%rank%'
```

---

### Method 3: Plugin with Webhook (Real-time) ⭐ RECOMMENDED

**Best for:** Real-time automatic sync

**Options:**

#### Option A: Use Existing Plugins

**WebSend Plugin:**
- Sends HTTP requests when events happen
- Can sync: Player join/leave, economy changes, rank changes
- Install: https://www.spigotmc.org/resources/websend.27621/

**DiscordSRV (for Discord sync + webhooks):**
- Already has webhook support
- Can be extended to send to Firebase
- Install: https://www.spigotmc.org/resources/discordsrv.18494/

#### Option B: Custom Simple Plugin

Create a simple plugin that sends data to Firebase when players join/leave.

**Basic plugin structure:**
```java
public class FirebaseSync extends JavaPlugin {
    @Override
    public void onEnable() {
        // Listen for player events
        getServer().getPluginManager().registerEvents(new PlayerListener(), this);
    }
}

class PlayerListener implements Listener {
    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        // Send player data to Firebase via HTTP
        syncPlayerToFirebase(event.getPlayer());
    }
    
    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent event) {
        // Update last seen
        updateLastSeen(event.getPlayer());
    }
}
```

#### Option C: Use PlaceholderAPI + WebSend

1. Install PlaceholderAPI
2. Install WebSend
3. Configure webhooks to send on player events

**Example WebSend config:**
```yaml
# WebSend config.yml
webhooks:
  firebase:
    url: "https://your-firebase-function-url.com/player"
    events:
      - PLAYER_JOIN
      - PLAYER_QUIT
    data:
      name: "%player_name%"
      uuid: "%player_uuid%"
      playtime: "%stat_time_played%"
      money: "%vault_eco_balance%"
      rank: "%vault_rank%"
```

---

### Method 4: Server API (If Available)

Some servers have built-in APIs or you can run a REST API plugin.

**Example using a simple API plugin:**

1. Install a REST API plugin like:
   - [Minecraft-REST-API](https://github.com/Gamebridge/minecraft-rest-api)
   - [BlueBotsAPI](https://www.spigotmc.org/resources/bluebotsapi.82730/)

2. Configure API to expose player data

3. Use the sync script to fetch from API instead of database

---

## 🚀 Quick Start (Recommended Path)

### For Immediate Results (Demo):

Use the manual sync in `seed_firebase.html`:
1. Open `seed_firebase.html` in browser
2. Click "Seed Sample Players"
3. Dashboard will show data immediately

### For Real Player Data:

**Step 1: Get Service Account Key**
```
Firebase Console → Project Settings → Service Accounts → Generate New Private Key
```

**Step 2: Choose Sync Method**

**If you have RCON access:**
- Use Method 1 (RCON)
- Best for: Online player count, basic player list

**If you have database access:**
- Use Method 2 (Database Export)
- Best for: Complete data migration, economy, playtime

**If you want real-time sync:**
- Use Method 3 (Plugin with Webhook)
- Best for: Automatic updates as players play

**Step 3: Configure and Run**

Edit `sync_mc_to_firebase.py` with your config:
```python
FIREBASE_CONFIG = {
    # Paste your service account key JSON here
}

MC_SERVER = {
    "host": "your-server-ip",
    "port": 25575,
    "password": "your-rcon-password"
}
```

Run:
```bash
pip install firebase-admin mysql-connector-python requests
python sync_mc_to_firebase.py
```

---

## 📊 Firebase Data Structure

After sync, your Firebase will have:

### `players` collection:
```javascript
{
  name: "PlayerName",
  uuid: "uuid-here",
  playtime: 1250,        // in minutes
  money: 50000,          // economy balance
  rank: "Member",
  joined: "2024-01-01",
  lastSeen: "2024-10-26T12:00:00Z"
}
```

### `server_stats` collection:
```javascript
{
  players: 45,
  max: 100,
  version: "1.20.4",
  timestamp: 1234567890,
  date: "2024-10-26T12:00:00Z"
}
```

---

## 🔒 Security Best Practices

1. **Never commit service account keys** to public repositories
2. **Use environment variables** for sensitive data
3. **Limit RCON access** to trusted IPs only
4. **Use Firebase Security Rules** to protect data
5. **Validate data** before syncing to Firebase

---

## 🛠️ Troubleshooting

### "Firebase initialization error"
- Check service account key is correct
- Verify project ID matches
- Ensure internet connection

### "RCON connection failed"
- Check RCON is enabled in server.properties
- Verify port and password are correct
- Check firewall allows RCON port

### "Database connection failed"
- Verify database file path (SQLite)
- Check MySQL credentials
- Ensure database server is running

### "No data synced"
- Check if players exist in database
- Verify SQL query matches your schema
- Check console for errors

---

## 📈 Automation

### Cron Job (Linux/Mac):
```bash
# Sync every 5 minutes
*/5 * * * * cd /path/to/script && python sync_mc_to_firebase.py
```

### Task Scheduler (Windows):
- Create task to run script every 5 minutes
- Set action to run `python sync_mc_to_firebase.py`

### Real-time with Plugin:
- Install WebSend plugin
- Configure webhooks
- No scheduling needed - automatic!

---

## 🎯 Which Method Should You Use?

| Method | Difficulty | Real-time | Data Completeness | Recommended For |
|--------|-----------|-----------|-------------------|-----------------|
| RCON | Easy | Partial | Basic | Quick start, basic stats |
| Database Export | Medium | No | Complete | One-time migration |
| Plugin/Webhook | Hard | Yes | Complete | Production, automatic |
| API | Medium | Yes | Varies | Custom setups |

**For CoconutSMP:**
1. **Start with:** Manual seed (seed_firebase.html) for demo
2. **Then:** Database export for initial data
3. **Finally:** Plugin with webhook for real-time sync

---

## 📞 Help

- **Firebase Docs**: https://firebase.google.com/docs
- **Minecraft Plugin Development**: https://www.spigotmc.org/wiki/
- **WebSend Plugin**: https://www.spigotmc.org/resources/websend.27621/

---

## ✅ Checklist

- [ ] Get Firebase service account key
- [ ] Choose sync method
- [ ] Configure sync script
- [ ] Test sync with small dataset
- [ ] Run full sync
- [ ] Verify data in Firebase Console
- [ ] Check dashboard displays data
- [ ] Set up automation (if needed)
- [ ] Monitor sync performance
