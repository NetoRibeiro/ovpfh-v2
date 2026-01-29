# -*- coding: utf-8 -*-
"""
OVPFH v2.0 - Upload JSON Data to Firestore
This script loads JSON files from /data/ and uploads them to Firestore
"""

import json
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from dotenv import load_dotenv

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK using environment variables"""
    
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print("ERROR: .env file not found!")
        print("Expected location: " + str(env_path))
        return None
    
    # Load the .env file
    load_dotenv(env_path)
    
    # Get credentials from environment variables
    try:
        # Build credentials dictionary from environment variables
        private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
        # Fix newlines in private key
        private_key = private_key.replace('\\n', '\n')
        
        cred_dict = {
            "type": os.getenv("FIREBASE_TYPE", "service_account"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": private_key,
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")
        }
        
        # Verify required fields are present
        if not cred_dict["project_id"] or not cred_dict["private_key"]:
            print("ERROR: Missing required Firebase credentials in .env file!")
            print("Required: FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY")
            return None
        
        # Initialize Firebase with credentials dictionary
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("SUCCESS: Firebase Admin SDK initialized")
        print("Project: " + cred_dict['project_id'])
        return db
        
    except Exception as e:
        print("ERROR initializing Firebase: " + str(e))
        print("\nMake sure your .env file contains all required Firebase credentials:")
        print("   - FIREBASE_PROJECT_ID")
        print("   - FIREBASE_PRIVATE_KEY")
        print("   - FIREBASE_CLIENT_EMAIL")
        return None


def load_json_file(file_path):
    """Load and parse a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("Loaded: " + file_path.name)
        return data
    except Exception as e:
        print("ERROR loading " + file_path.name + ": " + str(e))
        return None


def upload_collection(db, collection_name, items, id_field='id'):
    """Upload items to a Firestore collection"""
    
    if not items:
        print("WARNING: No items to upload for " + collection_name)
        return 0
    
    print("\nUploading to collection: " + collection_name)
    print("Items to upload: " + str(len(items)))
    
    uploaded = 0
    errors = 0
    
    for item in items:
        try:
            # Use the item's ID field as document ID
            doc_id = item.get(id_field)
            
            if not doc_id:
                print("WARNING: Skipping item without " + id_field)
                errors += 1
                continue
            
            # Add metadata
            item['uploadedAt'] = firestore.SERVER_TIMESTAMP
            
            # Upload to Firestore
            db.collection(collection_name).document(doc_id).set(item)
            uploaded += 1
            
            if uploaded % 10 == 0:
                print("   Uploaded " + str(uploaded) + "/" + str(len(items)) + "...")
                
        except Exception as e:
            print("ERROR uploading item " + item.get(id_field, 'unknown') + ": " + str(e))
            errors += 1
    
    print("SUCCESS: Uploaded " + str(uploaded) + " items to " + collection_name)
    if errors > 0:
        print("WARNING: " + str(errors) + " errors occurred")
    
    return uploaded


def main():
    """Main function to upload all JSON data to Firestore"""
    
    print("=" * 60)
    print("OVPFH v2.0 - Upload JSON Data to Firestore")
    print("=" * 60)
    print()
    
    # Initialize Firebase
    db = initialize_firebase()
    if not db:
        print("\nERROR: Failed to initialize Firebase. Exiting.")
        return
    
    # Define data directory
    data_dir = Path(__file__).parent.parent / 'data'
    
    if not data_dir.exists():
        print("ERROR: Data directory not found: " + str(data_dir))
        return
    
    print("\nData directory: " + str(data_dir))
    print()
    
    # Track statistics
    stats = {
        'total_uploaded': 0,
        'collections': []
    }
    
    # Upload Teams
    teams_file = data_dir / 'teams.json'
    if teams_file.exists():
        data = load_json_file(teams_file)
        if data and 'teams' in data:
            count = upload_collection(db, 'teams', data['teams'], id_field='id')
            stats['total_uploaded'] += count
            stats['collections'].append(('teams', count))
    
    # Upload Tournaments (Leagues)
    tournaments_file = data_dir / 'tournaments.json'
    if tournaments_file.exists():
        data = load_json_file(tournaments_file)
        if data and 'tournaments' in data:
            count = upload_collection(db, 'leagues', data['tournaments'], id_field='id')
            stats['total_uploaded'] += count
            stats['collections'].append(('leagues', count))
    
    # Upload Channels (Canais)
    canais_file = data_dir / 'canais.json'
    if canais_file.exists():
        data = load_json_file(canais_file)
        if data and 'canais' in data:
            count = upload_collection(db, 'canais', data['canais'], id_field='id')
            stats['total_uploaded'] += count
            stats['collections'].append(('canais', count))
    
    # Upload Matches
    matches_file = data_dir / 'matches.json'
    if matches_file.exists():
        data = load_json_file(matches_file)
        if data and 'matches' in data:
            count = upload_collection(db, 'matches', data['matches'], id_field='id')
            stats['total_uploaded'] += count
            stats['collections'].append(('matches', count))
    
    # Print summary
    print("\n" + "=" * 60)
    print("UPLOAD SUMMARY")
    print("=" * 60)
    print("\nTotal items uploaded: " + str(stats['total_uploaded']))
    print("\nBreakdown by collection:")
    for collection, count in stats['collections']:
        print("   - " + collection + ": " + str(count) + " items")
    
    print("\n" + "=" * 60)
    print("Upload complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Go to Firebase Console -> Firestore Database")
    print("2. Verify the collections were created:")
    for collection, _ in stats['collections']:
        print("   - " + collection)
    print("3. Check that the data looks correct")
    print("\nDone!")


if __name__ == "__main__":
    main()
