#!/usr/bin/env python3
"""
Advanced Scraper for cadeojogo.com.br using Playwright
- Intercepts XHR/Fetch requests to discover hidden APIs
- Handles JavaScript-rendered content
- Exports all discovered data

Install: pip install playwright && playwright install chromium
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse


try:
    from playwright.async_api import async_playwright, Page, Request, Response
except ImportError:
    print("Please install playwright: pip install playwright && playwright install chromium")
    exit(1)


class APIInterceptor:
    """Intercepts and logs all API/XHR requests"""
    
    def __init__(self):
        self.requests = []
        self.responses = []
        self.api_endpoints = []
        self.json_data = []
    
    async def handle_request(self, request: Request):
        """Log all requests"""
        url = request.url
        resource_type = request.resource_type
        
        # Filter for potential API calls
        if resource_type in ['xhr', 'fetch'] or any(x in url.lower() for x in ['api', 'json', 'data']):
            self.requests.append({
                "url": url,
                "method": request.method,
                "resource_type": resource_type,
                "post_data": request.post_data if request.method == "POST" else None
            })
            
            if 'api' in url.lower() or 'json' in url.lower():
                self.api_endpoints.append(url)
    
    async def handle_response(self, response: Response):
        """Log all responses, especially JSON ones"""
        url = response.url
        content_type = response.headers.get('content-type', '')
        
        if 'json' in content_type or url.endswith('.json'):
            try:
                data = await response.json()
                self.json_data.append({
                    "url": url,
                    "status": response.status,
                    "data": data
                })
                self.api_endpoints.append(url)
            except:
                pass
        
        self.responses.append({
            "url": url,
            "status": response.status,
            "content_type": content_type
        })


class PlaywrightScraper:
    """Scraper using Playwright for full browser automation"""
    
    def __init__(self, base_url: str = "https://www.cadeojogo.com.br"):
        self.base_url = base_url
        self.interceptor = APIInterceptor()
        self.matches = []
        self.rodadas = {}
    
    async def scrape(self, headless: bool = True) -> dict:
        """Main scraping function"""
        results = {
            "scraped_at": datetime.now().isoformat(),
            "source": self.base_url,
            "matches": [],
            "rodadas": {},
            "discovered_apis": [],
            "json_responses": [],
            "errors": []
        }
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Set up request/response interception
            page.on("request", self.interceptor.handle_request)
            page.on("response", self.interceptor.handle_response)
            
            try:
                # Navigate to the page
                print(f"Navigating to {self.base_url}...")
                await page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                
                # Wait for content to load
                await page.wait_for_timeout(3000)
                
                # Take a screenshot for debugging
                await page.screenshot(path="data/cadeojogo_screenshot.png", full_page=True)
                print("Screenshot saved: cadeojogo_screenshot.png")
                
                # Extract page content
                content = await page.content()
                
                # Parse matches from the rendered HTML
                self.matches = await self._parse_page_content(page)
                
                # Try to find and click on rodada selectors to trigger more API calls
                await self._explore_rodadas(page)
                
                # Parse matches again after exploring
                more_matches = await self._parse_page_content(page)
                
                # Merge matches
                for match in more_matches:
                    if match not in self.matches:
                        self.matches.append(match)
                
            except Exception as e:
                results["errors"].append(f"Scraping error: {str(e)}")
                print(f"Error: {e}")
            
            finally:
                await browser.close()
        
        # Compile results
        results["matches"] = self.matches
        results["discovered_apis"] = list(set(self.interceptor.api_endpoints))
        results["json_responses"] = self.interceptor.json_data
        results["all_requests"] = self.interceptor.requests
        
        # Group matches by rodada
        for match in self.matches:
            rodada = match.get("rodada", "unknown")
            if rodada not in results["rodadas"]:
                results["rodadas"][rodada] = []
            results["rodadas"][rodada].append(match)
        
        return results
    
    async def _parse_page_content(self, page: Page) -> list:
        """Parse match data from the rendered page"""
        matches = []
        
        # Try to extract data using JavaScript
        data = await page.evaluate("""
            () => {
                const matches = [];
                
                // Strategy 1: Look for structured data in __NEXT_DATA__
                const nextData = document.getElementById('__NEXT_DATA__');
                if (nextData) {
                    try {
                        const parsed = JSON.parse(nextData.textContent);
                        if (parsed.props && parsed.props.pageProps) {
                            return { nextData: parsed.props.pageProps };
                        }
                    } catch (e) {}
                }
                
                // Strategy 2: Extract from DOM
                // Look for rodada labels
                const rodadaElements = document.querySelectorAll('[class*="rodada"], [class*="round"]');
                let currentRodada = null;
                
                rodadaElements.forEach(el => {
                    const text = el.textContent;
                    const match = text.match(/RODADA\\s*(\\d+)/i);
                    if (match) {
                        currentRodada = parseInt(match[1]);
                    }
                });
                
                // Look for match cards
                const cardSelectors = [
                    '[class*="match"]', '[class*="game"]', '[class*="jogo"]',
                    '[class*="partida"]', '[class*="card"]', '[class*="fixture"]'
                ];
                
                cardSelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(card => {
                        const text = card.textContent || '';
                        
                        // Extract date
                        const dateMatch = text.match(/(\\d{1,2}\\/\\d{1,2}\\/\\d{4})/);
                        
                        // Extract time
                        const timeMatch = text.match(/(\\d{1,2}:\\d{2})/);
                        
                        // Extract teams (look for ✕ or x separator)
                        const teamsMatch = text.match(/([A-Za-zÀ-ÿ\\s]+)\\s*[✕xX]\\s*([A-Za-zÀ-ÿ\\s]+)/);
                        
                        if (dateMatch || teamsMatch) {
                            matches.push({
                                rodada: currentRodada,
                                date: dateMatch ? dateMatch[1] : null,
                                time: timeMatch ? timeMatch[1] : null,
                                home_team: teamsMatch ? teamsMatch[1].trim() : null,
                                away_team: teamsMatch ? teamsMatch[2].trim() : null,
                                raw_text: text.slice(0, 200)
                            });
                        }
                    });
                });
                
                // Strategy 3: Parse all visible text for patterns
                const allText = document.body.innerText;
                const lines = allText.split('\\n');
                
                let lastRodada = null;
                let lastDate = null;
                
                lines.forEach(line => {
                    const rodadaMatch = line.match(/RODADA\\s*(\\d+)/i);
                    if (rodadaMatch) {
                        lastRodada = parseInt(rodadaMatch[1]);
                    }
                    
                    const dateMatch = line.match(/(\\d{1,2}\\/\\d{1,2}\\/\\d{4})/);
                    if (dateMatch) {
                        lastDate = dateMatch[1];
                    }
                    
                    const teamsMatch = line.match(/([A-Za-zÀ-ÿ\\s]+)\\s*[✕xX]\\s*([A-Za-zÀ-ÿ\\s]+)/);
                    if (teamsMatch) {
                        matches.push({
                            rodada: lastRodada,
                            date: lastDate,
                            home_team: teamsMatch[1].trim(),
                            away_team: teamsMatch[2].trim(),
                            raw_text: line
                        });
                    }
                });
                
                return { matches };
            }
        """)
        
        if data.get("nextData"):
            print("Found Next.js data structure!")
            # Process Next.js data
            return self._process_next_data(data["nextData"])
        
        if data.get("matches"):
            return data["matches"]
        
        return matches
    
    def _process_next_data(self, next_data: dict) -> list:
        """Process Next.js pageProps data"""
        matches = []
        
        # Try to find match data in the structure
        def extract_matches(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if any(x in key.lower() for x in ['match', 'game', 'jogo', 'partida', 'rodada']):
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    matches.append({
                                        "source": f"{path}.{key}",
                                        **item
                                    })
                        elif isinstance(value, dict):
                            matches.append({
                                "source": f"{path}.{key}",
                                **value
                            })
                    extract_matches(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_matches(item, f"{path}[{i}]")
        
        extract_matches(next_data)
        return matches
    
    async def _explore_rodadas(self, page: Page):
        """Click on rodada buttons/tabs to trigger API calls"""
        try:
            # Find clickable rodada elements
            rodada_buttons = await page.query_selector_all('[class*="rodada"], button:has-text("RODADA"), [role="tab"]')
            
            for button in rodada_buttons[:5]:  # Limit to first 5 to avoid too many requests
                try:
                    await button.click()
                    await page.wait_for_timeout(1000)  # Wait for content to load
                except:
                    continue
        except Exception as e:
            print(f"Error exploring rodadas: {e}")


class AlternativeApproaches:
    """
    Document alternative approaches for API discovery
    """
    
    @staticmethod
    def browser_devtools_method():
        """Instructions for manual API discovery using DevTools"""
        print("""
        ╔══════════════════════════════════════════════════════════════╗
        ║          MANUAL API DISCOVERY USING BROWSER DEVTOOLS         ║
        ╠══════════════════════════════════════════════════════════════╣
        ║                                                              ║
        ║  1. Open Chrome/Firefox and navigate to cadeojogo.com.br    ║
        ║                                                              ║
        ║  2. Press F12 to open DevTools                              ║
        ║                                                              ║
        ║  3. Go to the "Network" tab                                 ║
        ║                                                              ║
        ║  4. Filter by "XHR" or "Fetch"                              ║
        ║                                                              ║
        ║  5. Interact with the page:                                 ║
        ║     - Click on different RODADAs                            ║
        ║     - Scroll through the page                               ║
        ║     - Change filters if available                           ║
        ║                                                              ║
        ║  6. Look for requests to:                                   ║
        ║     - /api/*                                                ║
        ║     - *.json files                                          ║
        ║     - GraphQL endpoints                                     ║
        ║     - _next/data/* (if Next.js)                             ║
        ║                                                              ║
        ║  7. Click on each request to see:                           ║
        ║     - Request URL                                           ║
        ║     - Request headers                                       ║
        ║     - Response data (Preview tab)                           ║
        ║                                                              ║
        ║  8. Document any patterns you find for future scraping      ║
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝
        """)
    
    @staticmethod
    def mitmproxy_method():
        """Instructions for using mitmproxy"""
        print("""
        ╔══════════════════════════════════════════════════════════════╗
        ║              API DISCOVERY USING MITMPROXY                   ║
        ╠══════════════════════════════════════════════════════════════╣
        ║                                                              ║
        ║  1. Install mitmproxy:                                      ║
        ║     pip install mitmproxy                                   ║
        ║                                                              ║
        ║  2. Start mitmproxy:                                        ║
        ║     mitmproxy --mode regular --listen-port 8080             ║
        ║                                                              ║
        ║  3. Configure browser to use proxy:                         ║
        ║     - HTTP Proxy: localhost:8080                            ║
        ║     - HTTPS Proxy: localhost:8080                           ║
        ║                                                              ║
        ║  4. Install mitmproxy CA certificate (for HTTPS)            ║
        ║                                                              ║
        ║  5. Navigate to cadeojogo.com.br                            ║
        ║                                                              ║
        ║  6. All requests will be logged in mitmproxy console        ║
        ║                                                              ║
        ║  7. Filter with: ~d cadeojogo.com.br & ~t json              ║
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝
        """)


async def main():
    print("=" * 70)
    print("CadeOJogo.com.br Advanced Scraper (Playwright)")
    print("=" * 70)
    
    scraper = PlaywrightScraper()
    
    print("\n[1] Starting browser and scraping...")
    results = await scraper.scrape(headless=True)
    
    print(f"\n[2] Results Summary:")
    print(f"    - Matches found: {len(results.get('matches', []))}")
    print(f"    - Rodadas found: {list(results.get('rodadas', {}).keys())}")
    print(f"    - Discovered APIs: {len(results.get('discovered_apis', []))}")
    print(f"    - JSON responses captured: {len(results.get('json_responses', []))}")
    print(f"    - Total requests intercepted: {len(results.get('all_requests', []))}")
    
    if results.get('discovered_apis'):
        print(f"\n[3] Discovered API Endpoints:")
        for api in results['discovered_apis'][:10]:
            print(f"    - {api}")
    
    if results.get('json_responses'):
        print(f"\n[4] JSON Response Samples:")
        for resp in results['json_responses'][:3]:
            print(f"    - URL: {resp['url']}")
            print(f"      Data sample: {str(resp['data'])[:200]}...")
    
    # Export results
    with open("data/cadeojogo_playwright_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n[5] Full results exported to: data/cadeojogo_playwright_results.json")
    
    # Show alternative approaches
    print("\n" + "=" * 70)
    print("ALTERNATIVE APPROACHES FOR API DISCOVERY:")
    print("=" * 70)
    AlternativeApproaches.browser_devtools_method()
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
