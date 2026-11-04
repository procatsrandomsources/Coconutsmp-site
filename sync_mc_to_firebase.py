"""
Minecraft to Firebase Player Data Sync Script

This script can sync player data from your Minecraft server to Firebase.
Supports multiple methods:
1. RCON Query (basic player info)
2. Database Export (SQLite/MySQL)
3. API Sync (if you have a server API)
"""

import firebase_admin
from firebase_admin import credentials, firestore
import socket
import json
import time
from datetime import datetime
import sqlite3
import mysql.connector

# Firebase Configuration
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "cocodash-6bf2d",
    "private_key_id": "YOUR_PRIVATE_KEY_ID",
    "private_key": "YOUR_PRIVATE_KEY",
    "client_email": "YOUR_CLIENT_EMAIL",
    "client_id": "YOUR_CLIENT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/YOUR_CLIENT_EMAIL"
}

# Minecraft Server Configuration
MC_SERVER = {
    "host": "play.coconutsmp.qzz.io",
    "port": 25575,  # Default RCON port
    "password": "YOUR_RCON_PASSWORD"
}

# Database Configuration (if using database export)
DB_CONFIG = {
    "type": "sqlite",  # or "mysql"
    "path": "path/to/your/server/database.db",  # for SQLite
    "host": "localhost",  # for MySQL
    "user": "username",
    "password": "password",
    "database": "minecraft"
}

class MinecraftFirebaseSync:
    def __init__(self):
        """Initialize Firebase connection"""
        try:
            cred = credentials.Certificate(FIREBASE_CONFIG)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✓ Firebase initialized successfully")
        except Exception as e:
            print(f"✗ Firebase initialization error: {e}")
            self.db = None

    def sync_via_rcon(self):
        """Sync player data using RCON (basic online players)"""
        try:
            # Connect to RCON
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((MC_SERVER["host"], MC_SERVER["port"]))
            
            # Send RCON authentication
            self._send_rcon(sock, 3, MC_SERVER["password"])
            response = self._receive_rcon(sock)
            
            if b"Authenticated" not in response:
                print("✗ RCON authentication failed")
                return False
            
            # Get online players
            self._send_rcon(sock, 2, "list")
            response = self._receive_rcon(sock)
            
            # Parse response and update Firebase
            self._process_rcon_response(response)
            
            sock.close()
            print("✓ RCON sync completed")
            return True
            
        except Exception as e:
            print(f"✗ RCON sync error: {e}")
            return False

    def _send_rcon(self, sock, type, data):
        """Send RCON packet"""
        payload = json.dumps(data).encode('utf-8') if isinstance(data, (dict, list)) else data.encode('utf-8')
        length = len(payload) + 10
        sock.send(length.to_bytes(4, 'little'))
        sock.send(type.to_bytes(4, 'little'))
        sock.send(payload)
        sock.send(b'\x00\x00')

    def _receive_rcon(self, sock):
        """Receive RCON response"""
        length = int.from_bytes(sock.recv(4), 'little')
        type = int.from_bytes(sock.recv(4), 'little')
        payload = sock.recv(length - 8)
        sock.recv(2)  # padding
        return payload

    def _process_rcon_response(self, response):
        """Process RCON response and update Firebase"""
        if not self.db:
            return
        
        # Parse player list (format depends on server)
        # This is a basic example - adjust based on your server's response
        try:
            response_str = response.decode('utf-8')
            players = self._parse_player_list(response_str)
            
            for player in players:
                self._update_player_in_firebase(player)
                
        except Exception as e:
            print(f"✗ Error processing RCON response: {e}")

    def _parse_player_list(self, response):
        """Parse player list from RCON response"""
        # This is a placeholder - adjust based on your server's format
        # Example response: "There are 5 players online: Steve, Alex, Bob, ..."
        players = []
        
        if "players online:" in response:
            player_part = response.split("players online:")[1].strip()
            player_names = [p.strip() for p in player_part.split(",")]
            
            for name in player_names:
                players.append({
                    "name": name,
                    "online": True,
                    "lastSeen": datetime.now().isoformat()
                })
        
        return players

    def sync_via_database(self):
        """Sync player data from server database"""
        try:
            if DB_CONFIG["type"] == "sqlite":
                conn = sqlite3.connect(DB_CONFIG["path"])
            elif DB_CONFIG["type"] == "mysql":
                conn = mysql.connector.connect(
                    host=DB_CONFIG["host"],
                    user=DB_CONFIG["user"],
                    password=DB_CONFIG["password"],
                    database=DB_CONFIG["database"]
                )
            else:
                print("✗ Unsupported database type")
                return False
            
            cursor = conn.cursor()
            
            # Query player data (adjust based on your database schema)
            cursor.execute("""
                SELECT username, playtime, money, rank, last_seen 
                FROM players
            """)
            
            players = cursor.fetchall()
            
            for player in players:
                player_data = {
                    "name": player[0],
                    "playtime": player[1],
                    "money": player[2],
                    "rank": player[3],
                    "lastSeen": player[4].isoformat() if player[4] else datetime.now().isoformat()
                }
                self._update_player_in_firebase(player_data)
            
            conn.close()
            print(f"✓ Synced {len(players)} players from database")
            return True
            
        except Exception as e:
            print(f"✗ Database sync error: {e}")
            return False

    def _update_player_in_firebase(self, player_data):
        """Update player data in Firebase"""
        if not self.db:
            return
        
        try:
            player_ref = self.db.collection('players').document(player_data['name'])
            player_ref.set(player_data, merge=True)
            print(f"  ✓ Updated player: {player_data['name']}")
        except Exception as e:
            print(f"  ✗ Error updating player {player_data['name']}: {e}")

    def sync_server_stats(self):
        """Sync server statistics to Firebase"""
        if not self.db:
            return
        
        try:
            # Get current player count from mcstatus.io
            import requests
            response = requests.get('https://api.mcstatus.io/v2/status/java/play.coconutsmp.qzz.io')
            data = response.json()
            
            if data['online']:
                stats = {
                    "players": data['players']['online'],
                    "max": data['players']['max'],
                    "version": data['version']['name'],
                    "timestamp": int(time.time() * 1000),
                    "date": datetime.now().isoformat()
                }
                
                self.db.collection('server_stats').add(stats)
                print(f"✓ Server stats synced: {stats['players']} players online")
            else:
                print("✗ Server is offline")
                
        except Exception as e:
            print(f"✗ Server stats sync error: {e}")

    def run_sync(self, method="rcon"):
        """Run the sync with specified method"""
        print(f"\n{'='*50}")
        print(f"Starting Minecraft to Firebase Sync")
        print(f"Method: {method}")
        print(f"{'='*50}\n")
        
        if method == "rcon":
            self.sync_via_rcon()
        elif method == "database":
            self.sync_via_database()
        elif method == "api":
            print("API sync not implemented yet")
        
        # Always sync server stats
        self.sync_server_stats()
        
        print(f"\n{'='*50}")
        print(f"Sync completed")
        print(f"{'='*50}\n")


# Manual sync function for existing players
def manual_sync():
    """Manually add/update specific players"""
    sync = MinecraftFirebaseSync()
    
    # Example: Add/update specific players
    players = [
        {
            "name": "Steve",
            "uuid": "8667ba71b85a4004af54457a9714e7e6",
            "playtime": 1250,
            "money": 50000,
            "rank": "Member",
            "joined": "2024-01-01",
            "lastSeen": datetime.now().isoformat()
        },
        {
            "name": "Alex",
            "uuid": "144485f2b9014b60970cb3f9e8b8ef04",
            "playtime": 890,
            "money": 125000,
            "rank": "VIP",
            "joined": "2024-02-15",
            "lastSeen": datetime.now().isoformat()
        }
    ]
    
    for player in players:
        sync._update_player_in_firebase(player)


if __name__ == "__main__":
    # Run sync
    sync = MinecraftFirebaseSync()
    
    # Choose sync method
    # sync.run_sync(method="rcon")      # Use RCON
    # sync.run_sync(method="database")  # Use database export
    # manual_sync()                     # Manual player sync
    
    print("\nUsage:")
    print("1. Edit FIREBASE_CONFIG with your Firebase service account key")
    print("2. Edit MC_SERVER with your RCON credentials")
    print("3. Edit DB_CONFIG with your database settings")
    print("4. Uncomment the sync method you want to use")
    print("5. Run: python sync_mc_to_firebase.py")
