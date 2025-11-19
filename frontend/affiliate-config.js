/**
 * Configuración de Afiliados
 *
 * INSTRUCCIONES:
 * 1. Registrate en cualquier programa de afiliados
 * 2. Cambia 'enabled: true' y agrega tu código
 * 3. No necesitas tocar nada más
 */

const AFFILIATE_CONFIG = {
    // Amazon Associates
    // Registro: https://affiliate-program.amazon.com/
    'Amazon': {
        enabled: false,  // ← Cambiar a true cuando tengas cuenta
        code: '',        // ← Tu código aquí (ejemplo: "priceflo-20")
        urlPattern: (url, code) => {
            // Amazon formato: ?tag=codigo-20
            const separator = url.includes('?') ? '&' : '?';
            return `${url}${separator}tag=${code}`;
        }
    },

    // AliExpress Affiliate
    // Registro: https://portals.aliexpress.com/
    'AliExpress': {
        enabled: false,
        code: '',  // ← Tu tracking ID
        urlPattern: (url, code) => {
            const separator = url.includes('?') ? '&' : '?';
            return `${url}${separator}aff_trace_key=${code}`;
        }
    },

    // Éxito (Cuando negocies CPA directo)
    // Contacto: marketingdigital@grupo-exito.com
    'Éxito': {
        enabled: false,
        code: '',  // ← Código que te den
        urlPattern: (url, code) => {
            const separator = url.includes('?') ? '&' : '?';
            return `${url}${separator}affiliate_id=${code}`;
        }
    },

    // Homecenter (Cuando negocies CPA directo)
    'Homecenter': {
        enabled: false,
        code: '',
        urlPattern: (url, code) => {
            const separator = url.includes('?') ? '&' : '?';
            return `${url}${separator}ref=${code}`;
        }
    },

    // Falabella (Cuando negocies)
    'Falabella': {
        enabled: false,
        code: '',
        urlPattern: (url, code) => {
            const separator = url.includes('?') ? '&' : '?';
            return `${url}${separator}aff=${code}`;
        }
    },

    // AWIN (Red de afiliados global)
    // Registro: https://www.awin.com/
    'AWIN': {
        enabled: false,
        code: '',
        urlPattern: (url, code) => {
            // AWIN usa su propio sistema de links
            return `https://www.awin1.com/cread.php?awinmid=${code}&awinaffid=TU_AFFILIATE_ID&clickref=&ued=${encodeURIComponent(url)}`;
        }
    }
};

/**
 * Obtiene URL con código de afiliado
 * @param {string} storeName - Nombre de la tienda
 * @param {string} originalUrl - URL original del producto
 * @returns {string} - URL con código de afiliado (o URL original si no aplica)
 */
function getAffiliateUrl(storeName, originalUrl) {
    // Si no hay URL, retornar null
    if (!originalUrl) {
        return null;
    }

    // Buscar configuración de la tienda
    const config = AFFILIATE_CONFIG[storeName];

    // Si no hay config o no está habilitado, retornar URL original
    if (!config || !config.enabled || !config.code) {
        return originalUrl;
    }

    // Aplicar pattern de afiliado
    try {
        return config.urlPattern(originalUrl, config.code);
    } catch (error) {
        console.error(`Error generando URL de afiliado para ${storeName}:`, error);
        return originalUrl;
    }
}

/**
 * Verifica si una tienda tiene afiliado configurado
 * @param {string} storeName - Nombre de la tienda
 * @returns {boolean}
 */
function hasAffiliateEnabled(storeName) {
    const config = AFFILIATE_CONFIG[storeName];
    return config && config.enabled && config.code;
}

// Exportar funciones para usar en app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { getAffiliateUrl, hasAffiliateEnabled, AFFILIATE_CONFIG };
}
