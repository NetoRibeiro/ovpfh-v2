/**
 * OVPFH v2.0 - Firestore Data Service
 * Abstraction layer for all database operations
 */

import { db } from './firebase-config.js';
import {
    collection,
    getDocs,
    setDoc,
    doc,
    getDoc,
    query,
    where,
    orderBy,
    onSnapshot,
    writeBatch,
    serverTimestamp
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

// --- COLLECTIONS ---
const COLLECTIONS = {
    MATCHES: 'matches',
    TEAMS: 'teams',
    LEAGUES: 'leagues',
    CANAIS: 'canais',
    USER_PREFS: 'user_preferences'
};

/**
 * Fetch all documents from a collection
 */
async function getAllFromCollection(collectionName) {
    try {
        const querySnapshot = await getDocs(collection(db, collectionName));
        return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error(`Error fetching collection ${collectionName}:`, error);
        return [];
    }
}

/**
 * Get all matches
 */
export async function getAllMatches() {
    return await getAllFromCollection(COLLECTIONS.MATCHES);
}

/**
 * Get all teams
 */
export async function getAllTeams() {
    return await getAllFromCollection(COLLECTIONS.TEAMS);
}

/**
 * Get all leagues (championships)
 */
export async function getAllLeagues() {
    return await getAllFromCollection(COLLECTIONS.LEAGUES);
}

// Keep alias for backward compatibility during transition if needed
export const getAllTournaments = getAllLeagues;

/**
 * Get all channels (canais)
 */
export async function getAllChannels() {
    return await getAllFromCollection(COLLECTIONS.CANAIS);
}

/**
 * Get user preferences by UID
 */
export async function getUserPreferences(uid) {
    if (!uid) return null;
    try {
        const docRef = doc(db, COLLECTIONS.USER_PREFS, uid);
        const docSnap = await getDoc(docRef);

        if (docSnap.exists()) {
            return docSnap.data();
        } else {
            // Return default empty preferences
            return {
                countries: [],
                leagues: [],
                teams: []
            };
        }
    } catch (error) {
        console.error("Error fetching user preferences:", error);
        return null;
    }
}

/**
 * Save user preferences for a user
 */
export async function saveUserPreferences(uid, preferences) {
    if (!uid) return { success: false, error: 'No user ID' };
    try {
        const docRef = doc(db, COLLECTIONS.USER_PREFS, uid);
        await setDoc(docRef, {
            ...preferences,
            updatedAt: serverTimestamp()
        }, { merge: true });

        return { success: true };
    } catch (error) {
        console.error("Error saving user preferences:", error);
        return { success: false, error: error.message || 'Erro desconhecido' };
    }
}

/**
 * Listen for real-time changes on matches (H1)
 */
export function listenToMatches(callback) {
    const q = query(collection(db, COLLECTIONS.MATCHES));
    return onSnapshot(q, (snapshot) => {
        const matches = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        callback(matches);
    }, (error) => {
        console.error("Real-time listener error:", error);
    });
}

/**
 * MIGRATION UTILITY
 * Loads data from local JSONs and uploads them to Firestore if they don't exist
 * ONLY RUN THIS ONCE
 */
export async function migrateLocalDataToFirestore() {
    console.log("🚀 Starting data migration to Firestore...");

    try {
        // 1. Migrate LEAGUES
        const tournamentsRes = await fetch('data/tournaments.json');
        const { tournaments } = await tournamentsRes.json();
        await batchWrite(COLLECTIONS.LEAGUES, tournaments);
        console.log("✅ Leagues migrated");

        // 2. Migrate TEAMS
        const teamsRes = await fetch('data/teams.json');
        const { teams } = await teamsRes.json();
        await batchWrite(COLLECTIONS.TEAMS, teams);
        console.log("✅ Teams migrated");

        // 3. Migrate CANAIS (Channels)
        const canaisRes = await fetch('data/canais.json');
        const { canais } = await canaisRes.json();
        await batchWrite(COLLECTIONS.CANAIS, canais);
        console.log("✅ Channels migrated");

        // 4. Migrate MATCHES (might be many, use smaller batches if needed)
        const matchesRes = await fetch('data/matches.json');
        const { matches } = await matchesRes.json();
        await batchWrite(COLLECTIONS.MATCHES, matches);
        console.log("✅ Matches migrated");

        console.log("🎉 Migration complete!");
    } catch (error) {
        console.error("❌ Migration failed:", error);
    }
}

/**
 * Helper to write a list of items using a Firestore batch
 */
async function batchWrite(collectionName, items) {
    const batch = writeBatch(db);
    items.forEach(item => {
        // Use item.id as document ID if it exists, otherwise Firestore generates one
        const docRef = item.id ? doc(db, collectionName, item.id) : doc(collection(db, collectionName));
        batch.set(docRef, item);
    });
    await batch.commit();
}
