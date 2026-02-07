# 📁 Scripts de ePriceFlo

Organización de scripts auxiliares del proyecto.

---

## 📂 Estructura

### `/scripts/migrations/`
Scripts para migrar y actualizar la base de datos.

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `migrate_to_db.py` | **🔥 IMPORTANTE**: Migración inicial - crea tablas y migra productos/tiendas | Primera vez, reset de BD, o para crear tiendas |
| `migrate_category_mappings_to_prod.py` | **🔥 IMPORTANTE**: Migra mapeos de categoría a Supabase (producción) | Una sola vez después de configurar categorías |
| `migrate_countries.py` | Agrega soporte multi-país a la BD | Para habilitar selector de países |
| `migrate_affiliate_fields.py` | Agrega campos de afiliados a stores | Para monetización con afiliados |
| `migrate_category_mappings.py` | Crea tabla category_mappings (OBSOLETO - ahora se crea en init_db()) | No usar |

**Uso**:
```bash
# Setup inicial
python scripts/migrations/migrate_to_db.py

# Migrar categorías a producción (una sola vez)
DATABASE_URL="postgresql://..." python scripts/migrations/migrate_category_mappings_to_prod.py

# Otros
python scripts/migrations/migrate_countries.py
```

---

### `/scripts/utils/`
Herramientas para agregar datos y mantenimiento.

#### 🔥 Scripts Principales (Más Usados)

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `add_test_data.py` | **🔥 MÁS IMPORTANTE**: Scrapea precios reales de todos los productos | Actualizar precios en BD (diario/semanal) |
| `add_popular_products.py` | Agrega 98 productos populares a la BD | Setup inicial - poblar productos |
| `view_db.py` | Ver contenido de la BD en formato legible | Ver qué productos/precios tienes |

#### 📊 Configuración de Categorías

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `insert_discovered_mappings.py` | Inserta mapeos de categoría iniciales (Audio, Celulares, etc.) | Ya ejecutado - tiene 4 categorías base |
| `generate_category_template.py` | Genera CSV para configurar categorías manualmente | Si quieres mapeo manual (OBSOLETO con detección de marca) |
| `import_category_mapping.py` | Importa CSV de categorías a BD | Si usaste generate_category_template.py |
| `discover_exito_categories.py` | Herramienta para descubrir categorías de Éxito | Debugging - explorar categorías |
| `verify_category.py` | Verifica si categoría existe en Éxito | Testing de categorías |
| `analyze_categories.py` | Analiza productos sin mapeo de categoría | Ver qué categorías faltan configurar |
| `apply_category_mapping.py` | Aplica mapeos a productos | Mantenimiento de categorías |

#### 🛠️ Herramientas Generales

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `backup_db.py` | Crea backup de la base de datos | Antes de migraciones grandes |
| `add_amazon_store.py` | Agrega Amazon como tienda | Expansión internacional |
| `activate_amazon_affiliate.py` | Activa programa de afiliados Amazon | Monetización |

**Uso típico - Actualizar precios**:
```bash
# 1. Scrapear todos los productos (local)
python scripts/utils/add_test_data.py

# 2. Ver lo que se guardó
python scripts/utils/view_db.py

# 3. Scrapear hacia producción (Supabase)
DATABASE_URL="postgresql://..." python scripts/utils/add_test_data.py
```

---

### `/scripts/` (Raíz)
Scripts misceláneos en la raíz de scripts/.

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `check_urls.py` | Ver URLs guardadas en price_snapshots | Verificar URLs de productos |

**Uso**:
```bash
python scripts/check_urls.py
```

---

### `/scripts/tests/`
Scripts de debug y pruebas.

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `test_brand_detection.py` | **🔥 NUEVO**: Prueba detección automática de marca | Verificar que marcas se detectan bien |
| `test_real_scraping.py` | **🔥 NUEVO**: Prueba scraping con detección de marca | Testing end-to-end de marca + categoría |
| `test_tienda_api.py` | Prueba configuración de una tienda antes de agregarla | Testing de scrapers nuevos |
| `test_airfryer_scraping.py` | Debug específico para Air Fryer Oster/Kalley | Debugging Air Fryer |
| `test_exito_url.py` | Prueba extracción de URLs de productos Éxito | Debugging URLs |
| `test_search_debug.py` | Prueba búsquedas en Éxito con diferentes términos | Debugging búsquedas |
| `check_products.py` | Ver productos en la BD filtrados por nombre | Ver qué hay en BD |

**Testing de detección de marca**:
```bash
# Verificar que AirPods → apple, Motorola → motorola, etc
python scripts/tests/test_brand_detection.py

# Probar scraping completo (requiere internet)
python scripts/tests/test_real_scraping.py
```

**Testing de nueva tienda**:
```bash
python scripts/tests/test_tienda_api.py
```

---

## 🚀 Archivos Principales (Raíz)

Estos quedan en la raíz porque son los más usados:

| Archivo | Descripción |
|---------|-------------|
| `api.py` | **Servidor FastAPI** - El corazón del backend |
| `database.py` | Abstracción de base de datos (SQLite/PostgreSQL) |
| `config_sitios.json` | Configuración de tiendas (Éxito, Homecenter) |
| `config_productos.json` | Configuración de productos con categorías |
| `job_scraper.py` | Job automático para scraping periódico |

---

## 📋 Flujo de Trabajo Típico

### 1️⃣ Setup Inicial Local (Primera vez)
```bash
# 1. Crear BD y migrar estructura (crea tablas + tiendas)
python scripts/migrations/migrate_to_db.py

# 2. Poblar con productos populares
python scripts/utils/add_popular_products.py

# 3. Insertar mapeos de categoría (Audio, Celulares, Smartwatches, Electrodomésticos)
python scripts/utils/insert_discovered_mappings.py

# 4. Scrapear precios (con detección automática de marca)
python scripts/utils/add_test_data.py

# 5. Ver resultados
python scripts/utils/view_db.py
```

### 2️⃣ Setup Inicial Producción (Supabase)
```bash
# 1. Código ya está en Railway (auto-deploy con git push)
#    - Tabla category_mappings se crea automáticamente

# 2. Migrar mapeos de categoría a Supabase (UNA SOLA VEZ)
DATABASE_URL="postgresql://..." python scripts/migrations/migrate_category_mappings_to_prod.py

# 3. Scrapear precios hacia producción
DATABASE_URL="postgresql://..." python scripts/utils/add_test_data.py

# 4. Verificar en https://epriceflo.com
```

### 3️⃣ Actualización de Precios (Diaria/Semanal)
```bash
# Opción A: Local → BD local (SQLite)
python scripts/utils/add_test_data.py

# Opción B: Local → Supabase (producción)
DATABASE_URL="postgresql://..." python scripts/utils/add_test_data.py

# Opción C: Verificar qué se actualizó
python scripts/utils/view_db.py
```

### 4️⃣ Configurar Nuevas Categorías
```bash
# 1. Ver qué categorías faltan configurar
python scripts/utils/analyze_categories.py

# 2. Ir a Éxito.com, F12 → Network → SearchQuery
#    Buscar un producto de la categoría
#    Copiar los filtros (category-X, value)

# 3. Agregar mapeo con Python (ver docs/CONFIGURAR_CATEGORIAS.md)

# 4. Probar que funcione
python scripts/tests/test_brand_detection.py
```

### 5️⃣ Agregar Nueva Tienda
```bash
# 1. Probar configuración
python scripts/tests/test_tienda_api.py

# 2. Si funciona, agregar a config_sitios.json
# 3. Migrar
python scripts/migrations/migrate_to_db.py
```

### 6️⃣ Debug de Problemas
```bash
# Ver productos en BD
python scripts/utils/view_db.py

# Verificar detección de marca
python scripts/tests/test_brand_detection.py

# Probar scraping específico
python scripts/tests/test_real_scraping.py

# Probar búsqueda específica
python scripts/tests/test_search_debug.py

# Verificar productos de una categoría
python scripts/tests/check_products.py
```

---

## 🏷️ Sistema de Detección de Marca y Categorías

### ✅ ¿Cómo Funciona?

El sistema combina **detección automática de marca** + **mapeo manual de categorías**:

1. **Marca**: Se detecta automáticamente del nombre del producto
   - `AirPods 3` → detecta `apple`
   - `Samsung Galaxy S24` → detecta `samsung`
   - `Motorola Edge 40` → detecta `motorola`

2. **Categoría**: Se lee de la tabla `category_mappings` en BD
   - `Audio` → `category-2:audio`
   - `Celulares` → `category-2:celulares`
   - `Smartwatches` → `category-2:reloj-inteligente`

3. **Resultado**: Genera filtros combinados automáticamente
   - `AirPods 3` + `Audio` → `category-2:audio` + `brand:apple`
   - `iPhone 14` + `Celulares` → `category-2:celulares` + `brand:apple`

### 📊 Categorías Configuradas

✅ **Ya Configuradas** (4/12):
- Audio
- Celulares
- Smartwatches
- Electrodomésticos

⚠️ **Pendientes** (8/12):
- Computadores, Gaming, Tablets, Televisores, Hogar, Cámaras, etc.

Ver `docs/CONFIGURAR_CATEGORIAS.md` para configurar las restantes.

### 🧪 Testing

```bash
# Verificar detección de marca
python scripts/tests/test_brand_detection.py

# Ver categorías sin configurar
python scripts/utils/analyze_categories.py
```

---

## 💡 Tips

### 🗄️ Base de Datos

**Scraping local vs producción**:
- Sin `DATABASE_URL`: Usa SQLite local (`data/prices.db` o `priceflo.db`)
- Con `DATABASE_URL`: Usa Supabase PostgreSQL (producción)

**Backup antes de migraciones**:
```bash
python scripts/utils/backup_db.py
```

### 🔍 Debugging

**Ver logs de scraping**:
```bash
# Los scrapers guardan archivos de debug:
# - Éxito_resultado.json
# - Homecenter_resultado.json
```

**Ver qué está pasando**:
```bash
# Ver productos y precios
python scripts/utils/view_db.py

# Ver detección de marca
python scripts/tests/test_brand_detection.py

# Ver categorías sin configurar
python scripts/utils/analyze_categories.py
```

### 🏷️ Marcas y Categorías

**Agregar nueva marca**:
Edita `scrapers/graphql_scraper.py` → `KNOWN_BRANDS` o `PRODUCT_TO_BRAND`

**Agregar nueva categoría**:
Ver `docs/CONFIGURAR_CATEGORIAS.md` con instrucciones paso a paso

**Verificar filtros generados**:
Los scripts de test muestran exactamente qué filtros se envían a cada tienda

### 📚 Documentación Adicional

- `docs/CONFIGURAR_CATEGORIAS.md` - Cómo configurar categorías con DevTools
- `docs/DETECCION_MARCA.md` - Sistema de detección de marca
- `docs/INFRAESTRUCTURA.md` - Railway, Supabase, dominios

---

**Última actualización**: 2025-01-30
