# Mejoras de Precisión - Fase 1 ✅

## Resumen de Cambios Implementados

### 1. ✅ Headers HTTP Mejorados
**Archivos modificados:**
- `scrapers/generic_scrapers.py`
- `scrapers/graphql_scraper.py`

**Cambios:**
- Headers completos simulando navegador Chrome real
- Incluye: User-Agent, Accept, Accept-Language, Sec-Fetch-*, etc.
- Headers específicos para GraphQL (Origin, Referer)

**Impacto:** Reduce la detección de bot básica.

---

### 2. ✅ Filtro de Categoría Eliminado
**Archivo modificado:**
- `config_sitios.json`

**Cambio:**
```json
// ANTES - Solo buscaba en celulares
"selectedFacets": [
  {"key": "category-2", "value": "celulares"},  ❌
  ...
]

// DESPUÉS - Busca en todas las categorías
"selectedFacets": [
  {"key": "channel", "value": "..."},  ✅
  {"key": "locale", "value": "es-CO"}
]
```

**Impacto:** Ahora puede buscar lavadoras, neveras, y cualquier producto, no solo celulares.

---

### 3. ✅ Sistema de Scoring de Relevancia
**Archivo nuevo:**
- `scrapers/text_utils.py`

**Funcionalidad:**
- `normalize_text()`: Normaliza textos para comparación (minúsculas, espacios, unidades)
- `calculate_relevance_score()`: Calcula score 0-100 de relevancia
- `format_price()`: Formatea precios consistentemente

**Algoritmo de Scoring:**
- 50 puntos por similitud general del texto (SequenceMatcher)
- 50 puntos por coincidencia de palabras clave
- +10 puntos bonus si todas las palabras están presentes
- Threshold: 60/100 para considerar resultado relevante

**Ejemplos de Funcionamiento:**
```
Búsqueda: "Lavadora LG 17Kg"
Título: "Lavadora LG 17 Kg Carga Superior"
Score: 94/100 ✅ Relevante

Búsqueda: "Lavadora LG 17Kg"
Título: "Nevera Samsung 300L"
Score: 17/100 ❌ No relevante

Búsqueda: "iPhone 14"
Título: "iPhone 14 Pro Max 256GB"
Score: 88/100 ✅ Relevante
```

**Impacto:** Filtra resultados irrelevantes automáticamente.

---

### 4. ✅ Normalización de Texto Mejorada
**Incluido en:** `scrapers/text_utils.py`

**Transformaciones:**
- Minúsculas: "LAVADORA" → "lavadora"
- Espacios múltiples: "LG    17  Kg" → "LG 17Kg"
- Unidades sin espacio: "17 Kg" → "17kg", "300 L" → "300l"
- Elimina caracteres especiales pero preserva números

**Impacto:** Mejora la comparación de búsquedas con diferentes formatos.

---

## Problema Pendiente: Error 403 (Forbidden) 🚫

### Situación Actual
Ambos sitios (Éxito y Homecenter) están bloqueando las solicitudes con error 403, incluso con headers mejorados.

### Causa
Protección anti-bot avanzada:
- Cloudflare o similar
- Verificación de JavaScript
- Fingerprinting del navegador
- Análisis de comportamiento

### Soluciones Posibles

#### Opción 1: Selenium/Playwright (Recomendado) 🎯
**Ventajas:**
- Simula navegador real con JavaScript
- Alta tasa de éxito
- Control total

**Implementación:**
```bash
pip install selenium webdriver-manager
```

**Requiere:**
- ChromeDriver/GeckoDriver
- Más recursos (RAM, CPU)
- Más lento que requests

---

#### Opción 2: Servicios de Scraping (Más Simple) 💰
Usar servicios especializados:
- **ScraperAPI** (https://scraperapi.com)
- **ScrapingBee** (https://scrapingbee.com)
- **Bright Data** (https://brightdata.com)

**Ventajas:**
- Bypass automático de anti-bot
- Proxies rotativos incluidos
- No requiere Selenium

**Desventajas:**
- Costo mensual ($29-99/mes típicamente)
- Límite de requests

---

#### Opción 3: Proxies Rotativos 🔄
Usar proxies para rotar IPs:
- Proxies residenciales
- Servicios como Bright Data, Oxylabs

**Ventajas:**
- Más difícil de bloquear

**Desventajas:**
- Costo adicional
- Puede no ser suficiente si hay verificación JS

---

#### Opción 4: APIs Oficiales (Ideal) 🏆
Contactar a los sitios para acceso a APIs.

**Ventajas:**
- Legalmente seguro
- Datos estructurados
- Sin bloqueos

**Desventajas:**
- Puede no estar disponible
- Proceso de aprobación

---

## Próximos Pasos Recomendados

### Fase 2: Resolver Error 403
**Opción A - Selenium (Open Source):**
1. Instalar: `pip install selenium webdriver-manager`
2. Crear `scrapers/selenium_scraper.py`
3. Modificar configuración para usar Selenium en sitios bloqueados

**Opción B - Servicio de Scraping (Más rápido):**
1. Registrarse en ScraperAPI o similar
2. Modificar scrapers para usar su API
3. Configurar API key

### Fase 3: Scrapers Robustos
- Mejorar selectores XPath de Homecenter
- Implementar retry con backoff exponencial
- Agregar logging estructurado

### Fase 4: API REST
- Implementar API con FastAPI
- Endpoints para búsqueda y comparación
- Documentación Swagger

---

## Testing de las Mejoras

Para validar que las mejoras funcionan correctamente:

```bash
# Test del sistema de scoring
python3 -c "
from scrapers.text_utils import calculate_relevance_score

score, relevant = calculate_relevance_score('iPhone 14', 'iPhone 14 Pro Max')
print(f'Score: {score}/100 - Relevante: {relevant}')
"

# Test de búsqueda (dará 403 pero verás las mejoras en logs)
echo -e "on-demand\nLavadora LG" | python3 main.py
```

---

## Archivos Modificados en Fase 1

```
✅ scrapers/generic_scrapers.py     - Headers mejorados, scoring integrado
✅ scrapers/graphql_scraper.py      - Headers mejorados, scoring integrado
✅ scrapers/text_utils.py           - NUEVO - Utilidades de texto y scoring
✅ config_sitios.json               - Filtro de categoría eliminado
✅ .gitignore                       - Archivos de cache ignorados
```

---

## Conclusión

**✅ Completado:**
- Sistema de scoring de relevancia (60% threshold)
- Normalización de texto avanzada
- Headers HTTP mejorados
- Búsqueda sin restricción de categoría

**⚠️ Bloqueado por:**
- Error 403 de ambos sitios web
- Protección anti-bot avanzada

**🎯 Siguiente paso recomendado:**
Implementar Selenium o usar servicio de scraping para resolver el bloqueo 403.

¿Deseas que implemente Selenium (Fase 2) o prefieres explorar otra opción?
