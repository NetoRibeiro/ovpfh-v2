# -*- coding: utf-8 -*-
"""Logo Downloader for Onde Vai Passar Futebol Hoje"""

import os
import requests
from pathlib import Path
import time

# Base directories
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / 'assets'
TIMES_DIR = ASSETS_DIR / 'times'
CAMPEONATOS_DIR = ASSETS_DIR / 'campeonatos'
CANAIS_DIR = ASSETS_DIR / 'canais'

# Create directories
for directory in [TIMES_DIR, CAMPEONATOS_DIR, CANAIS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Team logos
TEAMS_LOGOS = {
    'flamengo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flamengo-RJ_%28BRA%29.png/150px-Flamengo-RJ_%28BRA%29.png',
    'palmeiras': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/150px-Palmeiras_logo.svg.png',
    'corinthians': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/5a/Sport_Club_Corinthians_Paulista_crest.svg/960px-Sport_Club_Corinthians_Paulista_crest.svg.png',
    'sao-paulo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Brasao_do_Sao_Paulo_Futebol_Clube.svg/150px-Brasao_do_Sao_Paulo_Futebol_Clube.svg.png',
    'vasco': 'https://upload.wikimedia.org/wikipedia/pt/thumb/8/8b/EscudoDoVascoDaGama.svg/960px-EscudoDoVascoDaGama.svg.png',
    'santos': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Santos_Logo.png/960px-Santos_Logo.png',
    'botafogo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Botafogo_de_Futebol_e_Regatas_logo.svg/150px-Botafogo_de_Futebol_e_Regatas_logo.svg.png',
    'fluminense': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Fluminense_FC_escudo.png/150px-Fluminense_FC_escudo.png',
    'atletico-mg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Atletico_mineiro_galo.png/150px-Atletico_mineiro_galo.png',
    'cruzeiro': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Cruzeiro_Esporte_Clube_%28logo%29.svg/150px-Cruzeiro_Esporte_Clube_%28logo%29.svg.png',
    'gremio': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Gremio_logo.svg/960px-Gremio_logo.svg.png',
    'internacional': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Sport_Club_Internacional_logo.svg/960px-Sport_Club_Internacional_logo.svg.png',
    'athletico-pr': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Athletico_Paranaense_%28Logo_2019%29.svg/960px-Athletico_Paranaense_%28Logo_2019%29.svg.png',
    'bahia': 'https://upload.wikimedia.org/wikipedia/pt/9/90/ECBahia.png',
    'fortaleza': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Fortaleza_Esporte_Clube_logo.png/960px-Fortaleza_Esporte_Clube_logo.png',
}

# League Information
CAMPEONATOS = {
    'paulistao': 'https://pt.wikipedia.org/wiki/Campeonato_Paulista_de_Futebol_de_2026',
    'carioca': 'https://pt.wikipedia.org/wiki/Campeonato_Carioca_de_Futebol_de_2026',
    'mineiro': 'https://pt.wikipedia.org/wiki/Campeonato_Mineiro_de_Futebol_de_2026_-_M%C3%B3dulo_I',
    'brasileirao': 'https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_2026_-_S%C3%A9rie_A',
    'libertadores': 'https://pt.wikipedia.org/wiki/Copa_Libertadores_da_Am%C3%A9rica_de_2026',
    'copa-brasil': 'https://pt.wikipedia.org/wiki/Copa_do_Brasil_de_Futebol_de_2026',
}

# League logos
CAMPEONATOS_LOGOS = {
    'paulistao': 'https://upload.wikimedia.org/wikipedia/pt/1/1c/Paulist%C3%A3o_2026.png',
    'carioca': 'https://upload.wikimedia.org/wikipedia/pt/thumb/e/e3/Campeonato_Carioca_logo.png/150px-Campeonato_Carioca_logo.png',
    'mineiro': 'https://upload.wikimedia.org/wikipedia/pt/thumb/4/4f/Campeonato_Mineiro_logo.png/150px-Campeonato_Mineiro_logo.png',
    'brasileirao': 'https://upload.wikimedia.org/wikipedia/pt/thumb/3/3f/Brasileir%C3%A3o_2024_logo.png/150px-Brasileir%C3%A3o_2024_logo.png',
    'libertadores': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/CONMEBOL_Libertadores_logo.svg/150px-CONMEBOL_Libertadores_logo.svg.png',
    'copa-brasil': 'https://upload.wikimedia.org/wikipedia/pt/thumb/8/8f/Copa_do_Brasil_logo.png/150px-Copa_do_Brasil_logo.png',
}

# Channel logos
CANAIS_LOGOS = {
    'sportv': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Star%2B_logo_2021.svg/120px-Star%2B_logo_2021.svg.png',
    'globo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Logotipo_da_Rede_Globo.svg/150px-Logotipo_da_Rede_Globo.svg.png',
    'record': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Rede_Record_logo.svg/150px-Rede_Record_logo.svg.png',
    'band': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Band_logo_2024.svg/150px-Band_logo_2024.svg.png',
    'sbt': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/SBT_logo_2023.svg/150px-SBT_logo_2023.svg.png',
    'cazetv': 'https://upload.wikimedia.org/wikipedia/pt/2/22/Logotipo_da_Caz%C3%A9TV.png',
}

def download_image(url, filepath, retries=3):
    """Download an image from URL"""
    for attempt in range(retries):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print("[OK] Downloaded: " + filepath.name)
            return True
            
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print("[RETRY] Attempt " + str(attempt + 1) + "/" + str(retries) + " for " + filepath.name)
                time.sleep(1)
            else:
                print("[FAIL] Failed to download " + filepath.name + ": " + str(e))
                return False
    
    return False

def download_all_logos():
    """Download all logos"""
    print("=" * 60)
    print("ONDE VAI PASSAR FUTEBOL HOJE - Logo Downloader")
    print("=" * 60)
    print()
    
    # Download team logos
    print("[TEAMS] Downloading team logos...")
    print("-" * 60)
    success_count = 0
    for team_name, url in TEAMS_LOGOS.items():
        filepath = TIMES_DIR / (team_name + ".png")
        if download_image(url, filepath):
            success_count += 1
        time.sleep(0.5)
    
    print("\n[STATS] Teams: " + str(success_count) + "/" + str(len(TEAMS_LOGOS)) + " downloaded successfully\n")
    
    # Download league logos
    print("[LEAGUES] Downloading league logos...")
    print("-" * 60)
    success_count = 0
    for league_name, url in CAMPEONATOS_LOGOS.items():
        filepath = CAMPEONATOS_DIR / (league_name + ".png")
        if download_image(url, filepath):
            success_count += 1
        time.sleep(0.5)
    
    print("\n[STATS] Leagues: " + str(success_count) + "/" + str(len(CAMPEONATOS_LOGOS)) + " downloaded successfully\n")
    
    # Download channel logos
    print("[CHANNELS] Downloading channel logos...")
    print("-" * 60)
    success_count = 0
    for channel_name, url in CANAIS_LOGOS.items():
        filepath = CANAIS_DIR / (channel_name + ".png")
        if download_image(url, filepath):
            success_count += 1
        time.sleep(0.5)
    
    print("\n[STATS] Channels: " + str(success_count) + "/" + str(len(CANAIS_LOGOS)) + " downloaded successfully\n")
    
    print("=" * 60)
    print("[SUCCESS] Logo download complete!")
    print("[INFO] Logos saved to: " + str(ASSETS_DIR))
    print("=" * 60)

def list_downloaded_logos():
    """List all downloaded logos"""
    print("\n[LIST] Downloaded logos:")
    print("-" * 60)
    
    for category, directory in [("Teams", TIMES_DIR), ("Leagues", CAMPEONATOS_DIR), ("Channels", CANAIS_DIR)]:
        files = list(directory.glob("*.png"))
        print("\n" + category + " (" + str(len(files)) + " files):")
        for file in sorted(files):
            size_kb = file.stat().st_size / 1024
            print("  - " + file.name + " (" + str(round(size_kb, 1)) + " KB)")

if __name__ == "__main__":
    try:
        download_all_logos()
        list_downloaded_logos()
        
        print("\n[NEXT] Next steps:")
        print("  1. Run: python spiders/update_logo_paths.py")
        print("  2. This will update HTML/JS files to use local logos")
        
    except KeyboardInterrupt:
        print("\n\n[WARN] Download interrupted by user")
    except Exception as e:
        print("\n\n[ERROR] Error: " + str(e))
