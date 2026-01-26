# ⚽ Onde Vai Passar Futebol Hoje

A high-performance, mobile-first sports utility website showing today's football matches and their broadcasting channels, designed for Brazilian football fans.

## 🎯 Features

- **Static Site Generation (SSG)**: Pre-rendered match pages for near-instant loading and 100% SEO coverage
- **Clean URLs**: SEO-friendly Portuguese URLs like `/paulistao26/18-01-2026/corinthians-vs-santos/`
- **Dark Mode Design**: Professional stadium aesthetic with high-contrast colors
- **LIVE Indicators**: Pulsing animation for matches currently in progress
- **Quick Access**: One-click filtering by top teams (Flamengo, Palmeiras, Corinthians, etc.)
- **Real-time Search**: Instant filtering by team, league, or channel
- **Match Details**: Complete lineups, statistics, and broadcasting information
- **Mobile-First**: Responsive design that works perfectly on all devices

## 🚀 Quick Start

1. Update `data/matches.json` with new match data
2. Run the SSG script: `.venv\Scripts\python spiders/generate_match_pages.py`
3. Open `index.html` in your web browser
4. Click on any match to see the statically generated detail page

## 📁 Project Structure

```
ONDEVAIPASSARFUTEBOLHOJE/
├── index.html              # Main homepage with match feed
├── campeonatos.html        # League filter page
├── detalhes-do-jogo.html   # Match detail page (example)
├── styles.css              # Complete design system
├── app.js                  # Application logic
├── assets/                 # Logos and images
│   ├── times/             # Team logos
│   ├── campeonatos/       # League logos
│   └── canais/            # Channel logos
└── md/                    # Documentation
    ├── task.md
    ├── implementation_plan.md
    └── walkthrough.md
```

## 🎨 Design System

### Color Palette
- **Primary**: #001A33 (Deep Navy)
- **Accent**: #FFD700 (Gold) / #F2FF00 (Neon Yellow)
- **Live**: #FF0000 (Red)
- **Success**: #00FF41 (Neon Green)

### Typography
- **Headings**: Inter (Bold, 700-900 weight)
- **Body**: System UI fonts

## 🔧 Technology Stack

- **HTML5**: Semantic markup for SEO
- **CSS3**: Modern design with animations
- **Vanilla JavaScript**: No dependencies, fast performance
- **Mobile-First**: Responsive breakpoints at 640px, 768px, 1024px

## 📱 Pages

### 1. Homepage (`index.html`)
- Sticky header with date selector
- Search bar with real-time filtering
- Quick-access team chips
- Match cards with LIVE indicators
- Broadcasting channel information

### 2. League Page (`campeonatos.html`)
- Grid layout of all championships
- Match count per league
- Breadcrumb navigation

### 3. Match Detail Page (`detalhes-do-jogo.html`)
- Team lineups (Escalações)
- Broadcasting options (Onde Assistir)
- Head-to-head statistics
- SEO-optimized content

## 🎯 Nielsen's Heuristics Implementation

✅ **Heuristic #1**: Visibility of System Status (LIVE indicators)  
✅ **Heuristic #2**: Match Between System and Real World (Channel logos)  
✅ **Heuristic #4**: Consistency and Standards (Standardized match cards)  
✅ **Heuristic #6**: Recognition Rather Than Recall (Team chips)

## 📊 SEO Features

- Portuguese language meta tags
- Semantic HTML5 structure
- Optimized title and description tags
- Open Graph tags for social sharing
- SEO-friendly URL structure: `/onde-assistir-[time-a]-x-[time-b]-[data]/`

## 🔄 Next Steps for Production

### WordPress Integration
1. Install Elementor or Gutenberg
2. Create custom post type for matches
3. Map Sportmonks API data to custom fields
4. Create templates based on HTML files
5. Set up URL rewriting

### API Integration
- Connect to Sportmonks API
- Implement real-time score updates
- Add automatic LIVE status detection
- Schedule daily data refresh

## 📝 Documentation

See the `md/` folder for detailed documentation:
- `task.md` - Complete task checklist
- `implementation_plan.md` - Technical implementation details
- `walkthrough.md` - Feature walkthrough with screenshots

## 🌟 Key Highlights

- ⚡ **Fast**: Vanilla JavaScript, no frameworks
- 📱 **Responsive**: Works on all devices
- 🎨 **Beautiful**: Modern dark mode design
- 🔍 **SEO Ready**: Optimized for search engines
- ♿ **Accessible**: Semantic HTML and ARIA labels
- 🇧🇷 **Brazilian**: Portuguese language throughout

## 📄 License

© 2026 Onde Vai Passar Futebol Hoje. All rights reserved.

---

**Built with ⚽ for Brazilian football fans**
