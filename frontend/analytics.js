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
    enabled: true,  // ✅ Activado

    // Measurement IDs por ambiente
    measurementIds: {
        production: 'G-T57BY0R646',      // 🔴 Producción (epriceflo.com)
        qa: 'G-XXXXXXXXXX',               // 🟡 QA/Staging (configurar si tienes ambiente de pruebas)
        development: null                 // 🟢 Desarrollo (localhost) - NO medir
    },

    // Detectar ambiente automáticamente
    getEnvironment: function() {
        const hostname = window.location.hostname;

        if (hostname === 'epriceflo.com' || hostname === 'www.epriceflo.com') {
            return 'production';
        } else if (hostname.includes('railway.app') || hostname.includes('qa') || hostname.includes('staging')) {
            return 'qa';
        } else {
            return 'development';  // localhost, 127.0.0.1, etc
        }
    },

    // Obtener Measurement ID para el ambiente actual
    getMeasurementId: function() {
        const env = this.getEnvironment();
        const id = this.measurementIds[env];
        console.log(`📊 Analytics: Ambiente = ${env}, ID = ${id || 'no configurado'}`);
        return id;
    },

    // Deshabilitar en estos dominios (redundante, pero por seguridad)
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
        console.log(`📊 Analytics: Deshabilitado en ${hostname} (localhost/dev)`);
        return false;
    }

    const measurementId = ANALYTICS_CONFIG.getMeasurementId();
    if (!measurementId || measurementId === 'G-XXXXXXXXXX') {
        console.log('📊 Analytics: Measurement ID no configurado para este ambiente');
        return false;
    }

    return true;
}

/**
 * Carga Google Analytics 4
 */
function loadGoogleAnalytics() {
    if (!isAnalyticsEnabled()) {
        console.log('📊 Analytics: No se cargará (ambiente de desarrollo o ID no configurado)');
        return;
    }

    const measurementId = ANALYTICS_CONFIG.getMeasurementId();
    const environment = ANALYTICS_CONFIG.getEnvironment();

    // Cargar gtag.js
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    document.head.appendChild(script);

    // Inicializar gtag
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    window.gtag = gtag;

    gtag('js', new Date());
    gtag('config', measurementId, {
        send_page_view: true,
        cookie_flags: 'SameSite=None;Secure',
        // Agregar metadata de ambiente
        page_location: window.location.href,
        page_title: document.title,
        environment: environment
    });

    console.log(`✅ Analytics: GA4 cargado en ambiente "${environment}" con ID: ${measurementId}`);
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
