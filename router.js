// Router.js - Client-side routing for match pages
// Handles URLs like: /paulistao26/saopaulo-vs-corinthians/18-01-2026

class Router {
  constructor() {
    this.teamsData = null;
    this.tournamentsData = null;
    this.matchesData = null;
  }

  // Load all data files
  async loadData() {
    try {
      const [teams, tournaments, matches] = await Promise.all([
        fetch('/data/teams.json').then(r => r.json()),
        fetch('/data/tournaments.json').then(r => r.json()),
        fetch('/data/matches.json').then(r => r.json())
      ]);

      this.teamsData = teams.teams;
      this.tournamentsData = tournaments.tournaments;
      this.matchesData = matches.matches;

      return true;
    } catch (error) {
      console.error('Error loading data:', error);
      return false;
    }
  }

  // Parse match URL: /paulistao26/saopaulo-vs-corinthians/18-01-2026
  parseMatchURL(pathname) {
    // Remove leading/trailing slashes and split
    const parts = pathname.replace(/^\/|\/$/g, '').split('/');

    if (parts.length !== 3) return null;

    const [tournamentSlug, teamsSlug, dateSlug] = parts;

    // Validate format
    if (!teamsSlug.includes('-vs-')) return null;

    const teams = teamsSlug.split('-vs-');
    if (teams.length !== 2) return null;

    const [homeSlug, awaySlug] = teams;

    // Parse date: dd-mm-yyyy
    const dateParts = dateSlug.split('-');
    if (dateParts.length !== 3) return null;

    const [day, month, year] = dateParts;

    return {
      tournament: tournamentSlug,
      homeTeam: homeSlug,
      awayTeam: awaySlug,
      date: `${year}-${month}-${day}`,
      dateSlug: dateSlug
    };
  }

  // Build match URL from components
  buildMatchURL(tournament, homeTeam, awayTeam, date) {
    // date format: YYYY-MM-DD or Date object
    let dateStr;
    if (date instanceof Date) {
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      dateStr = `${day}-${month}-${year}`;
    } else {
      // Assume YYYY-MM-DD... format
      const datePart = date.split('T')[0];
      const [year, month, day] = datePart.split('-');
      dateStr = `${day}-${month}-${year}`;
    }

    return `/${tournament}/${dateStr}/${homeTeam}-vs-${awayTeam}/`;
  }

  // Find match by URL parameters
  findMatchByURL(params) {
    if (!this.matchesData) return null;

    const matchId = `${params.tournament}-${params.homeTeam}-vs-${params.awayTeam}-${params.dateSlug}`;

    return this.matchesData.find(match => match.id === matchId);
  }

  // Get team by slug
  getTeamBySlug(slug) {
    if (!this.teamsData) return null;
    return this.teamsData.find(team => team.slug === slug || team.id === slug);
  }

  // Get tournament by slug
  getTournamentBySlug(slug) {
    if (!this.tournamentsData) return null;
    return this.tournamentsData.find(t => t.slug === slug || t.id === slug);
  }

  // Get all matches for a tournament
  getMatchesByTournament(tournamentId) {
    if (!this.matchesData) return [];
    return this.matchesData.filter(match => match.tournament === tournamentId);
  }

  // Get all matches for a team
  getMatchesByTeam(teamSlug) {
    if (!this.matchesData) return [];
    return this.matchesData.filter(match =>
      match.homeTeam === teamSlug || match.awayTeam === teamSlug
    );
  }

  // Get upcoming matches for a team
  getUpcomingMatchesByTeam(teamSlug, limit = 5) {
    const now = new Date();
    return this.getMatchesByTeam(teamSlug)
      .filter(match => new Date(match.matchDate) >= now || match.isLive)
      .sort((a, b) => new Date(a.matchDate) - new Date(b.matchDate))
      .slice(0, limit);
  }

  // Get recent matches for a team
  getRecentMatchesByTeam(teamSlug, limit = 5) {
    const now = new Date();
    return this.getMatchesByTeam(teamSlug)
      .filter(match => new Date(match.matchDate) < now && !match.isLive)
      .sort((a, b) => new Date(b.matchDate) - new Date(a.matchDate))
      .slice(0, limit);
  }

  // Get upcoming matches for a tournament
  getUpcomingMatchesByTournament(tournamentId, limit = 10) {
    const now = new Date();
    return this.getMatchesByTournament(tournamentId)
      .filter(match => new Date(match.matchDate) >= now || match.isLive)
      .sort((a, b) => new Date(a.matchDate) - new Date(b.matchDate))
      .slice(0, limit);
  }

  // Get live matches
  getLiveMatches() {
    if (!this.matchesData) return [];
    return this.matchesData.filter(match => match.isLive);
  }

  // Format date to Portuguese
  formatDateToPT(dateStr) {
    const date = new Date(dateStr);
    const options = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };

    return date.toLocaleDateString('pt-BR', options);
  }

  // Format time only
  formatTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // Format date only (short)
  formatDateShort(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short'
    });
  }

  // Normalize string for search (remove accents, lowercase)
  normalizeString(str) {
    return str
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  // Search matches
  searchMatches(query) {
    if (!this.matchesData || !query) return this.matchesData || [];

    const normalized = this.normalizeString(query);

    return this.matchesData.filter(match => {
      const homeTeam = this.getTeamBySlug(match.homeTeam);
      const awayTeam = this.getTeamBySlug(match.awayTeam);
      const tournament = this.getTournamentBySlug(match.tournament);

      const searchStr = this.normalizeString(
        `${homeTeam?.name || ''} ${awayTeam?.name || ''} ${tournament?.name || ''}`
      );

      return searchStr.includes(normalized);
    });
  }

  // Check if tournament is active
  isTournamentActive(tournamentSlug) {
    const tournament = this.getTournamentBySlug(tournamentSlug);
    return tournament && tournament.status === 'active';
  }

  // Get teams by tournament
  getTeamsByTournament(tournamentId) {
    if (!this.teamsData) return [];
    return this.teamsData.filter(team =>
      team.tournaments && team.tournaments.includes(tournamentId)
    );
  }
}

// Create global router instance
const router = new Router();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Router;
}
