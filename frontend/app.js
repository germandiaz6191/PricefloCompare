// Configuración de la API
const API_URL = 'http://localhost:8000';

// Estado de la aplicación
let allProducts = [];
let selectedCategory = null;

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
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

        await displayProducts(allProducts);
    } catch (error) {
        console.error('Error cargando productos:', error);
        document.getElementById('productsGrid').innerHTML = `
            <div class="error">
                <h3>Error al cargar productos</h3>
                <p>${error.message}</p>
                <p>Asegúrate de que la API esté corriendo en ${API_URL}</p>
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
                <h3>No hay productos</h3>
                <p>Ejecuta <code>python scrape_and_save.py</code> para llenar la base de datos</p>
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

                return `
                    <div class="price-item ${isBest ? 'best-price' : ''} ${isStale ? 'stale' : ''}">
                        <div class="store-name">
                            ${isBest ? '🏆 ' : ''}${price.store_name}
                        </div>
                        <div class="price">
                            $${price.price.toLocaleString('es-CO')}
                        </div>
                        <div class="price-date">
                            ${date.toLocaleDateString('es-CO')}
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            pricesHTML = '<p class="no-prices">Sin precios disponibles</p>';
        }
    } catch (error) {
        console.error(`Error cargando precios de ${product.name}:`, error);
        pricesHTML = '<p class="no-prices">Error al cargar precios</p>';
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
            <button onclick="viewHistory(${product.id})" class="btn-secondary">
                📊 Ver histórico
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
        await displayProducts(products);
    } catch (error) {
        console.error('Error buscando productos:', error);
    } finally {
        showLoading(false);
    }
}

// Ver histórico de un producto
function viewHistory(productId) {
    window.open(`${API_URL}/products/${productId}/history`, '_blank');
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
    }
});
