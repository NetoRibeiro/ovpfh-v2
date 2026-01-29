# -*- coding: utf-8 -*-
"""
Team Page Generator from Wikipedia League Data
Scrapes Wikipedia league pages and creates individual team pages.
Updates Firestore 'teams' collection with Wiki URLs and league info.
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Base directories
BASE_DIR = Path(__file__).parent.parent
TEAMS_DIR = BASE_DIR / 'times'
TEAMS_DIR.mkdir(parents=True, exist_ok=True)

# Helper for Firebase Initialization
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

# ... (Previous ESTADOS, CAMPEONATOS constants remain same, including them for completeness)
ESTADOS = {
    'SP': {'Paulistão', 'Campeonato Paulista de Futebol', 'Campeonato Paulista de Futebol - Serie A1', 'https://www.futebolpaulista.com.br/Home/', 'https://www.futebolpaulista.com.br/Competicoes/Tabela.aspx?idCampeonato=73&ano=2026&idCategoria=39&nav=1', 'https://pt.wikipedia.org/wiki/Campeonato_Paulista_de_Futebol_de_2026'},
    'RJ': {'Carioca', 'Campeonato Carioca de Futebol', 'Campeonato Carioca de Futebol', 'https://www.fferj.com.br/', 'https://www.fferj.com.br/campeonatos/estadual/profissional/serie-a?temporada=18', 'https://pt.wikipedia.org/wiki/Campeonato_Carioca_de_Futebol_de_2026'},
    # ... (Keep other states if needed, truncated for brevity but functionality works via CAMPEONATOS dict below)
} 

CAMPEONATOS = {
    'paulistao': 'https://pt.wikipedia.org/wiki/Campeonato_Paulista_de_Futebol_de_2026',
    'carioca': 'https://pt.wikipedia.org/wiki/Campeonato_Carioca_de_Futebol_de_2026',
    'mineiro': 'https://pt.wikipedia.org/wiki/Campeonato_Mineiro_de_Futebol_de_2026_-_M%C3%B3dulo_I',
    'brasileirao': 'https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_2026_-_S%C3%A9rie_A',
    'libertadores': 'https://pt.wikipedia.org/wiki/Copa_Libertadores_da_Am%C3%A9rica_de_2026',
    'copa-brasil': 'https://pt.wikipedia.org/wiki/Copa_do_Brasil_de_Futebol_de_2026',
}

def slugify(text):
    """Convert team name to URL-friendly slug"""
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

def extract_teams_from_league(url, league_name):
    """Extract team names and Wikipedia URLs from league page"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        teams = {}
        
        # Look for tables with team information
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    links = cell.find_all('a')
                    for link in links:
                        href = link.get('href', '')
                        title = link.get('title', '')
                        text = link.get_text(strip=True)
                        
                        if href.startswith('/wiki/') and not any(x in href for x in ['Ficheiro:', 'File:', 'Categoria:', 'Category:', 'Wikipedia:', 'Ajuda:']):
                            if len(text) > 2 and not text.isdigit() and 'futebol' not in text.lower():
                                if any(x in text for x in ['FC', 'SC', 'EC', 'AC', 'Clube', 'Esporte', 'Sport', 'Futebol']):
                                    wiki_url = 'https://pt.wikipedia.org' + href
                                    teams[text] = {'name': text, 'wiki_url': wiki_url, 'wiki_title': title}
                                elif any(x in title for x in ['Futebol', 'Clube']):
                                    wiki_url = 'https://pt.wikipedia.org' + href
                                    teams[text] = {'name': text, 'wiki_url': wiki_url, 'wiki_title': title}
        
        print("[INFO] Found " + str(len(teams)) + " teams in " + league_name)
        return teams
        
    except Exception as e:
        print("[ERROR] Failed to extract teams from " + league_name + ": " + str(e))
        return {}

def create_team_page(team_data, league_name):
    """Create an HTML page for a team"""
    team_name = team_data['name']
    wiki_url = team_data.get('wiki_url', '')
    
    slug = slugify(team_name)
    filepath = TEAMS_DIR / (slug + ".html")
    
    # We always recreate to ensure fresh template/data
    
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<!-- Wikipedia Source: {wiki_url} -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{team_name} - Jogos, Escalação e Onde Assistir | Onde Vai Passar Futebol Hoje</title>
  <meta name="description" content="Veja todos os jogos do {team_name}, escalações, estatísticas e onde assistir ao vivo. Acompanhe o {team_name} no {league_name}.">
  <link rel="icon" type="image/png" href="../assets/favicon.png">
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <header class="header">
    <div class="container">
      <div class="header-content">
        <h1 class="logo"><a href="../index.html" style="color: inherit;">⚽ Futebol Hoje</a></h1>
      </div>
    </div>
  </header>

  <main class="container">
    <nav class="breadcrumb" style="padding: 1rem 0; color: #BDBDBD;">
      <a href="../index.html" style="color: #FFD700;">Início</a> › <span>{team_name}</span>
    </nav>
    
    <div style="background: linear-gradient(135deg, rgba(0, 26, 51, 0.9), rgba(0, 8, 20, 0.9)); border: 2px solid #FFD700; border-radius: 16px; padding: 2rem; margin-bottom: 2rem; text-align: center;">
      <h1 style="font-size: 2.25rem; color: #F2FF00; margin-bottom: 1rem;">{team_name}</h1>
      <p style="color: #BDBDBD;">{league_name}</p>
    </div>
    
    <section style="margin-bottom: 2rem;">
      <h2 style="color: #F2FF00;">Sobre o Time</h2>
      <div style="background: rgba(0, 26, 51, 0.6); border: 1px solid #424242; border-radius: 12px; padding: 1.5rem; color: #E0E0E0;">
        <p>O <strong>{team_name}</strong> disputa o <strong>{league_name}</strong>.</p>
        <p><a href="{wiki_url}" target="_blank" style="color: #FFD700;">Ver na Wikipedia</a></p>
      </div>
    </section>
  </main>

  <footer style="text-align: center; padding: 2rem 0; color: #BDBDBD;">
    <p>&copy; 2026 Onde Vai Passar Futebol Hoje.</p>
  </footer>
</body>
</html>
""".format(team_name=team_name, league_name=league_name, wiki_url=wiki_url)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return True

def create_teams_index(teams_dict):
    """Create an index page listing all teams"""
    index_path = TEAMS_DIR / "index.html"
    
    teams_html = ""
    for team_name in sorted(teams_dict.keys()):
        slug = slugify(team_name)
        team_info = teams_dict[team_name]
        leagues = ", ".join(team_info.get('leagues', []))
        wiki_url = team_info.get('wiki_url', '')
        teams_html += f"""
        <div style="background: rgba(0, 26, 51, 0.6); border: 1px solid #424242; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
          <h3 style="color: #FFD700; margin-bottom: 0.5rem;">
            <a href="{slug}.html" style="color: inherit; text-decoration: none;">{team_name}</a>
          </h3>
          <p style="color: #BDBDBD; font-size: 0.875rem;">Campeonatos: {leagues}</p>
        </div>
        """
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Todos os Times</title>
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <header class="header"><div class="container"><h1 class="logo">Futebol Hoje</h1></div></header>
  <main class="container" style="padding: 2rem 0;">
    <h2 style="color: #F2FF00; margin-bottom: 2rem;">Todos os Times</h2>
    {teams_html}
  </main>
</body>
</html>
"""
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_all_team_pages():
    """Generate team pages and sync to Firestore"""
    
    # Initialize Firebase
    db = initialize_firebase()
    existing_teams = {}
    
    if db:
        print("Loading existing teams from Firestore...")
        docs = db.collection('teams').stream()
        for doc in docs:
            data = doc.to_dict()
            t_name = data.get('name', '').lower()
            existing_teams[t_name] = doc.id
            # Also map slug to id just in case name varies slightly but slug matches
            if data.get('slug'):
                 existing_teams[data.get('slug')] = doc.id
    else:
        print("WARNING: Firestore not connected. Skipping Firestore sync.")
    
    print("=" * 60)
    print("TEAM PAGE GENERATOR - From Wikipedia")
    print("=" * 60)
    
    all_teams = {}
    total_created = 0
    
    for league_slug, league_url in CAMPEONATOS.items():
        print(f"\n[LEAGUE] Processing: {league_slug}")
        teams_data = extract_teams_from_league(league_url, league_slug)
        
        for team_name, team_data in teams_data.items():
            create_team_page(team_data, league_slug.title())
            total_created += 1
            
            if team_name not in all_teams:
                all_teams[team_name] = {'leagues': [], 'wiki_url': team_data.get('wiki_url', '')}
            all_teams[team_name]['leagues'].append(league_slug)
        
        time.sleep(1) 

    # Sync to Firestore
    if db:
        print("\nSyncing to Firestore...")
        batch = db.batch()
        batch_count = 0
        
        for team_name, info in all_teams.items():
            # Try to match with existing team
            team_id = existing_teams.get(team_name.lower()) or existing_teams.get(slugify(team_name))
            
            if not team_id:
                # If new, use slug as ID
                team_id = slugify(team_name)
                
            doc_ref = db.collection('teams').document(team_id)
            
            batch.set(doc_ref, {
                'name': team_name,
                'wiki_url': info.get('wiki_url', ''),
                'leagues': info.get('leagues', []),
                'updatedAt': firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            batch_count += 1
            if batch_count >= 400:
                batch.commit()
                batch = db.batch()
                batch_count = 0
        
        if batch_count > 0:
            batch.commit()
            
    # Create Index
    create_teams_index(all_teams)
    print(f"\nDone! Created {total_created} pages and synced to Firestore.")

if __name__ == "__main__":
    generate_all_team_pages()
