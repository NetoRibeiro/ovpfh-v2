import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
# Specific leagues to sync (Paulista: 268, Carioca: 10272)
ALLOWED_LEAGUES = [268, 10272]
# https://www.fotmob.com/api/data/tltable?leagueId=268 # Paulista 2026
# https://www.fotmob.com/api/data/tltable?leagueId=10272 # Carioca 2026
BASE_URL = "https://www.fotmob.com/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        # Construct credentials from environment variables
        cert_dict = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n') if os.getenv("FIREBASE_PRIVATE_KEY") else None,
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
        }
        
        # Check if project_id is set to verify env loading
        if not cert_dict["project_id"]:
            raise ValueError("Firebase environment variables not found. Check your .env file.")

        cred = credentials.Certificate(cert_dict)
        firebase_admin.initialize_app(cred)
        print("🔥 Firebase Admin SDK initialized for project:", firebase_admin.get_app().project_id)
    except Exception as e:
        print(f"❌ Firebase init error: {e}")
        exit(1)

db = firestore.client()

def fetch_data(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        r = requests.get(url, params=params, headers=HEADERS)
        if r.status_code != 200:
            print(f"❌ Error fetching {url}: {r.status_code}")
            return None
        return r.json()
    except Exception as e:
        print(f"❌ Request exception: {e}")
        return None

def sync_matches(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y%m%d")
    
    print(f"\n📡 --- SYNCING {date_str} ---")
    
    data = fetch_data("fixtures", params={"date": date_str})
    if not data: 
        print("⚠️ No data received from API")
        return

    leagues = data.get('leagues', []) if isinstance(data, dict) else data
    
    if not leagues or not isinstance(leagues, list):
        print(f"⚠️ No leagues list found for {date_str}")
        return

    print(f"📊 Found {len(leagues)} leagues in FotMob data")
    
    sync_count = 0
    
    for league in leagues:
        league_id_int = league.get('id')
        if league_id_int not in ALLOWED_LEAGUES:
            continue
            
        league_id = str(league_id_int)
        league_name = league.get('name', 'Unknown League')
        
        # Only log league info if it has matches
        matches = league.get('matches', [])
        if not matches: continue

        # Sync Tournament (Pass year from date_str)
        sync_tournament(league, year=int(date_str[:4]))
        
        for match in matches:
            match_id = str(match.get('id'))
            
            # Map score and status
            status_obj = match.get('status', {})
            home_obj = match.get('home', {})
            away_obj = match.get('away', {})
            
            home_name = home_obj.get('name')
            away_name = away_obj.get('name')
            
            is_live = status_obj.get('ongoing', False)
            is_finished = status_obj.get('finished', False)
            
            status_str = "scheduled"
            if is_live: status_str = "live"
            elif is_finished: status_str = "finished"
            
            match_doc = {
                "id": match_id,
                "tournament": league_id,
                "homeTeam": str(home_obj.get('id')),
                "awayTeam": str(away_obj.get('id')),
                "matchDate": status_obj.get('utcTime'),
                "status": status_str,
                "score": {
                    "home": home_obj.get('score'),
                    "away": away_obj.get('score')
                },
                "isLive": is_live,
                "lastUpdatedSync": firestore.SERVER_TIMESTAMP
            }
            
            # Update match in Firestore
            db.collection('matches').document(match_id).set(match_doc, merge=True)
            
            # Sync Teams
            sync_team(home_obj)
            sync_team(away_obj)
            
            print(f"  ✅ Sync [{league_name}]: {home_name} {match_doc['score']['home'] or 0} - {match_doc['score']['away'] or 0} {away_name}")
            sync_count += 1
            
    print(f"🏁 Completed sync for {date_str}: {sync_count} matches updated")

def sync_team(team_data):
    if not team_data: return
    team_id = str(team_data.get('id'))
    team_doc = {
        "id": team_id,
        "name": team_data.get('name'),
        "logo": f"https://images.fotmob.com/image_resources/logo/teamlogo/{team_id}.png",
        "slug": team_data.get('name').lower().replace(' ', '-')
    }
    db.collection('teams').document(team_id).set(team_doc, merge=True)

def sync_tournament(league_data, year=None):
    if not league_data: return
    t_id = str(league_data.get('id', ''))
    if not t_id: return
    t_doc = {
        "id": t_id,
        "name": league_data.get('name'),
        "logo": f"https://images.fotmob.com/image_resources/logo/leaguelogo/{t_id}.png",
        "ccode": league_data.get('ccode', 'INT'),
        "year": year or datetime.now().year
    }
    db.collection('leagues').document(t_id).set(t_doc, merge=True)

if __name__ == "__main__":
    now = datetime.now()
    dates = [
        (now - timedelta(days=1)).strftime("%Y%m%d"),
        now.strftime("%Y%m%d"),
        (now + timedelta(days=1)).strftime("%Y%m%d")
    ]
    for d in dates:
        sync_matches(d)
