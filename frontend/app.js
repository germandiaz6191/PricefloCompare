// Configuración de la API - Detecta ambiente automáticamente
const API_URL = (() => {
    const hostname = window.location.hostname;

    // Desarrollo local
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }

    // Vercel deployment
    if (hostname.includes('vercel.app')) {
        return `https://${hostname}`;
    }

    // Producción con dominio custom
    return window.location.origin;
})();

console.log('🌐 API URL configurada:', API_URL);

// ===== MANEJO DE ERRORES CON RETRY =====
const FetchManager = {
    // Fetch con retry automático y manejo de errores
    async safeFetch(url, options = {}, retries = 3) {
        const {
            method = 'GET',
            headers = {},
            body = null,
            timeout = 10000,
            showToast = true
        } = options;

        let lastError;

        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                // Crear AbortController para timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), timeout);

                const fetchOptions = {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                        ...headers
                    },
                    signal: controller.signal
                };

                if (body && method !== 'GET') {
                    fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
                }

                const response = await fetch(url, fetchOptions);
                clearTimeout(timeoutId);

                // Verificar si la respuesta es OK
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                // Intentar parsear JSON
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                } else {
                    return await response.text();
                }

            } catch (error) {
                lastError = error;

                // Si es el último intento, lanzar error
                if (attempt === retries) {
                    if (showToast) {
                        this.handleError(error, url);
                    }
                    throw error;
                }

                // Exponential backoff: esperar 2^attempt * 500ms
                const waitTime = Math.pow(2, attempt) * 500;
                console.log(`⚠️ Intento ${attempt + 1} falló. Reintentando en ${waitTime}ms...`);

                if (showToast && attempt === 0) {
                    ToastManager.warning(
                        'Reintentando...',
                        'Hubo un problema. Intentando nuevamente.',
                        2000
                    );
                }

                await new Promise(resolve => setTimeout(resolve, waitTime));
            }
        }

        throw lastError;
    },

    // Manejo centralizado de errores
    handleError(error, url) {
        console.error(`Error en ${url}:`, error);

        let title = 'Error de conexión';
        let message = 'No se pudo completar la solicitud.';

        if (error.name === 'AbortError') {
            title = 'Tiempo de espera agotado';
            message = 'La solicitud tardó demasiado. Verifica tu conexión.';
        } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
            title = 'Sin conexión';
            message = 'Verifica tu conexión a Internet e intenta nuevamente.';
        } else if (error.message.includes('HTTP 404')) {
            title = 'No encontrado';
            message = 'El recurso solicitado no existe.';
        } else if (error.message.includes('HTTP 500')) {
            title = 'Error del servidor';
            message = 'El servidor encontró un problema. Intenta más tarde.';
        } else if (error.message.includes('HTTP 401') || error.message.includes('HTTP 403')) {
            title = 'No autorizado';
            message = 'No tienes permisos para realizar esta acción.';
        }

        ToastManager.error(title, message, 7000);
    },

    // Atajos para métodos comunes
    async get(url, options = {}) {
        return this.safeFetch(url, { ...options, method: 'GET' });
    },

    async post(url, body, options = {}) {
        return this.safeFetch(url, { ...options, method: 'POST', body });
    },

    async put(url, body, options = {}) {
        return this.safeFetch(url, { ...options, method: 'PUT', body });
    },

    async delete(url, options = {}) {
        return this.safeFetch(url, { ...options, method: 'DELETE' });
    }
};

// ===== SISTEMA DE TOAST NOTIFICATIONS =====
const ToastManager = {
    container: null,

    // Inicializar el contenedor de toasts
    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },

    // Crear y mostrar un toast
    show(options) {
        this.init();

        const {
            type = 'info',           // 'success', 'error', 'warning', 'info'
            title,
            message,
            duration = 5000,         // ms (0 = no auto-close)
            closable = true
        } = options;

        // Iconos según el tipo
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        // Crear el toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} toast-enter`;

        toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                ${message ? `<div class="toast-message">${message}</div>` : ''}
            </div>
            ${closable ? `
                <button class="toast-close" aria-label="Cerrar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            ` : ''}
            ${duration > 0 ? `<div class="toast-progress" style="--duration: ${duration}ms;"></div>` : ''}
        `;

        // Agregar al contenedor
        this.container.appendChild(toast);

        // Auto-cerrar si tiene duración
        let autoCloseTimeout;
        if (duration > 0) {
            autoCloseTimeout = setTimeout(() => {
                this.close(toast);
            }, duration);
        }

        // Botón de cerrar
        if (closable) {
            const closeBtn = toast.querySelector('.toast-close');
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (autoCloseTimeout) clearTimeout(autoCloseTimeout);
                this.close(toast);
            });
        }

        // Click en el toast para cerrar
        toast.addEventListener('click', () => {
            if (autoCloseTimeout) clearTimeout(autoCloseTimeout);
            this.close(toast);
        });

        return toast;
    },

    // Cerrar un toast
    close(toast) {
        toast.classList.remove('toast-enter');
        toast.classList.add('toast-exit');

        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300); // Duración de la animación
    },

    // Atajos para tipos comunes
    success(title, message, duration) {
        return this.show({ type: 'success', title, message, duration });
    },

    error(title, message, duration) {
        return this.show({ type: 'error', title, message, duration });
    },

    warning(title, message, duration) {
        return this.show({ type: 'warning', title, message, duration });
    },

    info(title, message, duration) {
        return this.show({ type: 'info', title, message, duration });
    }
};

// ===== AUTOCOMPLETE SYSTEM =====
const AutocompleteManager = {
    dropdown: null,
    searchInput: null,
    selectedIndex: -1,
    suggestions: [],
    debounceTimer: null,

    init() {
        this.dropdown = document.getElementById('autocompleteDropdown');
        this.searchInput = document.getElementById('searchInput');

        if (!this.searchInput || !this.dropdown) return;

        // Event listeners
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));

        // Cerrar dropdown cuando se hace click fuera
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.autocomplete-wrapper')) {
                this.hide();
            }
        });
    },

    handleInput(e) {
        const query = e.target.value.trim();

        // Limpiar el timer anterior
        clearTimeout(this.debounceTimer);

        if (query.length < 2) {
            this.hide();
            return;
        }

        // Debounce: esperar 300ms después de que el usuario deje de escribir
        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    },

    async fetchSuggestions(query) {
        try {
            this.showLoading();

            const products = await FetchManager.get(
                `${API_URL}/search?q=${encodeURIComponent(query)}`,
                {
                    timeout: 5000,
                    showToast: false,
                    retries: 1
                }
            );

            // Limitar a 8 sugerencias
            this.suggestions = products.slice(0, 8);
            this.selectedIndex = -1;

            this.renderSuggestions(query);
        } catch (error) {
            console.error('Error fetching autocomplete suggestions:', error);
            this.hide();
        }
    },

    showLoading() {
        this.dropdown.innerHTML = `
            <div class="autocomplete-loading">
                <div class="autocomplete-spinner"></div>
                Buscando...
            </div>
        `;
        this.dropdown.classList.add('show');
    },

    renderSuggestions(query) {
        if (this.suggestions.length === 0) {
            this.dropdown.innerHTML = `
                <div class="autocomplete-no-results">
                    No se encontraron productos para "${query}"
                </div>
            `;
            this.dropdown.classList.add('show');
            return;
        }

        const html = this.suggestions.map((product, index) => `
            <div class="autocomplete-item" data-index="${index}" data-product-name="${product.name}">
                <div class="autocomplete-icon">🔍</div>
                <div class="autocomplete-text">
                    <div class="autocomplete-title">${this.highlightMatch(product.name, query)}</div>
                    ${product.category ? `<div class="autocomplete-subtitle">${product.category}</div>` : ''}
                </div>
            </div>
        `).join('');

        this.dropdown.innerHTML = html;
        this.dropdown.classList.add('show');

        // Event listeners para los items
        this.dropdown.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', () => this.selectItem(parseInt(item.dataset.index)));
            item.addEventListener('mouseenter', () => this.hoverItem(parseInt(item.dataset.index)));
        });
    },

    highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    },

    handleKeydown(e) {
        if (!this.dropdown.classList.contains('show')) return;

        const items = this.dropdown.querySelectorAll('.autocomplete-item');

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
                this.updateSelection();
                break;

            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;

            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectItem(this.selectedIndex);
                } else {
                    // Si no hay selección, ejecutar búsqueda normal
                    searchProducts();
                }
                break;

            case 'Escape':
                e.preventDefault();
                this.hide();
                // Si el input está vacío, recargar todos los productos
                if (!this.searchInput.value.trim()) {
                    loadProducts(selectedCategory);
                }
                break;
        }
    },

    updateSelection() {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');

        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            } else {
                item.classList.remove('selected');
            }
        });

        // Actualizar input con el texto seleccionado
        if (this.selectedIndex >= 0 && this.suggestions[this.selectedIndex]) {
            this.searchInput.value = this.suggestions[this.selectedIndex].name;
        }
    },

    hoverItem(index) {
        this.selectedIndex = index;
        this.updateSelection();
    },

    selectItem(index) {
        if (index < 0 || index >= this.suggestions.length) return;

        const product = this.suggestions[index];
        this.searchInput.value = product.name;
        this.hide();

        // Ejecutar búsqueda
        searchProducts();
    },

    hide() {
        this.dropdown.classList.remove('show');
        this.selectedIndex = -1;
        this.suggestions = [];
    }
};

// ===== SISTEMA DE BADGES DE URGENCIA =====
const UrgencyBadges = {
    // Analizar precios y retornar badges apropiados
    analyze(prices, currentPrice) {
        const badges = [];

        if (!prices || prices.length === 0) return badges;

        // Ordenar precios por fecha (más reciente primero)
        const sortedPrices = [...prices].sort((a, b) =>
            new Date(b.scraped_at) - new Date(a.scraped_at)
        );

        // Precio actual
        const current = currentPrice.price;
        const currentDate = new Date(currentPrice.scraped_at);

        // 1. Verificar si es el precio más bajo (comparar con el mismo store)
        const storePrices = prices.filter(p => p.store_name === currentPrice.store_name);
        const isLowestPrice = storePrices.every(p => current <= p.price);

        // Precio más bajo en 30 días
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const recentPrices = storePrices.filter(p => new Date(p.scraped_at) >= thirtyDaysAgo);

        if (recentPrices.length > 5 && isLowestPrice) {
            badges.push({
                type: 'lowest-price',
                text: 'Precio más bajo'
            });
        }

        // 2. Detectar precio subiendo (comparar últimos 3 registros)
        if (storePrices.length >= 3) {
            const recent3 = storePrices.slice(0, 3).map(p => p.price);
            const isRising = recent3[0] > recent3[1] && recent3[1] > recent3[2];

            if (isRising && !isLowestPrice) {
                const increase = ((recent3[0] - recent3[2]) / recent3[2] * 100).toFixed(0);
                badges.push({
                    type: 'price-rising',
                    text: `+${increase}%`
                });
            }
        }

        // 3. Detectar caída reciente de precio (últimas 48 horas)
        const twoDaysAgo = new Date();
        twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
        const veryRecentPrices = storePrices.filter(p => new Date(p.scraped_at) >= twoDaysAgo);

        if (veryRecentPrices.length >= 2) {
            const oldestRecent = veryRecentPrices[veryRecentPrices.length - 1].price;
            const drop = ((oldestRecent - current) / oldestRecent * 100);

            if (drop > 5) {
                badges.push({
                    type: 'recent-drop',
                    text: `Bajó ${drop.toFixed(0)}%`
                });
            }
        }

        // 4. Gran descuento (comparar con precio máximo de todos los stores)
        const allPrices = prices.map(p => p.price);
        const maxPrice = Math.max(...allPrices);
        const discount = ((maxPrice - current) / maxPrice * 100);

        if (discount >= 15 && !badges.some(b => b.type === 'lowest-price')) {
            badges.push({
                type: 'big-discount',
                text: `${discount.toFixed(0)}% off`
            });
        }

        // 5. Precio estable (sin cambios en últimos 7 días)
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        const weekPrices = storePrices.filter(p => new Date(p.scraped_at) >= sevenDaysAgo);

        if (weekPrices.length >= 3 && badges.length === 0) {
            const priceVariation = Math.max(...weekPrices.map(p => p.price)) -
                                   Math.min(...weekPrices.map(p => p.price));
            const variationPercent = (priceVariation / current * 100);

            if (variationPercent < 2) {
                badges.push({
                    type: 'stable-price',
                    text: 'Precio estable'
                });
            }
        }

        // Limitar a 2 badges por precio
        return badges.slice(0, 2);
    },

    // Renderizar badges HTML
    render(badges) {
        if (!badges || badges.length === 0) return '';

        return `
            <div class="urgency-badges">
                ${badges.map(badge => `
                    <span class="urgency-badge ${badge.type}">
                        ${badge.text}
                    </span>
                `).join('')}
            </div>
        `;
    }
};

// Estado de la aplicación
let allProducts = [];
let currentProducts = [];
let selectedCategory = null;

// Estado de paginación
let currentPage = 1;
let totalPages = 1;
let totalProducts = 0;
let pageSize = 20;

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 PricefloCompare iniciado');

    // Inicializar autocomplete
    AutocompleteManager.init();

    loadStats();
    loadCategories();
    loadProducts();
});

// Cargar estadísticas
async function loadStats() {
    try {
        const stats = await FetchManager.get(`${API_URL}/stats`, {
            timeout: 5000,
            showToast: false
        });

        document.getElementById('totalProducts').textContent = stats.total_products;
        document.getElementById('totalStores').textContent = stats.total_stores;
        document.getElementById('totalPrices').textContent = stats.total_snapshots;

        if (stats.last_scrape) {
            const date = new Date(stats.last_scrape);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);

            let timeText;
            if (diffMins < 1) {
                timeText = 'hace momentos';
            } else if (diffMins < 60) {
                timeText = `hace ${diffMins} min`;
            } else if (diffMins < 1440) {
                timeText = `hace ${Math.floor(diffMins / 60)} horas`;
            } else {
                timeText = `hace ${Math.floor(diffMins / 1440)} días`;
            }

            document.getElementById('updateBadge').textContent = `Actualizado ${timeText}`;
            document.getElementById('lastUpdate').textContent = date.toLocaleString('es-CO');
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
        ToastManager.error(
            'Error de conexión',
            'No se pudieron cargar las estadísticas. Verifica que la API esté corriendo.',
            7000
        );
    }
}

// Cargar categorías
async function loadCategories() {
    try {
        const categories = await FetchManager.get(`${API_URL}/categories`, {
            timeout: 5000,
            showToast: false
        });

        // Ordenar categorías por count descendente (más buscadas primero)
        const sortedCategories = categories.sort((a, b) => b.count - a.count);

        const categoriesDiv = document.getElementById('categories');
        categoriesDiv.innerHTML = '';

        // Botón "Todas"
        const allBtn = document.createElement('button');
        allBtn.className = `category-btn ${!selectedCategory ? 'active' : ''}`;
        allBtn.textContent = 'Todas';
        allBtn.onclick = () => filterByCategory(null);
        categoriesDiv.appendChild(allBtn);

        // Mostrar las primeras 4 categorías más buscadas
        const TOP_CATEGORIES = 4;
        const topCategories = sortedCategories.slice(0, TOP_CATEGORIES);
        const remainingCategories = sortedCategories.slice(TOP_CATEGORIES);

        topCategories.forEach(cat => {
            const btn = document.createElement('button');
            btn.className = `category-btn ${selectedCategory === cat.category ? 'active' : ''}`;
            btn.textContent = `${cat.category} (${cat.count})`;
            btn.onclick = () => filterByCategory(cat.category);
            categoriesDiv.appendChild(btn);
        });

        // Si hay más categorías, mostrar dropdown "+X más"
        if (remainingCategories.length > 0) {
            const moreContainer = document.createElement('div');
            moreContainer.className = 'category-more-container';

            const moreBtn = document.createElement('button');
            moreBtn.className = 'category-btn category-more-btn';
            moreBtn.innerHTML = `+${remainingCategories.length} más <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M2.5 4.5L6 8L9.5 4.5"/></svg>`;
            moreBtn.onclick = (e) => {
                e.stopPropagation();
                const dropdown = moreContainer.querySelector('.category-dropdown');
                dropdown.classList.toggle('show');
            };

            const dropdown = document.createElement('div');
            dropdown.className = 'category-dropdown';

            remainingCategories.forEach(cat => {
                const item = document.createElement('button');
                item.className = `category-dropdown-item ${selectedCategory === cat.category ? 'active' : ''}`;
                item.textContent = `${cat.category} (${cat.count})`;
                item.onclick = () => {
                    filterByCategory(cat.category);
                    dropdown.classList.remove('show');
                };
                dropdown.appendChild(item);
            });

            moreContainer.appendChild(moreBtn);
            moreContainer.appendChild(dropdown);
            categoriesDiv.appendChild(moreContainer);

            // Cerrar dropdown al hacer clic fuera
            document.addEventListener('click', (e) => {
                if (!moreContainer.contains(e.target)) {
                    dropdown.classList.remove('show');
                }
            });
        }
    } catch (error) {
        console.error('Error cargando categorías:', error);
        ToastManager.error(
            'Error al cargar categorías',
            'No se pudieron obtener las categorías de productos.',
            5000
        );
    }
}

// Cargar productos con paginación
async function loadProducts(category = null, page = 1) {
    showLoading(true);

    try {
        // Construir URL con parámetros de paginación
        let url = `${API_URL}/products?page=${page}&page_size=${pageSize}`;
        if (category) {
            url += `&category=${encodeURIComponent(category)}`;
        }

        // Obtener datos paginados
        const response = await FetchManager.get(url, {
            timeout: 15000,
            showToast: true
        });

        // Actualizar estado de paginación
        currentPage = response.page;
        totalPages = response.total_pages;
        totalProducts = response.total;
        allProducts = response.items;
        currentProducts = [...response.items];

        // Mostrar productos y controles de paginación
        await displayProducts(currentProducts);
        updatePaginationControls();

        // Scroll suave al inicio de los productos
        if (page > 1) {
            document.querySelector('.products-section').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    } catch (error) {
        console.error('Error cargando productos:', error);
        document.getElementById('productsGrid').innerHTML = `
            <div class="error">
                <h3>⚠️ Error al cargar productos</h3>
                <p>No se pudieron cargar los productos</p>
                <p>Asegúrate de que la API esté corriendo en <code>${API_URL}</code></p>
                <button onclick="loadProducts(${category ? `'${category}'` : 'null'})" class="btn-history" style="margin-top: 20px;">
                    🔄 Reintentar
                </button>
            </div>
        `;
        document.getElementById('paginationContainer').style.display = 'none';
    } finally {
        showLoading(false);
    }
}

// Cambiar de página (relativo: -1 para anterior, +1 para siguiente)
function changePage(delta) {
    const newPage = currentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
        loadProducts(selectedCategory, newPage);
    }
}

// Ir a página específica
function goToPage(page) {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
        loadProducts(selectedCategory, page);
    }
}

// Actualizar controles de paginación
function updatePaginationControls() {
    const container = document.getElementById('paginationContainer');
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    const pagesContainer = document.getElementById('paginationPages');
    const infoSpan = document.getElementById('paginationInfo');

    // Mostrar/ocultar contenedor
    if (totalPages <= 1) {
        container.style.display = 'none';
        return;
    }
    container.style.display = 'flex';

    // Actualizar botones anterior/siguiente
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;

    // Actualizar información
    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, totalProducts);
    infoSpan.textContent = `Mostrando ${start}-${end} de ${totalProducts} productos`;

    // Generar números de página
    pagesContainer.innerHTML = '';
    const pages = generatePageNumbers(currentPage, totalPages);

    pages.forEach(page => {
        if (page === '...') {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'pagination-ellipsis';
            ellipsis.textContent = '...';
            pagesContainer.appendChild(ellipsis);
        } else {
            const pageBtn = document.createElement('button');
            pageBtn.className = 'pagination-page';
            if (page === currentPage) {
                pageBtn.classList.add('active');
            }
            pageBtn.textContent = page;
            pageBtn.onclick = () => goToPage(page);
            pagesContainer.appendChild(pageBtn);
        }
    });
}

// Generar array de números de página con elipsis
function generatePageNumbers(current, total) {
    const pages = [];
    const delta = 2; // Cuántas páginas mostrar alrededor de la actual

    if (total <= 7) {
        // Si hay pocas páginas, mostrar todas
        for (let i = 1; i <= total; i++) {
            pages.push(i);
        }
    } else {
        // Siempre mostrar primera página
        pages.push(1);

        // Calcular rango alrededor de la página actual
        let start = Math.max(2, current - delta);
        let end = Math.min(total - 1, current + delta);

        // Ajustar si estamos cerca del inicio
        if (current <= delta + 2) {
            end = Math.min(5, total - 1);
            start = 2;
        }

        // Ajustar si estamos cerca del final
        if (current >= total - delta - 1) {
            start = Math.max(total - 4, 2);
            end = total - 1;
        }

        // Agregar elipsis izquierda si es necesario
        if (start > 2) {
            pages.push('...');
        }

        // Agregar páginas del rango
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }

        // Agregar elipsis derecha si es necesario
        if (end < total - 1) {
            pages.push('...');
        }

        // Siempre mostrar última página
        pages.push(total);
    }

    return pages;
}

// Mostrar skeletons de carga
function showSkeletons(count = 6) {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = '';
    grid.className = 'skeletons-grid';

    for (let i = 0; i < count; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-card';
        skeleton.innerHTML = `
            <div class="skeleton-header"></div>
            <div class="skeleton-line"></div>
            <div class="skeleton-line medium"></div>
            <div class="skeleton-price"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-button"></div>
        `;
        grid.appendChild(skeleton);
    }
}

// Mostrar productos en la grilla
async function displayProducts(products) {
    const grid = document.getElementById('productsGrid');

    if (products.length === 0) {
        grid.className = 'products-grid';
        grid.innerHTML = `
            <div class="no-results">
                <h3>📦 No hay productos</h3>
                <p>Ejecuta <code>python add_test_data.py</code> para agregar datos de prueba</p>
                <p>O ejecuta <code>python scrape_and_save.py</code> para scraping real</p>
            </div>
        `;
        return;
    }

    // Mostrar skeletons mientras carga
    showSkeletons(products.length);

    // OPTIMIZACIÓN: Cargar todos los precios en PARALELO
    const startTime = performance.now();
    console.log(`⚡ Cargando ${products.length} productos en paralelo...`);

    // Crear todas las promesas de fetch en paralelo
    const pricesPromises = products.map(product =>
        FetchManager.get(`${API_URL}/products/${product.id}/prices`, {
            timeout: 10000,
            showToast: false,
            retries: 2
        }).catch(error => {
            console.error(`Error cargando precios de ${product.name}:`, error);
            return [];
        })
    );

    // Esperar a que TODAS terminen
    const allPrices = await Promise.all(pricesPromises);

    const endTime = performance.now();
    console.log(`✅ Precios cargados en ${(endTime - startTime).toFixed(0)}ms`);

    // Ahora crear las cards con los datos ya disponibles
    grid.className = 'products-grid';
    grid.innerHTML = '';

    products.forEach((product, index) => {
        const card = createProductCardSync(product, allPrices[index]);
        grid.appendChild(card);
    });
}

// Crear tarjeta de producto (versión síncrona con precios pre-cargados)
function createProductCardSync(product, prices = []) {
    const card = document.createElement('div');
    card.className = 'product-card';

    let pricesHTML;

    if (prices.length > 0) {
        // Ordenar por precio
        prices.sort((a, b) => a.price - b.price);

        pricesHTML = prices.map((price, index) => {
            const isStale = price.is_stale;
            const isBest = index === 0;
            const date = new Date(price.scraped_at);

            // Calcular ahorro vs el más caro
            const maxPrice = Math.max(...prices.map(p => p.price));
            const savings = maxPrice - price.price;
            const savingsPercent = ((savings / maxPrice) * 100).toFixed(0);

            // Analizar y generar badges de urgencia
            const urgencyBadges = UrgencyBadges.analyze(prices, price);
            const badgesHTML = UrgencyBadges.render(urgencyBadges);

            // Botón para ver en tienda (si hay URL)
            const affiliateUrl = getAffiliateUrl(price.store_name, price.url);
            const isAffiliate = hasAffiliateEnabled(price.store_name);
            const relAttr = isAffiliate ? 'noopener noreferrer sponsored' : 'noopener noreferrer';

            const visitButton = affiliateUrl ? `
                <a href="${affiliateUrl}"
                   target="_blank"
                   rel="${relAttr}"
                   class="btn-visit-store"
                   onclick="trackClick('${price.store_name}', ${product.id})">
                    Ver en tienda
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                        <polyline points="15 3 21 3 21 9"></polyline>
                        <line x1="10" y1="14" x2="21" y2="3"></line>
                    </svg>
                </a>
            ` : '';

            return `
                <div class="price-item ${isBest ? 'best-price' : ''} ${isStale ? 'stale' : ''}">
                    <div class="store-name">
                        ${price.store_name}
                        ${isBest && savings > 0 ? `<br><small style="color: #059669; font-weight: 600;">Ahorro: ${savingsPercent}%</small>` : ''}
                    </div>
                    <div class="price">
                        $${price.price.toLocaleString('es-CO')}
                    </div>
                    <div class="price-date">
                        ${date.toLocaleDateString('es-CO')}
                    </div>
                    ${badgesHTML}
                    ${visitButton}
                </div>
            `;
        }).join('');
    } else {
        pricesHTML = '<p class="no-prices">💤 Sin precios disponibles</p>';
    }

    card.innerHTML = `
        <div class="product-header">
            <h3>${product.name}</h3>
            ${product.category ? `<span class="category-tag">${product.category}</span>` : ''}
        </div>
        <div class="prices-list">
            ${pricesHTML}
        </div>
        <div class="product-footer">
            <button onclick="viewHistory(${product.id})" class="btn-history">
                📊 Ver histórico de precios
            </button>
        </div>
    `;

    return card;
}

// Versión async de createProductCard (mantener para compatibilidad)
async function createProductCard(product) {
    try {
        const prices = await FetchManager.get(`${API_URL}/products/${product.id}/prices`, {
            timeout: 8000,
            showToast: false,
            retries: 2
        });
        return createProductCardSync(product, prices);
    } catch (error) {
        console.error(`Error cargando precios de ${product.name}:`, error);
        return createProductCardSync(product, []);
    }
}

// Filtrar por categoría
function filterByCategory(category) {
    selectedCategory = category;
    loadCategories();
    loadProducts(category);

    // Mostrar feedback
    if (category) {
        ToastManager.info(
            'Filtro aplicado',
            `Mostrando productos de categoría: ${category}`,
            3000
        );
    } else {
        ToastManager.info(
            'Filtro removido',
            'Mostrando todos los productos',
            3000
        );
    }
}

// Buscar productos
async function searchProducts() {
    const query = document.getElementById('searchInput').value.trim();

    // Cerrar autocomplete
    AutocompleteManager.hide();

    if (!query) {
        loadProducts(selectedCategory);
        return;
    }

    showLoading(true);

    try {
        const products = await FetchManager.get(
            `${API_URL}/search?q=${encodeURIComponent(query)}`,
            {
                timeout: 10000,
                showToast: true
            }
        );
        currentProducts = products;
        await displayProducts(products);

        // Mostrar feedback al usuario
        if (products.length === 0) {
            ToastManager.warning(
                'Sin resultados',
                `No encontramos productos que coincidan con "${query}". Intenta con otros términos.`,
                6000
            );

            // Registrar la búsqueda sin resultados
            try {
                await FetchManager.post(
                    `${API_URL}/reports/search-not-found`,
                    { search_term: query },
                    { showToast: false, timeout: 5000, retries: 1 }
                );
                console.log(`📊 Búsqueda sin resultados registrada: "${query}"`);
            } catch (error) {
                console.error('Error registrando búsqueda sin resultados:', error);
            }
        } else {
            ToastManager.success(
                'Búsqueda exitosa',
                `Encontramos ${products.length} producto${products.length !== 1 ? 's' : ''} para "${query}"`,
                4000
            );
        }
    } catch (error) {
        console.error('Error buscando productos:', error);
        // El error ya fue mostrado por FetchManager
    } finally {
        showLoading(false);
    }
}

// Ordenar productos
async function sortProducts() {
    const sortBy = document.getElementById('sortSelect').value;

    showLoading(true);

    // Crear copias de los productos con sus precios
    const productsWithPrices = await Promise.all(
        currentProducts.map(async (product) => {
            try {
                const prices = await FetchManager.get(`${API_URL}/products/${product.id}/prices`, {
                    timeout: 8000,
                    showToast: false,
                    retries: 2
                });
                const minPrice = prices.length > 0 ? Math.min(...prices.map(p => p.price)) : Infinity;
                return { ...product, minPrice };
            } catch (error) {
                return { ...product, minPrice: Infinity };
            }
        })
    );

    // Ordenar según la opción seleccionada
    switch (sortBy) {
        case 'price-low':
            productsWithPrices.sort((a, b) => a.minPrice - b.minPrice);
            break;
        case 'price-high':
            productsWithPrices.sort((a, b) => b.minPrice - a.minPrice);
            break;
        case 'name':
        default:
            productsWithPrices.sort((a, b) => a.name.localeCompare(b.name));
            break;
    }

    currentProducts = productsWithPrices;
    await displayProducts(currentProducts);
    showLoading(false);
}

// Ver histórico de un producto
function viewHistory(productId) {
    const url = `${API_URL}/products/${productId}/history`;
    window.open(url, '_blank');
}

// Mostrar/ocultar loading
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

// Tracking de clics en botones "Ver en tienda"
async function trackClick(storeName, productId) {
    try {
        // Registrar el clic en el backend para estadísticas
        await FetchManager.post(
            `${API_URL}/track/click`,
            {
                store_name: storeName,
                product_id: productId,
                timestamp: new Date().toISOString()
            },
            {
                showToast: false,
                timeout: 3000,
                retries: 1
            }
        );

        // Mostrar feedback al usuario
        ToastManager.info(
            'Redirigiendo...',
            `Te llevamos a ${storeName} para completar tu compra.`,
            3000
        );

        // Log para debugging
        console.log(`📊 Click tracked: ${storeName} - Product ${productId}`);
    } catch (error) {
        // No bloquear la navegación si falla el tracking
        console.error('Error tracking click:', error);
    }
}

// Auto-refresh cada 5 minutos
setInterval(() => {
    console.log('🔄 Auto-refresh de estadísticas');
    loadStats();
}, 300000); // 5 minutos
