// ============================================
// ONDE VAI PASSAR FUTEBOL HOJE - App Logic
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
  quickAccessChips: document.querySelectorAll('.team-chip')
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

// === DATA LOADING ===
async function loadData() {
  try {
    const [matchesRes, teamsRes, tournamentsRes, canaisRes] = await Promise.all([
      fetch('data/matches.json'),
      fetch('data/teams.json'),
      fetch('data/tournaments.json'),
      fetch('data/canais.json')
    ]);

    const matchesData = await matchesRes.json();
    const teamsDataRes = await teamsRes.json();
    const tournamentsDataRes = await tournamentsRes.json();
    const canaisDataRes = await canaisRes.json();

    allMatches = matchesData.matches;
    teamsData = teamsDataRes.teams;
    tournamentsData = tournamentsDataRes.tournaments;
    canaisData = canaisDataRes.canais;

    return true;
  } catch (error) {
    console.error('Error loading data:', error);
    return false;
  }
}

// === MATCH CARD COMPONENT ===
function createMatchCard(match) {
  // Get team and tournament data
  const homeTeam = teamsData.find(t => t.id === match.homeTeam || t.slug === match.homeTeam);
  const awayTeam = teamsData.find(t => t.id === match.awayTeam || t.slug === match.awayTeam);
  const tournament = tournamentsData.find(t => t.id === match.tournament || t.slug === match.tournament);

  // Format date and time
  const matchDate = new Date(match.matchDate);
  const time = matchDate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  const dateStr = matchDate.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });

  const liveIndicator = match.isLive
    ? `<div class="live-indicator">
         <span class="live-dot"></span>
         AO VIVO
       </div>`
    : '';

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

  // Score display for live/finished matches (between teams)
  const hasScore = match.score && (match.score.home !== null && match.score.away !== null);
  const centerDisplay = hasScore
    ? `<div class="match-score">
         <span class="score">${match.score.home}</span>
         <span class="score-separator">x</span>
         <span class="score">${match.score.away}</span>
       </div>`
    : `<span class="vs">VS</span>`;

  return `
    <article class="match-card ${match.isLive ? 'live' : ''}" data-match-id="${match.id}">
      <div class="match-header">
        <div class="match-info">
          <span class="date">${dateStr}</span>
          <span class="time">${time}</span>
          <span class="league">${tournament?.shortName || tournament?.name || match.tournament}</span>
        </div>
        ${liveIndicator}
      </div>

      <div class="match-teams">
        <div class="team">
          <img src="${homeTeam?.logo || ''}" alt="${homeTeam?.name || match.homeTeam}" class="team-logo" onerror="this.style.display='none'">
          <span class="team-name">${homeTeam?.name || match.homeTeam}</span>
        </div>

        ${centerDisplay}

        <div class="team">
          <img src="${awayTeam?.logo || ''}" alt="${awayTeam?.name || match.awayTeam}" class="team-logo" onerror="this.style.display='none'">
          <span class="team-name">${awayTeam?.name || match.awayTeam}</span>
        </div>
      </div>

      <div class="match-broadcast">
        <span class="broadcast-label">Onde Assistir:</span>
        <div class="channels">
          ${channelBadges}
        </div>
      </div>
    </article>
  `;
}

// === RENDER FUNCTIONS ===
function renderMatches(matches) {
  elements.matchesContainer.innerHTML = '';

  if (matches.length === 0) {
    elements.emptyState.classList.remove('hidden');
    elements.matchesContainer.classList.add('hidden');
    return;
  }

  elements.emptyState.classList.add('hidden');
  elements.matchesContainer.classList.remove('hidden');

  // Sort matches by matchDate
  const sortedMatches = [...matches].sort((a, b) => {
    return new Date(a.matchDate) - new Date(b.matchDate);
  });

  sortedMatches.forEach(match => {
    elements.matchesContainer.innerHTML += createMatchCard(match);
  });

  // Add click handlers to match cards
  document.querySelectorAll('.match-card').forEach(card => {
    card.addEventListener('click', () => {
      const matchId = card.dataset.matchId;
      const match = allMatches.find(m => m.id == matchId);
      if (match) {
        navigateToMatchDetail(match);
      }
    });
  });
}

function updateDateDisplay() {
  elements.currentDateEl.textContent = formatDate(currentDate);
}

// === FILTER & SEARCH FUNCTIONS ===
function filterMatches() {
  const searchTerm = elements.searchInput?.value || '';
  let matches = [...allMatches];

  // Filter by date ONLY if no team is selected (todos means use date filter)
  if (useDateFilter) {
    matches = matches.filter(match => {
      const matchDate = new Date(match.matchDate);
      return isSameDay(matchDate, currentDate);
    });
  }

  // Filter by tournament
  if (activeTournamentFilter !== 'todos') {
    matches = matches.filter(match => match.tournament === activeTournamentFilter);
  }

  // Filter by team
  if (activeTeamFilter !== 'todos') {
    matches = matches.filter(match => {
      const homeTeam = teamsData.find(t => t.id === match.homeTeam);
      const awayTeam = teamsData.find(t => t.id === match.awayTeam);

      if (!homeTeam && !awayTeam) return false;

      const homeTeamId = match.homeTeam;
      const awayTeamId = match.awayTeam;

      // Match by team ID or slug
      return homeTeamId === activeTeamFilter ||
        awayTeamId === activeTeamFilter ||
        homeTeam?.slug === activeTeamFilter ||
        awayTeam?.slug === activeTeamFilter;
    });
  }

  // Filter by search term
  if (searchTerm) {
    const searchNorm = normalizeString(searchTerm);
    matches = matches.filter(match => {
      const homeTeam = teamsData.find(t => t.id === match.homeTeam);
      const awayTeam = teamsData.find(t => t.id === match.awayTeam);
      const tournament = tournamentsData.find(t => t.id === match.tournament);

      const homeTeamNorm = homeTeam ? normalizeString(homeTeam.name) : '';
      const awayTeamNorm = awayTeam ? normalizeString(awayTeam.name) : '';
      const tournamentNorm = tournament ? normalizeString(tournament.name) : '';
      const channelsNorm = match.broadcasting.map(c => normalizeString(c.channel)).join(' ');

      return homeTeamNorm.includes(searchNorm) ||
        awayTeamNorm.includes(searchNorm) ||
        tournamentNorm.includes(searchNorm) ||
        channelsNorm.includes(searchNorm);
    });
  }

  filteredMatches = matches;
  renderMatches(filteredMatches);
  updateDateSelectorState();
}

function updateDateSelectorState() {
  // Disable date selector when a team is selected
  if (elements.dateSelector) {
    if (useDateFilter) {
      elements.dateSelector.classList.remove('disabled');
    } else {
      elements.dateSelector.classList.add('disabled');
    }
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
function handleSearch(e) {
  filterMatches();
}

function handleTeamFilter(e) {
  const chip = e.target.closest('.team-chip');
  if (!chip) return;

  const team = chip.dataset.team;

  // Update active state
  elements.quickAccessChips.forEach(c => c.classList.remove('active'));
  chip.classList.add('active');

  activeTeamFilter = team;

  // When a team is selected (not "todos"), disable date filter
  // When "todos" is selected, enable date filter
  useDateFilter = (team === 'todos');

  filterMatches();
}

function handleTournamentFilter(e) {
  activeTournamentFilter = e.target.value;
  filterMatches();
}

function handleDateChange(direction) {
  if (!useDateFilter) return; // Don't change date if team filter is active

  if (direction === 'prev') {
    currentDate.setDate(currentDate.getDate() - 1);
  } else {
    currentDate.setDate(currentDate.getDate() + 1);
  }

  updateDateDisplay();
  filterMatches();
}

// === INITIALIZATION ===
async function init() {
  // Get date selector element
  elements.dateSelector = document.querySelector('.date-selector');

  // Set initial date
  updateDateDisplay();

  // Show loading state
  if (elements.loadingState) {
    elements.loadingState.classList.remove('hidden');
  }

  // Load data from JSON files
  const dataLoaded = await loadData();

  if (!dataLoaded) {
    if (elements.emptyState) {
      elements.emptyState.classList.remove('hidden');
      elements.emptyState.innerHTML = '<p>Erro ao carregar dados. Tente novamente mais tarde.</p>';
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

  // Set first chip as active
  if (elements.quickAccessChips.length > 0) {
    elements.quickAccessChips[0].classList.add('active');
  }

  // Event listeners
  if (elements.searchInput) {
    elements.searchInput.addEventListener('input', handleSearch);
  }
  if (elements.prevDayBtn) {
    elements.prevDayBtn.addEventListener('click', () => handleDateChange('prev'));
  }
  if (elements.nextDayBtn) {
    elements.nextDayBtn.addEventListener('click', () => handleDateChange('next'));
  }

  // Tournament filter
  const tournamentFilterEl = document.getElementById('tournamentFilter');
  if (tournamentFilterEl) {
    tournamentFilterEl.addEventListener('change', handleTournamentFilter);
  }

  // Quick access chips (team filter)
  const quickAccessEl = document.getElementById('quickAccess');
  if (quickAccessEl) {
    quickAccessEl.addEventListener('click', handleTeamFilter);
  }

  console.log('⚽ Onde Vai Passar Futebol Hoje - Initialized');
  console.log(`📅 Showing ${allMatches.length} matches`);
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
