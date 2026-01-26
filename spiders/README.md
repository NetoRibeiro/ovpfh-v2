# 🕷️ Spiders - Logo Download Scripts

Python scripts to download and manage team, league, and channel logos for the website.

## 📋 Scripts

### 1. `download_logos.py`
Downloads all team, league, and channel logos from Wikipedia.

**Features:**
- Downloads 15+ team logos
- Downloads 6+ league/championship logos  
- Downloads 5+ channel logos
- Automatic retry on failure
- Progress tracking
- Organized into folders

### 2. `update_logo_paths.py`
Updates all HTML and JS files to use local logo paths instead of external URLs.

**Features:**
- Replaces Wikipedia URLs with local paths
- Updates `index.html`, `campeonatos.html`, `detalhes-do-jogo.html`, and `app.js`
- Tracks number of replacements made

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download Logos
```bash
python spiders/download_logos.py
```

This will download all logos to:
- `assets/times/` - Team logos
- `assets/campeonatos/` - League logos
- `assets/canais/` - Channel logos

### Step 3: Update File Paths
```bash
python spiders/update_logo_paths.py
```

This will update all HTML and JS files to use the local logos.

### Step 4: Verify
Open `index.html` in your browser to verify all logos are loading correctly.

## 📁 Downloaded Logos

### Teams (15 logos)
- Flamengo
- Palmeiras
- Corinthians
- São Paulo
- Vasco
- Santos
- Botafogo
- Fluminense
- Atlético-MG
- Cruzeiro
- Grêmio
- Internacional
- Athletico-PR
- Bahia
- Fortaleza

### Leagues (6 logos)
- Paulistão
- Campeonato Carioca
- Campeonato Mineiro
- Brasileirão
- Libertadores
- Copa do Brasil

### Channels (5 logos)
- SporTV
- Globo
- Record
- Band
- SBT

## 🔧 Customization

### Add More Teams
Edit `download_logos.py` and add to the `TEAMS` dictionary:

```python
TEAMS = {
    'team-slug': 'https://wikipedia.org/path/to/logo.png',
    # ...
}
```

### Add More Channels
Edit `download_logos.py` and add to the `CANAIS` dictionary:

```python
CANAIS = {
    'channel-slug': 'https://source.com/logo.png',
    # ...
}
```

## 📝 Notes

- All logos are downloaded as PNG files
- File naming uses lowercase with hyphens (e.g., `sao-paulo.png`)
- Script includes 0.5s delay between downloads to be respectful to Wikipedia servers
- Failed downloads are automatically retried up to 3 times

## ⚠️ Troubleshooting

**Issue**: Some logos fail to download
- Check your internet connection
- Verify the Wikipedia URL is still valid
- Some logos may have been moved or renamed on Wikipedia

**Issue**: Update script doesn't find files
- Make sure you're running from the project root
- Verify HTML/JS files exist in the expected locations

## 📄 License

These scripts download publicly available logos from Wikipedia and other sources. Please ensure you have the right to use these logos for your specific use case.
