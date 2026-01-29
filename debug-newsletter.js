/**
 * Newsletter Subscription Debugger
 * 
 * This script helps debug newsletter subscription issues.
 * Open browser console and paste this code to test the newsletter subscription.
 */

// Test 1: Check if Firebase is initialized
console.log('=== Newsletter Subscription Debugger ===');
console.log('');
console.log('Test 1: Checking Firebase initialization...');

import { db } from './js/firebase-config.js';
import { addNewsletterSubscriber } from './js/data-service.js';

if (db) {
    console.log('✅ Firestore is initialized');
} else {
    console.error('❌ Firestore is NOT initialized');
}

// Test 2: Check if addNewsletterSubscriber function exists
console.log('');
console.log('Test 2: Checking addNewsletterSubscriber function...');
if (typeof addNewsletterSubscriber === 'function') {
    console.log('✅ addNewsletterSubscriber function exists');
} else {
    console.error('❌ addNewsletterSubscriber function NOT found');
}

// Test 3: Try to subscribe with a test email
console.log('');
console.log('Test 3: Attempting to subscribe test@example.com...');

async function testSubscription() {
    try {
        const result = await addNewsletterSubscriber('test@example.com');

        if (result.success) {
            console.log('✅ Subscription successful!');
            console.log('📧 Email: test@example.com');
            console.log('📝 Document ID should be: test_example_com');
            console.log('');
            console.log('🔍 Check Firestore Console:');
            console.log('   Collection: newsletter_subscribers');
            console.log('   Document ID: test_example_com');
        } else {
            console.error('❌ Subscription failed:', result.error);
        }
    } catch (error) {
        console.error('❌ Error during subscription:', error);
        console.error('Error details:', error.message);
        console.error('Error stack:', error.stack);
    }
}

// Run the test
testSubscription();

// Test 4: Check Firestore permissions
console.log('');
console.log('Test 4: Checking Firestore permissions...');
console.log('If you see permission errors above, check your Firestore Security Rules.');
console.log('');
console.log('Expected Security Rules:');
console.log(`
match /newsletter_subscribers/{subscriberId} {
  allow create: if true;  // Allow anyone to subscribe
  allow read, update: if request.auth != null;
  allow delete: if false;  // Only admins can delete
}
`);

// Test 5: Manual Firestore write test
console.log('');
console.log('Test 5: Testing direct Firestore write...');

import { doc, setDoc, serverTimestamp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

async function testDirectWrite() {
    try {
        const testDoc = doc(db, 'newsletter_subscribers', 'debug_test');
        await setDoc(testDoc, {
            email: 'debug@test.com',
            subscribedAt: serverTimestamp(),
            source: 'debug',
            receive_own: true,
            receive_partners: true,
            receive_third_party: true
        });
        console.log('✅ Direct Firestore write successful!');
        console.log('📝 Document ID: debug_test');
    } catch (error) {
        console.error('❌ Direct Firestore write failed:', error);
        console.error('This usually means a permissions issue.');
    }
}

testDirectWrite();

console.log('');
console.log('=== Debugger Complete ===');
console.log('Check the messages above for any errors.');
