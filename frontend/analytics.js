/**
 * Google Analytics 4 - Medición de tráfico para ePriceFlo
 * 
 * INSTRUCCIONES:
 * 1. Crear cuenta: https://analytics.google.com
 * 2. Crear propiedad GA4
 * 3. Obtener MEASUREMENT_ID (formato: G-XXXXXXXXXX)
 * 4. Pegar en ANALYTICS_CONFIG.measurementId
 */

const ANALYTICS_CONFIG = {
    // Activar/desactivar analytics
    enabled: true,  // Cambiar a true cuando tengas tu ID
    
    // Tu Measurement ID de Google Analytics 4
    measurementId: 'G-XXXXXXXXXX',  // TU ID AQUÍ (formato: G-XXXXXXXXXX)
    
    // Deshabilitar en estos dominios
    disabledDomains: [
        'localhost',
        '127.0.0.1'
    ],
    
    // Eventos personalizados que rastrear
    trackEvents: {
        productView: true,      // Ver producto
        priceCompare: true,     // Comparar precios
        storeClick: true,       // Click en tienda
        search: true            // Búsquedas
    }
};

/**
 * Verifica si analytics está habilitado
 */
function isAnalyticsEnabled() {
    if (!ANALYTICS_CONFIG.enabled) {
        console.log('📊 Analytics: Deshabilitado en configuración');
        return false;
    }
    
    const hostname = window.location.hostname;
    if (ANALYTICS_CONFIG.disabledDomains.includes(hostname)) {
        console.log(`📊 Analytics: Deshabilitado en ${hostname}`);
        return false;
    }
    
    if (ANALYTICS_CONFIG.measurementId === 'G-XXXXXXXXXX') {
        console.log('📊 Analytics: Measurement ID no configurado');
        return false;
    }
    
    return true;
}

/**
 * Carga Google Analytics 4
 */
function loadGoogleAnalytics() {
    if (!isAnalyticsEnabled()) {
        return;
    }
    
    // Cargar gtag.js
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${ANALYTICS_CONFIG.measurementId}`;
    document.head.appendChild(script);
    
    // Inicializar gtag
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    window.gtag = gtag;
    
    gtag('js', new Date());
    gtag('config', ANALYTICS_CONFIG.measurementId, {
        send_page_view: true,
        cookie_flags: 'SameSite=None;Secure'
    });
    
    console.log('✅ Analytics: Google Analytics 4 cargado');
}

/**
 * Rastrea evento personalizado
 */
function trackEvent(eventName, params = {}) {
    if (!isAnalyticsEnabled() || !window.gtag) {
        return;
    }
    
    gtag('event', eventName, params);
    console.log(`📊 Analytics: Evento "${eventName}"`, params);
}

/**
 * Rastrea vista de producto
 */
function trackProductView(productName, category) {
    if (!ANALYTICS_CONFIG.trackEvents.productView) return;
    
    trackEvent('view_item', {
        item_name: productName,
        item_category: category
    });
}

/**
 * Rastrea comparación de precios
 */
function trackPriceComparison(productName, numStores, lowestPrice) {
    if (!ANALYTICS_CONFIG.trackEvents.priceCompare) return;
    
    trackEvent('price_comparison', {
        product: productName,
        stores_compared: numStores,
        lowest_price: lowestPrice
    });
}

/**
 * Rastrea click en tienda
 */
function trackStoreClick(storeName, productName, price) {
    if (!ANALYTICS_CONFIG.trackEvents.storeClick) return;
    
    trackEvent('store_click', {
        store: storeName,
        product: productName,
        price: price
    });
}

/**
 * Rastrea búsqueda
 */
function trackSearch(searchTerm, resultsCount) {
    if (!ANALYTICS_CONFIG.trackEvents.search) return;
    
    trackEvent('search', {
        search_term: searchTerm,
        results: resultsCount
    });
}

// Auto-inicialización
loadGoogleAnalytics();

// Exportar para uso global
window.ePriceFloAnalytics = {
    trackEvent,
    trackProductView,
    trackPriceComparison,
    trackStoreClick,
    trackSearch
};
