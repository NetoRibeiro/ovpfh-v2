# Scraping Guide for cadeojogo.com.br

## Site Overview

**cadeojogo.com.br** is a website created by **Live Mode** for the **Federação Paulista de Futebol (FPF)** that shows where to watch football matches (Paulistão, Copinha, etc.).

### Data Structure
- **Rodada** (Round): Numbered rounds (1, 2, 3, 4...)
- **Data**: Match date (DD/MM/YYYY format)
- **Hora**: Match time (HH:MM format)
- **Teams**: Home ✕ Away
- **Onde Assistir**: Broadcasting platforms (SporTV, YouTube, UOL, Max, Record, etc.)

---

## Access Challenges

1. **robots.txt blocking**: The site blocks automated crawlers
2. **No documented public API**: No official API documentation found
3. **Dynamic content**: Likely uses JavaScript rendering (possibly Next.js)

---

## Recommended Approaches

### Approach 1: Browser DevTools (Manual API Discovery)

The fastest way to discover hidden APIs:

1. Open Chrome/Firefox → Navigate to `https://www.cadeojogo.com.br`
2. Press **F12** → Go to **Network** tab
3. Filter by **XHR** or **Fetch**
4. Click on different **RODADA** buttons
5. Look for requests to:
   - `/api/*`
   - `*.json` files
   - `/_next/data/*` (Next.js)
   - GraphQL endpoints

### Approach 2: Python + Requests (Basic Scraping)

```bash
pip install requests beautifulsoup4
python cadeojogo_scraper.py
```

File: `cadeojogo_scraper.py`

### Approach 3: Python + Playwright (Advanced)

Best for JavaScript-rendered sites with API interception:

```bash
pip install playwright
playwright install chromium
python cadeojogo_playwright_scraper.py
```

File: `cadeojogo_playwright_scraper.py`

---

## Known API Endpoints for Brazilian Football Data

If cadeojogo.com.br doesn't expose an API, consider these alternatives:

### 1. API Futebol (Brazilian)
- **URL**: https://api-futebol.com.br/
- **Coverage**: Brasileirão, Copa do Brasil, Paulistão, etc.
- **Format**: REST API, JSON responses
- **Pricing**: Has free tier

### 2. Globo Esporte API (Undocumented)
```
https://api.globoesporte.globo.com/tabela/{championship-id}/fase/{phase}/rodada/{round}/jogos/
```

Example for Brasileirão 2024:
```
https://api.globoesporte.globo.com/tabela/d1a37fa4-e948-43a6-ba53-ab24ab3a45b1/fase/fase-unica-campeonato-brasileiro-2024/rodada/01/jogos/
```

### 3. API-Football (International)
- **URL**: https://www.api-football.com/
- **Coverage**: 1200+ leagues worldwide
- **Pricing**: Free tier available

### 4. Footstats API
- **URL**: http://apifutebol.footstats.com.br/
- **Coverage**: Brazilian football statistics

---

## Sample Code: Quick API Check

```python
import requests

def check_api(url):
    """Quick check for API availability"""
    try:
        r = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('content-type')}")
        if 'json' in r.headers.get('content-type', ''):
            print(f"JSON Data: {r.json()[:500]}")
    except Exception as e:
        print(f"Error: {e}")

# Test common endpoints
endpoints = [
    "https://www.cadeojogo.com.br/api/",
    "https://www.cadeojogo.com.br/api/jogos",
    "https://www.cadeojogo.com.br/api/rodadas",
    "https://www.cadeojogo.com.br/_next/data/",
]

for ep in endpoints:
    print(f"\nTesting: {ep}")
    check_api(ep)
```

---

## Data Extraction Patterns

Based on the search results, the site displays data like:

```
RODADA 1
14/05/2025 · 16:00
Taubaté Futebol Feminino ✕ Realidade Jovem
ONDE ASSISTIR: YouTube Paulistão

14/05/2025 · 18:00
Palmeiras ✕ Ferroviária
ONDE ASSISTIR: SporTV
```

### Regex Patterns for Extraction:

```python
import re

# Date pattern
date_pattern = r'(\d{1,2}/\d{1,2}/\d{4})'

# Time pattern
time_pattern = r'(\d{1,2}:\d{2})'

# Teams pattern (with ✕ separator)
teams_pattern = r'([A-Za-zÀ-ÿ\s]+)\s*[✕xX]\s*([A-Za-zÀ-ÿ\s]+)'

# Rodada pattern
rodada_pattern = r'RODADA\s*(\d+)'

# Broadcasting pattern
broadcast_keywords = ['YouTube', 'SporTV', 'UOL', 'Max', 'Record', 'News', 'Space', 'Globo']
```

---

## Expected Output Format

```json
{
  "rodadas": {
    "1": [
      {
        "date": "14/05/2025",
        "time": "16:00",
        "home_team": "Taubaté Futebol Feminino",
        "away_team": "Realidade Jovem",
        "broadcast": ["YouTube Paulistão"]
      },
      {
        "date": "14/05/2025",
        "time": "18:00",
        "home_team": "Palmeiras",
        "away_team": "Ferroviária",
        "broadcast": ["SporTV"]
      }
    ],
    "2": [...]
  }
}
```

---

## Tips for Successful Scraping

1. **Respect rate limits**: Add delays between requests (1-2 seconds)
2. **Use proper headers**: Include User-Agent and Accept headers
3. **Handle errors gracefully**: Sites may block after multiple requests
4. **Cache responses**: Save raw HTML/JSON for debugging
5. **Check for CAPTCHAs**: The site may require human verification
6. **Consider scheduling**: Run scraper during off-peak hours

---

## Legal Considerations

- The site blocks crawlers via robots.txt
- Personal/research use is generally acceptable
- Avoid excessive requests that could impact the server
- Check the site's Terms of Service
- Consider contacting Live Mode for official data access

---

## Files Included

1. `cadeojogo_scraper.py` - Basic scraper using requests + BeautifulSoup
2. `cadeojogo_playwright_scraper.py` - Advanced scraper with API interception
3. `README.md` - This guide

## Quick Start

```bash
# Install dependencies
pip install requests beautifulsoup4 playwright

# Install Playwright browsers
playwright install chromium

# Run basic scraper
python cadeojogo_scraper.py

# Run advanced scraper (headless browser)
python cadeojogo_playwright_scraper.py
```
