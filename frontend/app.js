// Configuración de la API
const API_URL = 'http://localhost:8000';

// Estado de la aplicación
let allProducts = [];
let currentProducts = [];
let selectedCategory = null;

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 PricefloCompare iniciado');
    loadStats();
    loadCategories();
    loadProducts();
});

// Cargar estadísticas
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const stats = await response.json();

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
    }
}

// Cargar categorías
async function loadCategories() {
    try {
        const response = await fetch(`${API_URL}/categories`);
        const categories = await response.json();

        const categoriesDiv = document.getElementById('categories');
        categoriesDiv.innerHTML = `
            <button class="category-btn ${!selectedCategory ? 'active' : ''}" onclick="filterByCategory(null)">
                Todas
            </button>
        `;

        categories.forEach(cat => {
            const btn = document.createElement('button');
            btn.className = `category-btn ${selectedCategory === cat.category ? 'active' : ''}`;
            btn.textContent = `${cat.category} (${cat.count})`;
            btn.onclick = () => filterByCategory(cat.category);
            categoriesDiv.appendChild(btn);
        });
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

// Cargar productos
async function loadProducts(category = null) {
    showLoading(true);

    try {
        let url = `${API_URL}/products`;
        if (category) {
            url += `?category=${encodeURIComponent(category)}`;
        }

        const response = await fetch(url);
        allProducts = await response.json();
        currentProducts = [...allProducts];

        await displayProducts(currentProducts);
    } catch (error) {
        console.error('Error cargando productos:', error);
        document.getElementById('productsGrid').innerHTML = `
            <div class="error">
                <h3>⚠️ Error al cargar productos</h3>
                <p>${error.message}</p>
                <p>Asegúrate de que la API esté corriendo en <code>${API_URL}</code></p>
                <button onclick="location.reload()" class="btn-history" style="margin-top: 20px;">
                    🔄 Reintentar
                </button>
            </div>
        `;
    } finally {
        showLoading(false);
    }
}

// Mostrar productos en la grilla
async function displayProducts(products) {
    const grid = document.getElementById('productsGrid');

    if (products.length === 0) {
        grid.innerHTML = `
            <div class="no-results">
                <h3>📦 No hay productos</h3>
                <p>Ejecuta <code>python add_test_data.py</code> para agregar datos de prueba</p>
                <p>O ejecuta <code>python scrape_and_save.py</code> para scraping real</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = '';

    for (const product of products) {
        const card = await createProductCard(product);
        grid.appendChild(card);
    }
}

// Crear tarjeta de producto
async function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';

    // Obtener precios del producto
    let pricesHTML = '<p class="no-prices">Cargando precios...</p>';

    try {
        const response = await fetch(`${API_URL}/products/${product.id}/prices`);
        const prices = await response.json();

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

                // Botón para ver en tienda (si hay URL)
                const visitButton = price.url ? `
                    <a href="${price.url}" target="_blank" rel="noopener noreferrer" class="btn-visit-store">
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
                        ${visitButton}
                    </div>
                `;
            }).join('');
        } else {
            pricesHTML = '<p class="no-prices">💤 Sin precios disponibles</p>';
        }
    } catch (error) {
        console.error(`Error cargando precios de ${product.name}:`, error);
        pricesHTML = '<p class="no-prices">❌ Error al cargar precios</p>';
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

// Filtrar por categoría
function filterByCategory(category) {
    selectedCategory = category;
    loadCategories();
    loadProducts(category);
}

// Buscar productos
async function searchProducts() {
    const query = document.getElementById('searchInput').value.trim();

    if (!query) {
        loadProducts(selectedCategory);
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
        const products = await response.json();
        currentProducts = products;
        await displayProducts(products);

        // Si no se encontraron resultados, registrar la búsqueda
        if (products.length === 0) {
            try {
                await fetch(`${API_URL}/reports/search-not-found`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ search_term: query })
                });
                console.log(`📊 Búsqueda sin resultados registrada: "${query}"`);
            } catch (error) {
                console.error('Error registrando búsqueda sin resultados:', error);
            }
        }
    } catch (error) {
        console.error('Error buscando productos:', error);
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
                const response = await fetch(`${API_URL}/products/${product.id}/prices`);
                const prices = await response.json();
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

// Enter para buscar
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchProducts();
            }
        });

        // Limpiar búsqueda con Escape
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                loadProducts(selectedCategory);
            }
        });
    }
});

// Auto-refresh cada 5 minutos
setInterval(() => {
    console.log('🔄 Auto-refresh de estadísticas');
    loadStats();
}, 300000); // 5 minutos
