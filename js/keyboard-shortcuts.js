/**
 * OVPFH v2.0 - Keyboard Shortcuts
 * Nielsen Heuristic H7: Flexibility and efficiency of use
 */

class KeyboardShortcuts {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));

        // Setup help overlay
        this.setupHelpOverlay();
    }

    handleKeyPress(e) {
        // Don't trigger shortcuts if user is typing in an input
        const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName);

        // "/" - Focus search (works even when typing)
        if (e.key === '/' && !isTyping) {
            e.preventDefault();
            this.focusSearch();
            return;
        }

        // Don't process other shortcuts if typing
        if (isTyping) return;

        switch (e.key) {
            case 'Escape':
                this.clearSearch();
                this.closeHelp();
                break;

            case 'ArrowLeft':
                e.preventDefault();
                this.navigateDate('prev');
                break;

            case 'ArrowRight':
                e.preventDefault();
                this.navigateDate('next');
                break;

            case '?':
                e.preventDefault();
                this.toggleHelp();
                break;

            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
                e.preventDefault();
                this.quickTeamFilter(parseInt(e.key));
                break;
        }
    }

    focusSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
            this.showToast('Busca ativada', 'success');
        }
    }

    clearSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput && searchInput.value) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            this.showToast('Busca limpa', 'success');
        }
    }

    navigateDate(direction) {
        const button = document.getElementById(direction === 'prev' ? 'prevDay' : 'nextDay');
        if (button && !button.disabled) {
            button.click();
            this.showToast(`Navegando para ${direction === 'prev' ? 'dia anterior' : 'próximo dia'}`, 'success');
        }
    }

    quickTeamFilter(index) {
        const chips = document.querySelectorAll('.chip-team');
        if (chips[index]) {
            chips[index].click();
            const teamName = chips[index].textContent.trim();
            this.showToast(`Filtro: ${teamName}`, 'success');
        }
    }

    toggleHelp() {
        const helpOverlay = document.getElementById('keyboardHelp');
        if (helpOverlay) {
            helpOverlay.classList.toggle('hidden');
        }
    }

    closeHelp() {
        const helpOverlay = document.getElementById('keyboardHelp');
        if (helpOverlay && !helpOverlay.classList.contains('hidden')) {
            helpOverlay.classList.add('hidden');
        }
    }

    setupHelpOverlay() {
        const closeBtn = document.getElementById('closeHelp');
        const backdrop = document.getElementById('keyboardHelp');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeHelp());
        }

        if (backdrop) {
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    this.closeHelp();
                }
            });
        }
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type} animate-slide-in-right`;
        toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: var(--space-3);">
        <span style="font-size: var(--text-lg);">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
        <span style="font-weight: var(--weight-semibold);">${message}</span>
      </div>
    `;

        container.appendChild(toast);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('animate-fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new KeyboardShortcuts());
} else {
    new KeyboardShortcuts();
}
