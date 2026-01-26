# Implementation Plan: Tournament & Match Pages
## "Onde Vai Passar Futebol Hoje"

**Date:** January 19, 2026
**Status:** Planning Phase

---

## 📋 Project Overview

Create dedicated tournament pages for **Campeonato Paulista (Paulistão)** and **Campeonato Carioca**, with individual match pages following a specific URL structure. Other tournaments will display a "under construction" message with a contact form.

---

## 🎯 Requirements Summary

### 1. Tournament Pages
- ✅ **Paulistão 2026** - Full tournament page
- ✅ **Carioca 2026** - Full tournament page
- ⚠️ **All Others** - "Under construction" page with contact form

### 2. URL Structure
```
/{tournament-slug}{year}/{team-a}-vs-{team-b}/{dd-mm-yyyy}

Examples:
- /paulistao26/saopaulo-vs-corinthians/18-01-2026
- /carioca26/flamengo-vs-vasco/20-01-2026
- /mineiro26/cruzeiro-vs-atletico-mg/22-01-2026 (under construction)
```

### 3. Team Pages
- Individual page for each team
- URL: `/times/{team-slug}`
- Example: `/times/saopaulo`, `/times/flamengo`

### 4. Match Update Methods
Four approaches to consider:
1. **JSON Files** - Static JSON imports
2. **Admin Form** - Web-based data entry
3. **REST API** - Backend API integration
4. **Web Scraper (Spider)** - Automated data collection

---

## 🏗️ Architecture Design

### Current Tech Stack
- **Frontend:** Vanilla HTML5 + CSS3 + JavaScript
- **No Backend:** Pure static site
- **No Database:** Mock data in `app.js`
- **Assets:** Local images in `/assets/`

### Proposed Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND LAYER                     │
│  (Vanilla HTML/CSS/JS - No Framework)               │
├─────────────────────────────────────────────────────┤
│  Pages:                                             │
│  • index.html (Home - Match Feed)                   │
│  • /campeonatos/{tournament-slug} (Tournament)      │
│  • /{tournament}{year}/{teams}/{date} (Match)       │
│  • /times/{team-slug} (Team Page)                   │
│  • /em-construcao.html (Under Construction)         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                   DATA LAYER                         │
│  (Choose ONE approach initially)                    │
├─────────────────────────────────────────────────────┤
│  Option 1: JSON Files (/data/matches.json)         │
│  Option 2: Admin Panel + Local Storage/JSON        │
│  Option 3: REST API (Node.js + MongoDB/PostgreSQL) │
│  Option 4: Web Scraper + JSON Cache                │
└─────────────────────────────────────────────────────┘
```

---

## 📂 New File Structure

```
relaxed-mendel/
├── index.html                           # Homepage (existing)
├── campeonatos.html                     # Tournaments listing (existing)
├── em-construcao.html                   # NEW: Under construction page
├── app.js                               # Main logic (existing)
├── router.js                            # NEW: Client-side routing
├── match-detail.js                      # NEW: Match page logic
├── team-detail.js                       # NEW: Team page logic
├── tournament-detail.js                 # NEW: Tournament page logic
├── styles.css                           # Styles (existing)
├── data/                                # NEW: Data directory
│   ├── matches.json                     # Match data
│   ├── teams.json                       # Team data
│   ├── tournaments.json                 # Tournament metadata
│   └── broadcasting.json                # Channel information
├── campeonatos/                         # NEW: Tournament pages
│   ├── paulistao26.html                 # Paulistão 2026
│   ├── carioca26.html                   # Carioca 2026
│   └── template-tournament.html         # Template for future tournaments
├── times/                               # Team pages (existing, will restructure)
│   ├── flamengo.html
│   ├── saopaulo.html
│   └── ... (other teams)
└── partidas/                            # NEW: Match detail pages (dynamic)
    └── [generated dynamically via JS routing]
```

---

## 🗂️ Data Models

### Match Data Model
```json
{
  "id": "paulistao26-saopaulo-vs-corinthians-18-01-2026",
  "tournament": {
    "id": "paulistao26",
    "name": "Campeonato Paulista 2026",
    "slug": "paulistao26",
    "logo": "/assets/campeonatos/paulistao.png"
  },
  "homeTeam": {
    "id": "saopaulo",
    "name": "São Paulo",
    "slug": "saopaulo",
    "logo": "/assets/times/sao-paulo.png",
    "shortName": "SPO"
  },
  "awayTeam": {
    "id": "corinthians",
    "name": "Corinthians",
    "slug": "corinthians",
    "logo": "/assets/times/corinthians.png",
    "shortName": "COR"
  },
  "matchDate": "2026-01-18T21:30:00-03:00",
  "venue": {
    "name": "Morumbi",
    "city": "São Paulo",
    "state": "SP"
  },
  "status": "scheduled",
  "isLive": false,
  "score": {
    "home": null,
    "away": null
  },
  "broadcasting": [
    {
      "channel": "Premiere",
      "logo": "/assets/canais/premiere.png",
      "type": "pay-tv",
      "streamingUrl": null
    }
  ],
  "lineups": {
    "home": {
      "formation": "4-3-3",
      "players": []
    },
    "away": {
      "formation": "4-4-2",
      "players": []
    }
  },
  "statistics": {
    "possession": {"home": 0, "away": 0},
    "shots": {"home": 0, "away": 0},
    "shotsOnTarget": {"home": 0, "away": 0}
  },
  "headToHead": {
    "totalMatches": 0,
    "homeWins": 0,
    "awayWins": 0,
    "draws": 0,
    "lastMatches": []
  }
}
```

### Team Data Model
```json
{
  "id": "saopaulo",
  "name": "São Paulo Futebol Clube",
  "shortName": "São Paulo",
  "slug": "saopaulo",
  "logo": "/assets/times/sao-paulo.png",
  "founded": 1930,
  "stadium": "Morumbi",
  "state": "SP",
  "colors": {
    "primary": "#FF0000",
    "secondary": "#000000",
    "tertiary": "#FFFFFF"
  },
  "tournaments": ["paulistao26", "brasileirao26"],
  "socialMedia": {
    "website": "https://www.saopaulofc.net",
    "instagram": "@saopaulofc",
    "twitter": "@SaoPauloFC"
  }
}
```

### Tournament Data Model
```json
{
  "id": "paulistao26",
  "name": "Campeonato Paulista 2026",
  "shortName": "Paulistão",
  "slug": "paulistao26",
  "year": 2026,
  "logo": "/assets/campeonatos/paulistao.png",
  "status": "active",
  "startDate": "2026-01-15",
  "endDate": "2026-04-30",
  "teams": ["saopaulo", "corinthians", "palmeiras", "santos"],
  "phase": "group-stage",
  "description": "Campeonato Estadual de São Paulo - Edição 2026"
}
```

---

## 🎨 Page Designs

### 1. Tournament Page (`/campeonatos/paulistao26.html`)

**Components:**
- Header with tournament logo and name
- Current phase indicator (Group Stage, Semifinals, Final)
- Upcoming matches carousel
- Standings table (if available)
- Recent results
- Top scorers list
- Breadcrumb navigation
- CTA to contact form for updates

**Layout:**
```html
<section class="tournament-hero">
  <img src="/assets/campeonatos/paulistao.png" alt="Paulistão">
  <h1>Campeonato Paulista 2026</h1>
  <p class="tournament-phase">Fase de Grupos</p>
</section>

<section class="tournament-matches">
  <h2>Próximos Jogos</h2>
  <div class="matches-grid">
    <!-- Match cards -->
  </div>
</section>

<section class="tournament-standings">
  <h2>Classificação</h2>
  <table class="standings-table">
    <!-- Standings rows -->
  </table>
</section>
```

---

### 2. Match Detail Page (`/{tournament}{year}/{teams}/{date}`)

**URL Examples:**
- `/paulistao26/saopaulo-vs-corinthians/18-01-2026`
- `/carioca26/flamengo-vs-vasco/20-01-2026`

**Components:**
- Match hero (teams, score/time, status)
- Broadcasting channels (Onde Assistir)
- Live score updates (if live)
- Team lineups
- Match statistics
- Head-to-head history
- Breadcrumb: Home > Tournament > Match

**JavaScript Routing Logic:**
```javascript
// router.js
function parseMatchURL(pathname) {
  // Extract: /paulistao26/saopaulo-vs-corinthians/18-01-2026
  const parts = pathname.split('/').filter(p => p);

  if (parts.length !== 3) return null;

  const [tournamentSlug, teamsSlug, dateSlug] = parts;
  const [homeSlug, awaySlug] = teamsSlug.split('-vs-');
  const [day, month, year] = dateSlug.split('-');

  return {
    tournament: tournamentSlug,
    homeTeam: homeSlug,
    awayTeam: awaySlug,
    date: `${year}-${month}-${day}`
  };
}

function loadMatchDetail(matchParams) {
  // Fetch match data from JSON or API
  // Render match detail page
}
```

---

### 3. Team Page (`/times/{team-slug}`)

**Components:**
- Team header (logo, name, stadium)
- Upcoming matches
- Recent results
- Squad list (optional for v1)
- Team statistics
- Social media links

**Example:** `/times/saopaulo`

---

### 4. Under Construction Page (`/em-construcao.html`)

**Components:**
- Hero message: "Página do Campeonato em Construção"
- Tournament logo (if available)
- Contact form with fields:
  - Nome (Name)
  - Email
  - Campeonato de Interesse (Tournament of Interest)
  - Mensagem (Message)
- CTA: "Preencha o formulário para maiores informações"

**Form Submission:**
- Option 1: Email via Formspree or EmailJS
- Option 2: Store in LocalStorage for admin review
- Option 3: POST to backend API

---

## 🔄 Match Update Methods - Detailed Analysis

### **Option 1: JSON Files** 🗂️

**How It Works:**
```
1. Store match data in /data/matches.json
2. Frontend fetches JSON on page load
3. Manual updates via code editor or JSON editor
4. Commit changes to Git
```

**Pros:**
- ✅ Simple to implement
- ✅ No backend required
- ✅ Version control with Git
- ✅ Fast loading (static files)
- ✅ No database setup

**Cons:**
- ❌ Manual updates required
- ❌ No real-time updates
- ❌ Requires technical knowledge
- ❌ No audit trail
- ❌ Risk of JSON syntax errors

**Best For:** Small scale, infrequent updates, technical team

**Implementation:**
```javascript
// app.js
async function loadMatches() {
  const response = await fetch('/data/matches.json');
  const matches = await response.json();
  return matches;
}
```

**Sample JSON:**
```json
{
  "matches": [
    {
      "id": "paulistao26-saopaulo-vs-corinthians-18-01-2026",
      "tournament": "paulistao26",
      "homeTeam": "saopaulo",
      "awayTeam": "corinthians",
      "matchDate": "2026-01-18T21:30:00-03:00",
      "status": "scheduled"
    }
  ]
}
```

---

### **Option 2: Admin Form Panel** 📝

**How It Works:**
```
1. Create admin page (/admin/index.html)
2. Form to add/edit matches
3. Store data in LocalStorage or IndexedDB
4. Export to JSON for production
```

**Pros:**
- ✅ User-friendly interface
- ✅ No coding required for updates
- ✅ Form validation
- ✅ Quick to add matches
- ✅ No backend needed (LocalStorage)

**Cons:**
- ❌ Data stored in browser (can be lost)
- ❌ No multi-user support
- ❌ Manual export/import needed
- ❌ Limited to single device
- ❌ No authentication

**Best For:** Single admin user, quick prototyping

**Implementation:**
```html
<!-- /admin/index.html -->
<form id="match-form">
  <select name="tournament">
    <option value="paulistao26">Paulistão 2026</option>
    <option value="carioca26">Carioca 2026</option>
  </select>

  <select name="homeTeam">
    <!-- Team options -->
  </select>

  <select name="awayTeam">
    <!-- Team options -->
  </select>

  <input type="datetime-local" name="matchDate">

  <button type="submit">Adicionar Jogo</button>
</form>

<script>
  document.getElementById('match-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const match = Object.fromEntries(formData);

    // Save to LocalStorage
    const matches = JSON.parse(localStorage.getItem('matches') || '[]');
    matches.push(match);
    localStorage.setItem('matches', JSON.stringify(matches));

    alert('Jogo adicionado com sucesso!');
  });
</script>
```

---

### **Option 3: REST API** 🌐

**How It Works:**
```
1. Build backend API (Node.js + Express)
2. Database (MongoDB or PostgreSQL)
3. Admin panel makes API calls
4. Frontend fetches from API
5. Real-time updates possible
```

**Pros:**
- ✅ Real-time updates
- ✅ Multi-user support
- ✅ Centralized data
- ✅ Authentication & authorization
- ✅ Audit logs
- ✅ Scalable

**Cons:**
- ❌ Requires backend development
- ❌ Server hosting costs
- ❌ Database setup
- ❌ More complex architecture
- ❌ Longer development time

**Best For:** Production-ready app, multiple admins, frequent updates

**Tech Stack:**
- **Backend:** Node.js + Express.js
- **Database:** MongoDB (flexible schema) or PostgreSQL (relational)
- **Hosting:** Vercel, Railway, Render, or AWS
- **Auth:** JWT or session-based

**API Endpoints:**
```
GET    /api/matches              # List all matches
GET    /api/matches/:id          # Get single match
POST   /api/matches              # Create match (admin only)
PUT    /api/matches/:id          # Update match (admin only)
DELETE /api/matches/:id          # Delete match (admin only)

GET    /api/tournaments          # List tournaments
GET    /api/teams                # List teams
GET    /api/teams/:id/matches    # Team's matches
```

**Sample API Response:**
```json
{
  "success": true,
  "data": {
    "id": "paulistao26-saopaulo-vs-corinthians-18-01-2026",
    "tournament": {
      "id": "paulistao26",
      "name": "Campeonato Paulista 2026"
    },
    "homeTeam": {
      "id": "saopaulo",
      "name": "São Paulo"
    },
    "awayTeam": {
      "id": "corinthians",
      "name": "Corinthians"
    },
    "matchDate": "2026-01-18T21:30:00-03:00",
    "status": "scheduled"
  }
}
```

**Backend Structure:**
```
backend/
├── server.js                # Express app
├── routes/
│   ├── matches.js          # Match routes
│   ├── teams.js            # Team routes
│   └── tournaments.js      # Tournament routes
├── models/
│   ├── Match.js            # Match model
│   ├── Team.js             # Team model
│   └── Tournament.js       # Tournament model
├── controllers/
│   ├── matchController.js
│   ├── teamController.js
│   └── tournamentController.js
├── middleware/
│   └── auth.js             # Authentication
└── package.json
```

---

### **Option 4: Web Scraper (Spider)** 🕷️

**How It Works:**
```
1. Build Python/Node.js scraper
2. Target sports websites (GE, ESPN, etc.)
3. Extract match data automatically
4. Store in JSON or database
5. Run on schedule (cron job)
```

**Pros:**
- ✅ Automated data collection
- ✅ Always up-to-date
- ✅ No manual entry
- ✅ Can scrape multiple sources
- ✅ Rich data (lineups, stats)

**Cons:**
- ❌ Legal/ethical concerns (check terms of service)
- ❌ Website structure changes break scraper
- ❌ Rate limiting issues
- ❌ Data accuracy depends on source
- ❌ Complex maintenance

**Best For:** Large-scale app, frequent updates, aggregating multiple sources

**Tech Stack:**
- **Python:** Scrapy or BeautifulSoup + Requests
- **Node.js:** Puppeteer or Cheerio
- **Scheduling:** Cron jobs or GitHub Actions
- **Storage:** JSON files or database

**Sample Scraper (Python + Scrapy):**
```python
# spiders/globoesporte_spider.py
import scrapy
from datetime import datetime

class GloboEsporteSpider(scrapy.Spider):
    name = 'globoesporte'
    start_urls = ['https://ge.globo.com/futebol/']

    def parse(self, response):
        matches = response.css('.match-card')

        for match in matches:
            yield {
                'home_team': match.css('.home-team::text').get(),
                'away_team': match.css('.away-team::text').get(),
                'match_time': match.css('.match-time::text').get(),
                'tournament': match.css('.tournament-name::text').get(),
                'channel': match.css('.broadcast-channel::text').get(),
                'scraped_at': datetime.now().isoformat()
            }
```

**Legal Considerations:**
- ⚠️ Check website's `robots.txt`
- ⚠️ Review Terms of Service
- ⚠️ Use respectful scraping (rate limits, user agent)
- ⚠️ Consider using official APIs if available (e.g., API-Football)

---

## 📊 Comparison Matrix

| Criteria | JSON Files | Admin Form | REST API | Web Scraper |
|----------|------------|------------|----------|-------------|
| **Ease of Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Real-time Updates** | ❌ | ❌ | ✅ | ✅ |
| **Scalability** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cost** | Free | Free | $5-50/mo | Free-$20/mo |
| **Maintenance** | Low | Low | Medium | High |
| **Technical Skill** | Medium | Low | High | High |
| **Multi-user** | ❌ | ❌ | ✅ | ✅ (with API) |
| **Automation** | ❌ | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Recommended Approach

### **Phase 1: MVP (Minimum Viable Product)** - JSON Files
**Timeline:** 1-2 weeks
**Why:** Quick to launch, no backend complexity

1. ✅ Create JSON data files (`/data/matches.json`)
2. ✅ Build tournament pages (Paulistão, Carioca)
3. ✅ Implement dynamic match pages
4. ✅ Create team pages
5. ✅ Add under construction page for other tournaments

### **Phase 2: Admin Panel** - Admin Form
**Timeline:** 1 week
**Why:** Enable non-technical updates

1. Build admin panel UI
2. LocalStorage integration
3. Export to JSON functionality
4. Import existing JSON data

### **Phase 3: Backend API** - REST API
**Timeline:** 2-3 weeks
**Why:** Scale to production with real-time updates

1. Build Node.js backend
2. Set up MongoDB/PostgreSQL
3. Migrate JSON data to database
4. Add authentication
5. Deploy to cloud hosting

### **Phase 4: Automation** - Web Scraper (Optional)
**Timeline:** 2-4 weeks
**Why:** Automate data collection for continuous updates

1. Build scraper for Globo Esporte or similar
2. Schedule automated runs
3. Data validation and cleaning
4. Store in database via API

---

## 🛠️ Implementation Steps

### **Step 1: Set Up Data Structure**

1. Create `/data/` directory
2. Create `matches.json` with sample data
3. Create `teams.json` with team metadata
4. Create `tournaments.json` with tournament info
5. Create `broadcasting.json` with channel data

### **Step 2: Build Routing System**

1. Create `router.js` for client-side routing
2. Implement URL parsing for match pages
3. Handle 404 pages
4. Add breadcrumb navigation

### **Step 3: Tournament Pages**

1. Create `/campeonatos/paulistao26.html`
2. Create `/campeonatos/carioca26.html`
3. Load tournament data from JSON
4. Display upcoming matches
5. Add standings table (Phase 2)

### **Step 4: Match Detail Pages**

1. Create dynamic match detail template
2. Parse URL parameters
3. Fetch match data from JSON
4. Render match information
5. Add broadcasting channels
6. Add head-to-head statistics

### **Step 5: Team Pages**

1. Create team page template
2. Load team data from JSON
3. Display team information
4. Show upcoming matches
5. Add team statistics

### **Step 6: Under Construction Page**

1. Create `/em-construcao.html`
2. Add contact form
3. Implement form submission (EmailJS or API)
4. Route all non-Paulistão/Carioca tournaments to this page

### **Step 7: Update Homepage**

1. Update `index.html` to link to new pages
2. Add tournament filter
3. Update match cards to link to new URLs
4. Test navigation flow

---

## 📝 Sample Data Files

### `/data/tournaments.json`
```json
{
  "tournaments": [
    {
      "id": "paulistao26",
      "name": "Campeonato Paulista 2026",
      "shortName": "Paulistão",
      "slug": "paulistao26",
      "year": 2026,
      "status": "active",
      "logo": "/assets/campeonatos/paulistao.png",
      "startDate": "2026-01-15",
      "endDate": "2026-04-30"
    },
    {
      "id": "carioca26",
      "name": "Campeonato Carioca 2026",
      "shortName": "Carioca",
      "slug": "carioca26",
      "year": 2026,
      "status": "active",
      "logo": "/assets/campeonatos/carioca.png",
      "startDate": "2026-01-12",
      "endDate": "2026-04-15"
    },
    {
      "id": "mineiro26",
      "name": "Campeonato Mineiro 2026",
      "shortName": "Mineiro",
      "slug": "mineiro26",
      "year": 2026,
      "status": "coming-soon",
      "logo": "/assets/campeonatos/mineiro.png"
    }
  ]
}
```

### `/data/teams.json`
```json
{
  "teams": [
    {
      "id": "saopaulo",
      "name": "São Paulo",
      "slug": "saopaulo",
      "logo": "/assets/times/sao-paulo.png",
      "state": "SP",
      "stadium": "Morumbi",
      "founded": 1930
    },
    {
      "id": "corinthians",
      "name": "Corinthians",
      "slug": "corinthians",
      "logo": "/assets/times/corinthians.png",
      "state": "SP",
      "stadium": "Neo Química Arena",
      "founded": 1910
    },
    {
      "id": "flamengo",
      "name": "Flamengo",
      "slug": "flamengo",
      "logo": "/assets/times/flamengo.png",
      "state": "RJ",
      "stadium": "Maracanã",
      "founded": 1895
    }
  ]
}
```

### `/data/matches.json`
```json
{
  "matches": [
    {
      "id": "paulistao26-saopaulo-vs-corinthians-18-01-2026",
      "tournament": "paulistao26",
      "homeTeam": "saopaulo",
      "awayTeam": "corinthians",
      "matchDate": "2026-01-18T21:30:00-03:00",
      "venue": "Morumbi",
      "status": "scheduled",
      "isLive": false,
      "broadcasting": [
        {
          "channel": "Premiere",
          "logo": "/assets/canais/premiere.png"
        },
        {
          "channel": "HBO Max",
          "logo": "/assets/canais/hbo-max.png"
        }
      ]
    },
    {
      "id": "carioca26-flamengo-vs-vasco-20-01-2026",
      "tournament": "carioca26",
      "homeTeam": "flamengo",
      "awayTeam": "vasco",
      "matchDate": "2026-01-20T16:00:00-03:00",
      "venue": "Maracanã",
      "status": "live",
      "isLive": true,
      "score": {
        "home": 2,
        "away": 1
      },
      "broadcasting": [
        {
          "channel": "SporTV",
          "logo": "/assets/canais/sportv.png"
        }
      ]
    }
  ]
}
```

---

## 🎨 UI/UX Enhancements

### 1. Tournament Page Features
- Tournament logo and hero banner
- Phase indicator (Group Stage, Semifinals, Final)
- Live matches highlighted
- Countdown to next match
- Standings table with position changes
- Top scorers leaderboard
- Match history/results

### 2. Match Detail Features
- Real-time score updates (for live matches)
- Match timeline (goals, cards, substitutions)
- Live text commentary
- Player ratings
- Match statistics (possession, shots, corners)
- Head-to-head history
- Similar upcoming matches recommendation

### 3. Responsive Design
- Mobile-first approach
- Touch-friendly buttons
- Swipeable match carousels
- Collapsible sections
- Fast loading on 3G/4G

---

## 🔒 Security Considerations

### 1. Input Validation
- Sanitize all form inputs
- Validate date formats
- Prevent XSS attacks

### 2. Rate Limiting
- Limit API requests per IP
- Throttle form submissions

### 3. Authentication (Phase 3)
- JWT-based auth for admin panel
- Role-based access control
- Secure password hashing (bcrypt)

---

## 📈 Analytics & Monitoring

### Track Key Metrics:
- Page views per tournament
- Most viewed matches
- Popular teams
- User engagement time
- Form submission rate
- Search queries

### Tools:
- Google Analytics 4
- Plausible Analytics (privacy-focused)
- Custom event tracking

---

## 🚀 Deployment Strategy

### Phase 1 (JSON):
- **Hosting:** GitHub Pages, Netlify, or Vercel
- **Deployment:** Push to `main` branch
- **CDN:** Automatic via hosting provider

### Phase 3 (API):
- **Frontend:** Vercel or Netlify
- **Backend:** Railway, Render, or AWS
- **Database:** MongoDB Atlas or Railway PostgreSQL
- **CI/CD:** GitHub Actions

---

## 📅 Timeline Estimate

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1: JSON + Pages** | 1-2 weeks | Working tournament & match pages |
| **Phase 2: Admin Panel** | 1 week | Form-based data entry |
| **Phase 3: REST API** | 2-3 weeks | Production-ready backend |
| **Phase 4: Scraper** | 2-4 weeks | Automated data updates |

**Total: 6-10 weeks for full implementation**

---

## ✅ Next Steps

1. **Choose Data Update Method** (Recommendation: Start with JSON)
2. **Create data files** in `/data/` directory
3. **Build tournament pages** for Paulistão and Carioca
4. **Implement routing** for dynamic match URLs
5. **Create team pages**
6. **Add under construction page** for other tournaments
7. **Test end-to-end flow**
8. **Deploy to production**

---

## 📞 Questions to Answer

Before starting implementation, please clarify:

1. **Data Update Preference:** Which method do you prefer initially?
   - JSON Files (quick start)
   - Admin Form (user-friendly)
   - REST API (scalable)
   - Web Scraper (automated)

2. **Tournament Scope:** How many teams per tournament?
   - Paulistão: 16 teams?
   - Carioca: 12 teams?

3. **Match Frequency:** How many matches per day?
   - Will affect data update strategy

4. **Admin Users:** How many people will update match data?
   - Single admin → JSON or Admin Form
   - Multiple admins → REST API

5. **Budget:** Any hosting budget for backend?
   - $0 → JSON Files + GitHub Pages
   - $5-20/mo → REST API + Railway/Render

6. **Timeline:** When do you need this live?
   - Urgent (2 weeks) → JSON approach
   - Flexible (6+ weeks) → Full API implementation

---

## 📚 Resources

### Documentation:
- [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [JSON Schema](https://json-schema.org/)
- [REST API Design](https://restfulapi.net/)

### Tools:
- [JSON Editor Online](https://jsoneditoronline.org/)
- [Postman](https://www.postman.com/) (API testing)
- [Mockaroo](https://www.mockaroo.com/) (Mock data generation)

### Inspiration:
- [Flashscore](https://www.flashscore.com.br/)
- [ESPN](https://www.espn.com.br/)
- [Globo Esporte](https://ge.globo.com/)

---

**Document Version:** 1.0
**Last Updated:** January 19, 2026
**Author:** Claude Code
