#!/usr/bin/env python3
"""
Paulistão Match Data Scraper
============================

Extracts football match data from resultados-futbol.com and outputs JSON format.

Dependencies:
    pip install requests beautifulsoup4 lxml

Usage:
    python paulistao_scraper.py
"""

import json
import re
import unicodedata
from typing import Optional, Dict, Tuple

import requests
from bs4 import BeautifulSoup


# =============================================================================
# Configuration
# =============================================================================

target_url = "https://www.resultados-futbol.com/competicion/paulistaa1/2026/grupo1/jornada5"


# =============================================================================
# Helper Functions
# =============================================================================

def normalize_team_name(name: str) -> str:
    """
    Normalize team name to URL-friendly slug.
    """
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore').decode('ASCII')
    name = name.lower().strip()
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'[^a-z0-9-]', '', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip('-')
    return name


def parse_spanish_date(date_str: str, time_str: str) -> Optional[str]:
    """
    Parse Spanish date format to ISO 8601 with Brazil timezone.
    """
    month_map = {
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
    }
    
    try:
        parts = date_str.strip().split()
        if len(parts) >= 3:
            day = parts[0].zfill(2)
            month = month_map.get(parts[1].lower()[:3], '01')
            year = '20' + parts[2] if len(parts[2]) == 2 else parts[2]
            
            time_parts = time_str.strip().split(':')
            hour = time_parts[0].zfill(2)
            minute = time_parts[1].zfill(2) if len(time_parts) > 1 else '00'
            
            return f"{year}-{month}-{day}T{hour}:{minute}:00-03:00"
    except Exception:
        pass
    
    return None


def extract_stadium_info(stadium_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract stadium name and city from raw stadium text.
    """
    if not stadium_name:
        return None, None
    
    stadium_name = stadium_name.strip()
    stadium_name = re.sub(r'\s+', ' ', stadium_name)
    
    stadium_cities = {
        'morumbi': 'São Paulo',
        'cícero pompeu de toledo': 'São Paulo',
        'pacaembu': 'São Paulo',
        'allianz parque': 'São Paulo',
        'neo química arena': 'São Paulo',
        'vila belmiro': 'Santos',
        'urbano caldeira': 'Santos',
        'moisés lucarelli': 'Campinas',
        'brinco de ouro': 'Campinas',
        'nabi abi chedid': 'Bragança Paulista',
        'jorge ismael de biase': 'Novo Horizonte',
        'alfredo de castilho': 'Bauru',
        'benito agnelo castellano': 'Rio Claro',
        'santa cruz': 'Ribeirão Preto',
        'josé maria de campos maia': 'Mirassol',
        'walter ribeiro': 'Sorocaba',
        'primeiro de maio': 'São Bernardo do Campo',
    }
    
    name_lower = stadium_name.lower()
    city = None
    
    for key, mapped_city in stadium_cities.items():
        if key in name_lower:
            city = mapped_city
            break
    
    return stadium_name, city


def determine_status(text: str, has_score: bool) -> str:
    """
    Determine match status from text content.
    """
    text_lower = text.lower()
    
    if any(x in text_lower for x in ['finalizado', 'fin', 'terminado']):
        return 'finished'
    elif any(x in text_lower for x in ['sin comenzar', 'próximo', 'programado']):
        return 'scheduled'
    elif any(x in text_lower for x in ['en juego', 'live', 'en vivo']):
        return 'live'
    elif any(x in text_lower for x in ['aplazado', 'postponed']):
        return 'postponed'
    elif any(x in text_lower for x in ['suspendido', 'suspended']):
        return 'suspended'
    elif has_score:
        return 'finished'
    else:
        return 'scheduled'


def extract_teams_from_match_url(match_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract home and away team slugs from matchURL.
    URL format: /partido/HomeTeam/AwayTeam/YYYYDDSequencialNumber
    
    Returns:
        Tuple of (home_team_slug, away_team_slug)
    """
    if not match_url:
        return None, None
    
    # Pattern: /partido/home-team/away-team/numbers
    match = re.search(r'/partido/([^/]+)/([^/]+)/\d+', match_url)
    if match:
        return match.group(1), match.group(2)
    
    return None, None


def extract_teams_from_match_url(match_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract home and away team slugs from matchURL.
    Format: /partido/HomeTeam/AwayTeam/YYYYDDSequencialNumber
    """
    if not match_url:
        return None, None
    
    # Pattern: /partido/team1/team2/number
    match = re.search(r'/partido/([^/]+)/([^/]+)/\d+', match_url)
    if match:
        return match.group(1), match.group(2)
    
    return None, None


# =============================================================================
# HTML Parser
# =============================================================================

def parse_html_content(html: str, url: str) -> Dict:
    """
    Parse HTML content using BeautifulSoup.
    """
    soup = BeautifulSoup(html, 'lxml')
    matches = []
    
    round_name = "Jornada 1"
    
    url_match = re.search(r'/competicion/([^/]+)/(\d{4})', url)
    if url_match:
        tournament = f"{url_match.group(1)}{url_match.group(2)[-2:]}"
                    
    round_match = re.search(r'jornada(\d+)', url.lower())
    if round_match:
        round_name = f"Jornada {round_match.group(1)}"
    
    seen = set()
    
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            team_links = row.find_all('a', href=re.compile(r'/equipo/'))
            if len(team_links) < 2:
                continue
            
            home_team = team_links[0].get_text(strip=True)
            away_team = team_links[1].get_text(strip=True)
            
            key = f"{home_team}-{away_team}"
            if key in seen:
                continue
            seen.add(key)
            
            row_text = row.get_text()
            
            # Extract date/time
            dt_match = re.search(r'(\d{1,2}\s+\w{3}\s+\d{2})\s+(\d{2}:\d{2})', row_text)
            match_date = None
            if dt_match:
                match_date = parse_spanish_date(dt_match.group(1), dt_match.group(2))
            
            # Extract score
            score_link = row.find('a', href=re.compile(r'/partido/'))
            score_home, score_away = None, None
            match_url = None
            
            if score_link:
                match_url = score_link.get('href')
                score_text = score_link.get_text(strip=True)
                score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', score_text)
                if score_match:
                    score_home = int(score_match.group(1))
                    score_away = int(score_match.group(2))
            
            # Extract teams from matchURL (more reliable)
            url_home, url_away = extract_teams_from_match_url(match_url)
            
            # Use URL-extracted teams, fallback to page-scraped teams
            home_slug = url_home if url_home else normalize_team_name(home_team)
            away_slug = url_away if url_away else normalize_team_name(away_team)
            
            status = determine_status(row_text, score_home is not None)
            
            # Venue
            venue_match = re.search(r'Estádio[^|<\n]+', row_text)
            venue_name, venue_city = None, None
            if venue_match:
                venue_name, venue_city = extract_stadium_info(venue_match.group(0))
            
            # Build match ID (without tournament prefix)
            date_for_id = "unknown"
            if match_date:
                date_parts = match_date.split('T')[0]
                y, m, d = date_parts.split('-')
                date_for_id = f"{d}-{m}-{y}"
            
            match_data = {
                "id": f"{tournament}-{home_slug}-vs-{away_slug}-{date_for_id}",
                "tournament": tournament,
                "homeTeam": home_slug,
                "awayTeam": away_slug,
                "matchDate": match_date,
                "round": round_name,
                "status": status,
                "score": {"home": score_home, "away": score_away},
                "venue": {"name": venue_name, "city": venue_city, "state": "SP"},
                "broadcasting": [],
                "matchURL": match_url
            }
            
            matches.append(match_data)
    
    return {"matches": matches}


# =============================================================================
# Text/Markdown Parser
# =============================================================================

def parse_text_content(content: str, url: str) -> Dict:
    """
    Parse text/markdown content (from web fetch tools).
    """
    matches = []
    
    round_name = "Jornada 4"
    
    url_match = re.search(r'/competicion/([^/]+)/(\d{4})', url)
    if url_match:
        tournament = f"{url_match.group(1)}{url_match.group(2)[-2:]}"
            
    round_match = re.search(r'jornada(\d+)', url.lower())
    if round_match:
        round_name = f"Jornada {round_match.group(1)}"
    
    seen = set()
    blocks = re.split(r'(?=\|\s*\d{1,2}\s+\w{3}\s+\d{2}\s+\d{2}:\d{2})', content)
    
    for block in blocks:
        if not block.strip():
            continue
        
        dt_match = re.search(
            r'(\d{1,2}\s+\w{3}\s+\d{2})\s+(\d{2}:\d{2})\s+(Finalizado|Sin comenzar|En juego)',
            block, re.IGNORECASE
        )
        if not dt_match:
            continue
        
        date_str = dt_match.group(1)
        time_str = dt_match.group(2)
        status_text = dt_match.group(3)
        
        teams = re.findall(r'\[([^\]]+)\]\(/equipo/', block)
        if len(teams) < 2:
            continue
        
        home_team = teams[0]
        away_team = teams[1]
        
        key = f"{home_team}-{away_team}"
        if key in seen:
            continue
        seen.add(key)
        
        match_date = parse_spanish_date(date_str, time_str)
        
        score_match = re.search(r'\[(\d+)-(\d+)\]', block)
        score_home = int(score_match.group(1)) if score_match else None
        score_away = int(score_match.group(2)) if score_match else None
        
        status = determine_status(status_text, score_home is not None)
        
        url_match_result = re.search(r'/partido/([^)]+)', block)
        match_url = f"/partido/{url_match_result.group(1)}" if url_match_result else None
        
        # Extract teams from matchURL (more reliable)
        url_home, url_away = extract_teams_from_match_url(match_url)
        
        # Use URL-extracted teams, fallback to page-scraped teams
        home_slug = url_home if url_home else normalize_team_name(home_team)
        away_slug = url_away if url_away else normalize_team_name(away_team)
        
        venue_match = re.search(r'Estádio[^\[\n|]+', block)
        venue_name, venue_city = None, None
        if venue_match:
            venue_name, venue_city = extract_stadium_info(venue_match.group(0))
        
        # Build match ID (without tournament prefix)
        date_for_id = "unknown"
        if match_date:
            date_parts = match_date.split('T')[0]
            y, m, d = date_parts.split('-')
            date_for_id = f"{d}-{m}-{y}"
        
        match_data = {
            "id": f"{tournament}-{home_slug}-vs-{away_slug}-{date_for_id}",
            "tournament": tournament,
            "homeTeam": home_slug,
            "awayTeam": away_slug,
            "matchDate": match_date,
            "round": round_name,
            "status": status,
            "score": {"home": score_home, "away": score_away},
            "venue": {"name": venue_name, "city": venue_city, "state": "SP"},
            "broadcasting": [],
            "matchURL": match_url
        }
        
        matches.append(match_data)
    
    return {"matches": matches}


# =============================================================================
# URL Fetcher
# =============================================================================

def fetch_and_parse(url: str) -> Dict:
    """
    Fetch URL and parse content.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    return parse_html_content(response.text, url)


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    from datetime import datetime
    
    print(f"Scraping: {target_url}")
    print("-" * 60)
    
    try:
        result = fetch_and_parse(target_url)
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None
    
    output_json = json.dumps(result, indent=2, ensure_ascii=False)
        
    # Save to file with datetime filename
    timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
    filename = f"resultados/{timestamp}_resultados.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(output_json)
    
    print("-" * 60)
    print(f"Total matches: {len(result.get('matches', []))}")
    print(f"Saved to: {filename}")
    
    return result


if __name__ == "__main__":
    main()