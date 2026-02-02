# 📋 Guía: Configurar Categorías Restantes

## ✅ Categorías Ya Configuradas

| Categoría | Filtros | Productos |
|-----------|---------|-----------|
| Audio | `category-2:audio` + marca | 10 productos |
| Celulares | `category-2:celulares` + marca | 13 productos |
| Smartwatches | `category-2:reloj-inteligente` + marca | 7 productos |
| Electrodomésticos | `category-2:electrodomesticos-hogar` + marca | 12 productos |

## ⚠️ Categorías Pendientes (8)

1. **Computadores** (10 productos)
2. **Cámaras** (7 productos)
3. **Gaming** (12 productos)
4. **Hogar** (10 productos)
5. **Tablets** (7 productos)
6. **Televisores** (10 productos)
7. **celulares** (1 producto) - duplicado, limpiar
8. **electrodomesticos** (2 productos) - duplicado, limpiar

## 🔍 Cómo Descubrir Filtros en DevTools

### Paso 1: Abrir DevTools
1. Ve a https://www.exito.com
2. Presiona **F12**
3. Ve a la pestaña **Network**

### Paso 2: Buscar un Producto
Busca un producto de la categoría que quieres configurar. Por ejemplo:
- **Computadores**: Busca "MacBook Air M2" o "Portátil HP"
- **Gaming**: Busca "Control PS5" o "Mouse Gamer"
- **Tablets**: Busca "iPad 10" o "Samsung Galaxy Tab"

### Paso 3: Capturar la Petición
1. En Network, filtra por: `SearchQuery`
2. Click en la petición
3. Ve a **Payload** o **Request**
4. Copia el JSON de `selectedFacets`

### Ejemplo de lo que verás:
```json
{
  "selectedFacets": [
    {"key": "category-2", "value": "computadores"},
    {"key": "brand", "value": "apple"},
    {"key": "channel", "value": "{\"salesChannel\":\"1\",\"regionId\":\"\"}"},
    {"key": "locale", "value": "es-CO"}
  ]
}
```

**Lo que necesitas anotar:**
- `category-X` (el nivel: category-1, category-2, category-3)
- El valor (ej: "computadores", "televisores", "gaming")
- Si usa marca o no

## 💾 Cómo Agregar el Mapeo

### Opción A: Comando Python Rápido

```bash
python -c "
from database import get_db, _param_placeholder

with get_db() as conn:
    cursor = conn.cursor()
    ph = _param_placeholder()

    cursor.execute(f'SELECT id FROM stores WHERE name = {ph}', ('Éxito',))
    result = cursor.fetchone()
    exito_id = result['id'] if isinstance(result, dict) else result[0]

    # EDITAR ESTOS VALORES ↓
    category_name = 'Computadores'  # Nombre en tu BD
    filter_level = 'category-2'     # Lo que encontraste en DevTools
    filter_value = 'computadores'   # Lo que encontraste en DevTools
    use_brand = 1                   # 1 = usa marca, 0 = no usa marca

    if ph == '%s':
        sql = f'''INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value, use_brand)
                  VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
                  ON CONFLICT (store_id, category_name) DO UPDATE
                  SET filter_level = EXCLUDED.filter_level, filter_value = EXCLUDED.filter_value, use_brand = EXCLUDED.use_brand'''
    else:
        sql = f'''INSERT OR REPLACE INTO category_mappings (store_id, category_name, filter_level, filter_value, use_brand)
                  VALUES ({ph}, {ph}, {ph}, {ph}, {ph})'''

    cursor.execute(sql, (exito_id, category_name, filter_level, filter_value, use_brand))
    conn.commit()
    print(f'✅ {category_name} configurado: {filter_level}:{filter_value}')
"
```

### Opción B: Script con Múltiples Categorías

Crea un archivo `configure_categories.py`:

```python
from database import get_db, _param_placeholder

# EDITAR AQUÍ - Agrega las categorías que descubriste
mappings = [
    # Ejemplo:
    # {"category": "Computadores", "level": "category-2", "value": "computadores", "use_brand": 1},
    # {"category": "Gaming", "level": "category-2", "value": "gaming", "use_brand": 1},
    # {"category": "Tablets", "level": "category-2", "value": "tablets", "use_brand": 1},
]

with get_db() as conn:
    cursor = conn.cursor()
    ph = _param_placeholder()

    cursor.execute(f'SELECT id FROM stores WHERE name = {ph}', ('Éxito',))
    result = cursor.fetchone()
    exito_id = result['id'] if isinstance(result, dict) else result[0]

    for m in mappings:
        if ph == '%s':
            sql = f'''INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value, use_brand)
                      VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
                      ON CONFLICT (store_id, category_name) DO UPDATE
                      SET filter_level = EXCLUDED.filter_level, filter_value = EXCLUDED.filter_value, use_brand = EXCLUDED.use_brand'''
        else:
            sql = f'''INSERT OR REPLACE INTO category_mappings (store_id, category_name, filter_level, filter_value, use_brand)
                      VALUES ({ph}, {ph}, {ph}, {ph}, {ph})'''

        cursor.execute(sql, (exito_id, m['category'], m['level'], m['value'], m['use_brand']))
        print(f"✅ {m['category']} → {m['level']}:{m['value']}")

    conn.commit()
    print(f"\n🎉 {len(mappings)} categorías configuradas")
```

Luego ejecuta:
```bash
python configure_categories.py
```

## 📊 Verificar Mapeos

Ver todos los mapeos configurados:

```bash
python -c "
from database import get_db, _param_placeholder

with get_db() as conn:
    cursor = conn.cursor()
    ph = _param_placeholder()

    cursor.execute(f'''
        SELECT cm.category_name, cm.filter_level, cm.filter_value, cm.use_brand
        FROM category_mappings cm
        JOIN stores s ON cm.store_id = s.id
        WHERE s.name = {ph}
        ORDER BY cm.category_name
    ''', ('Éxito',))

    print('📊 Categorías Configuradas:')
    print('='*70)
    for row in cursor.fetchall():
        if isinstance(row, dict):
            cat, lvl, val, brand = row['category_name'], row['filter_level'], row['filter_value'], row['use_brand']
        else:
            cat, lvl, val, brand = row[0], row[1], row[2], row[3]

        brand_txt = '+ marca' if brand else ''
        if lvl:
            print(f'{cat:20s} → {lvl}:{val:30s} {brand_txt}')
        else:
            print(f'{cat:20s} → solo marca')
"
```

## 🧪 Probar un Producto

Después de configurar, prueba que funcione:

```bash
python -c "
from scrapers.generic_scrapers import scrape_price
import json

with open('config_sitios.json') as f:
    sites = json.load(f)
    exito = next(s for s in sites if s['sitio'] == 'Éxito')

# Probar con un producto de la categoría configurada
result = scrape_price(exito, 'MacBook Air M2', 'Computadores')
if result:
    print(f'✅ Encontrado: {result[\"title\"]}')
    print(f'Precio: {result[\"price\"]}')
"
```

## 🔄 Workflow Completo

1. **Busca en Éxito.com** un producto de la categoría
2. **Captura filtros** en DevTools (F12 → Network → SearchQuery)
3. **Anota** el nivel (category-X) y valor
4. **Ejecuta** el comando Python para agregar el mapeo
5. **Verifica** con el script de prueba
6. **Repite** para las 8 categorías restantes

## 🚀 Al Terminar

Cuando hayas configurado todas las categorías, el scraper automáticamente:
- ✅ Detectará la marca del producto
- ✅ Usará la categoría correcta de la BD
- ✅ Generará los filtros exactos que usa Éxito
- ✅ Encontrará más productos con mejores resultados

---

**💡 Tip:** Empieza con las categorías que más productos tienen (Gaming: 12, Electrodomésticos ya está, Celulares ya está).
