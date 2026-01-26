# Implementation Plan: Onde Vai Passar Futebol Hoje

A high-performance, mobile-first sports utility website showing today's football matches and their broadcasting channels, designed with Nielsen's usability heuristics and modern dark-mode aesthetics.

## User Review Required

> [!IMPORTANT]
> **team/channel logo**: Do not create the team/channel logo, use the ones provided by Wikipedia, Google or any other source.

> [!IMPORTANT]
> **Audience**: The website is designed for Brazilian football fans, all /urls to be create, use Portuguese language for a better SEO indexability. Please review the design and functionality of the website to ensure it meets your requirements.

> [!IMPORTANT]
> **Design Approach**: Architecture: Hybrid Performance Model (SPA + Dynamic SSR) The platform will utilize a Hybrid Performance Architecture. The homepage and navigation will function as a Single-Page Application (SPA) using vanilla JavaScript and client-side routing to provide instantaneous, app-like transitions. However, each match will also have a dedicated Server-Side Rendered (SSR) URL (e.g., /onde-assistir-flamengo-x-bangu/) to ensure maximum SEO indexability and keyword matching for specific match-day searches.

Visual Language: High-Contrast "Stadium" Aesthetic The UI will adopt a Dark Mode aesthetic (Navy Blue #001A33 and Deep Black #000000) to reduce eye strain and mimic professional sports broadcasting interfaces. High-contrast accents in Neon Yellow (#F2FF00) and Crisp White will be used for critical action items, such as "LIVE" status indicators and "Where to Watch" buttons.

UX Philosophy: Heuristics-Driven Utility The interface will prioritize Heuristic #6 (Recognition over Recall) by utilizing official broadcast and team logos, allowing fans to identify games and channels in milliseconds without reading heavy text. Heuristic #1 (Visibility of System Status) will be maintained through real-time score updates and pulsing live indicators.

> [!IMPORTANT]
> **Data Source**: The initial implementation will use mock data for demonstration. For production, you'll need to integrate with the Sportmonks API and map the data to WordPress custom fields as mentioned in your requirements.

> [!IMPORTANT]
> **URL & Metadata Strategy**: To capture the specific trends from your data, each match page will follow this strict SEO-optimized structure:
URL Pattern: ondevapassarfutebolhoje.com.br/onde-assistir-[time-a]-x-[time-b]-[data]/
Targeting: This structure captures long-tail searches like "north x atlético-mg onde assistir" or "bangu x flamengo escalação".

> [!NOTE]
> **WordPress Integration**: After approval, I'll provide guidance on how to integrate this design with Elementor/Gutenberg using dynamic tags for your API data.

## Proposed Changes

### Design System & Assets

#### [NEW] [assets/](file:///c:/Antigravity/ONDEVAIPASSARFUTEBOLHOJE/assets/)
Creating an assets directory structure for logos and images:
- `assets/times/` - Team crest images (Palmeiras, Corinthians, Flamengo, etc.)
- `assets/campeonatos/` - League crest images (Paulistão, Carioca, Brasileirão, etc.)
- `assets/canais/` - Broadcasting channel logos (CazéTV, Rede Record, SporTV, etc.)

#### [NEW] [styles.css](file:///c:/Antigravity/ONDEVAIPASSARFUTEBOLHOJE/styles.css)
Complete design system implementation:
- **Color Tokens**: Primary (#001A33 Deep Navy), Accent (#FFD700 Gold), Live (#FF0000), Success (#00FF41 Neon Green)
- **Typography System**: Inter for headings (bold, condensed), system UI for body text
- **Component Styles**: Match cards, LIVE indicators, team chips, channel badges
- **Animations**: Pulsing LIVE dot, smooth hover effects, micro-interactions
- **Mobile-First Layout**: Card-based design with responsive breakpoints

---

### Core Application

#### [NEW] [index.html](file:///c:/Antigravity/ONDEVAIPASSARFUTEBOLHOJE/index.html)
Main application structure with semantic HTML5:
- **SEO Optimization**: Proper meta tags, title, description, Open Graph tags
- **Sticky Header**: Date selector and search bar with unique IDs for testing
- **Quick Access Chips**: Top teams (Palmeiras, Corinthians, Flamengo) for one-click filtering
- **Match Feed**: Vertical list of match cards sorted by time
- **Accessibility**: ARIA labels, semantic elements, keyboard navigation

#### [NEW] [app.js](file:///c:/Antigravity/ONDEVAIPASSARFUTEBOLHOJE/app.js)
Core application logic:
- **Client-Side Routing**: Hash-based routing for Home, League, and Match Detail pages
- **Match Card Component**: Reusable component with time/status, teams, broadcast channels
- **LIVE Status System**: Real-time detection and pulsing indicator
- **Search & Filter**: Instant search by team name, league filtering
- **Date Selection**: Navigate between different dates
- **Mock Data**: Realistic sample data for demonstration

---

### Additional Pages

#### [NEW] [campeonatos.html](file:///c:/Antigravity/ONDEVAIPASSARFUTEBOLHOJE/campeonatos.html)
League-specific filtered view:
- Filter matches by competition (Paulistão, Carioca, Brasileirão, etc.)
- Same match card component for consistency
- Breadcrumb navigation back to home

#### [NEW] [detalhes-do-jogo.html](file:///c:/Antigravity/ONDEVAIPASSARFUTEBOLHOJE/detalhes-do-jogo.html)
Deep-dive match page with SEO-optimized content:
- **Escalações** (Team Lineups) section
- **Onde Assistir** (Where to Watch) with all broadcasting options
- Match statistics and timeline
- Rich keyword integration for SEO

## Verification Plan

### Automated Tests
- Validate HTML5 semantic structure
- Check CSS for mobile-first responsive breakpoints
- Verify all interactive elements have unique IDs
- Test search and filter functionality

### Manual Verification
1. **Visual Design Review**: Confirm dark mode aesthetics, color contrast, typography
2. **Heuristics Validation**:
   - ✓ LIVE indicator visibility (Heuristic #1)
   - ✓ Channel logos vs text (Heuristic #2)
   - ✓ Consistent match card layout (Heuristic #4)
   - ✓ Quick-access team chips (Heuristic #6)
3. **Mobile Testing**: Test on various screen sizes using browser dev tools
4. **Performance**: Verify fast loading times and smooth animations
5. **SEO**: Check meta tags, heading hierarchy, semantic HTML

### Browser Testing
- Test interactive features (search, filter, navigation)
- Verify LIVE indicator animation
- Test date selector and team chip filtering
- Validate responsive layout on mobile/tablet/desktop
