/**
 * OVPFH v2.0 - Firebase Configuration
 * Initializes Firebase services for authentication and analytics
 */

import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getAuth } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { getAnalytics } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js';
import { getFirestore, enableMultiTabIndexedDbPersistence } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyB0eoLYyHla5qm7z9fTq5IFIh_ZPjsLj8A",
    authDomain: "ovpfh-28cee.firebaseapp.com",
    projectId: "ovpfh-28cee",
    storageBucket: "ovpfh-28cee.firebasestorage.app",
    messagingSenderId: "171939062993",
    appId: "1:171939062993:web:b48a85a3cb6158dfead1f0",
    measurementId: "G-PLQL8H0RE1"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

// Initialize Firestore
export const db = getFirestore(app);

// Initialize Firebase Analytics
export const analytics = getAnalytics(app);

// Enable Offline Persistence (H1)
enableMultiTabIndexedDbPersistence(db).catch((err) => {
    if (err.code == 'failed-precondition') {
        console.warn('Persistence failed: Multiple tabs open');
    } else if (err.code == 'unimplemented') {
        console.warn('Persistence failed: Browser not supported');
    }
});

// Log initialization
console.log('🔥 Firebase & Firestore initialized successfully');
console.log('📊 Analytics enabled');
