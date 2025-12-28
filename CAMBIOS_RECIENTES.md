# 📝 Cambios Recientes - ePriceFlo

Resumen de las mejoras implementadas.

---

## ✅ 1. Organización de Archivos

### Antes
```
/PricefloCompare
├── migrate_to_db.py
├── migrate_countries.py
├── test_tienda_api.py
├── add_test_data.py
├── add_popular_products.py
├── backup_db.py
├── ... (20+ archivos en la raíz)
```

### Ahora
```
/PricefloCompare
├── api.py                    # Backend principal
├── database.py               # Abstracción BD
├── config_sitios.json        # Config tiendas
├── config_productos.json     # Config productos
├── category_mapping.json     # Mapeo de categorías
│
├── /scripts
│   ├── README.md             # 📚 Guía de scripts
│   ├── /migrations           # Scripts de BD
│   │   ├── migrate_to_db.py
│   │   ├── migrate_countries.py
│   │   └── migrate_affiliate_fields.py
│   │
│   ├── /utils                # Herramientas
│   │   ├── add_test_data.py          # 🔥 Scraper principal
│   │   ├── add_popular_products.py   # Poblar BD
│   │   ├── backup_db.py
│   │   └── view_db.py
│   │
│   └── /tests                # Debug y pruebas
│       ├── test_tienda_api.py
│       ├── test_exito_url.py         # 🆕 Debug URLs
│       └── check_products.py
```

**Ventajas**:
- ✅ Fácil identificar qué hace cada script
- ✅ Raíz del proyecto más limpia
- ✅ README.md en /scripts con guía completa

---

## ✅ 2. Sistema de Mapeo de Categorías

### Problema
```
BD tiene: "Electrodomésticos", "Audio", "Gaming"
Éxito espera: "electrodomesticos", "tecnologia", "celulares"
```

### Solución
Archivo **`category_mapping.json`**:
```json
{
  "mappings": {
    "Electrodomésticos": "electrodomesticos",
    "Audio": "tecnologia",
    "Gaming": "tecnologia",
    "Celulares": "celulares"
  }
}
```

**Actualización en scraper** (`scrapers/graphql_scraper.py`):
```python
def map_category(category):
    """Mapea categoría de ePriceFlo a Éxito"""
    mapping = load_category_mapping()
    return mapping.get(category, category.lower())
```

**Ahora cuando scrapeas**:
```
Producto: Air Fryer Oster
Categoría en BD: Electrodomésticos
[Categoría mapeada]: electrodomesticos  ← ✅ Mapeada automáticamente
```

---

## ✅ 3. Filtro de Categoría Restaurado

### Estado Anterior (Incorrecto)
```json
"selectedFacets": [
  {"key": "channel", "value": "..."},
  {"key": "locale", "value": "es-CO"}
]
```
❌ Sin filtro de categoría → Resultados demasiado amplios → Baja precisión

### Estado Actual (Correcto)
```json
"selectedFacets": [
  {"key": "category-2", "value": "{product_category}"},  ← ✅ Restaurado
  {"key": "channel", "value": "..."},
  {"key": "locale", "value": "es-CO"}
]
```
✅ Con filtro → Busca solo en la categoría correcta → Alta precisión

---

## ⚠️ 4. Problema de URLs (POR RESOLVER)

### Síntoma
Cuando haces click en "Ver en tienda", se muestra la URL de la API:
```
https://www.exito.com/api/graphql?operationName=SearchQuery&variables=...
```

En lugar de la URL del producto:
```
https://www.exito.com/audifonos-apple-airpodspro3-ame-inalambricos-blanco-3226422/p
```

### Causa
El campo `linkText` no se está extrayendo correctamente del JSON de Éxito.

**Path actual**: `data.search.products.edges[0].node.linkText`

**Posibles causas**:
1. Éxito cambió la estructura del JSON
2. El path está incorrecto
3. linkText viene en otro formato

### Debug
Creado script: **`scripts/tests/test_exito_url.py`**

**Para ejecutar** (desde tu máquina, no desde ambiente con restricciones):
```bash
python scripts/tests/test_exito_url.py
```

Esto:
- ✅ Consulta la API de Éxito
- ✅ Guarda respuesta en `exito_airpods_response.json`
- ✅ Muestra dónde está `linkText` en la estructura
- ✅ Prueba construir la URL

### Cómo Arreglar (después de ejecutar el test)
1. Ejecuta el script de prueba
2. Abre `exito_airpods_response.json`
3. Busca el campo con el slug del producto (ej: `audifonos-apple-airpodspro3-ame...`)
4. Actualiza `url_xpath` en `config_sitios.json` con el path correcto

---

## 📚 Documentación Agregada

### `/scripts/README.md`
Guía completa de todos los scripts:
- Qué hace cada script
- Cuándo usarlo
- Ejemplos de uso
- Flujos de trabajo típicos

### `/CATEGORIAS_CONFIGURABLES.md`
Explicación del sistema de categorías (ya existía).

### `/docs/INFRAESTRUCTURA.md`
Documentación de la infraestructura completa (actualizada).

---

## 🚀 Cómo Usar los Cambios

### 1. Scrapear Precios (con categorías correctas)
```bash
# Ahora con mapeo automático de categorías
python scripts/utils/add_test_data.py
```

### 2. Verificar Productos en BD
```bash
python scripts/tests/check_products.py
```

### 3. Debug de URLs de Éxito
```bash
python scripts/tests/test_exito_url.py
```

### 4. Ver Estructura de Scripts
```bash
cat scripts/README.md
```

---

## 📊 Resumen de Commits

```
1. feat: Reorganizar archivos en carpetas scripts/
2. feat: Sistema de mapeo de categorías
3. fix: Restaurar filtro de categoría en Éxito
4. docs: Agregar scripts/README.md con guía completa
5. debug: Agregar test_exito_url.py para debug de URLs
```

---

## ✅ Pendiente

1. **Ejecutar test de URLs** para identificar path correcto de `linkText`
2. **Actualizar config_sitios.json** con el path correcto
3. **Verificar que las categorías mapeadas** funcionan en Éxito (probar con `add_test_data.py`)

---

**Fecha**: 2025-12-28
**Autor**: Claude + Germán Díaz
