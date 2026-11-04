# Firebase Setup Guide for CoconutSMP

This guide will help you set up Firebase for the CoconutSMP dashboard and forms.

## Step 1: Create a Firebase Project

1. Go to [https://console.firebase.google.com/](https://console.firebase.google.com/)
2. Click "Add project" or create a new project
3. Name your project (e.g., "coconutsmp-dashboard")
4. Follow the setup wizard (you can disable Google Analytics for now)
5. Click "Create project"

## Step 2: Get Your Firebase Configuration

1. In your Firebase project, click the gear icon (Project Settings)
2. Scroll down to "Your apps" section
3. Click the web icon (`</>`) to add a web app
4. Give it a name (e.g., "CoconutSMP Website")
5. **Don't** check "Firebase Hosting" for now
6. Click "Register app"
7. Copy the `firebaseConfig` object that appears

## Step 3: Enable Firestore Database

1. In your Firebase project, go to "Build" → "Firestore Database"
2. Click "Create database"
3. Choose a location (select one closest to your users)
4. Start in "Test mode" for development (or production mode with proper rules)
5. Wait for database to be created

## Step 4: Enable Realtime Database (for Chat)

1. In your Firebase project, go to "Build" → "Realtime Database"
2. Click "Create database"
3. Choose a location
4. Start in "Test mode" for development
5. Wait for database to be created

## Step 5: Update Your Files

Replace the `firebaseConfig` object in both `forms.html` and `dashboard.html` with your actual config:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_ACTUAL_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};
```

## Step 6: Set Up Firestore Rules (Security)

In Firestore Database → Rules, use these rules for development:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

For production, you should use more restrictive rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /forms/{document=**} {
      allow create: if true;
      allow read: if request.auth != null;
      allow update, delete: if request.auth != null;
    }
  }
}
```

## Step 7: Set Up Realtime Database Rules

In Realtime Database → Rules, use these rules for development:

```javascript
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

For production:

```javascript
{
  "rules": {
    "chat": {
      ".read": true,
      ".write": "newData.hasChild('message') && newData.child('message').val().length > 0 && newData.child('message').val().length <= 500"
    }
  }
}
```

## Step 8: Test Your Setup

1. Open `forms.html` in your browser
2. Fill out a form and submit it
3. Check the Firebase Console → Firestore Database to see if the submission appears
4. Open `dashboard.html` in your browser
5. Try the chat feature
6. Check the Firebase Console → Realtime Database to see chat messages

## Features Now Working

✅ Forms submit to Firebase Firestore
✅ Chat messages stored in Firebase Realtime Database
✅ Dashboard displays recent form submissions
✅ Real-time chat with NSFW filtering
✅ Player search (demo data - can be connected to Firebase later)

## Optional: Connect Player Search to Firebase

To make player search work with real data from your server:

1. Add a `players` collection to Firestore
2. Store player data like:
   ```javascript
   {
     name: "PlayerName",
     uuid: "player-uuid",
     joined: "2024-01-01",
     lastSeen: "2024-10-26",
     skinUrl: "https://..."
   }
   ```
3. Update the `dashboard.html` player search to query Firestore instead of using mock data

## Security Notes

- Never commit your Firebase config with real API keys to public repositories
- Use environment variables for sensitive data in production
- Implement proper authentication for admin features
- Consider using Firebase Authentication for user login
- Add rate limiting to prevent spam in forms and chat

## Additional Features You Can Add

- Firebase Authentication for user login
- Cloud Functions for form processing
- Firebase Storage for file uploads (screenshots, etc.)
- Firebase Analytics for tracking
- Firebase Crashlytics for error reporting

## Troubleshooting

**Forms not submitting:**
- Check browser console for errors
- Verify Firebase config is correct
- Ensure Firestore is enabled
- Check Firestore rules

**Chat not working:**
- Verify Realtime Database is enabled
- Check Realtime Database rules
- Look for console errors

**Dashboard not showing data:**
- Ensure Firestore has data
- Check if the collection name matches ("forms")
- Verify query is correct

## Support

For Firebase documentation: https://firebase.google.com/docs
For CoconutSMP support: Join our Discord server
