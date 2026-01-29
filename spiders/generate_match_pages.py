# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os
from pathlib import Path
from datetime import datetime
import re
import traceback
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

def initialize_firebase():
    """Initialize Firebase Admin SDK using environment variables from .env"""
    env_path = BASE_DIR / '.env'
    if not env_path.exists():
        print("ERROR: .env file not found at " + str(env_path))
        return None
    
    load_dotenv(env_path)
    
    try:
        private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
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
        
        if not cred_dict["project_id"] or not cred_dict["private_key"]:
            print("ERROR: Missing required Firebase credentials")
            return None
            
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        return firestore.client()
        
    except Exception as e:
        print("ERROR initializing Firebase: " + str(e))
        return None

def slugify(text):
    text = text.lower()
    text = text.replace('ã', 'a').replace('á', 'a').replace('â', 'a')
    text = text.replace('é', 'e').replace('ê', 'e')
    text = text.replace('í', 'i')
    text = text.replace('ó', 'o').replace('õ', 'o').replace('ô', 'o')
    text = text.replace('ú', 'u')
    text = text.replace('ç', 'c')
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

def load_data(db):
    print("Loading data from Firestore...")
    
    # Matches
    docs = db.collection('matches').stream()
    matches = []
    for doc in docs:
        m = doc.to_dict()
        m['id'] = doc.id
        matches.append(m)
    print(f"Loaded {len(matches)} matches")

    # Teams
    docs = db.collection('teams').stream()
    teams = {}
    for doc in docs:
        t = doc.to_dict()
        t['id'] = doc.id
        teams[doc.id] = t
    print(f"Loaded {len(teams)} teams")

    # Tournaments (Leagues)
    docs = db.collection('leagues').stream()
    tournaments = {}
    for doc in docs:
        t = doc.to_dict()
        t['id'] = doc.id
        tournaments[doc.id] = t
    print(f"Loaded {len(tournaments)} leagues")

    # Canais
    docs = db.collection('canais').stream()
    canais = []
    for doc in docs:
        c = doc.to_dict()
        c['id'] = doc.id
        canais.append(c)
    print(f"Loaded {len(canais)} canais")

    return matches, teams, tournaments, canais

def generate_match_pages():
    db = initialize_firebase()
    if not db:
        return

    matches, teams, tournaments, canais = load_data(db)
    
    # Load template
    with open(BASE_DIR / 'match.html', 'r', encoding='utf-8') as f:
        template = f.read()

    total_created = 0
    batch = db.batch()
    batch_count = 0
    
    for match in matches:
        try:
            home_team = teams.get(match['homeTeam'], {'name': match['homeTeam']})
            away_team = teams.get(match['awayTeam'], {'name': match['awayTeam']})
            tournament = tournaments.get(match['tournament'], {'name': match['tournament']})
            
            # Handle date format safely
            try:
                if 'matchDate' in match:
                    iso_date = match['matchDate'].replace('Z', '+00:00')
                    match_date = datetime.fromisoformat(iso_date)
                else:
                    match_date = datetime.now() # Fallback
            except ValueError:
                match_date = datetime.now()

            date_slug = match_date.strftime('%d-%m-%Y')
            
            home_name = home_team.get('name', match['homeTeam'])
            away_name = away_team.get('name', match['awayTeam'])
            
            teams_slug = f"{slugify(home_name)}-vs-{slugify(away_name)}"
            
            # URL and Path
            relative_url = f"/{match['tournament']}/{date_slug}/{teams_slug}/"
            
            # Update matchURL in Firestore if changed
            if match.get('matchURL') != relative_url:
                match_ref = db.collection('matches').document(match['id'])
                batch.update(match_ref, {'matchURL': relative_url})
                batch_count += 1
                if batch_count >= 400: # Limit per batch
                    batch.commit()
                    batch = db.batch()
                    batch_count = 0

            match['matchURL'] = relative_url
            
            path = BASE_DIR / match['tournament'] / date_slug / teams_slug
            path.mkdir(parents=True, exist_ok=True)
            
            # Prepare static data injection
            static_data_js = "\n<script>\n"
            static_data_js += "  window.STATIC_MATCH_DATA = " + json.dumps(match, ensure_ascii=False) + ";\n"
            static_data_js += "  window.STATIC_TEAMS_DATA = " + json.dumps(list(teams.values()), ensure_ascii=False) + ";\n"
            static_data_js += "  window.STATIC_TOURNAMENTS_DATA = " + json.dumps(list(tournaments.values()), ensure_ascii=False) + ";\n"
            static_data_js += "  window.STATIC_CANAIS_DATA = " + json.dumps(canais, ensure_ascii=False) + ";\n"
            static_data_js += "</script>\n"
            
            # Inject data and SEO tags
            page_content = template.replace('</head>', static_data_js + "</head>")
            
            tournament_name = tournament.get('name', match['tournament'])
            
            title_text = f"{home_name} x {away_name} - {tournament_name} | Onde Vai Passar"
            description_text = f"Onde assistir {home_name} x {away_name} ao vivo. Veja horários, canais de transmissão e detalhes do jogo."
            
            # Replace title/meta
            page_content = re.sub(r'(<title id="page-title">)(.*?)(</title>)', rf'\1{title_text}\3', page_content)
            if 'id="page-title"' not in page_content:
                page_content = re.sub(r'(<title>)(.*?)(</title>)', rf'<title id="page-title">{title_text}</title>', page_content)
            
            page_content = re.sub(r'<meta\s+name="description"[^>]*content=".*?"[^>]*>', 
                                 f'<meta name="description" id="page-description" content="{description_text}">', 
                                 page_content)

            # Fix relative paths
            page_content = page_content.replace('href="styles.css"', 'href="../../../styles.css"')
            page_content = page_content.replace('src="router.js"', 'src="../../../router.js"')
            page_content = page_content.replace('href="index.html"', 'href="../../../index.html"')
            page_content = page_content.replace('href="campeonatos.html"', 'href="../../../campeonatos.html"')
            page_content = page_content.replace('href="sobre.html"', 'href="../../../sobre.html"')
            page_content = page_content.replace('href="contato.html"', 'href="../../../contato.html"')
            page_content = page_content.replace('href="privacidade.html"', 'href="../../../privacidade.html"')
            page_content = page_content.replace('src="assets/root/logo_8_original_name.png"', 'src="../../../assets/root/logo_8_original_name.png"')
            # Fix canais.json fetch path - although we injected static data, scripts might still fetch
            page_content = page_content.replace("fetch('/data/canais.json')", "fetch('../../../data/canais.json')")
            
            with open(path / 'index.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            total_created += 1
            if total_created % 50 == 0:
                print(f"Generated {total_created} pages...")
                
        except Exception as e:
            print(f"Error processing match {match.get('id', 'N/A')}: {e}")
            traceback.print_exc()

    if batch_count > 0:
        batch.commit()

    print(f"\nFinished! Total pages generated: {total_created}")
    print("Firestore matches collection updated with matchURLs.")

if __name__ == "__main__":
    generate_match_pages()
