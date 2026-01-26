# -*- coding: utf-8 -*-
"""
Team Page Generator from Wikipedia League Data
Scrapes Wikipedia league pages and creates individual team pages
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re

# Base directories
BASE_DIR = Path(__file__).parent.parent
TEAMS_DIR = BASE_DIR / 'times'
TEAMS_DIR.mkdir(parents=True, exist_ok=True)
# UF: Apelido do Campeonato, Nome do Campeonato, Nome real do Campeonato, Link da Federação, Link do Campeonato na Federação, Pagina do Campeonato na WikiPedia
ESTADOS = {
    'SP': {'Paulistão', 'Campeonato Paulista de Futebol', 'Campeonato Paulista de Futebol - Serie A1', 'https://www.futebolpaulista.com.br/Home/', 'https://www.futebolpaulista.com.br/Competicoes/Tabela.aspx?idCampeonato=73&ano=2026&idCategoria=39&nav=1', 'https://pt.wikipedia.org/wiki/Campeonato_Paulista_de_Futebol_de_2026'},
    'RJ': {'Carioca', 'Campeonato Carioca de Futebol', 'Campeonato Carioca de Futebol', 'https://www.fferj.com.br/', 'https://www.fferj.com.br/campeonatos/estadual/profissional/serie-a?temporada=18', 'https://pt.wikipedia.org/wiki/Campeonato_Carioca_de_Futebol_de_2026'},
    'MG': {'Mineiro', 'Campeonato Mineiro de Futebol', 'Campeonato Mineiro de Futebol - Módulo I','https://www.fmf.com.br/', 'https://www.fmf.com.br/Competicoes/ProxJogos.aspx?d=1', 'https://pt.wikipedia.org/wiki/Campeonato_Mineiro_de_Futebol_de_2026_-_M%C3%B3dulo_I'},
    'BA': {'Baianão', 'Campeonato Baiano de Futebol', 'Campeonato Baiano de Futebol - Serie A1', 'https://www.fbf.org.br/', 'https://www.fbf.org.br/competicoes/1/2026', 'https://www.fbf.org.br/competicoes/1', 'https://pt.wikipedia.org/wiki/Campeonato_Baiano_de_Futebol_de_2026'},
    'PE': {'Pernambucano', 'Campeonato Pernambucano de Futebol', 'Campeonato Pernambucano da Serie A1', 'https://www.fpf-pe.com.br/pt/home/', 'https://www.fpf-pe.com.br/pt/competicoes/jogos.php?q=1651', 'https://pt.wikipedia.org/wiki/Campeonato_Pernambucano_de_Futebol_de_2026'},
    'CE': {'Cearense', 'Campeonato Cearense de Futebol', 'Campeonato Cearense de Futebol', 'https://www.futebolcearense.com.br/', 'https://www.futebolcearense.com.br/2023/clubes.asp?q=serie-a', 'https://pt.wikipedia.org/wiki/Campeonato_Cearense_de_Futebol_de_2026'},
    'RS': {'Gauchão', 'Campeonato Gaúcho de Futebol', 'Campeonato Gaúcho de Futebol - Serie A', 'https://www.fgf.com.br/', 'https://fgf.com.br/competicoes/profissional', 'https://pt.wikipedia.org/wiki/Campeonato_Ga%C3%BAcho_de_Futebol_de_2026_-_S%C3%A9rie_A'},
    'PR': {'Paranaense', 'Campeonato Paranaense de Futebol', 'Campeonato Paranaense de Futebol', 'https://federacaopr.com.br/', 'https://federacaopr.com.br/competicoes/Profissional/2026/33', 'https://pt.wikipedia.org/wiki/Campeonato_Paranaense_de_Futebol_de_2026'},
    'SC': {'Catarinense', 'Campeonato Catarinense de Futebol', 'Campeonato Catarinense de Futebol', 'https://fcf.com.br/', 'https://fcf.com.br/ligas/', 'https://pt.wikipedia.org/wiki/Campeonato_Catarinense_de_Futebol_de_2025_-_S%C3%A9rie_A'},
    'GO': {'Goiano', 'Campeonato Goiano de Futebol', 'Campeonato Goiano de Futebol', 'http://www.fgf.esp.br/pt/home/', 'http://www.fgf.esp.br/pt/competicoes/jogos.php?q=1643', 'https://pt.wikipedia.org/wiki/Campeonato_Goiano_de_Futebol_de_2026'},
    'DF': {'Candangão', 'Campeonato Brasiliense de Futebol', 'Campeonato Brasiliense de Futebol', 'https://www.ffdf.com.br/pt/home/', 'https://www.ffdf.com.br/pt/competicoes/jogos.php?q=1626', 'https://pt.wikipedia.org/wiki/Campeonato_Brasiliense_de_Futebol_de_2025'},
    'MT': {'Mato-Grossense', 'Campeonato Mato Grossoense de Futebol', 'Campeonato Mato Grossoense de Futebol', 'https://fmfmt.com.br/pt/home/', 'https://fmfmt.com.br/pt/competicoes/tabela.php?ID=1659', 'https://pt.wikipedia.org/wiki/Campeonato_Mato-Grossense_de_Futebol_de_2025'},
    'MS': {'Sul-Mato-Grossense', 'Campeonato Mato Grossoense de Futebol', 'Campeonato Mato Grossoense de Futebol', 'http://www.futebolms.com.br/', 'http://www.futebolms.com.br/', 'https://pt.wikipedia.org/wiki/Campeonato_Sul-Mato-Grossense_de_Futebol_de_2025'},
    'RO': {'Rondôniaense', 'Campeonato Rondôniaense de Futebol', 'Campeonato Rondôniaense de Futebol', 'https://www.ffer.com.br/', 'https://www.ffer.com.br/Publicacao.aspx?id=393357', 'https://pt.wikipedia.org/wiki/Campeonato_Rondoniense_de_Futebol_de_2025'},
    'AC': {'Acreano', 'Campeonato Acreano de Futebol', 'Campeonato Acreano de Futebol - Serie A', 'https://www.ffac.com.br/', 'https://ffac.com.br/competicao/2026/acreanao-sicredi-2026', 'https://pt.wikipedia.org/wiki/Campeonato_Acreano_de_Futebol_de_2025'},
    'AM': {'Amazonense', 'Campeonato Amazonense de Futebol', 'Campeonato Amazonense de Futebol', 'http://www.fafamazonas.com.br/site/', 'https://www.fafamazonas.com.br/site/', 'https://pt.wikipedia.org/wiki/Campeonato_Amazonense_de_Futebol_de_2025'},
    'RR': {'Roraimense', 'Campeonato Roraimense de Futebol', 'Campeonato Roraimense de Futebol', 'https://pt.wikipedia.org/wiki/Federa%C3%A7%C3%A3o_Roraimense_de_Futebol', 'https://pt.wikipedia.org/wiki/Federa%C3%A7%C3%A3o_Roraimense_de_Futebol', 'https://pt.wikipedia.org/wiki/Campeonato_Roraimense_de_Futebol_de_2026'},
    'PA': {'Paraense', 'Campeonato Paraense de Futebol', 'Campeonato Paraense de Futebol - Serie A', 'https://www.fpfpara.com.br/', 'https://www.fpfpara.com.br/competicao/95', 'https://pt.wikipedia.org/wiki/Campeonato_Paraense_de_Futebol_de_2026_-_S%C3%A9rie_A'},
    'AP': {'Amapazao', 'Campeonato Amapense de Futebol', 'Campeonato Amapense de Futebol - Serie A', 'https://fafamapa.com.br/', 'https://fafamapa.com.br/competicao/95', 'https://pt.wikipedia.org/wiki/Campeonato_Amapense_de_Futebol_de_2026'},
    'TO': {'Tocantinense', 'Campeonato Tocantinense de Futebol', 'Campeonato Tocantinense de Futebol', 'https://www.ftf.org.br/', 'https://www.ftf.org.br/federacao;page=Clubes;id=44', 'https://pt.wikipedia.org/wiki/Campeonato_Tocantinense_de_Futebol_de_2025'},
    'MA': {'Maranhense', 'Campeonato Maranhense de Futebol', 'Campeonato Maranhense de Futebol', 'https://www.futebolmaranhense.com.br/', 'https://www.futebolmaranhense.com.br/conteudo/27/14', 'https://pt.wikipedia.org/wiki/Campeonato_Maranhense_de_Futebol'},
    'PI': {'Piauiense', 'Campeonato Piauiense de Futebol', 'Campeonato Piauiense de Futebol', 'https://ffp-pi.com.br/', 'https://ffp-pi.com.br/competicoes/tabela/1628', 'https://pt.wikipedia.org/wiki/Campeonato_Piauiense_de_Futebol_de_2025'},
    'RN': {'Potiguar', 'Campeonato Potiguar de Futebol', 'Campeonato Potiguar de Futebol', 'https://fnf.org.br/', 'https://fnf.org.br/tabela/195/estadual-primeira-divisao-2026', 'https://pt.wikipedia.org/wiki/Campeonato_Potiguar_de_Futebol_de_2025'},
    'PB': {'Paraibano', 'Campeonato Paraibano de Futebol', 'Campeonato Paraibano de Futebol', 'https://federacaopbfutebol.com.br/pt/home/', 'https://federacaopbfutebol.com.br/pt/home/', 'https://pt.wikipedia.org/wiki/Campeonato_Paraibano_de_Futebol_de_2026'},
    'AL': {'Alagoano', 'Campeonato Alagoano de Futebol', 'Campeonato Alagoano de Futebol', 'https://www.futeboldealagoas.net/novo/', 'https://www.futeboldealagoas.net/novo/tabela?ID=1642', 'https://pt.wikipedia.org/wiki/Campeonato_Alagoano_de_Futebol'},
    'SE': {'Sergipao', 'Campeonato Sergipano de Futebol', 'Campeonato Sergipano de Futebol', 'https://fsf-se.com.br/', 'https://fsf-se.com.br/camp/campeonato-sergipano-2026/', 'https://pt.wikipedia.org/wiki/Campeonato_Sergipano_de_Futebol_de_2026'},
} 

# League Information (Campeonatos Estudais)
CAMPEONATOS_ESTADUAIS = {
    'paulistao': 'https://pt.wikipedia.org/wiki/Campeonato_Paulista_de_Futebol_de_2026',
    'carioca': 'https://pt.wikipedia.org/wiki/Campeonato_Carioca_de_Futebol_de_2026',
    'mineiro': 'https://pt.wikipedia.org/wiki/Campeonato_Mineiro_de_Futebol_de_2026_-_M%C3%B3dulo_I',
    }

CAMPEONATOS_NACIONAIS = {
    'brasileirao': {'https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_2026_-_S%C3%A9rie_A', 'https://www.cbf.com.br/', 'https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-a/2026'},
    'libertadores': 'https://pt.wikipedia.org/wiki/Copa_Libertadores_da_Am%C3%A9rica_de_2026',
    'copa-brasil': 'https://pt.wikipedia.org/wiki/Copa_do_Brasil_de_Futebol_de_2026',
}

CAMPEONATOS_INTERNACIONAIS = {
    'libertadores': 'https://pt.wikipedia.org/wiki/Copa_Libertadores_da_Am%C3%A9rica_de_2026',
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
        teams = {}  # Changed to dict to store team data
        
        # Look for tables with team information
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    # Look for links to team pages
                    links = cell.find_all('a')
                    for link in links:
                        href = link.get('href', '')
                        title = link.get('title', '')
                        text = link.get_text(strip=True)
                        
                        # Filter for team links (exclude references, years, etc.)
                        if href.startswith('/wiki/') and not any(x in href for x in ['Ficheiro:', 'File:', 'Categoria:', 'Category:', 'Wikipedia:', 'Ajuda:']):
                            if len(text) > 2 and not text.isdigit() and 'futebol' not in text.lower():
                                # Common team indicators
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
    
    # Skip if page already exists
    if filepath.exists():
        print("[SKIP] Page already exists: " + slug + ".html")
        return False
    
    # Create HTML content
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<!-- Wikipedia Source: {wiki_url} -->
<!-- Team Data: {{"name": "{team_name}", "league": "{league_name}", "slug": "{slug}"}} -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <!-- SEO Meta Tags -->
  <title>{team_name} - Jogos, Escalação e Onde Assistir | Onde Vai Passar Futebol Hoje</title>
  <meta name="description" content="Veja todos os jogos do {team_name}, escalações, estatísticas e onde assistir ao vivo. Acompanhe o {team_name} no {league_name}.">
  <meta name="keywords" content="{team_name}, {team_name} jogos, {team_name} onde assistir, {team_name} escalação, {league_name}">
  
  <!-- Favicon -->
  <link rel="icon" type="image/png" href="../assets/favicon.png">
  
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">
  
  <!-- Stylesheet -->
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  
  <!-- Header -->
  <header class="header">
    <div class="container">
      <div class="header-content">
        <div class="header-top">
          <h1 class="logo">
            <a href="../index.html" style="color: inherit;">⚽ Futebol Hoje</a>
          </h1>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="container">
    
    <!-- Breadcrumb -->
    <nav class="breadcrumb" aria-label="Breadcrumb" style="padding: 1rem 0; font-size: 0.875rem; color: #BDBDBD;">
      <a href="../index.html" style="color: #FFD700;">Início</a>
      <span style="margin: 0 0.5rem;">›</span>
      <a href="../campeonatos.html" style="color: #FFD700;">Campeonatos</a>
      <span style="margin: 0 0.5rem;">›</span>
      <span>{team_name}</span>
    </nav>
    
    <!-- Team Hero -->
    <div style="background: linear-gradient(135deg, rgba(0, 26, 51, 0.9), rgba(0, 8, 20, 0.9)); border: 2px solid #FFD700; border-radius: 16px; padding: 2rem; margin-bottom: 2rem; text-align: center;">
      <h1 style="font-size: 2.25rem; color: #F2FF00; margin-bottom: 1rem;">{team_name}</h1>
      <p style="color: #BDBDBD; font-size: 1.125rem;">{league_name}</p>
    </div>
    
    <!-- Próximos Jogos -->
    <section style="margin-bottom: 2rem;">
      <h2 style="color: #F2FF00; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="width: 4px; height: 32px; background: #FFD700; border-radius: 4px;"></span>
        Próximos Jogos
      </h2>
      <div style="background: rgba(0, 26, 51, 0.6); border: 1px solid #424242; border-radius: 12px; padding: 1.5rem; text-align: center; color: #BDBDBD;">
        <p>Informações sobre os próximos jogos do {team_name} serão exibidas aqui.</p>
        <p style="margin-top: 1rem;"><a href="../index.html" style="color: #FFD700;">Ver todos os jogos de hoje</a></p>
      </div>
    </section>
    
    <!-- Últimos Resultados -->
    <section style="margin-bottom: 2rem;">
      <h2 style="color: #F2FF00; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="width: 4px; height: 32px; background: #FFD700; border-radius: 4px;"></span>
        Últimos Resultados
      </h2>
      <div style="background: rgba(0, 26, 51, 0.6); border: 1px solid #424242; border-radius: 12px; padding: 1.5rem; text-align: center; color: #BDBDBD;">
        <p>Resultados recentes do {team_name} serão exibidos aqui.</p>
      </div>
    </section>
    
    <!-- Sobre o Time -->
    <section style="margin-bottom: 2rem;">
      <h2 style="color: #F2FF00; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="width: 4px; height: 32px; background: #FFD700; border-radius: 4px;"></span>
        Sobre o {team_name}
      </h2>
      <div style="background: rgba(0, 26, 51, 0.6); border: 1px solid #424242; border-radius: 12px; padding: 1.5rem; color: #E0E0E0; line-height: 1.8;">
        <p>O <strong>{team_name}</strong> é um dos times participantes do <strong>{league_name}</strong>.</p>
        <p style="margin-top: 1rem;">Acompanhe todos os jogos, escalações e informações sobre onde assistir o {team_name} ao vivo.</p>
      </div>
    </section>
    
  </main>

  <!-- Footer -->
  <footer style="text-align: center; padding: 2rem 0; color: #BDBDBD; font-size: 0.875rem; margin-top: 2.5rem;">
    <div class="container">
      <p>&copy; 2026 Onde Vai Passar Futebol Hoje. Todos os direitos reservados.</p>
    </div>
  </footer>

</body>
</html>
""".format(team_name=team_name, league_name=league_name, slug=slug, wiki_url=wiki_url)
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("[OK] Created: " + slug + ".html")
    return True

def generate_all_team_pages():
    """Generate team pages for all leagues"""
    print("=" * 60)
    print("TEAM PAGE GENERATOR - From Wikipedia League Data")
    print("=" * 60)
    print()
    
    all_teams = {}
    total_created = 0
    total_skipped = 0
    
    for league_slug, league_url in CAMPEONATOS.items():
        print("\n[LEAGUE] Processing: " + league_slug)
        print("-" * 60)
        
        # Extract teams from Wikipedia
        teams_data = extract_teams_from_league(league_url, league_slug)
        
        # Create pages for each team
        for team_name, team_data in teams_data.items():
            if create_team_page(team_data, league_slug.title()):
                total_created += 1
            else:
                total_skipped += 1
            
            # Store team info with Wikipedia URL
            if team_name not in all_teams:
                all_teams[team_name] = {'leagues': [], 'wiki_url': team_data.get('wiki_url', '')}
            all_teams[team_name]['leagues'].append(league_slug)
        
        time.sleep(2)  # Be nice to Wikipedia
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Team page generation complete!")
    print("[STATS] Created: " + str(total_created) + " pages")
    print("[STATS] Skipped: " + str(total_skipped) + " pages (already exist)")
    print("[INFO] Pages saved to: " + str(TEAMS_DIR))
    print("=" * 60)
    
    print("[INFO] Pages saved to: " + str(TEAMS_DIR))
    print("=" * 60)
    
    # Save basic team data to JSON
    data_dir = BASE_DIR / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    json_path = data_dir / 'teams_data.json'
    
    import json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_teams, f, ensure_ascii=False, indent=2)
    print("[OK] Saved team data to: " + str(json_path))
    
    # Create index file
    create_teams_index(all_teams)

def create_teams_index(teams_dict):
    """Create an index page listing all teams"""
    index_path = TEAMS_DIR / "index.html"
    
    teams_html = ""
    for team_name in sorted(teams_dict.keys()):
        slug = slugify(team_name)
        team_info = teams_dict[team_name]
        leagues = ", ".join(team_info.get('leagues', []))
        wiki_url = team_info.get('wiki_url', '')
        teams_html += """
        <div style="background: rgba(0, 26, 51, 0.6); border: 1px solid #424242; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
          <h3 style="color: #FFD700; margin-bottom: 0.5rem;">
            <a href="{slug}.html" style="color: inherit; text-decoration: none;">{team_name}</a>
          </h3>
          <p style="color: #BDBDBD; font-size: 0.875rem;">Campeonatos: {leagues}</p>
          <p style="color: #757575; font-size: 0.75rem; margin-top: 0.5rem;"><a href="{wiki_url}" target="_blank" style="color: #FFD700;">Wikipedia</a></p>
        </div>
        """.format(slug=slug, team_name=team_name, leagues=leagues, wiki_url=wiki_url)
    
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Todos os Times | Onde Vai Passar Futebol Hoje</title>
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <header class="header">
    <div class="container">
      <h1 class="logo"><a href="../index.html" style="color: inherit;">⚽ Futebol Hoje</a></h1>
    </div>
  </header>
  <main class="container" style="padding: 2rem 0;">
    <h2 style="color: #F2FF00; margin-bottom: 2rem;">Todos os Times</h2>
    {teams_html}
  </main>
</body>
</html>
""".format(teams_html=teams_html)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n[OK] Created teams index: times/index.html")

if __name__ == "__main__":
    try:
        generate_all_team_pages()
        
        print("\n[NEXT] Next steps:")
        print("  1. Check the 'times/' folder for generated pages")
        print("  2. Open times/index.html to see all teams")
        print("  3. Customize team pages with real data from your API")
        
    except KeyboardInterrupt:
        print("\n\n[WARN] Generation interrupted by user")
    except Exception as e:
        print("\n\n[ERROR] Error: " + str(e))
        import traceback
        traceback.print_exc()
