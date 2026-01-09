# 🔍 Cómo Verificar y Ajustar Categorías de Éxito

Guía para validar que los filtros de categoría están correctamente configurados.

---

## ❓ ¿Por qué es necesario?

Éxito usa filtros específicos para categorías en su API GraphQL:
- **Nivel**: `category-2`, `category-3`, `category-4`, etc.
- **Valor**: `celulares`, `accesorios-de-computador`, `electrodomesticos`, etc.

Si usamos valores incorrectos, la búsqueda no retorna resultados.

---

## ✅ Mapeo Actual (Pre-completado)

| Categoría ePriceFlo | Nivel | Valor Éxito | Estado |
|---------------------|-------|-------------|--------|
| **Gaming** | `category-3` | `accesorios-de-computador` | ✅ CONFIRMADO |
| Celulares | `category-3` | `celulares` | ⚠️ Verificar |
| Audio | `category-3` | `audifonos` | ⚠️ Verificar |
| Computadores | `category-3` | `portatiles` | ⚠️ Verificar |
| Tablets | `category-3` | `tablets` | ⚠️ Verificar |
| Electrodomésticos | `category-3` | `electrodomesticos` | ⚠️ Verificar |
| Televisores | `category-3` | `televisores` | ⚠️ Verificar |
| Smartwatches | `category-3` | `smartwatches` | ⚠️ Verificar |
| Hogar | `category-3` | `hogar` | ⚠️ Verificar |
| Cámaras | `category-3` | `camaras` | ⚠️ Verificar |

---

## 🔧 Cómo Verificar una Categoría

### Paso 1: Ir a Éxito.com

1. Abre https://www.exito.com
2. Busca un producto de la categoría (ej: "Teclado Gamer" para Gaming)

### Paso 2: Abrir DevTools

1. Presiona **F12** para abrir DevTools
2. Ve a la pestaña **Network**
3. Filtra por: `SearchQuery`

### Paso 3: Buscar en Éxito

1. Busca el producto en Éxito.com
2. En DevTools, verás una petición llamada `SearchQuery`
3. Click en la petición

### Paso 4: Examinar el Request

1. Ve a la pestaña **Payload** o **Request**
2. Busca el objeto `variables`
3. Dentro de `selectedFacets`, busca el facet de categoría

**Ejemplo para Gaming (Teclado Gamer)**:
```json
{
  "variables": {
    "term": "Teclado Gamer",
    "selectedFacets": [
      {
        "key": "category-3",           ← Este es el NIVEL
        "value": "accesorios-de-computador"  ← Este es el VALOR
      },
      {
        "key": "channel",
        "value": "{\"salesChannel\":\"1\",\"regionId\":\"\"}"
      }
    ]
  }
}
```

### Paso 5: Actualizar el Mapping (si es diferente)

Si el valor encontrado es diferente al pre-completado:

1. Edita `category_mapping_template.json`
2. Actualiza `exito_level` y/o `exito_value` para esa categoría
3. Ejecuta: `python scripts/utils/apply_category_mapping.py`

---

## 📝 Ejemplo Completo: Verificar "Celulares"

### 1. Buscar en Éxito
- Producto: "Samsung Galaxy S24"
- URL: https://www.exito.com

### 2. DevTools → Network → SearchQuery

**Request encontrado**:
```json
{
  "variables": {
    "term": "Samsung Galaxy S24",
    "selectedFacets": [
      {
        "key": "category-3",
        "value": "celulares"
      }
    ]
  }
}
```

### 3. Comparar con Mapping Actual

**Mapping actual**:
```json
"Celulares": {
  "level": "category-3",
  "value": "celulares"
}
```

**Resultado**: ✅ Coincide, no requiere cambios

### 4. Si NO coincidiera

**Ejemplo**: Si el valor real fuera `"smartphones"` en vez de `"celulares"`:

1. Editar `category_mapping_template.json`:
   ```json
   "Celulares": {
     "exito_level": "category-3",
     "exito_value": "smartphones",  ← Actualizar aquí
     "example_product": "Samsung Galaxy S24",
     "notes": "Verificado: usa 'smartphones' en vez de 'celulares'"
   }
   ```

2. Aplicar cambios:
   ```bash
   python scripts/utils/apply_category_mapping.py
   ```

3. Probar scraper:
   ```bash
   python scripts/utils/add_test_data.py
   ```

---

## 🚀 Verificación Rápida (10 categorías)

Ejecuta este proceso para cada categoría:

```
1. Gaming         → Buscar: "Teclado Gamer"       ✅ CONFIRMADO
2. Celulares      → Buscar: "Samsung Galaxy S24"  ⚠️ Verificar
3. Audio          → Buscar: "AirPods 3"           ⚠️ Verificar
4. Computadores   → Buscar: "MacBook Air M2"      ⚠️ Verificar
5. Tablets        → Buscar: "iPad 10"             ⚠️ Verificar
6. Electrodomésticos → Buscar: "Air Fryer Oster" ⚠️ Verificar
7. Televisores    → Buscar: "Smart TV Samsung"    ⚠️ Verificar
8. Smartwatches   → Buscar: "Apple Watch SE"      ⚠️ Verificar
9. Hogar          → Buscar: "Batidora KitchenAid" ⚠️ Verificar
10. Cámaras       → Buscar: "Canon EOS Rebel T7"  ⚠️ Verificar
```

**Tiempo estimado**: ~20 minutos para verificar las 10 categorías

---

## 💡 Tips

### Tip 1: Algunos productos pueden estar en múltiples niveles
```
Ejemplo: "iPhone 15"
  - category-2: "tecnologia"
  - category-3: "celulares"
  - category-4: "apple"
```
Usa el más específico (`category-3` o `category-4` suele funcionar mejor).

### Tip 2: Valores con guiones
Éxito usa `kebab-case` en algunos valores:
- ✅ `accesorios-de-computador`
- ❌ `accesorios de computador`

### Tip 3: URLs de prueba
Puedes probar directamente con URLs:
```
https://www.exito.com/api/graphql?operationName=SearchQuery&variables=%7B%22first%22%3A16%2C%22term%22%3A%22Teclado+Gamer%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22category-3%22%2C%22value%22%3A%22accesorios-de-computador%22%7D%5D%7D
```

Si retorna productos → ✅ Correcto
Si retorna vacío → ❌ Valor incorrecto

---

## ✅ Checklist Final

Antes de scrapear todos los productos:

- [ ] Verificar al menos 3-5 categorías más usadas
- [ ] Actualizar `category_mapping_template.json` con valores correctos
- [ ] Ejecutar `python scripts/utils/apply_category_mapping.py`
- [ ] Probar scraper: `python scripts/utils/add_test_data.py`
- [ ] Verificar en logs que las categorías se mapean correctamente

---

**Última actualización**: 2025-12-28
**Autor**: Claude + Germán Díaz
