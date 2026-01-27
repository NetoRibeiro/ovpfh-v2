/**
 * OVPFH v2.0 - Authentication Modal Logic
 * Handles authentication UI interactions
 */

import { signUp, signIn, signInWithGoogle, resetPassword } from './auth.js';
import { showVerificationScreen } from './verification-screen.js';

class AuthModal {
  constructor() {
    this.modal = null;
    this.currentTab = 'login';
    this.init();
  }

  init() {
    // Create modal HTML
    this.createModal();

    // Setup event listeners
    this.setupEventListeners();
  }

  createModal() {
    const modalHTML = `
      <div id="authModalBackdrop" class="auth-modal-backdrop hidden">
        <div class="auth-modal" role="dialog" aria-labelledby="authModalTitle" aria-modal="true">
          <!-- Decorative accent handled by CSS ::before -->
          
          <!-- Header -->
          <div class="auth-modal-header">
            <button class="auth-modal-close" aria-label="Fechar" id="authModalClose">
              ✕
            </button>
            <h2 id="authModalTitle" class="auth-modal-title">Bem-vindo!</h2>
            <p class="auth-modal-subtitle">Entre para acessar recursos exclusivos</p>
          </div>

          <!-- Tabs -->
          <div class="auth-tabs" role="tablist">
            <button class="auth-tab active" role="tab" aria-selected="true" aria-controls="loginForm" id="loginTab">
              Entrar
            </button>
            <button class="auth-tab" role="tab" aria-selected="false" aria-controls="signupForm" id="signupTab">
              Criar Conta
            </button>
          </div>

          <!-- Modal Body -->
          <div class="auth-modal-body">
            <!-- Login Form -->
            <form id="loginForm" class="auth-form" role="tabpanel" aria-labelledby="loginTab">
              <div class="form-group">
                <label for="loginEmail" class="form-label">
                  E-mail <span class="required">*</span>
                </label>
                <input
                  type="email"
                  id="loginEmail"
                  class="form-input"
                  placeholder="seu@email.com"
                  required
                  autocomplete="email"
                >
                <div class="form-error hidden" id="loginEmailError"></div>
              </div>

              <div class="form-group">
                <label for="loginPassword" class="form-label">
                  Senha <span class="required">*</span>
                </label>
                <div class="input-wrapper">
                  <input
                    type="password"
                    id="loginPassword"
                    class="form-input"
                    placeholder="••••••••"
                    required
                    autocomplete="current-password"
                  >
                  <button type="button" class="password-toggle" aria-label="Mostrar senha" data-target="loginPassword">
                    👁
                  </button>
                </div>
                <div class="form-error hidden" id="loginPasswordError"></div>
              </div>

              <div class="forgot-password">
                <a href="#" id="forgotPasswordLink">Esqueceu a senha?</a>
              </div>

              <button type="submit" class="auth-submit" id="loginSubmit">
                Entrar
              </button>

              <div class="auth-divider">ou</div>

              <button type="button" class="google-signin" id="googleSigninBtn">
                <svg class="google-icon" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continuar com Google
              </button>
            </form>

            <!-- Signup Form -->
            <form id="signupForm" class="auth-form hidden" role="tabpanel" aria-labelledby="signupTab">
              <div class="form-group">
                <label for="signupName" class="form-label">
                  Nome
                </label>
                <input
                  type="text"
                  id="signupName"
                  class="form-input"
                  placeholder="Seu nome"
                  autocomplete="name"
                >
              </div>

              <div class="form-group">
                <label for="signupEmail" class="form-label">
                  E-mail <span class="required">*</span>
                </label>
                <input
                  type="email"
                  id="signupEmail"
                  class="form-input"
                  placeholder="seu@email.com"
                  required
                  autocomplete="email"
                >
                <div class="form-error hidden" id="signupEmailError"></div>
              </div>

              <div class="form-group">
                <label for="signupPassword" class="form-label">
                  Senha <span class="required">*</span>
                </label>
                <div class="input-wrapper">
                  <input
                    type="password"
                    id="signupPassword"
                    class="form-input"
                    placeholder="Mínimo 6 caracteres"
                    required
                    autocomplete="new-password"
                  >
                  <button type="button" class="password-toggle" aria-label="Mostrar senha" data-target="signupPassword">
                    👁
                  </button>
                </div>
                <div class="form-error hidden" id="signupPasswordError"></div>
              </div>

              <div class="form-group">
                <label for="signupConfirmPassword" class="form-label">
                  Confirmar Senha <span class="required">*</span>
                </label>
                <div class="input-wrapper">
                  <input
                    type="password"
                    id="signupConfirmPassword"
                    class="form-input"
                    placeholder="Digite a senha novamente"
                    required
                    autocomplete="new-password"
                  >
                  <button type="button" class="password-toggle" aria-label="Mostrar senha" data-target="signupConfirmPassword">
                    👁
                  </button>
                </div>
                <div class="form-error hidden" id="signupConfirmPasswordError"></div>
              </div>

              <button type="submit" class="auth-submit" id="signupSubmit">
                Criar Conta
              </button>

              <div class="auth-divider">ou</div>

              <button type="button" class="google-signin" id="googleSignupBtn">
                <svg class="google-icon" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continuar com Google
              </button>
            </form>
          </div>
        </div>
      </div>
    `;

    // Insert modal into DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    this.modal = document.getElementById('authModalBackdrop');
  }

  setupEventListeners() {
    // Close button
    document.getElementById('authModalClose').addEventListener('click', () => this.close());

    // Click outside to close
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.close();
      }
    });

    // Escape key to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
        this.close();
      }
    });

    // Tab switching
    document.getElementById('loginTab').addEventListener('click', () => this.switchTab('login'));
    document.getElementById('signupTab').addEventListener('click', () => this.switchTab('signup'));

    // Password toggle buttons
    document.querySelectorAll('.password-toggle').forEach(btn => {
      btn.addEventListener('click', (e) => this.togglePassword(e.target));
    });

    // Form submissions
    document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));
    document.getElementById('signupForm').addEventListener('submit', (e) => this.handleSignup(e));

    // Google signin buttons
    document.getElementById('googleSigninBtn').addEventListener('click', () => this.handleGoogleSignin());
    document.getElementById('googleSignupBtn').addEventListener('click', () => this.handleGoogleSignin());

    // Forgot password link
    document.getElementById('forgotPasswordLink').addEventListener('click', (e) => this.handleForgotPassword(e));
  }

  open(tab = 'login') {
    this.modal.classList.remove('hidden');
    this.switchTab(tab);

    // Focus first input
    setTimeout(() => {
      const firstInput = this.modal.querySelector('.auth-form:not(.hidden) input');
      if (firstInput) firstInput.focus();
    }, 100);
  }

  close() {
    this.modal.classList.add('hidden');
    this.clearForms();
  }

  switchTab(tab) {
    this.currentTab = tab;

    // Update tabs
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    if (tab === 'login') {
      loginTab.classList.add('active');
      signupTab.classList.remove('active');
      loginTab.setAttribute('aria-selected', 'true');
      signupTab.setAttribute('aria-selected', 'false');
      loginForm.classList.remove('hidden');
      signupForm.classList.add('hidden');
    } else {
      signupTab.classList.add('active');
      loginTab.classList.remove('active');
      signupTab.setAttribute('aria-selected', 'true');
      loginTab.setAttribute('aria-selected', 'false');
      signupForm.classList.remove('hidden');
      loginForm.classList.add('hidden');
    }
  }

  togglePassword(button) {
    const targetId = button.getAttribute('data-target');
    const input = document.getElementById(targetId);

    if (input.type === 'password') {
      input.type = 'text';
      button.textContent = '👁‍🗨';
    } else {
      input.type = 'password';
      button.textContent = '👁';
    }
  }

  async handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const submitBtn = document.getElementById('loginSubmit');

    // Clear previous errors
    this.clearErrors('login');

    // Validate
    if (!this.validateEmail(email)) {
      this.showError('loginEmailError', 'Digite um e-mail válido');
      return;
    }

    // Show loading
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '<span class="spinner-small"></span> Entrando...';

    // Sign in
    const result = await signIn(email, password);

    // Hide loading
    submitBtn.disabled = false;
    submitBtn.classList.remove('loading');
    submitBtn.textContent = 'Entrar';

    if (result.success) {
      this.showToast('Login realizado com sucesso!', 'success');
      this.close();
      // Trigger auth state change event
      window.dispatchEvent(new CustomEvent('authStateChanged', { detail: result.user }));
    } else if (result.needsVerification) {
      // Show verification screen
      this.close();
      showVerificationScreen(result.email);
    } else {
      this.showError('loginPasswordError', result.error);
    }
  }

  async handleSignup(e) {
    e.preventDefault();

    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;
    const submitBtn = document.getElementById('signupSubmit');

    // Clear previous errors
    this.clearErrors('signup');

    // Validate
    if (!this.validateEmail(email)) {
      this.showError('signupEmailError', 'Digite um e-mail válido');
      return;
    }

    if (password.length < 6) {
      this.showError('signupPasswordError', 'A senha deve ter no mínimo 6 caracteres');
      return;
    }

    if (password !== confirmPassword) {
      this.showError('signupConfirmPasswordError', 'As senhas não coincidem');
      return;
    }

    // Show loading
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '<span class="spinner-small"></span> Criando conta...';

    // Sign up
    const result = await signUp(email, password, name || null);

    // Hide loading
    submitBtn.disabled = false;
    submitBtn.classList.remove('loading');
    submitBtn.textContent = 'Criar Conta';

    if (result.success) {
      // Show verification screen instead of success toast
      this.close();
      showVerificationScreen(result.email);
    } else {
      this.showError('signupPasswordError', result.error);
    }
  }

  async handleGoogleSignin() {
    const result = await signInWithGoogle();

    if (result.success) {
      this.showToast('Login realizado com sucesso!', 'success');
      this.close();
      // Trigger auth state change event
      window.dispatchEvent(new CustomEvent('authStateChanged', { detail: result.user }));
    } else {
      this.showToast(result.error, 'error');
    }
  }

  async handleForgotPassword(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value;

    if (!email) {
      this.showError('loginEmailError', 'Digite seu e-mail para recuperar a senha');
      return;
    }

    if (!this.validateEmail(email)) {
      this.showError('loginEmailError', 'Digite um e-mail válido');
      return;
    }

    const result = await resetPassword(email);

    if (result.success) {
      this.showToast(result.message, 'success');
    } else {
      this.showToast(result.error, 'error');
    }
  }

  validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    const inputId = elementId.replace('Error', '');
    const input = document.getElementById(inputId);

    if (errorEl) {
      errorEl.textContent = message;
      errorEl.classList.remove('hidden');
    }

    if (input) {
      input.classList.add('error');
    }
  }

  clearErrors(form) {
    const prefix = form === 'login' ? 'login' : 'signup';
    const errors = this.modal.querySelectorAll(`#${prefix}Form .form-error`);
    const inputs = this.modal.querySelectorAll(`#${prefix}Form .form-input`);

    errors.forEach(el => {
      el.textContent = '';
      el.classList.add('hidden');
    });

    inputs.forEach(input => {
      input.classList.remove('error');
    });
  }

  clearForms() {
    document.getElementById('loginForm').reset();
    document.getElementById('signupForm').reset();
    this.clearErrors('login');
    this.clearErrors('signup');
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
}

// Initialize auth modal when DOM is ready
let authModalInstance;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    authModalInstance = new AuthModal();
  });
} else {
  authModalInstance = new AuthModal();
}

// Export for use in other scripts
export function openAuthModal(tab = 'login') {
  if (authModalInstance) {
    authModalInstance.open(tab);
  }
}

export function closeAuthModal() {
  if (authModalInstance) {
    authModalInstance.close();
  }
}
