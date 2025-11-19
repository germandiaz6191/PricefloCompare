/**
 * Configuración de Afiliados
 *
 * NOTA: Esta configuración ahora se carga desde la base de datos.
 *
 * Para configurar afiliados:
 * 1. Ejecuta: python activate_amazon_affiliate.py TU_CODIGO
 * 2. O actualiza directamente la tabla 'stores' en la BD
 *
 * NO necesitas editar este archivo.
 */

// Configuración local (fallback si la API falla)
const AFFILIATE_CONFIG_FALLBACK = {
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

// Configuración real cargada desde API
let AFFILIATE_CONFIG = {};

/**
 * Carga la configuración de afiliados desde el backend
 */
async function loadAffiliateConfig() {
    try {
        const response = await fetch(`${API_URL || 'http://localhost:8000'}/affiliate-config`);
        if (response.ok) {
            const config = await response.json();

            // Convertir el formato de BD a formato del frontend
            AFFILIATE_CONFIG = {};
            for (const [storeName, storeConfig] of Object.entries(config)) {
                AFFILIATE_CONFIG[storeName] = {
                    enabled: storeConfig.enabled,
                    code: storeConfig.code,
                    urlPattern: (url, code) => {
                        // El patrón viene de BD (ej: "?tag={code}")
                        const pattern = storeConfig.url_pattern;
                        const finalPattern = pattern.replace('{code}', code);
                        const separator = url.includes('?') ? '&' : '';
                        return url + separator + finalPattern;
                    }
                };
            }

            console.log(`📊 Configuración de afiliados cargada: ${Object.keys(AFFILIATE_CONFIG).length} tiendas`);
        } else {
            console.warn('⚠️ No se pudo cargar configuración de afiliados, usando fallback');
            AFFILIATE_CONFIG = AFFILIATE_CONFIG_FALLBACK;
        }
    } catch (error) {
        console.error('Error cargando configuración de afiliados:', error);
        AFFILIATE_CONFIG = AFFILIATE_CONFIG_FALLBACK;
    }
}

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

// Cargar configuración al inicio
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        loadAffiliateConfig();
    });
}

// Exportar funciones para usar en app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { getAffiliateUrl, hasAffiliateEnabled, AFFILIATE_CONFIG };
}
