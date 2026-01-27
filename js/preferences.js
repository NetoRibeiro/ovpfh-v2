/**
 * OVPFH v2.0 - Preferences Page Logic
 * Manages user selection and Firestore integration
 */

import {
    getAllTeams,
    getAllLeagues,
    getUserPreferences,
    saveUserPreferences
} from './data-service.js';
import { onAuthStateChange, getUserDisplayName, getUserPhotoURL } from './auth.js';

// === STATE ===
let currentUser = null;
let allTeams = [];
let allTournaments = [];
let userPrefs = {
    countries: [],
    leagues: [],
    teams: []
};

const staticCountries = [
    { id: 'brasil', name: 'Brasil', flag: '🇧🇷' },
    { id: 'espanha', name: 'Espanha', flag: '🇪🇸' },
    { id: 'inglaterra', name: 'Inglaterra', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
    { id: 'alemanha', name: 'Alemanha', flag: '🇩🇪' },
    { id: 'italia', name: 'Itália', flag: '🇮🇹' },
    { id: 'franca', name: 'França', flag: '🇫🇷' },
    { id: 'argentina', name: 'Argentina', flag: '🇦🇷' },
    { id: 'portugal', name: 'Portugal', flag: '🇵🇹' }
];

// === DOM ELEMENTS ===
const elements = {
    userProfile: document.getElementById('userProfile'),
    countriesGrid: document.getElementById('countriesGrid'),
    leaguesGrid: document.getElementById('leaguesGrid'),
    teamsGrid: document.getElementById('teamsGrid'),
    saveBtn: document.getElementById('saveBtn'),
    cancelBtn: document.getElementById('cancelBtn'),
    toastContainer: document.getElementById('toastContainer'),
    countrySearch: document.getElementById('countrySearch'),
    leagueSearch: document.getElementById('leagueSearch'),
    teamSearch: document.getElementById('teamSearch')
};

// === INITIALIZATION ===
async function init() {
    // 1. Auth check
    onAuthStateChange(async (user) => {
        if (!user) {
            // Redirect to home if not logged in
            window.location.href = 'index.html';
            return;
        }

        currentUser = user;
        updateUserHeader();

        // 2. Load data
        await loadAllData();

        // 3. Render initial UI
        renderPreferences();
    });

    // 4. Setup listeners
    elements.saveBtn.addEventListener('click', handleSave);
    elements.cancelBtn.addEventListener('click', () => window.location.href = 'index.html');

    // 5. Search listeners
    elements.countrySearch.addEventListener('input', (e) => renderCountries(e.target.value));
    elements.leagueSearch.addEventListener('input', (e) => renderLeagues(e.target.value));
    elements.teamSearch.addEventListener('input', (e) => renderTeams(e.target.value));
}

async function loadAllData() {
    try {
        const [teams, leagues, prefs] = await Promise.all([
            getAllTeams(),
            getAllLeagues(),
            getUserPreferences(currentUser.uid)
        ]);

        allTeams = teams || [];
        allTournaments = leagues || [];
        if (prefs) userPrefs = prefs;

        console.log(`✅ Data loaded: ${allTeams.length} teams, ${allTournaments.length} tournaments`);

        if (allTournaments.length === 0) {
            console.warn('⚠️ No tournaments found in Firestore. Check your collection name ("tournaments").');
        }
    } catch (error) {
        console.error('❌ Error loading data:', error);
        showToast('Erro ao carregar dados', 'error');
    }
}

// === RENDER FUNCTIONS ===

function updateUserHeader() {
    if (!elements.userProfile) return;

    const photoURL = getUserPhotoURL();
    const displayName = getUserDisplayName();

    elements.userProfile.innerHTML = `
        <div style="text-align: right;">
            <div style="font-weight: var(--weight-bold); color: var(--text-primary);">${displayName}</div>
            <div style="font-size: var(--text-xs); color: var(--text-tertiary);">${currentUser.email}</div>
        </div>
        <div class="user-avatar" style="width: 40px; height: 40px;">
            ${photoURL ? `<img src="${photoURL}" alt="" style="width: 100%; border-radius: 50%;">` : displayName.substring(0, 2).toUpperCase()}
        </div>
    `;
}

function renderPreferences() {
    renderCountries();
    renderLeagues();
    renderTeams();
}

function renderCountries(filter = '') {
    const query = normalizeString(filter);
    const filtered = staticCountries.filter(c => normalizeString(c.name).includes(query));

    if (filtered.length === 0) {
        elements.countriesGrid.innerHTML = '<div class="empty-pref">Nenhum país encontrado.</div>';
        return;
    }

    elements.countriesGrid.innerHTML = filtered.map(country => `
        <div class="pref-item ${userPrefs.countries?.includes(country.id) ? 'active' : ''}" 
             onclick="this.classList.toggle('active'); updatePref('countries', '${country.id}')">
            <span>${country.flag}</span>
            <span>${country.name}</span>
        </div>
    `).join('');
}

function renderLeagues(filter = '') {
    const query = normalizeString(filter);
    const targetYear = 2026;

    // Filter by year and search query
    const filtered = (allTournaments || []).filter(l => {
        const matchesQuery = normalizeString(l.name || '').includes(query) ||
            normalizeString(l.shortName || '').includes(query) ||
            normalizeString(l.id || '').includes(query);
        const matchesYear = l.year === targetYear || (l.name && l.name.includes(targetYear.toString()));
        return matchesQuery && matchesYear;
    });

    if (filtered.length === 0) {
        elements.leaguesGrid.innerHTML = `<div class="empty-pref">${allTournaments.length === 0 ? 'Nenhum campeonato encontrado no banco de dados.' : `Nenhum campeonato de ${targetYear} corresponde ao filtro.`}</div>`;
        return;
    }

    elements.leaguesGrid.innerHTML = filtered.map(league => `
        <div class="pref-item ${userPrefs.leagues?.includes(league.id) ? 'active' : ''}" 
             onclick="this.classList.toggle('active'); updatePref('leagues', '${league.id}')">
            <img src="${league.logo || 'assets/campeonatos/default.png'}" alt="" onerror="this.src='assets/campeonatos/default.png'">
            <span>${league.shortName || league.name || league.id}</span>
        </div>
    `).join('');
}

function renderTeams(filter = '') {
    const query = normalizeString(filter);
    const sortedTeams = [...allTeams].sort((a, b) => a.name.localeCompare(b.name));
    const filtered = sortedTeams.filter(t => normalizeString(t.name).includes(query));

    if (filtered.length === 0) {
        elements.teamsGrid.innerHTML = '<div class="empty-pref">Nenhum time encontrado.</div>';
        return;
    }

    elements.teamsGrid.innerHTML = filtered.map(team => `
        <div class="pref-item ${userPrefs.teams?.includes(team.id) ? 'active' : ''}" 
             onclick="this.classList.toggle('active'); updatePref('teams', '${team.id}')">
            <img src="${team.logo}" alt="">
            <span>${team.name}</span>
        </div>
    `).join('');
}

function normalizeString(str) {
    if (!str) return '';
    return str
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
}

// === LOGIC ===

window.updatePref = (category, id) => {
    if (!userPrefs[category]) userPrefs[category] = [];

    const index = userPrefs[category].indexOf(id);
    if (index > -1) {
        userPrefs[category].splice(index, 1);
    } else {
        userPrefs[category].push(id);
    }
};

async function handleSave() {
    elements.saveBtn.disabled = true;
    elements.saveBtn.textContent = '⌛ Salvando...';

    try {
        const result = await saveUserPreferences(currentUser.uid, userPrefs);
        if (result.success) {
            showToast('Preferências salvas com sucesso!', 'success');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        } else {
            console.error('❌ Firestore Error:', result.error);
            showToast(`Erro ao salvar: ${result.error}`, 'error');
            elements.saveBtn.disabled = false;
            elements.saveBtn.textContent = '💾 Salvar Preferências';
        }
    } catch (error) {
        console.error('❌ Unexpected Save error:', error);
        showToast('Erro inesperado ao salvar', 'error');
        elements.saveBtn.disabled = false;
        elements.saveBtn.textContent = '💾 Salvar Preferências';
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: var(--space-3);">
        <span>${type === 'success' ? '✓' : '✕'}</span>
        <span>${message}</span>
      </div>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Start
init();
