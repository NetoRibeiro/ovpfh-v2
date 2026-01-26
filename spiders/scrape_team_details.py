# -*- coding: utf-8 -*-
"""
Team Historical Data Scraper
Scrapes Wikipedia team pages to extract historical details, statistics, and information
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json

# Base directories
BASE_DIR = Path(__file__).parent.parent
TIMES_DIR = BASE_DIR / 'times'
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

def extract_wiki_url_from_page(html_file):
    """Extract Wikipedia URL from HTML comment in team page"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for Wikipedia Source comment
        match = re.search(r'<!-- Wikipedia Source: (https://[^\s]+) -->', content)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print("[ERROR] Failed to extract URL from " + html_file.name + ": " + str(e))
        return None

def scrape_team_details(wiki_url, team_name):
    """Scrape team historical details from Wikipedia"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(wiki_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        team_data = {
            'name': team_name,
            'wiki_url': wiki_url,
            'founded': None,
            'stadium': None,
            'capacity': None,
            'nickname': None,
            'colors': None,
            'titles': [],
            'description': None
        }
        
        # Look for infobox (common in Wikipedia team pages)
        infobox = soup.find('table', {'class': 'infobox'})
        
        if infobox:
            rows = infobox.find_all('tr')
            for row in rows:
                header = row.find('th')
                data = row.find('td')
                
                if header and data:
                    header_text = header.get_text(strip=True).lower()
                    data_text = data.get_text(strip=True)
                    
                    # Extract founded date
                    if 'fundado' in header_text or 'fundacao' in header_text or 'fundação' in header_text:
                        team_data['founded'] = data_text
                    
                    # Extract stadium
                    elif 'estadio' in header_text or 'estádio' in header_text:
                        team_data['stadium'] = data_text
                    
                    # Extract capacity
                    elif 'capacidade' in header_text:
                        team_data['capacity'] = data_text
                    
                    # Extract nickname
                    elif 'alcunha' in header_text or 'apelido' in header_text:
                        team_data['nickname'] = data_text
                    
                    # Extract colors
                    elif 'cores' in header_text:
                        team_data['colors'] = data_text
        
        # Extract first paragraph as description
        first_para = soup.find('p', {'class': None})
        if first_para:
            description = first_para.get_text(strip=True)
            if len(description) > 50:  # Only if substantial
                team_data['description'] = description[:500]  # Limit to 500 chars
        
        print("[OK] Scraped: " + team_name)
        return team_data
        
    except Exception as e:
        print("[ERROR] Failed to scrape " + team_name + ": " + str(e))
        return None

def scrape_all_teams():
    """Scrape historical details for all teams"""
    print("=" * 60)
    print("TEAM HISTORICAL DATA SCRAPER")
    print("=" * 60)
    print()
    
    # Try to load existing data
    json_path = DATA_DIR / 'teams_data.json'
    all_team_data = {}
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                all_team_data = json.load(f)
            print("[INFO] Loaded " + str(len(all_team_data)) + " teams from existing database")
        except:
            print("[WARN] Could not load existing database, starting fresh")
    
    success_count = 0
    fail_count = 0
    
    # Get all team HTML files
    team_files = list(TIMES_DIR.glob("*.html"))
    team_files = [f for f in team_files if f.name != 'index.html']
    
    print("[INFO] Found " + str(len(team_files)) + " team pages")
    print()
    
    try:
        for i, team_file in enumerate(team_files):
            team_slug = team_file.stem
            team_name = team_slug.replace('-', ' ').title()
            
            # Skip if we already have detailed data (check for a specific field like 'founded')
            if team_slug in all_team_data and 'founded' in all_team_data[team_slug] and all_team_data[team_slug]['founded']:
                print("[SKIP] Already have data for: " + team_name)
                continue
            
            print(f"[{i+1}/{len(team_files)}] Processing {team_name}...")
            
            # Extract Wikipedia URL from HTML
            wiki_url = extract_wiki_url_from_page(team_file)
            
            if not wiki_url:
                # Try to get from loaded data if available
                if team_slug in all_team_data and 'wiki_url' in all_team_data[team_slug]:
                    wiki_url = all_team_data[team_slug]['wiki_url']
                
                if not wiki_url:
                    print("  [SKIP] No Wikipedia URL found")
                    fail_count += 1
                    continue
            
            # Scrape team details
            team_data = scrape_team_details(wiki_url, team_name)
            
            if team_data:
                # Merge with existing data
                if team_slug not in all_team_data:
                    all_team_data[team_slug] = {}
                all_team_data[team_slug].update(team_data)
                success_count += 1
                
                # Save progress every 5 teams
                if success_count % 5 == 0:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(all_team_data, f, ensure_ascii=False, indent=2)
                    print("  [SAVE] Progress saved")
            else:
                fail_count += 1
            
            # Be nice to Wikipedia - Variable delay
            import time
            import random
            time.sleep(random.uniform(2.0, 4.0))
            
    except KeyboardInterrupt:
        print("\n[WARN] Operations interrupted! Saving progress...")
    
    # Final Save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_team_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print("[SUCCESS] Scraping session complete!")
    print("[STATS] Newly Scraped: " + str(success_count) + " teams")
    print("[INFO] Data saved to: " + str(json_path))
    print("=" * 60)
    
    return all_team_data

def generate_summary_report(teams_data):
    """Generate a summary report of scraped data"""
    report_file = DATA_DIR / 'teams_summary.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("TEAM HISTORICAL DATA SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        
        for slug, data in sorted(teams_data.items()):
            f.write(f"Team: {data['name']}\n")
            f.write(f"  Founded: {data.get('founded', 'N/A')}\n")
            f.write(f"  Stadium: {data.get('stadium', 'N/A')}\n")
            f.write(f"  Capacity: {data.get('capacity', 'N/A')}\n")
            f.write(f"  Nickname: {data.get('nickname', 'N/A')}\n")
            f.write(f"  Colors: {data.get('colors', 'N/A')}\n")
            f.write(f"  Wikipedia: {data['wiki_url']}\n")
            f.write("\n")
    
    print("\n[OK] Summary report saved to: " + str(report_file))

if __name__ == "__main__":
    try:
        teams_data = scrape_all_teams()
        
        if teams_data:
            generate_summary_report(teams_data)
        
        print("\n[NEXT] Next steps:")
        print("  1. Check data/teams_data.json for all scraped data")
        print("  2. Use this data to enhance team pages")
        print("  3. Integrate with your match API")
        
    except KeyboardInterrupt:
        print("\n\n[WARN] Scraping interrupted by user")
    except Exception as e:
        print("\n\n[ERROR] Error: " + str(e))
        import traceback
        traceback.print_exc()
