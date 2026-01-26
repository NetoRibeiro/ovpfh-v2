# Wikipedia Scraping System - Summary

## ✅ Enhanced Features

Successfully enhanced the team page generation system to capture and store Wikipedia URLs for future data scraping.

## 🔧 What Changed

### 1. Enhanced `generate_team_pages.py`

**New Features:**
- ✅ Captures Wikipedia URL for each team
- ✅ Stores URL in HTML comment for easy extraction
- ✅ Adds Wikipedia link to team index page
- ✅ Stores team metadata in nested dictionary structure

**Data Structure:**
```python
teams_data = {
    'Flamengo': {
        'name': 'Flamengo',
        'wiki_url': 'https://pt.wikipedia.org/wiki/Clube_de_Regatas_do_Flamengo',
        'wiki_title': 'Clube de Regatas do Flamengo'
    }
}
```

**HTML Comments Added:**
```html
<!-- Wikipedia Source: https://pt.wikipedia.org/wiki/... -->
<!-- Team Data: {"name": "Flamengo", "league": "Carioca", "slug": "flamengo"} -->
```

### 2. Created `scrape_team_details.py`

**New Script Features:**
- ✅ Extracts Wikipedia URLs from team pages
- ✅ Scrapes team historical details from Wikipedia
- ✅ Saves data to JSON file
- ✅ Generates summary report

**Data Extracted:**
- Founded date
- Stadium name
- Stadium capacity
- Team nickname
- Team colors
- Team description (first paragraph)

## 📊 Usage

### Generate Team Pages with URLs
```bash
python spiders/generate_team_pages.py
```

This will:
1. Scrape Wikipedia league pages
2. Extract team names and Wikipedia URLs
3. Generate HTML pages with embedded URLs
4. Create index with Wikipedia links

### Scrape Team Historical Details
```bash
python spiders/scrape_team_details.py
```

This will:
1. Read all team HTML pages
2. Extract Wikipedia URLs from comments
3. Scrape each team's Wikipedia page
4. Save data to `data/teams_data.json`
5. Generate summary report in `data/teams_summary.txt`

## 📁 Output Files

### `data/teams_data.json`
Complete team data in JSON format:
```json
{
  "flamengo": {
    "name": "Flamengo",
    "wiki_url": "https://pt.wikipedia.org/wiki/...",
    "founded": "15 de novembro de 1895",
    "stadium": "Maracanã",
    "capacity": "78.838",
    "nickname": "Mengão, Rubro-Negro",
    "colors": "Vermelho e preto",
    "description": "O Clube de Regatas do Flamengo..."
  }
}
```

### `data/teams_summary.txt`
Human-readable summary report with all team details.

## 🎯 Integration Examples

### Use in Team Pages

Update team pages to show historical data:

```javascript
// Load team data
fetch('../data/teams_data.json')
  .then(response => response.json())
  .then(data => {
    const teamData = data['flamengo'];
    document.getElementById('founded').textContent = teamData.founded;
    document.getElementById('stadium').textContent = teamData.stadium;
    document.getElementById('description').textContent = teamData.description;
  });
```

### Enhance About Section

Replace placeholder text with real data:

```html
<div class="team-info">
  <h3>Sobre o Flamengo</h3>
  <p><strong>Fundado:</strong> <span id="founded">...</span></p>
  <p><strong>Estádio:</strong> <span id="stadium">...</span></p>
  <p><strong>Capacidade:</strong> <span id="capacity">...</span></p>
  <p><strong>Apelido:</strong> <span id="nickname">...</span></p>
  <p id="description">...</p>
</div>
```

## 🌟 Benefits

- ✅ **Automated Data Collection**: No manual entry needed
- ✅ **Scalable**: Works for all 188 teams
- ✅ **Up-to-date**: Re-run script to refresh data
- ✅ **Structured Data**: JSON format for easy integration
- ✅ **SEO Boost**: Rich content for each team page
- ✅ **User Experience**: Real historical information

## 🔄 Workflow

1. **Generate Pages** → `generate_team_pages.py`
   - Creates 188 team pages with Wikipedia URLs

2. **Scrape Details** → `scrape_team_details.py`
   - Extracts historical data from Wikipedia

3. **Integrate Data** → Update team pages with JavaScript
   - Load JSON and populate team information

4. **Refresh Data** → Re-run scraper periodically
   - Keep information up-to-date

## 📝 Files Created

1. **`spiders/generate_team_pages.py`** (Enhanced)
   - Now captures Wikipedia URLs
   - Stores metadata in HTML comments

2. **`spiders/scrape_team_details.py`** (New)
   - Scrapes team historical details
   - Saves to JSON and text report

3. **`data/teams_data.json`** (Generated)
   - Complete team database

4. **`data/teams_summary.txt`** (Generated)
   - Human-readable report

## ⚠️ Important Notes

- **Rate Limiting**: Script includes 1-second delay between requests
- **Wikipedia Respect**: Be nice to Wikipedia servers
- **Data Accuracy**: Wikipedia data may vary in completeness
- **Manual Review**: Check scraped data for accuracy

## 🚀 Next Steps

1. Run `scrape_team_details.py` to collect historical data
2. Review `data/teams_data.json` for accuracy
3. Update team page templates to use JSON data
4. Add JavaScript to load and display team information
5. Consider adding more data fields (coach, president, etc.)
