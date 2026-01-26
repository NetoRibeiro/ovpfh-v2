#!/usr/bin/env python3
"""
Scraper for cadeojogo.com.br - Football Match Schedule
Extracts: Rodada (Round), Data (Date), Time, Teams, Broadcasting Info

IMPORTANT: Run this from your local machine as the site blocks automated requests.
Make sure to respect the site's terms of service.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import Optional
import time


class CadeOJogoScraper:
    def __init__(self):
        self.base_url = "https://www.cadeojogo.com.br"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
    def check_for_api(self) -> dict:
        """
        Check if the site uses any API endpoints by analyzing:
        1. JavaScript files for API calls
        2. Network requests patterns
        3. Common API paths
        """
        api_info = {
            "found_apis": [],
            "potential_endpoints": [],
            "notes": []
        }
        
        # Common API paths to check
        common_api_paths = [
            "/api/",
            "/api/v1/",
            "/api/v2/",
            "/api/jogos",
            "/api/rodadas",
            "/api/matches",
            "/api/games",
            "/json/",
            "/data/",
            "/_next/data/",  # Next.js
            "/graphql",
            "/api/graphql",
        ]
        
        try:
            # First, get the main page and check for JS files
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check script tags for API URLs
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Look for API patterns in inline scripts
                        api_patterns = [
                            r'fetch\s*\(\s*["\']([^"\']+)["\']',
                            r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)["\']',
                            r'\.get\s*\(\s*["\']([^"\']+)["\']',
                            r'\.post\s*\(\s*["\']([^"\']+)["\']',
                            r'api["\s]*[:=]\s*["\']([^"\']+)["\']',
                            r'endpoint["\s]*[:=]\s*["\']([^"\']+)["\']',
                        ]
                        
                        for pattern in api_patterns:
                            matches = re.findall(pattern, script.string, re.IGNORECASE)
                            for match in matches:
                                if match not in api_info["potential_endpoints"]:
                                    api_info["potential_endpoints"].append(match)
                    
                    # Check external script sources
                    if script.get('src'):
                        src = script.get('src')
                        if 'api' in src.lower() or 'data' in src.lower():
                            api_info["notes"].append(f"Potential API-related script: {src}")
                
                # Check for Next.js data
                next_data = soup.find('script', id='__NEXT_DATA__')
                if next_data:
                    api_info["notes"].append("Site uses Next.js - check /_next/data/ endpoints")
                    try:
                        next_json = json.loads(next_data.string)
                        api_info["next_data_sample"] = str(next_json)[:500] + "..."
                    except:
                        pass
                
                # Check for data attributes that might contain API info
                elements_with_data = soup.find_all(attrs={"data-api": True})
                for el in elements_with_data:
                    api_info["potential_endpoints"].append(el.get('data-api'))
                
        except Exception as e:
            api_info["error"] = str(e)
        
        # Try common API endpoints
        for path in common_api_paths:
            try:
                test_url = f"{self.base_url}{path}"
                resp = self.session.get(test_url, timeout=5)
                if resp.status_code == 200:
                    content_type = resp.headers.get('content-type', '')
                    if 'json' in content_type:
                        api_info["found_apis"].append({
                            "url": test_url,
                            "status": resp.status_code,
                            "content_type": content_type,
                            "sample": resp.text[:200] if resp.text else None
                        })
            except:
                pass
        
        return api_info

    def get_page_content(self, url: Optional[str] = None) -> Optional[str]:
        """Fetch page content"""
        target_url = url or self.base_url
        try:
            response = self.session.get(target_url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {target_url}: {e}")
            return None

    def parse_matches(self, html: str) -> list:
        """
        Parse match data from HTML.
        Returns list of matches with: rodada, data, hora, home_team, away_team, broadcast
        """
        matches = []
        soup = BeautifulSoup(html, 'html.parser')
        
        current_rodada = None
        
        # Strategy 1: Look for structured data patterns
        # The site seems to use a pattern like: RODADA X followed by match cards
        
        # Find all text that might indicate a rodada
        rodada_elements = soup.find_all(string=re.compile(r'RODADA\s*\d+', re.IGNORECASE))
        
        for rodada_el in rodada_elements:
            rodada_match = re.search(r'RODADA\s*(\d+)', rodada_el, re.IGNORECASE)
            if rodada_match:
                current_rodada = int(rodada_match.group(1))
        
        # Strategy 2: Look for match containers
        # Common patterns: divs with match info, tables, lists
        
        # Try finding date patterns (DD/MM/YYYY or similar)
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
        time_pattern = r'\d{1,2}:\d{2}'
        
        # Look for elements containing match data
        all_text = soup.get_text()
        
        # Find all dates and times
        dates = re.findall(date_pattern, all_text)
        times = re.findall(time_pattern, all_text)
        
        # Strategy 3: Find match cards/containers
        # Common class names for match containers
        match_selectors = [
            '[class*="match"]',
            '[class*="game"]',
            '[class*="jogo"]',
            '[class*="partida"]',
            '[class*="card"]',
            '[class*="fixture"]',
        ]
        
        for selector in match_selectors:
            try:
                elements = soup.select(selector)
                for el in elements:
                    match_data = self._extract_match_from_element(el, current_rodada)
                    if match_data:
                        matches.append(match_data)
            except:
                continue
        
        # Strategy 4: Parse tables if present
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    match_data = self._extract_match_from_row(cells, current_rodada)
                    if match_data:
                        matches.append(match_data)
        
        # Strategy 5: Generic element parsing based on text patterns
        # Look for div/span elements that contain team names and dates
        team_keywords = ['✕', 'vs', 'x', 'X']
        
        for keyword in team_keywords:
            elements = soup.find_all(string=re.compile(re.escape(keyword)))
            for el in elements:
                parent = el.parent
                if parent:
                    # Get surrounding context
                    context = parent.get_text(separator=' ', strip=True)
                    match_data = self._parse_match_from_text(context, current_rodada)
                    if match_data:
                        matches.append(match_data)
        
        # Remove duplicates
        seen = set()
        unique_matches = []
        for m in matches:
            key = f"{m.get('date')}-{m.get('home_team')}-{m.get('away_team')}"
            if key not in seen:
                seen.add(key)
                unique_matches.append(m)
        
        return unique_matches

    def _extract_match_from_element(self, element, rodada: Optional[int]) -> Optional[dict]:
        """Extract match data from a DOM element"""
        text = element.get_text(separator=' ', strip=True)
        return self._parse_match_from_text(text, rodada)

    def _extract_match_from_row(self, cells, rodada: Optional[int]) -> Optional[dict]:
        """Extract match data from table row cells"""
        if len(cells) < 3:
            return None
        
        cell_texts = [c.get_text(strip=True) for c in cells]
        combined = ' '.join(cell_texts)
        return self._parse_match_from_text(combined, rodada)

    def _parse_match_from_text(self, text: str, rodada: Optional[int]) -> Optional[dict]:
        """Parse match information from raw text"""
        if not text:
            return None
        
        match_data = {
            "rodada": rodada,
            "date": None,
            "time": None,
            "home_team": None,
            "away_team": None,
            "broadcast": None,
            "raw_text": text[:200]
        }
        
        # Extract date
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
        if date_match:
            match_data["date"] = date_match.group(1)
        
        # Extract time
        time_match = re.search(r'(\d{1,2}:\d{2})', text)
        if time_match:
            match_data["time"] = time_match.group(1)
        
        # Extract teams (look for patterns like "Team A ✕ Team B" or "Team A x Team B")
        team_patterns = [
            r'([A-Za-zÀ-ÿ\s]+)\s*[✕xX]\s*([A-Za-zÀ-ÿ\s]+)',
            r'([A-Za-zÀ-ÿ\s]+)\s*vs\.?\s*([A-Za-zÀ-ÿ\s]+)',
        ]
        
        for pattern in team_patterns:
            teams_match = re.search(pattern, text)
            if teams_match:
                match_data["home_team"] = teams_match.group(1).strip()
                match_data["away_team"] = teams_match.group(2).strip()
                break
        
        # Extract broadcast info
        broadcast_keywords = ['YouTube', 'SporTV', 'UOL', 'Max', 'Record', 'News', 'Space', 'Globo']
        found_broadcasts = []
        for keyword in broadcast_keywords:
            if keyword.lower() in text.lower():
                found_broadcasts.append(keyword)
        
        if found_broadcasts:
            match_data["broadcast"] = ', '.join(found_broadcasts)
        
        # Only return if we have essential data
        if match_data["date"] or (match_data["home_team"] and match_data["away_team"]):
            return match_data
        
        return None

    def scrape_all_rodadas(self) -> dict:
        """
        Main scraping function to get all available data
        """
        results = {
            "scraped_at": datetime.now().isoformat(),
            "source": self.base_url,
            "api_check": self.check_for_api(),
            "matches": [],
            "rodadas": {},
            "errors": []
        }
        
        # Get main page
        html = self.get_page_content()
        if not html:
            results["errors"].append("Failed to fetch main page")
            return results
        
        # Parse matches
        matches = self.parse_matches(html)
        results["matches"] = matches
        
        # Group by rodada
        for match in matches:
            rodada = match.get("rodada") or "unknown"
            if rodada not in results["rodadas"]:
                results["rodadas"][rodada] = []
            results["rodadas"][rodada].append(match)
        
        return results

    def export_to_json(self, data: dict, filename: str = "cadeojogo_data.json"):
        """Export scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data exported to {filename}")

    def export_to_csv(self, data: dict, filename: str = "cadeojogo_data.csv"):
        """Export scraped data to CSV file"""
        import csv
        
        matches = data.get("matches", [])
        if not matches:
            print("No matches to export")
            return
        
        fieldnames = ["rodada", "date", "time", "home_team", "away_team", "broadcast"]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(matches)
        
        print(f"Data exported to {filename}")


class APIDiscovery:
    """
    Additional class to discover hidden APIs through various methods
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def check_common_frameworks(self) -> dict:
        """Check for common framework-specific API patterns"""
        results = {
            "framework": None,
            "api_routes": []
        }
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            html = response.text
            
            # Check for Next.js
            if '/_next/' in html or '__NEXT_DATA__' in html:
                results["framework"] = "Next.js"
                results["api_routes"].append("/_next/data/[build-id]/[path].json")
                
                # Try to extract build ID
                build_match = re.search(r'/_next/static/([a-zA-Z0-9_-]+)/', html)
                if build_match:
                    build_id = build_match.group(1)
                    results["build_id"] = build_id
                    results["api_routes"].append(f"/_next/data/{build_id}/index.json")
            
            # Check for React/Create React App
            if 'static/js/main' in html:
                results["framework"] = "React (CRA)"
            
            # Check for Vue.js
            if '__vue__' in html or 'Vue.js' in html:
                results["framework"] = "Vue.js"
            
            # Check for Angular
            if 'ng-version' in html:
                results["framework"] = "Angular"
            
            # Check for WordPress
            if 'wp-content' in html or 'wp-json' in html:
                results["framework"] = "WordPress"
                results["api_routes"].append("/wp-json/wp/v2/posts")
                results["api_routes"].append("/wp-json/")
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def discover_xhr_endpoints(self) -> list:
        """
        Note: This would require browser automation (Selenium/Playwright) to properly
        intercept XHR requests. This is a placeholder for the approach.
        """
        print("""
        To discover XHR/API endpoints, use browser DevTools:
        
        1. Open Chrome/Firefox DevTools (F12)
        2. Go to Network tab
        3. Filter by 'XHR' or 'Fetch'
        4. Navigate through the site and click on rodadas
        5. Look for API calls to endpoints like:
           - /api/*
           - /data/*
           - /graphql
           - External APIs
        
        Alternatively, use Playwright/Selenium with request interception:
        
        ```python
        from playwright.sync_api import sync_playwright
        
        def intercept_requests():
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                
                # Intercept all requests
                def handle_request(request):
                    if 'api' in request.url or 'json' in request.url:
                        print(f"API call: {request.url}")
                
                page.on('request', handle_request)
                page.goto('https://www.cadeojogo.com.br')
                
                # Interact with the page to trigger API calls
                # ...
                
                browser.close()
        ```
        """)
        return []


def main():
    print("=" * 60)
    print("CadeOJogo.com.br Scraper")
    print("=" * 60)
    
    scraper = CadeOJogoScraper()
    
    # Step 1: Check for APIs
    print("\n[1] Checking for available APIs...")
    api_info = scraper.check_for_api()
    print(f"Found APIs: {len(api_info.get('found_apis', []))}")
    print(f"Potential endpoints: {api_info.get('potential_endpoints', [])}")
    print(f"Notes: {api_info.get('notes', [])}")
    
    # Step 2: Check framework
    print("\n[2] Checking frontend framework...")
    discovery = APIDiscovery("https://www.cadeojogo.com.br")
    framework_info = discovery.check_common_frameworks()
    print(f"Framework detected: {framework_info.get('framework')}")
    print(f"API routes to try: {framework_info.get('api_routes', [])}")
    
    # Step 3: Scrape the page
    print("\n[3] Scraping main page...")
    results = scraper.scrape_all_rodadas()
    
    print(f"\nMatches found: {len(results.get('matches', []))}")
    print(f"Rodadas found: {list(results.get('rodadas', {}).keys())}")
    
    if results.get('errors'):
        print(f"Errors: {results['errors']}")
    
    # Step 4: Export data
    scraper.export_to_json(results, "data/cadeojogo_data.json")
    scraper.export_to_csv(results, "data/cadeojogo_data.csv")
    
    # Print sample data
    print("\n[4] Sample data:")
    for match in results.get('matches', [])[:5]:
        print(f"  - Rodada {match.get('rodada')}: {match.get('home_team')} x {match.get('away_team')} "
              f"({match.get('date')} {match.get('time')})")
    
    print("\n" + "=" * 60)
    print("Done! Check data/cadeojogo_data.json and data/cadeojogo_data.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()
