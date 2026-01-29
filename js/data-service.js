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
    serverTimestamp,
    limit
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

// --- COLLECTIONS ---
const COLLECTIONS = {
    MATCHES: 'matches',
    TEAMS: 'teams',
    LEAGUES: 'leagues',
    CANAIS: 'canais',
    USER_PREFS: 'user_preferences',
    NEWS: 'news',
    SUBSCRIBERS: 'newsletter_subscribers'
};

/**
 * Fetch all documents from a collection
 */
async function getAllFromCollection(collectionName) {
    console.log(`📡 [Firestore] Requested collection: ${collectionName}`);
    try {
        const querySnapshot = await getDocs(collection(db, collectionName));
        const data = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        console.log(`✅ [Firestore] Received ${data.length} items from ${collectionName}`);
        return data;
    } catch (error) {
        console.error(`❌ [Firestore] Error fetching collection ${collectionName}:`, error);
        throw error;
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
 * Get latest highlight news (is_highlight = true)
 * Simple query to avoid index requirements
 */
export async function getHighlightNews() {
    try {
        const newsRef = collection(db, COLLECTIONS.NEWS);
        // We fetch the latest news and filter in client if needed,
        // or use a simple query if we are sure of the field
        const q = query(
            newsRef,
            where('is_highlight', '==', true),
            orderBy('last_updated_date_time', 'desc'),
            limit(1)
        );
        const querySnapshot = await getDocs(q);
        return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error("Error fetching highlight news:", error);
        return [];
    }
}

/**
 * Get latest news cards (is_highlight = false)
 * Simplified to avoid composite index requirement
 */
export async function getLatestNewsCards(limitCount = 3) {
    try {
        const newsRef = collection(db, COLLECTIONS.NEWS);
        // To avoid index requirements for (!=) we fetch more and filter in JS
        const q = query(
            newsRef,
            orderBy('last_updated_date_time', 'desc'),
            limit(limitCount + 2) // Fetch a few more to filter out highlights
        );
        const querySnapshot = await getDocs(q);
        return querySnapshot.docs
            .map(doc => ({ id: doc.id, ...doc.data() }))
            .filter(item => !item.is_highlight)
            .slice(0, limitCount);
    } catch (error) {
        console.error("Error fetching news cards:", error);
        return [];
    }
}

/**
 * Listen for real-time news updates with highlights
 * Simplified to avoid index errors and catch raw data for debugging
 */
export function listenToHighlights(callback) {
    console.log("📡 [News] Starting Highlight listener...");
    const newsRef = collection(db, COLLECTIONS.NEWS);

    // Simple query: JUST get the latest news items. We will filter is_highlight in JS.
    // This is the MOST ROBUST way to ensure data shows up without requiring composite indices.
    const q = query(newsRef, orderBy('last_updated_date_time', 'desc'), limit(10));

    return onSnapshot(q, (snapshot) => {
        const allNews = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        console.log(`⭐ [News] Received ${allNews.length} raw news documents`);

        if (allNews.length > 0) {
            console.log("📍 [News] First doc sample fields:", Object.keys(allNews[0]).join(', '));
            console.log("📍 [News] First doc highlight value:", allNews[0].is_highlight);
        }

        // Find the highlight Document
        const highlight = allNews.find(item => item.is_highlight === true || item.is_highlight === 'true');

        if (highlight) {
            console.log("✅ [News] Found highlight document:", highlight.title);
            callback([highlight]);
        } else if (allNews.length > 0) {
            console.warn("⚠️ [News] No item marked as highlight in the latest 10. Using LATEST as fallback highlight.");
            callback([allNews[0]]);
        } else {
            console.warn("⚠️ [News] 'news' collection returned 0 items.");
            callback([]);
        }
    }, (error) => {
        console.error("❌ [News] Highlight snapshot error (Firestore probably unreachable):", error);
    });
}

/**
 * Listen for real-time news cards updates
 * Simplified to avoid index requirements
 */
export function listenToNewsCards(callback, limitCount = 3) {
    console.log("📡 [News] Starting News Cards listener...");
    const newsRef = collection(db, COLLECTIONS.NEWS);

    // Simple query to avoid index errors
    const q = query(newsRef, orderBy('last_updated_date_time', 'desc'), limit(10));

    return onSnapshot(q, (snapshot) => {
        const allNews = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));

        // Filter out items that are marked as highlights to avoid duplication
        const nonHighlights = allNews.filter(item => !(item.is_highlight === true || item.is_highlight === 'true'));

        // If everything is a highlight or if we have very little data, just show whatever we have
        const finalNews = nonHighlights.length > 0 ? nonHighlights : allNews;
        const result = finalNews.slice(0, limitCount);

        console.log(`📰 [News] Displaying ${result.length} news cards`);
        callback(result);
    }, (error) => {
        console.error("❌ [News] Cards snapshot error:", error);
    });
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
                teams: [],
                newsletter: {
                    own: false,
                    partners: false,
                    thirdParty: false
                }
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
 * Add email to newsletter subscribers
 * Can be used for both anonymous (footer) and authenticated (preferences) subscriptions
 */
export async function addNewsletterSubscriber(email, options = {}) {
    try {
        // Use email as ID to prevent duplicates (sanitized)
        const id = email.replace(/[^a-zA-Z0-9]/g, '_');

        const subscriberData = {
            email: email,
            subscribedAt: serverTimestamp(),
            source: options.source || 'footer',
            receive_own: options.receive_own !== undefined ? options.receive_own : true,
            receive_partners: options.receive_partners !== undefined ? options.receive_partners : true,
            receive_third_party: options.receive_third_party !== undefined ? options.receive_third_party : true
        };

        // If user is authenticated, store their UID for reference
        if (options.uid) {
            subscriberData.uid = options.uid;
        }

        await setDoc(doc(db, COLLECTIONS.SUBSCRIBERS, id), subscriberData, { merge: true });
        return { success: true };
    } catch (error) {
        console.error("Error subscribing to newsletter:", error);
        return { success: false, error: error.message };
    }
}

/**
 * Get newsletter preferences for a user by email or UID
 */
export async function getNewsletterPreferences(emailOrUid) {
    if (!emailOrUid) return null;

    try {
        // Try to find by sanitized email first
        const id = emailOrUid.replace(/[^a-zA-Z0-9]/g, '_');
        const docRef = doc(db, COLLECTIONS.SUBSCRIBERS, id);
        const docSnap = await getDoc(docRef);

        if (docSnap.exists()) {
            return {
                receive_own: docSnap.data().receive_own || false,
                receive_partners: docSnap.data().receive_partners || false,
                receive_third_party: docSnap.data().receive_third_party || false
            };
        }

        // Return default (all false)
        return {
            receive_own: false,
            receive_partners: false,
            receive_third_party: false
        };
    } catch (error) {
        console.error("Error fetching newsletter preferences:", error);
        return null;
    }
}

/**
 * Update newsletter preferences for a user
 */
export async function updateNewsletterPreferences(email, uid, preferences) {
    if (!email) return { success: false, error: 'No email provided' };

    try {
        const id = email.replace(/[^a-zA-Z0-9]/g, '_');
        const docRef = doc(db, COLLECTIONS.SUBSCRIBERS, id);

        await setDoc(docRef, {
            email: email,
            uid: uid || null,
            receive_own: preferences.own || false,
            receive_partners: preferences.partners || false,
            receive_third_party: preferences.thirdParty || false,
            updatedAt: serverTimestamp(),
            source: 'preferences'
        }, { merge: true });

        return { success: true };
    } catch (error) {
        console.error("Error updating newsletter preferences:", error);
        return { success: false, error: error.message };
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
