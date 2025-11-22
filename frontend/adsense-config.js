/**
 * Configuración de Google AdSense para PricefloCompare
 *
 * INSTRUCCIONES PARA CONFIGURAR:
 *
 * 1. Regístrate en Google AdSense: https://www.google.com/adsense
 * 2. Obtén tu código de cliente (formato: ca-pub-XXXXXXXXXXXXXXXX)
 * 3. Crea unidades de anuncio en AdSense Dashboard
 * 4. Reemplaza los valores en CONFIG abajo
 * 5. Activa los anuncios: enabled: true
 */

const ADSENSE_CONFIG = {
    // ========================================
    // CONFIGURACIÓN PRINCIPAL
    // ========================================
    enabled: false,  // Cambiar a true cuando tengas tu cuenta de AdSense
    client: 'ca-pub-XXXXXXXXXXXXXXXX',  // TU CÓDIGO DE CLIENTE AQUÍ

    // ========================================
    // IDS DE SLOTS (Unidades de anuncio)
    // ========================================
    // Crea estas unidades en: https://adsense.google.com > Anuncios > Por unidad de anuncio
    slots: {
        header: '1234567890',       // Banner superior (728x90 o responsive)
        sidebar: '1234567891',      // Sidebar derecho (300x250)
        betweenResults: '1234567892', // Entre resultados de búsqueda (responsive)
        footer: '1234567893'        // Footer (728x90 o responsive)
    },

    // ========================================
    // CONFIGURACIÓN POR AMBIENTE
    // ========================================
    // NO mostrar anuncios en estos dominios
    disabledDomains: [
        'localhost',
        '127.0.0.1',
        'priceflocompare-qa.vercel.app',  // QA
        'priceflocompare-dev.vercel.app'  // Dev
    ]
};

/**
 * Verifica si los anuncios están habilitados para este ambiente
 */
function isAdsEnabled() {
    // Si está explícitamente deshabilitado
    if (!ADSENSE_CONFIG.enabled) {
        console.log('📢 AdSense: Deshabilitado en configuración');
        return false;
    }

    // Si estamos en dominio de desarrollo/QA
    const hostname = window.location.hostname;
    if (ADSENSE_CONFIG.disabledDomains.includes(hostname)) {
        console.log(`📢 AdSense: Deshabilitado en ${hostname}`);
        return false;
    }

    // Si el código de cliente no está configurado
    if (ADSENSE_CONFIG.client === 'ca-pub-XXXXXXXXXXXXXXXX') {
        console.log('📢 AdSense: Código de cliente no configurado');
        return false;
    }

    return true;
}

/**
 * Carga el script de AdSense de forma asíncrona
 */
function loadAdSenseScript() {
    if (!isAdsEnabled()) {
        console.log('📢 AdSense: No se cargará el script');
        return;
    }

    // Verificar que no se haya cargado ya
    if (document.querySelector(`script[src*="adsbygoogle.js"]`)) {
        console.log('📢 AdSense: Script ya cargado');
        return;
    }

    const script = document.createElement('script');
    script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CONFIG.client}`;
    script.async = true;
    script.crossOrigin = 'anonymous';
    script.onerror = () => {
        console.error('❌ AdSense: Error cargando script. Verifica tu código de cliente.');
    };
    script.onload = () => {
        console.log('✅ AdSense: Script cargado correctamente');
    };

    document.head.appendChild(script);
}

/**
 * Crea un anuncio AdSense en el contenedor especificado
 *
 * @param {string} containerId - ID del contenedor HTML
 * @param {string} slotId - ID del slot de AdSense
 * @param {string} format - Formato del anuncio (auto, rectangle, horizontal, vertical)
 * @param {boolean} fullWidthResponsive - Hacer el anuncio responsive de ancho completo
 */
function createAdUnit(containerId, slotId, format = 'auto', fullWidthResponsive = true) {
    if (!isAdsEnabled()) {
        return;
    }

    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`❌ AdSense: Contenedor ${containerId} no encontrado`);
        return;
    }

    // Crear el elemento ins para el anuncio
    const adElement = document.createElement('ins');
    adElement.className = 'adsbygoogle';
    adElement.style.display = 'block';
    adElement.setAttribute('data-ad-client', ADSENSE_CONFIG.client);
    adElement.setAttribute('data-ad-slot', slotId);
    adElement.setAttribute('data-ad-format', format);

    if (fullWidthResponsive) {
        adElement.setAttribute('data-full-width-responsive', 'true');
    }

    container.appendChild(adElement);

    // Inicializar el anuncio
    try {
        (adsbygoogle = window.adsbygoogle || []).push({});
        console.log(`✅ AdSense: Anuncio creado en ${containerId}`);
    } catch (error) {
        console.error(`❌ AdSense: Error inicializando anuncio en ${containerId}:`, error);
    }
}

/**
 * Inicializa todos los anuncios de la página
 */
function initializeAds() {
    if (!isAdsEnabled()) {
        console.log('📢 AdSense: Anuncios deshabilitados - Modo desarrollo');
        showDevPlaceholders();
        return;
    }

    console.log('📢 AdSense: Inicializando anuncios...');

    // Cargar script de AdSense
    loadAdSenseScript();

    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createAllAds);
    } else {
        createAllAds();
    }
}

/**
 * Crea todos los anuncios definidos
 */
function createAllAds() {
    // Header banner
    createAdUnit('ad-header', ADSENSE_CONFIG.slots.header, 'horizontal', true);

    // Sidebar
    createAdUnit('ad-sidebar', ADSENSE_CONFIG.slots.sidebar, 'rectangle', false);

    // Footer
    createAdUnit('ad-footer', ADSENSE_CONFIG.slots.footer, 'horizontal', true);

    console.log('✅ AdSense: Todos los anuncios inicializados');
}

/**
 * Crea un anuncio entre resultados de búsqueda
 * Llamar esta función al mostrar resultados
 */
function createResultAd(containerId) {
    createAdUnit(
        containerId,
        ADSENSE_CONFIG.slots.betweenResults,
        'fluid',
        true
    );
}

/**
 * Muestra placeholders en desarrollo (cuando los ads están deshabilitados)
 */
function showDevPlaceholders() {
    const placeholders = document.querySelectorAll('.ad-container');
    placeholders.forEach(container => {
        if (container.children.length === 0) {
            container.innerHTML = `
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                    border-radius: 8px;
                    font-family: system-ui, -apple-system, sans-serif;
                ">
                    <div style="font-size: 2em; margin-bottom: 10px;">📢</div>
                    <div style="font-weight: bold; margin-bottom: 5px;">Espacio publicitario</div>
                    <div style="opacity: 0.9; font-size: 0.9em;">
                        Configura AdSense en <code style="background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 3px;">adsense-config.js</code>
                    </div>
                </div>
            `;
        }
    });
}

// ========================================
// AUTO-INICIALIZACIÓN
// ========================================
// Los anuncios se inicializan automáticamente al cargar la página
initializeAds();

// ========================================
// EXPORTAR PARA USO EXTERNO
// ========================================
window.AdSenseManager = {
    config: ADSENSE_CONFIG,
    isEnabled: isAdsEnabled,
    createResultAd: createResultAd,
    refresh: initializeAds
};
