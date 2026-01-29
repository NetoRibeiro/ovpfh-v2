import { getAllNews, addNewsletterSubscriber } from './data-service.js';

/**
 * Notícias Page Logic
 */

const elements = {
    newsFeedGrid: document.getElementById('newsFeedGrid'),
    sidebarNewsletterForm: document.getElementById('sidebarNewsletterForm'),
    sidebarEmailInput: document.getElementById('sidebarEmailInput'),
    toastContainer: document.getElementById('toastContainer')
};

async function initNoticias() {
    console.log('📰 Initializing Notícias page...');

    // 1. Load Data
    try {
        const news = await getAllNews();
        renderNewsFeed(news);
    } catch (error) {
        console.error('Error loading news:', error);
        elements.newsFeedGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <p>Erro ao carregar notícias. Por favor, tente novamente mais tarde.</p>
            </div>
        `;
    }

    // 2. Newsletter Listener
    if (elements.sidebarNewsletterForm) {
        elements.sidebarNewsletterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = elements.sidebarEmailInput.value;
            const btn = elements.sidebarNewsletterForm.querySelector('button');
            const originalText = btn.textContent;

            if (!email) return;

            btn.disabled = true;
            btn.textContent = 'Enviando...';

            const result = await addNewsletterSubscriber(email, { source: 'news_sidebar' });

            if (result.success) {
                btn.textContent = '✓ Inscrito!';
                elements.sidebarEmailInput.value = '';
                showToast('Inscrição realizada com sucesso!', 'success');
                setTimeout(() => {
                    btn.disabled = false;
                    btn.textContent = originalText;
                }, 3000);
            } else {
                btn.textContent = 'Erro';
                showToast('Erro ao inscrever.', 'error');
                setTimeout(() => {
                    btn.disabled = false;
                    btn.textContent = originalText;
                }, 3000);
            }
        });
    }
}

function renderNewsFeed(newsList) {
    if (!elements.newsFeedGrid) return;

    if (newsList.length === 0) {
        elements.newsFeedGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <p>Nenhuma notícia encontrada no momento.</p>
            </div>
        `;
        return;
    }

    elements.newsFeedGrid.innerHTML = newsList.map(item => {
        const dateObj = item.last_updated_date_time?.toDate ? item.last_updated_date_time.toDate() : new Date(item.last_updated_date_time);
        const dateStr = dateObj.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
        const link = item.source_url || '#';
        const target = item.source_url ? "_blank" : "_self";

        return `
            <article class="blog-card animate-fade-in">
                <img src="${item.image_url}" alt="" class="blog-card-img" loading="lazy">
                <div class="blog-card-content">
                    <div class="blog-card-meta">
                        <span class="tag">${item.category || 'Geral'}</span>
                        <time datetime="${dateObj.toISOString()}">${dateStr}</time>
                    </div>
                    <h3 class="blog-card-title">${item.title}</h3>
                    <p class="blog-card-excerpt">${item.subtitle || 'Confira os detalhes desta notícia sobre o futebol brasileiro e internacional.'}</p>
                    <div class="blog-card-footer">
                        <a href="${link}" target="${target}" class="read-more">
                            Ler notícia completa <span>→</span>
                        </a>
                    </div>
                </div>
            </article>
        `;
    }).join('');
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.style.padding = 'var(--space-3) var(--space-4)';
    toast.style.background = type === 'success' ? 'var(--color-navy-700)' : 'var(--color-red-600)';
    toast.style.borderLeft = `4px solid ${type === 'success' ? 'var(--color-cyan-500)' : 'white'}`;
    toast.style.borderRadius = 'var(--radius-md)';
    toast.style.color = 'white';
    toast.style.boxShadow = 'var(--shadow-lg)';
    toast.style.marginBottom = 'var(--space-3)';
    toast.style.animation = 'slideIn 0.3s ease-out';

    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: var(--space-3);">
            <span>${type === 'success' ? '✓' : '✕'}</span>
            <span>${message}</span>
        </div>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Start
initNoticias();
