// Seed Firebase with initial player data
// Run this in browser console or as a standalone script
// First, load Firebase SDK in your HTML or include this script after Firebase is loaded

// Firebase SDK
const firebaseScript = document.createElement('script');
firebaseScript.src = 'https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js';
document.head.appendChild(firebaseScript);

const firestoreScript = document.createElement('script');
firestoreScript.src = 'https://www.gstatic.com/firebasejs/9.22.0/firebase-firestore-compat.js';
document.head.appendChild(firestoreScript);

// Wait for scripts to load
firebaseScript.onload = function() {
    firestoreScript.onload = function() {
        initSeeding();
    };
};

function initSeeding() {
    const firebaseConfig = {
    apiKey: "AIzaSyD3kXUbpPL7IEB41pYssJx-6vP4-VGr2sU",
    authDomain: "cocodash-6bf2d.firebaseapp.com",
    projectId: "cocodash-6bf2d",
    storageBucket: "cocodash-6bf2d.firebasestorage.app",
    messagingSenderId: "599890056838",
    appId: "1:599890056838:web:ee6c4c6c7aa6ebf30c6307",
    measurementId: "G-DXVHTKNJWX"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Sample player data
const samplePlayers = [
    {
        name: 'Steve',
        uuid: '8667ba71b85a4004af54457a9714e7e6',
        joined: '2024-01-01',
        lastSeen: new Date().toISOString(),
        playtime: 1250,
        rank: 'Member'
    },
    {
        name: 'Alex',
        uuid: '144485f2b9014b60970cb3f9e8b8ef04',
        joined: '2024-02-15',
        lastSeen: new Date(Date.now() - 86400000).toISOString(),
        playtime: 890,
        rank: 'VIP'
    },
    {
        name: 'CoconutKing',
        uuid: 'c12b5f3d6e8a4b2c9d1f8e7a6b5c4d3e',
        joined: '2024-03-20',
        lastSeen: new Date().toISOString(),
        playtime: 2100,
        rank: 'Admin'
    },
    {
        name: 'Procat999',
        uuid: 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6',
        joined: '2024-04-10',
        lastSeen: new Date().toISOString(),
        playtime: 1560,
        rank: 'Moderator'
    },
    {
        name: 'Ray8921',
        uuid: 'f1e2d3c4b5a697886950413276543210',
        joined: '2024-05-05',
        lastSeen: new Date(Date.now() - 172800000).toISOString(),
        playtime: 750,
        rank: 'Member'
    }
];

// Add players to Firestore
async function seedPlayers() {
    console.log('Seeding players...');
    
    for (const player of samplePlayers) {
        try {
            await db.collection('players').doc(player.name).set(player);
            console.log(`Added player: ${player.name}`);
        } catch (error) {
            console.error(`Error adding player ${player.name}:`, error);
        }
    }
    
    console.log('Done seeding players!');
}

// Create indexes for better search performance
async function createIndexes() {
    console.log('Note: You may need to create indexes manually in Firebase Console');
    console.log('Go to: Firestore Database -> Indexes -> Create Index');
    console.log('Collection: players');
    console.log('Fields: name (ascending)');
}

// Run seeding
seedPlayers().then(() => {
    createIndexes();
});

// Function to add a new player
window.addPlayer = async function(name, uuid, rank = 'Member') {
    const player = {
        name: name,
        uuid: uuid,
        joined: new Date().toISOString(),
        lastSeen: new Date().toISOString(),
        playtime: 0,
        rank: rank
    };
    
    try {
        await db.collection('players').doc(name).set(player);
        console.log(`Added player: ${name}`);
        return true;
    } catch (error) {
        console.error('Error adding player:', error);
        return false;
    }
};

// Function to update player last seen
window.updatePlayerSeen = async function(name) {
    try {
        await db.collection('players').doc(name).update({
            lastSeen: new Date().toISOString()
        });
        console.log(`Updated last seen for: ${name}`);
        return true;
    } catch (error) {
        console.error('Error updating player:', error);
        return false;
    }
};
