#!/bin/sh

# Replace placeholders in firebase-config.js with environment variables
# This script runs inside the Nginx container on startup

TARGET_FILE="/usr/share/nginx/html/js/firebase-config.js"

echo "💉 Injecting Firebase environment variables into $TARGET_FILE..."

sed -i "s|__FIREBASE_API_KEY__|${FIREBASE_API_KEY}|g" $TARGET_FILE
sed -i "s|__FIREBASE_AUTH_DOMAIN__|${FIREBASE_AUTH_DOMAIN}|g" $TARGET_FILE
sed -i "s|__FIREBASE_PROJECT_ID__|${FIREBASE_PROJECT_ID_FRONTEND}|g" $TARGET_FILE
sed -i "s|__FIREBASE_STORAGE_BUCKET__|${FIREBASE_STORAGE_BUCKET}|g" $TARGET_FILE
sed -i "s|__FIREBASE_MESSAGING_SENDER_ID__|${FIREBASE_MESSAGING_SENDER_ID}|g" $TARGET_FILE
sed -i "s|__FIREBASE_APP_ID__|${FIREBASE_APP_ID}|g" $TARGET_FILE
sed -i "s|__FIREBASE_MEASUREMENT_ID__|${FIREBASE_MEASUREMENT_ID}|g" $TARGET_FILE

echo "✅ Injection complete."
