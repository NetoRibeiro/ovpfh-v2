// ============================================
// ONDE VAI PASSAR FUTEBOL HOJE - v2.0 App Logic
// Nielsen Heuristics Implementation
// ============================================

// === CHANNEL DATA ===
let canaisData = [];

// Channel name aliases mapping to canonical IDs
const channelAliases = {
  'record': 'record',
  'tv globo': 'globo',
  'globo': 'globo',
  'band': 'band',
  'sbt': 'sbt',
  'rede-tv': 'redetv',
  'redetv': 'redetv',
  'redetv!': 'redetv',
  'tv-cultura': 'tvcultura',
  'tv cultura': 'tvcultura',
  'cultura': 'tvcultura',
  'sportv': 'sportv',
  'premiere': 'premiere',
  'cazetv': 'cazetv',
  'cazétv': 'cazetv',
  'caze tv': 'cazetv',
  'youtube': 'youtube',
  'hbo-max': 'max',
  'hbo max': 'max',
  'max': 'max',
  'disneyplus': 'disneyplus',
  'disney+': 'disneyplus',
  'disney plus': 'disneyplus',
  'goat-tv': 'goattv',
  'goat tv': 'goattv',
  'goattv': 'goattv',
  'tnt': 'tnt',
  'tnt sports': 'tnt'
};

function getChannelData(channelName) {
  const normalizedName = channelName.toLowerCase().trim();
  const canonicalId = channelAliases[normalizedName];
  if (canonicalId && canaisData.length > 0) {
    return canaisData.find(c => c.id === canonicalId || c.slug === canonicalId);
  }
  return null;
}

function getChannelLogo(channelName) {
  const channelData = getChannelData(channelName);
  return channelData?.logo || null;
}

function getChannelUrl(channelName) {
  const channelData = getChannelData(channelName);
  return channelData?.thirdpartyurl || null;
}

// === STATE MANAGEMENT ===
let currentDate = new Date();
let allMatches = [];
let filteredMatches = [];
let activeTeamFilter = 'todos';
let activeTournamentFilter = 'todos';
let teamsData = [];
let tournamentsData = [];
let useDateFilter = true; // When team is selected, this becomes false
let filterHistory = []; // For undo functionality (H3)

// === DOM ELEMENTS ===
const elements = {
  searchInput: document.getElementById('searchInput'),
  currentDateEl: document.getElementById('currentDate'),
  prevDayBtn: document.getElementById('prevDay'),
  nextDayBtn: document.getElementById('nextDay'),
  dateSelector: null, // Will be set after DOM loads
  tournamentFilter: document.getElementById('tournamentFilter'),
  matchesContainer: document.getElementById('matchesContainer'),
  emptyState: document.getElementById('emptyState'),
  loadingState: document.getElementById('loadingState'),
  quickAccessChips: document.querySelectorAll('.team-chip'),
  matchCount: document.getElementById('matchCount'),
  clearFiltersBtn: document.getElementById('clearFilters'),
  resetFiltersBtn: document.getElementById('resetFiltersBtn'),
  sectionTitle: document.getElementById('sectionTitleText'),
  topLeaguesContainer: document.getElementById('topLeaguesContainer'),
  newsContainer: document.getElementById('newsContainer'),
  highlightContainer: document.getElementById('highlightContainer'),
  livescoreContainer: document.getElementById('livescore-widget-container'),
};

// === UTILITY FUNCTIONS ===
function formatDate(date) {
  const options = { weekday: 'long', day: 'numeric', month: 'short' };
  const formatted = date.toLocaleDateString('pt-BR', options);

  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  if (date.toDateString() === today.toDateString()) {
    return 'Hoje, ' + date.toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' });
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return 'Amanhã, ' + date.toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' });
  }

  return formatted.charAt(0).toUpperCase() + formatted.slice(1);
}

function normalizeString(str) {
  return str
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function isSameDay(date1, date2) {
  return date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate();
}

import { getAllMatches, getAllTeams, getAllLeagues, getAllChannels, listenToMatches, migrateLocalDataToFirestore } from './js/data-service.js';

// --- DATA LOADING ---
async function loadData() {
  try {
    // Check if migration is requested (one-time utility)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('migrate')) {
      await migrateLocalDataToFirestore();
      console.log("Migration triggered via URL");
    }

    // Load initial static data from Firestore
    const [teams, leagues, canais] = await Promise.all([
      getAllTeams(),
      getAllLeagues(),
      getAllChannels()
    ]);

    teamsData = teams;
    tournamentsData = leagues; // keeping tournamentsData variable name for now to avoid massive refactor
    canaisData = canais;

    // Set up real-time listener for matches (H1)
    listenToMatches((matches) => {
      allMatches = matches;
      console.log(`🔥 Real-time update: ${matches.length} matches received`);
      filterMatches(); // Re-filter and re-render on any DB change
    });

    return true;
  } catch (error) {
    console.error('Error loading Firestore data:', error);
    return false;
  }
}

// === MATCH ROW COMPONENT (v2.0 Compact) ===
function createMatchRow(match) {
  // Get team and tournament data
  const homeTeam = teamsData.find(t => t.id === match.homeTeam || t.slug === match.homeTeam);
  const awayTeam = teamsData.find(t => t.id === match.awayTeam || t.slug === match.awayTeam);
  const tournament = tournamentsData.find(t => t.id === match.tournament || t.slug === match.tournament);

  // Format date and time
  const matchDate = new Date(match.matchDate);
  const time = matchDate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  const dateStr = matchDate.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });

  const channelBadges = match.broadcasting.map(channel => {
    const logoPath = channel.logo || getChannelLogo(channel.channel);
    const channelUrl = getChannelUrl(channel.channel);
    const logoHtml = logoPath
      ? (channelUrl
        ? `<a href="${channelUrl}" target="_blank" rel="noopener noreferrer" class="channel-logo-link" onclick="event.stopPropagation()"><img src="${logoPath}" alt="${channel.channel}" class="channel-logo"></a>`
        : `<img src="${logoPath}" alt="${channel.channel}" class="channel-logo">`)
      : '';
    return `
      <span class="channel-badge">
        ${logoHtml}
        ${channel.channel}
      </span>
    `;
  }).join('');

  // Score display
  const hasScore = match.score && (match.score.home !== null && match.score.away !== null);
  const scoreDisplay = hasScore
    ? `<span class="score">${match.score.home} - ${match.score.away}</span>`
    : `<span class="vs">VS</span>`;

  return `
    <article class="match-row ${match.isLive ? 'live' : ''}" data-match-id="${match.id}">
      <!-- Line 1: Date, Time and League -->
      <div class="row-line row-meta">
        <span class="meta-item timestamp">${dateStr} • ${time}</span>
        <span class="meta-item league-name">${tournament?.name || match.tournament}</span>
      </div>

      <!-- Line 2: Teams and Score -->
      <div class="row-line row-matchup">
        <div class="row-team home">
          <span class="team-name">${homeTeam?.name || match.homeTeam}</span>
          <img src="${homeTeam?.logo || ''}" alt="" class="team-logo-small">
        </div>
        
        <div class="row-score">
          ${scoreDisplay}
        </div>

        <div class="row-team away">
          <img src="${awayTeam?.logo || ''}" alt="" class="team-logo-small">
          <span class="team-name">${awayTeam?.name || match.awayTeam}</span>
        </div>
      </div>

      <!-- Line 3: Broadcast -->
      <div class="row-line row-broadcast">
        <span class="broadcast-label">Assistir:</span>
        <div class="channels-compact">
          ${channelBadges}
        </div>
      </div>
    </article>
  `;
}

// === RENDER FUNCTIONS ===
function renderMatches(matches) {
  showLoadingSkeletons();

  setTimeout(() => {
    elements.matchesContainer.innerHTML = '';

    if (matches.length === 0) {
      elements.emptyState.classList.remove('hidden');
      elements.matchesContainer.classList.add('hidden');
      updateMatchCount(0);
      return;
    }

    elements.emptyState.classList.add('hidden');
    elements.matchesContainer.classList.remove('hidden');

    // Group matches by tournament
    const grouped = {};
    matches.forEach(match => {
      const tId = match.tournament;
      if (!grouped[tId]) grouped[tId] = [];
      grouped[tId].push(match);
    });

    // Render league groups
    Object.keys(grouped).forEach((tId, index) => {
      const tournament = tournamentsData.find(t => t.id === tId || t.slug === tId);
      const leagueMatches = grouped[tId];

      const groupEl = document.createElement('div');
      groupEl.className = 'league-group animate-fade-in';
      groupEl.style.animationDelay = `${index * 100}ms`;

      groupEl.innerHTML = `
        <div class="league-header">
          <img src="${tournament?.logo || 'assets/campeonatos/default.png'}" alt="" class="league-logo-small">
          <h3 class="league-title">${tournament?.name || tId}</h3>
        </div>
        <div class="league-matches">
          ${leagueMatches.sort((a, b) => new Date(a.matchDate) - new Date(b.matchDate))
          .map(m => createMatchRow(m)).join('')}
        </div>
      `;

      elements.matchesContainer.appendChild(groupEl);
    });

    // Add click handlers
    document.querySelectorAll('.match-row').forEach(row => {
      row.addEventListener('click', () => {
        const matchId = row.dataset.matchId;
        const match = allMatches.find(m => m.id == matchId);
        if (match) navigateToMatchDetail(match);
      });
    });

    updateMatchCount(matches.length);
  }, 200);
}

function updateDateDisplay() {
  elements.currentDateEl.textContent = formatDate(currentDate);
}

// H1: Show loading skeletons
function showLoadingSkeletons() {
  const skeletonHTML = `
    <div class="league-group-skeleton">
      <div class="skeleton" style="height: 40px; margin-bottom: 10px; width: 200px;"></div>
      <div class="skeleton" style="height: 100px; margin-bottom: 20px;"></div>
      <div class="skeleton" style="height: 100px;"></div>
    </div>
  `;
  elements.matchesContainer.innerHTML = skeletonHTML;
  elements.matchesContainer.classList.remove('hidden');
  elements.emptyState.classList.add('hidden');
}

// H1: Update match count display
function updateMatchCount(count) {
  if (!elements.matchCount) return;

  if (count > 0) {
    elements.matchCount.textContent = `${count} ${count === 1 ? 'jogo encontrado' : 'jogos encontrados'}`;
    elements.matchCount.classList.remove('hidden');
  } else {
    elements.matchCount.classList.add('hidden');
  }
}

// H1: Update section title based on filters
function updateSectionTitle() {
  if (!elements.sectionTitle) return;

  let title = 'Jogos';

  const today = new Date();
  if (isSameDay(currentDate, today)) {
    title = 'Jogos de Hoje';
  } else {
    title = `Jogos de ${formatDate(currentDate)}`;
  }

  elements.sectionTitle.textContent = title;
}

// === SIDEBAR RENDERING ===
function renderTopLeagues() {
  if (!elements.topLeaguesContainer) return;

  if (tournamentsData.length === 0) {
    elements.topLeaguesContainer.innerHTML = '<div class="empty-pref" style="padding: var(--space-4); font-size: var(--text-sm);">Nenhum campeonato ativo.</div>';
    return;
  }

  // Filter by year (2026 is the target year)
  const targetYear = 2026;
  const leagues = tournamentsData
    .filter(l => l.year === targetYear || (l.name && l.name.includes(targetYear.toString())))
    .sort((a, b) => (a.name || '').localeCompare(b.name || ''));

  if (leagues.length === 0) {
    elements.topLeaguesContainer.innerHTML = `<div class="empty-pref" style="padding: var(--space-4); font-size: var(--text-sm);">Nenhum campeonato de ${targetYear} ativo.</div>`;
    return;
  }

  elements.topLeaguesContainer.innerHTML = leagues.map(league => `
    <a href="#" class="sidebar-nav-item" data-league-id="${league.id}">
      <img src="${league.logo || 'assets/campeonatos/default.png'}" alt="" onerror="this.src='assets/campeonatos/default.png'">
      <span>${league.name}</span>
    </a>
  `).join('');

  // Add click handlers
  elements.topLeaguesContainer.querySelectorAll('.sidebar-nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const leagueId = item.dataset.leagueId;
      console.log(`Filtering by league: ${leagueId}`);
      // Highlight selection
      elements.topLeaguesContainer.querySelectorAll('.sidebar-nav-item').forEach(el => el.classList.remove('active'));
      item.classList.add('active');

      // Filter current matches
      activeTournamentFilter = leagueId;
      filterMatches();
    });
  });
}

function renderHighlight() {
  if (!elements.highlightContainer) return;

  const highlight = {
    title: "Mbappé brilha e Real Madrid assume a liderança",
    tag: "DESTAQUE",
    image: "https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=600&auto=format&fit=crop",
    url: "#"
  };

  elements.highlightContainer.innerHTML = `
    <div class="highlight-card" onclick="window.location.href='${highlight.url}'">
      <img src="${highlight.image}" alt="">
      <div class="highlight-content">
        <span class="highlight-tag">${highlight.tag}</span>
        <h3 class="highlight-title">${highlight.title}</h3>
      </div>
    </div>
  `;
}

function renderNews() {
  if (!elements.newsContainer) return;

  const news = [
    {
      title: "Brasileirão 2026: Confira a tabela completa e jogos do final de semana",
      time: "Há 2 horas",
      image: "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=200&auto=format&fit=crop"
    },
    {
      title: "Mercado da Bola: Neymar pode retornar ao Santos em julho",
      time: "Há 4 horas",
      image: "https://images.unsplash.com/photo-1624891151634-192064166649?q=80&w=200&auto=format&fit=crop"
    },
    {
      title: "Champions League: Sorteio define confrontos das quartas de final",
      time: "Há 6 horas",
      image: "https://images.unsplash.com/photo-1543351611-58f69d7c1781?q=80&w=200&auto=format&fit=crop"
    }
  ];

  elements.newsContainer.innerHTML = news.map(item => `
    <div class="news-item" onclick="window.location.href='#'">
      <img src="${item.image}" alt="" class="news-item-img">
      <div class="news-item-content">
        <h3 class="news-item-title">${item.title}</h3>
        <span class="news-item-time">${item.time}</span>
      </div>
    </div>
  `).join('');
}

async function loadLivescoreWidget(date = new Date()) {
  if (!elements.livescoreContainer) return;

  try {
    const response = await fetch('data/liveScores.json');
    if (!response.ok) throw new Error('Failed to load livescore config');

    const data = await response.json();
    const config = data.widget;

    if (!config) return;

    // Format date as YYYY-MM-DD
    const formattedDate = date.toISOString().split('T')[0];

    // Cleanup previous widget and script
    elements.livescoreContainer.innerHTML = '';
    const oldScript = document.getElementById('livescore-widget-script');
    if (oldScript) oldScript.remove();

    // Create widget div
    const widgetDiv = document.createElement('div');
    widgetDiv.id = config.id;
    widgetDiv.className = config.className;
    widgetDiv.setAttribute('data-w', config.dataW);
    // Setting data-date allows the widget to load for a specific day
    widgetDiv.setAttribute('data-date', formattedDate);
    elements.livescoreContainer.appendChild(widgetDiv);

    // Load external script
    const script = document.createElement('script');
    script.id = 'livescore-widget-script';
    script.type = 'text/javascript';
    script.src = config.scriptSrc;
    document.body.appendChild(script);

    console.log(`✅ Livescore Widget updated for date: ${formattedDate}`);
  } catch (error) {
    console.error('❌ Error loading Livescore Widget:', error);
    elements.livescoreContainer.innerHTML = '<p style="color: var(--text-tertiary); text-align: center;">Erro ao carregar placar ao vivo.</p>';
  }
}

// === FILTER & SEARCH FUNCTIONS ===
function filterMatches() {
  let matches = [...allMatches];

  // Primary filter is now just the Date
  matches = matches.filter(match => {
    const matchDate = new Date(match.matchDate);
    return isSameDay(matchDate, currentDate);
  });

  filteredMatches = matches;
  renderMatches(filteredMatches);
  updateDateSelectorState();
  updateSectionTitle();
}

function updateDateSelectorState() {
  if (elements.dateSelector) {
    elements.dateSelector.classList.remove('disabled');
  }
}

// === NAVIGATION ===
function navigateToMatchDetail(match) {
  if (match.matchURL) {
    window.location.href = match.matchURL;
    return;
  }
  const url = router.buildMatchURL(
    match.tournament,
    match.homeTeam,
    match.awayTeam,
    match.matchDate
  );
  window.location.href = url;
}

// === EVENT HANDLERS ===
function handleDateChange(direction) {
  if (direction === 'prev') {
    currentDate.setDate(currentDate.getDate() - 1);
  } else {
    currentDate.setDate(currentDate.getDate() + 1);
  }

  updateDateDisplay();
  filterMatches();

  // Update Widget
  loadLivescoreWidget(currentDate);
}

// === INITIALIZATION ===
async function init() {
  console.log('🚀 Initializing OVPFH v2.0...');

  // Get date selector element
  elements.dateSelector = document.querySelector('.date-selector');

  // Set initial date
  updateDateDisplay();

  // Show loading state
  if (elements.loadingState) {
    elements.loadingState.classList.remove('hidden');
  }

  // Safety timeout: If data doesn't load in 8 seconds, show error/empty state
  const loadTimeout = setTimeout(() => {
    if (allMatches.length === 0) {
      console.warn('⚠️ Data loading timed out');
      if (elements.loadingState) elements.loadingState.classList.add('hidden');
      if (elements.emptyState) {
        elements.emptyState.classList.remove('hidden');
        elements.emptyState.innerHTML = '<h3>Tempo de carregamento excedido</h3><p>O servidor está demorando para responder. Por favor, recarregue a página.</p>';
      }
    }
  }, 8000);

  // Load data from JSON files
  const dataLoaded = await loadData();
  clearTimeout(loadTimeout);

  if (!dataLoaded) {
    console.error('❌ Data loading failed');
    if (elements.emptyState) {
      elements.emptyState.classList.remove('hidden');
      elements.emptyState.innerHTML = '<h3>Erro ao carregar dados</h3><p>Não foi possível conectar ao banco de dados. Tente novamente mais tarde.</p>';
    }
    if (elements.loadingState) {
      elements.loadingState.classList.add('hidden');
    }
    return;
  }

  // Hide loading state
  if (elements.loadingState) {
    elements.loadingState.classList.add('hidden');
  }

  // Filter and render matches for today
  filterMatches();

  // Render sidebars
  try {
    renderTopLeagues();
    renderHighlight();
    renderNews();
  } catch (err) {
    console.error('Error rendering sidebars:', err);
  }

  // Load Livescore Widget
  try {
    loadLivescoreWidget(currentDate);
  } catch (err) {
    console.warn('Livescore widget failed to load:', err);
  }

  // Date listeners
  if (elements.prevDayBtn) {
    elements.prevDayBtn.addEventListener('click', () => handleDateChange('prev'));
  }
  if (elements.nextDayBtn) {
    elements.nextDayBtn.addEventListener('click', () => handleDateChange('next'));
  }

  console.log('⚽ Onde Vai Passar Futebol Hoje v2.0 (Grouped) - Initialized');
  console.log(`📅 Loaded ${allMatches.length} matches`);
  console.log('✨ Nielsen Heuristics: H1 (Status), H3 (Control), H7 (Efficiency)');
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
