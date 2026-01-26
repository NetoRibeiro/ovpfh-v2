# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os
from pathlib import Path
from datetime import datetime
import re
import traceback

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

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

def load_data():
    with open(DATA_DIR / 'matches.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)['matches']
    with open(DATA_DIR / 'teams.json', 'r', encoding='utf-8') as f:
        teams = {t['id']: t for t in json.load(f)['teams']}
    with open(DATA_DIR / 'tournaments.json', 'r', encoding='utf-8') as f:
        tournaments = {t['id']: t for t in json.load(f)['tournaments']}
    with open(DATA_DIR / 'canais.json', 'r', encoding='utf-8') as f:
        canais = json.load(f)['canais']
    return matches, teams, tournaments, canais

def generate_match_pages():
    matches, teams, tournaments, canais = load_data()
    
    # Load template
    with open(BASE_DIR / 'match.html', 'r', encoding='utf-8') as f:
        template = f.read()

    total_created = 0
    updated_matches = []
    
    for match in matches:
        try:
            home_team = teams.get(match['homeTeam'], {'name': match['homeTeam']})
            away_team = teams.get(match['awayTeam'], {'name': match['awayTeam']})
            tournament = tournaments.get(match['tournament'], {'name': match['tournament']})
            
            match_date = datetime.fromisoformat(match['matchDate'].replace('Z', '+00:00'))
            date_slug = match_date.strftime('%d-%m-%Y')
            teams_slug = f"{slugify(home_team['name'])}-vs-{slugify(away_team['name'])}"
            
            # URL and Path
            relative_url = f"/{match['tournament']}/{date_slug}/{teams_slug}/"
            match['matchURL'] = relative_url
            updated_matches.append(match)
            
            path = BASE_DIR / match['tournament'] / date_slug / teams_slug
            path.mkdir(parents=True, exist_ok=True)
            
            # Prepare static data injection (using simple string concat to avoid f-string brace issues)
            static_data_js = "\n<script>\n"
            static_data_js += "  window.STATIC_MATCH_DATA = " + json.dumps(match, ensure_ascii=False) + ";\n"
            static_data_js += "  window.STATIC_TEAMS_DATA = " + json.dumps(list(teams.values()), ensure_ascii=False) + ";\n"
            static_data_js += "  window.STATIC_TOURNAMENTS_DATA = " + json.dumps(list(tournaments.values()), ensure_ascii=False) + ";\n"
            static_data_js += "  window.STATIC_CANAIS_DATA = " + json.dumps(canais, ensure_ascii=False) + ";\n"
            static_data_js += "</script>\n"
            
            # Inject data and SEO tags
            page_content = template.replace('</head>', static_data_js + "</head>")
            
            home_name = home_team.get('name', match['homeTeam'])
            away_name = away_team.get('name', match['awayTeam'])
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
            # Fix canais.json fetch path
            page_content = page_content.replace("fetch('/data/canais.json')", "fetch('../../../data/canais.json')")
            
            with open(path / 'index.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            total_created += 1
            if total_created % 20 == 0:
                print(f"Generated {total_created} pages...")
                
        except Exception as e:
            print(f"Error processing match {match.get('id', 'N/A')}: {e}")
            traceback.print_exc()

    # Save updated matches.json
    with open(DATA_DIR / 'matches.json', 'w', encoding='utf-8') as f:
        json.dump({"matches": updated_matches}, f, ensure_ascii=False, indent=2)
    
    print(f"\nFinalizado! Total de páginas geradas: {total_created}")
    print("matches.json atualizado com matchURL.")

if __name__ == "__main__":
    generate_match_pages()
