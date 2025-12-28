# 📁 Scripts de ePriceFlo

Organización de scripts auxiliares del proyecto.

---

## 📂 Estructura

### `/scripts/migrations/`
Scripts para migrar y actualizar la base de datos.

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `migrate_to_db.py` | Migración inicial: crea tablas y migra productos/tiendas | Primera vez o reset de BD |
| `migrate_countries.py` | Agrega soporte multi-país a la BD | Para habilitar selector de países |
| `migrate_affiliate_fields.py` | Agrega campos de afiliados a stores | Para monetización con afiliados |

**Uso**:
```bash
python scripts/migrations/migrate_to_db.py
python scripts/migrations/migrate_countries.py
```

---

### `/scripts/utils/`
Herramientas para agregar datos y mantenimiento.

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `add_test_data.py` | **🔥 PRINCIPAL**: Scrapea precios de todos los productos | Actualizar precios en BD |
| `add_popular_products.py` | Agrega 98 productos populares basados en investigación | Poblar BD inicial |
| `backup_db.py` | Crea backup de la base de datos | Antes de migraciones grandes |
| `view_db.py` | Ver contenido de la BD en formato legible | Debugging |
| `add_amazon_store.py` | Agrega Amazon como tienda | Expansión internacional |
| `activate_amazon_affiliate.py` | Activa programa de afiliados Amazon | Monetización |

**Scraping de precios** (el más usado):
```bash
# Scrapear todos los productos
python scripts/utils/add_test_data.py

# Ver lo que se guardó
python scripts/utils/view_db.py
```

---

### `/scripts/tests/`
Scripts de debug y pruebas.

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `test_tienda_api.py` | Prueba configuración de una tienda antes de agregarla | Testing de scrapers |
| `test_airfryer_scraping.py` | Debug específico para Air Fryer Oster/Kalley | Debugging |
| `test_search_debug.py` | Prueba búsquedas en Éxito con diferentes términos | Debugging |
| `check_products.py` | Ver productos en la BD filtrados por nombre | Ver qué hay en BD |

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

### 1️⃣ Setup Inicial (Primera vez)
```bash
# 1. Crear BD y migrar estructura
python scripts/migrations/migrate_to_db.py

# 2. Agregar soporte multi-país (opcional)
python scripts/migrations/migrate_countries.py

# 3. Poblar con productos populares
python scripts/utils/add_popular_products.py

# 4. Scrapear precios
python scripts/utils/add_test_data.py
```

### 2️⃣ Actualización de Precios (Diaria/Semanal)
```bash
# Opción A: Local → BD local
python scripts/utils/add_test_data.py

# Opción B: Local → Supabase (producción)
DATABASE_URL="postgresql://..." python scripts/utils/add_test_data.py
```

### 3️⃣ Agregar Nueva Tienda
```bash
# 1. Probar configuración
python scripts/tests/test_tienda_api.py

# 2. Si funciona, agregar a config_sitios.json
# 3. Migrar
python scripts/migrations/migrate_to_db.py
```

### 4️⃣ Debug de Problemas
```bash
# Ver productos en BD
python scripts/utils/view_db.py

# Probar búsqueda específica
python scripts/tests/test_search_debug.py

# Verificar productos de una categoría
python scripts/tests/check_products.py
```

---

## 💡 Tips

**Scraping local vs producción**:
- Sin `DATABASE_URL`: Usa SQLite local (`data/prices.db`)
- Con `DATABASE_URL`: Usa Supabase (producción)

**Backup antes de migraciones**:
```bash
python scripts/utils/backup_db.py
```

**Ver logs de scraping**:
```bash
# Los scrapers guardan archivos de debug:
# - Éxito_resultado.json
# - Homecenter_resultado.json
```

---

**Última actualización**: 2025-12-28
