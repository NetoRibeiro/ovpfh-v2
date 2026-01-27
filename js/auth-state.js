/**
 * OVPFH v2.0 - Authentication State Manager
 * Manages authentication state and UI updates
 */

import { onAuthStateChange, signOut, getCurrentUser, getUserDisplayName, getUserPhotoURL } from './auth.js';
import { openAuthModal } from './auth-modal.js';

class AuthStateManager {
    constructor() {
        this.user = null;
        this.init();
    }

    init() {
        // Listen to auth state changes
        onAuthStateChange((user) => {
            this.user = user;

            // If user is logged in but not verified, sign them out and show verification screen
            if (user && !user.emailVerified) {
                import('./verification-screen.js').then(module => {
                    module.showVerificationScreen(user.email);
                });
                signOut(); // Ensure they are signed out as per requirements
                return;
            }

            this.updateUI();

            if (user) {
                console.log('👤 User logged in:', user.email);
            } else {
                console.log('👤 User logged out');
            }
        });

        // Setup UI event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Login button click
        const loginBtn = document.getElementById('headerLoginBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', () => openAuthModal('login'));
        }

        // User menu toggle
        const userMenuBtn = document.getElementById('userMenuBtn');
        if (userMenuBtn) {
            userMenuBtn.addEventListener('click', () => this.toggleUserMenu());
        }

        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // Close user menu when clicking outside
        document.addEventListener('click', (e) => {
            const userMenu = document.getElementById('userMenu');
            const userMenuBtn = document.getElementById('userMenuBtn');

            if (userMenu && !userMenu.contains(e.target) && e.target !== userMenuBtn) {
                userMenu.classList.add('hidden');
            }
        });
    }

    updateUI() {
        const loginBtn = document.getElementById('headerLoginBtn');
        const userMenu = document.getElementById('userMenuContainer');

        if (this.user) {
            // User is logged in
            if (loginBtn) loginBtn.classList.add('hidden');
            if (userMenu) {
                userMenu.classList.remove('hidden');
                this.updateUserMenu();
            }
        } else {
            // User is logged out
            if (loginBtn) loginBtn.classList.remove('hidden');
            if (userMenu) userMenu.classList.add('hidden');
        }
    }

    updateUserMenu() {
        const userName = document.getElementById('userName');
        const userEmail = document.getElementById('userEmail');
        const userAvatar = document.getElementById('userAvatar');

        if (userName) {
            userName.textContent = getUserDisplayName();
        }

        if (userEmail) {
            userEmail.textContent = this.user.email;
        }

        if (userAvatar) {
            const photoURL = getUserPhotoURL();
            if (photoURL) {
                userAvatar.innerHTML = `<img src="${photoURL}" alt="Avatar" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
            } else {
                const initials = getUserDisplayName().substring(0, 2).toUpperCase();
                userAvatar.textContent = initials;
            }
        }
    }

    toggleUserMenu() {
        const userMenu = document.getElementById('userMenu');
        if (userMenu) {
            userMenu.classList.toggle('hidden');
        }
    }

    async handleLogout() {
        const result = await signOut();

        if (result.success) {
            this.showToast('Logout realizado com sucesso', 'success');

            // Close user menu
            const userMenu = document.getElementById('userMenu');
            if (userMenu) {
                userMenu.classList.add('hidden');
            }
        } else {
            this.showToast('Erro ao fazer logout', 'error');
        }
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type} animate-slide-in-right`;
        toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: var(--space-3);">
        <span style="font-size: var(--text-lg);">${type === 'success' ? '✓' : '✕'}</span>
        <span style="font-weight: var(--weight-semibold);">${message}</span>
      </div>
    `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('animate-fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    isLoggedIn() {
        return this.user !== null;
    }

    getUser() {
        return this.user;
    }
}

// Initialize auth state manager
const authStateManager = new AuthStateManager();

// Export for use in other scripts
export default authStateManager;
export function isUserLoggedIn() {
    return authStateManager.isLoggedIn();
}

export function getAuthUser() {
    return authStateManager.getUser();
}
