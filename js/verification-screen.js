/**
 * OVPFH v2.0 - Email Verification Screen
 * Handles email verification UI and logic
 */

import { resendVerificationEmail } from './auth.js';

class VerificationScreen {
    constructor() {
        this.screen = null;
        this.userEmail = '';
        this.resendCooldown = 60; // seconds
        this.resendTimer = null;
        this.init();
    }

    init() {
        this.createScreen();
        this.setupEventListeners();
    }

    createScreen() {
        const screenHTML = `
      <div id="verificationScreen" class="verification-screen hidden">
        <div class="verification-container">
          <!-- Email Icon -->
          <div class="verification-icon">
            📧
          </div>

          <!-- Title -->
          <h1 class="verification-title">Verifique seu E-mail</h1>

          <!-- Message -->
          <p class="verification-message">
            We have sent you a verification email to <span class="verification-email" id="verificationEmail"></span>. Please verify it and log in.
          </p>

          <!-- Instructions -->
          <div class="verification-instructions">
            <p style="margin: 0;">
              Por favor, verifique sua caixa de entrada (e spam) e clique no link de verificação para ativar sua conta.
            </p>
          </div>

          <!-- Actions -->
          <div class="verification-actions">
            <button id="verificationLoginBtn" class="btn btn-primary">
              Login
            </button>
            
            <button id="verificationBackBtn" class="btn btn-outline">
              Voltar ao Início
            </button>
          </div>

          <!-- Resend Email -->
          <div class="resend-info">
            Não recebeu o e-mail? 
            <a href="#" id="resendVerificationLink" class="resend-link">
              Reenviar
            </a>
            <span id="resendCooldownText" class="hidden"></span>
          </div>
        </div>
      </div>
    `;

        document.body.insertAdjacentHTML('beforeend', screenHTML);
        this.screen = document.getElementById('verificationScreen');
    }

    setupEventListeners() {
        // Login button
        const loginBtn = document.getElementById('verificationLoginBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.handleLogin());
        }

        // Back button
        const backBtn = document.getElementById('verificationBackBtn');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.hide());
        }

        // Resend link
        const resendLink = document.getElementById('resendVerificationLink');
        if (resendLink) {
            resendLink.addEventListener('click', (e) => this.handleResend(e));
        }
    }

    show(email) {
        this.userEmail = email;

        // Update email in UI
        const emailEl = document.getElementById('verificationEmail');
        if (emailEl) {
            emailEl.textContent = email;
        }

        // Show screen
        this.screen.classList.remove('hidden');

        // Hide main content
        const mainContent = document.querySelector('main');
        const header = document.querySelector('.header');
        const secondaryBar = document.querySelector('.secondary-bar');
        const footer = document.querySelector('footer');

        if (mainContent) mainContent.style.display = 'none';
        if (header) header.style.display = 'none';
        if (secondaryBar) secondaryBar.style.display = 'none';
        if (footer) footer.style.display = 'none';
    }

    hide() {
        this.screen.classList.add('hidden');

        // Show main content
        const mainContent = document.querySelector('main');
        const header = document.querySelector('.header');
        const secondaryBar = document.querySelector('.secondary-bar');
        const footer = document.querySelector('footer');

        if (mainContent) mainContent.style.display = '';
        if (header) header.style.display = '';
        if (secondaryBar) secondaryBar.style.display = '';
        if (footer) footer.style.display = '';
    }

    handleLogin() {
        this.hide();

        // Open auth modal to login tab
        import('./auth-modal.js').then(module => {
            module.openAuthModal('login');
        });
    }

    async handleResend(e) {
        e.preventDefault();

        const resendLink = document.getElementById('resendVerificationLink');
        const cooldownText = document.getElementById('resendCooldownText');

        // Disable link
        resendLink.classList.add('disabled');
        resendLink.style.pointerEvents = 'none';

        // Attempt to resend
        // Note: We can't resend without being logged in, so we'll show a message
        this.showToast('Para reenviar, faça login novamente e o e-mail será reenviado automaticamente.', 'info');

        // Start cooldown
        this.startResendCooldown(resendLink, cooldownText);
    }

    startResendCooldown(linkEl, textEl) {
        let timeLeft = this.resendCooldown;

        // Hide link, show countdown
        linkEl.classList.add('hidden');
        textEl.classList.remove('hidden');

        // Update countdown
        const updateCountdown = () => {
            if (timeLeft > 0) {
                textEl.textContent = `Aguarde ${timeLeft}s para reenviar`;
                timeLeft--;
                this.resendTimer = setTimeout(updateCountdown, 1000);
            } else {
                // Re-enable link
                linkEl.classList.remove('hidden', 'disabled');
                linkEl.style.pointerEvents = '';
                textEl.classList.add('hidden');
            }
        };

        updateCountdown();
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type} animate-slide-in-right`;

        const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';

        toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: var(--space-3);">
        <span style="font-size: var(--text-lg);">${icon}</span>
        <span style="font-weight: var(--weight-semibold);">${message}</span>
      </div>
    `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('animate-fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    cleanup() {
        if (this.resendTimer) {
            clearTimeout(this.resendTimer);
        }
    }
}

// Initialize verification screen
let verificationScreenInstance;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        verificationScreenInstance = new VerificationScreen();
    });
} else {
    verificationScreenInstance = new VerificationScreen();
}

// Export for use in other scripts
export function showVerificationScreen(email) {
    if (verificationScreenInstance) {
        verificationScreenInstance.show(email);
    }
}

export function hideVerificationScreen() {
    if (verificationScreenInstance) {
        verificationScreenInstance.hide();
    }
}
