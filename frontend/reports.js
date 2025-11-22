// Configuración de la API
const API_URL = 'http://localhost:8000';

// Estado
let reportData = [];

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    console.log('📊 Reportes iniciados');
    loadReport();
});

// Cargar reporte
async function loadReport() {
    try {
        const response = await fetch(`${API_URL}/reports/not-found?limit=50&include_ignored=true`);
        reportData = await response.json();

        displayStats();
        displayReport();
    } catch (error) {
        console.error('Error cargando reporte:', error);
        document.getElementById('reportTableBody').innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <div>Error al cargar el reporte</div>
                </td>
            </tr>
        `;
    }
}

// Mostrar estadísticas
function displayStats() {
    const totalSearches = reportData.reduce((sum, item) => sum + item.search_count, 0);
    const ignoredCount = reportData.filter(item => item.ignored === 1).length;
    const activeCount = reportData.filter(item => item.ignored === 0).length;

    const statsHTML = `
        <div class="stat-card">
            <div class="stat-value">${reportData.length}</div>
            <div class="stat-label">Términos Únicos</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${totalSearches}</div>
            <div class="stat-label">Total de Búsquedas</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${activeCount}</div>
            <div class="stat-label">Activos</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${ignoredCount}</div>
            <div class="stat-label">Ignorados</div>
        </div>
    `;

    document.getElementById('statsContainer').innerHTML = statsHTML;
}

// Mostrar tabla de reporte
function displayReport() {
    const tbody = document.getElementById('reportTableBody');

    if (reportData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    <div class="empty-state-icon">🎉</div>
                    <div>No hay búsquedas sin resultados registradas</div>
                    <div style="font-size: 0.875rem; margin-top: 8px; color: var(--gray-500);">
                        Cuando los usuarios busquen productos que no existen, aparecerán aquí
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    const rows = reportData.map(item => {
        const firstSearched = new Date(item.first_searched_at).toLocaleDateString('es-CO');
        const lastSearched = new Date(item.last_searched_at).toLocaleDateString('es-CO');
        const isIgnored = item.ignored === 1;

        return `
            <tr class="${isIgnored ? 'ignored' : ''}" data-id="${item.id}">
                <td>
                    <span class="search-term">${escapeHtml(item.search_term)}</span>
                    ${isIgnored ? ' <span style="color: var(--gray-500); font-size: 0.75rem;">(ignorado)</span>' : ''}
                </td>
                <td><span class="count-badge">${item.search_count}</span></td>
                <td>${firstSearched}</td>
                <td>${lastSearched}</td>
                <td>
                    <div class="action-buttons">
                        ${!isIgnored ? `
                            <button class="btn-action btn-ignore" onclick="toggleIgnore(${item.id}, true)">
                                🚫 Ignorar
                            </button>
                        ` : `
                            <button class="btn-action btn-reactivate" onclick="toggleIgnore(${item.id}, false)">
                                ✅ Reactivar
                            </button>
                        `}
                        <button class="btn-action btn-delete" onclick="deleteEntry(${item.id})">
                            🗑️ Eliminar
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = rows;
}

// Ignorar/Reactivar búsqueda
async function toggleIgnore(id, ignored) {
    try {
        const response = await fetch(`${API_URL}/reports/not-found/${id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ignored })
        });

        if (response.ok) {
            console.log(`✅ Búsqueda ${ignored ? 'ignorada' : 'reactivada'}`);
            // Actualizar estado local
            const item = reportData.find(r => r.id === id);
            if (item) {
                item.ignored = ignored ? 1 : 0;
            }
            displayStats();
            displayReport();
        } else {
            alert('Error al actualizar el estado');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar el estado');
    }
}

// Eliminar entrada
async function deleteEntry(id) {
    if (!confirm('¿Estás seguro de eliminar esta búsqueda permanentemente?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/reports/not-found/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            console.log('✅ Búsqueda eliminada');
            // Remover del estado local
            reportData = reportData.filter(r => r.id !== id);
            displayStats();
            displayReport();
        } else {
            alert('Error al eliminar');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar');
    }
}

// Utilidad para escapar HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
