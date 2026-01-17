# 📁 Mapeo de Categorías - Simple y en BD

Sistema simple para mapear categorías de ePriceFlo a filtros de cada tienda.

---

## ✅ Solución Simple: Todo en Base de Datos

En lugar de archivos JSON complicados, **todo está en la BD** en una tabla simple.

### Tabla: `category_mappings`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID auto-incremental |
| store_id | INTEGER | ID de la tienda (FK a stores) |
| category_name | VARCHAR(100) | Nombre de categoría (ej: "Gaming") |
| filter_level | VARCHAR(20) | Nivel del filtro (ej: "category-3") |
| filter_value | VARCHAR(100) | Valor del filtro (ej: "accesorios-de-computador") |

---

## 🚀 Setup Inicial

### 1. Ejecutar migración
```bash
python scripts/migrations/migrate_category_mappings.py
```

Esto:
- ✅ Crea la tabla `category_mappings`
- ✅ Migra datos del JSON existente
- ✅ Muestra resumen de categorías migradas

### 2. Verificar
```bash
python scripts/utils/view_db.py
```

---

## 📝 Agregar/Editar Categorías

### Opción 1: SQL Directo (más simple)

```sql
-- Agregar nueva categoría
INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value)
VALUES (1, 'Deportes', 'category-3', 'deportes');

-- Actualizar categoría existente
UPDATE category_mappings
SET filter_value = 'accesorios-de-computador', filter_level = 'category-3'
WHERE store_id = 1 AND category_name = 'Gaming';

-- Ver todas las categorías de una tienda
SELECT * FROM category_mappings WHERE store_id = 1;
```

### Opción 2: Desde Python

```python
from database import execute_query

# Agregar
execute_query("""
    INSERT OR IGNORE INTO category_mappings
    (store_id, category_name, filter_level, filter_value)
    VALUES (?, ?, ?, ?)
""", (1, 'Deportes', 'category-3', 'deportes'))

# Actualizar
execute_query("""
    UPDATE category_mappings
    SET filter_value = ?
    WHERE store_id = ? AND category_name = ?
""", ('audifonos-inalambricos', 1, 'Audio'))
```

---

## 🔍 Cómo Encontrar los Valores Correctos

### Paso 1: Buscar en Éxito.com

1. Abre https://www.exito.com
2. Busca un producto de la categoría (ej: "Teclado Gamer")

### Paso 2: DevTools

1. F12 → Network
2. Busca `SearchQuery`
3. Mira el objeto `selectedFacets`

### Paso 3: Copiar valores

```json
{
  "selectedFacets": [
    {
      "key": "category-3",                    ← filter_level
      "value": "accesorios-de-computador"     ← filter_value
    }
  ]
}
```

### Paso 4: Agregar a BD

```sql
INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value)
VALUES (1, 'Gaming', 'category-3', 'accesorios-de-computador');
```

---

## ✅ Categorías Pre-configuradas (Éxito)

| Categoría | Level | Value | Estado |
|-----------|-------|-------|--------|
| Gaming | category-3 | accesorios-de-computador | ✅ Confirmado |
| Celulares | category-3 | celulares | ⚠️ Verificar |
| Audio | category-3 | audifonos | ⚠️ Verificar |
| Computadores | category-3 | portatiles | ⚠️ Verificar |
| Tablets | category-3 | tablets | ⚠️ Verificar |
| Electrodomésticos | category-3 | electrodomesticos | ⚠️ Verificar |
| Televisores | category-3 | televisores | ⚠️ Verificar |
| Smartwatches | category-3 | smartwatches | ⚠️ Verificar |
| Hogar | category-3 | hogar | ⚠️ Verificar |
| Cámaras | category-3 | camaras | ⚠️ Verificar |

---

## 🎯 Cómo Funciona (Internamente)

1. **Scraper necesita categoría** → Llama a `get_category_mapping("Éxito", "Gaming")`
2. **BD retorna** → `{"level": "category-3", "value": "accesorios-de-computador"}`
3. **Scraper usa** → Reemplaza el filtro con estos valores
4. **Cache** → Se guarda en memoria para no repetir queries

**Ventajas**:
- ✅ Simple: Solo una tabla
- ✅ Por tienda: Cada tienda puede tener sus propios valores
- ✅ Fácil editar: SQL directo o herramientas visuales
- ✅ Performance: Cache en memoria
- ✅ Producción: Los cambios en Supabase se reflejan inmediatamente

---

## 📊 Resumen

**Antes** (complicado):
- category_mapping.json
- category_mapping_template.json
- Scripts de análisis/aplicación
- Archivos sincronización

**Ahora** (simple):
- 1 tabla: `category_mappings`
- SQL directo para editar
- Lectura automática desde scraper

---

**Última actualización**: 2025-12-28
**Autor**: Germán Díaz + Claude
