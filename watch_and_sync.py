"""
Watch and Sync Script
Watches the Firebase sync file created by Skript and syncs data to Firebase
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import time
import os
from datetime import datetime

# Firebase Configuration
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "cocodash-6bf2d",
    # Add your service account key fields here
    # Or use a service account JSON file
}

# File to watch
SYNC_FILE = "plugins/FirebaseSync/data.json"

class FileWatcher:
    def __init__(self, file_path):
        self.file_path = file_path
        self.last_modified = 0
        self.db = None
        
        # Initialize Firebase
        try:
            # Option 1: Use service account JSON file
            cred = credentials.Certificate("service-account.json")
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✓ Firebase initialized")
        except:
            try:
                # Option 2: Use config dict
                cred = credentials.Certificate(FIREBASE_CONFIG)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                print("✓ Firebase initialized")
            except Exception as e:
                print(f"✗ Firebase initialization error: {e}")
                print("Please provide a service account key")

    def watch(self):
        """Watch the file for changes"""
        print(f"Watching file: {self.file_path}")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                if os.path.exists(self.file_path):
                    current_modified = os.path.getmtime(self.file_path)
                    
                    if current_modified > self.last_modified:
                        print(f"\n[{datetime.now()}] File changed, syncing...")
                        self.sync_file()
                        self.last_modified = current_modified
                
                time.sleep(1)  # Check every second
                
            except KeyboardInterrupt:
                print("\nStopping watcher...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)

    def sync_file(self):
        """Sync data from file to Firebase"""
        if not self.db:
            print("✗ Firebase not initialized")
            return
        
        try:
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
            
            # Process each line (JSON object)
            for line in lines:
                line = line.strip()
                if not line or line == '[]':
                    continue
                
                try:
                    data = json.loads(line)
                    self.process_data(data)
                except json.JSONDecodeError:
                    print(f"✗ Invalid JSON: {line}")
            
            # Clear file after processing
            with open(self.file_path, 'w') as f:
                f.write('[]')
            
            print("✓ Sync completed, file cleared")
            
        except Exception as e:
            print(f"✗ Error syncing file: {e}")

    def process_data(self, data):
        """Process individual data entry"""
        action = data.get('action')
        
        if action == 'sync':
            self.sync_player(data)
        elif action == 'quit':
            self.update_last_seen(data)
        elif action == 'stats':
            self.sync_server_stats(data)
        else:
            print(f"Unknown action: {action}")

    def sync_player(self, data):
        """Sync player data to Firebase"""
        try:
            player_ref = self.db.collection('players').document(data['name'])
            player_ref.set({
                'name': data['name'],
                'uuid': data['uuid'],
                'playtime': data.get('playtime', 0),
                'money': data.get('money', 0),
                'rank': data.get('rank', 'Member'),
                'joined': data.get('joined', datetime.now().isoformat()),
                'lastSeen': data.get('lastSeen', datetime.now().isoformat()),
                'online': data.get('online', True)
            }, merge=True)
            print(f"  ✓ Synced player: {data['name']}")
        except Exception as e:
            print(f"  ✗ Error syncing player {data['name']}: {e}")

    def update_last_seen(self, data):
        """Update player last seen"""
        try:
            player_ref = self.db.collection('players').document(data['name'])
            player_ref.update({
                'lastSeen': data.get('lastSeen', datetime.now().isoformat()),
                'online': False
            })
            print(f"  ✓ Updated last seen: {data['name']}")
        except Exception as e:
            print(f"  ✗ Error updating last seen for {data['name']}: {e}")

    def sync_server_stats(self, data):
        """Sync server statistics"""
        try:
            self.db.collection('server_stats').add({
                'players': data.get('players', 0),
                'max': data.get('max', 0),
                'timestamp': data.get('timestamp', int(time.time() * 1000)),
                'date': data.get('date', datetime.now().isoformat())
            })
            print(f"  ✓ Server stats: {data.get('players')} players online")
        except Exception as e:
            print(f"  ✗ Error syncing server stats: {e}")


if __name__ == "__main__":
    print("="*50)
    print("Firebase File Watcher - CoconutSMP")
    print("="*50)
    
    # Check if file exists
    if not os.path.exists(SYNC_FILE):
        print(f"⚠ File not found: {SYNC_FILE}")
        print("Make sure the Skript is running and has created the file")
        print("The file will be created at: plugins/FirebaseSync/data.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(SYNC_FILE), exist_ok=True)
        
        # Create empty file
        with open(SYNC_FILE, 'w') as f:
            f.write('[]')
        
        print(f"✓ Created empty file: {SYNC_FILE}")
    
    # Start watcher
    watcher = FileWatcher(SYNC_FILE)
    watcher.watch()
