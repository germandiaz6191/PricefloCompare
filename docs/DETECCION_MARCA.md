# 🏷️ Sistema de Detección Automática de Marca

## 📋 Resumen

El sistema ahora detecta automáticamente la **marca** del producto desde su nombre y genera los filtros correctos para Éxito, sin necesidad de configuración manual.

## 🎯 ¿Qué cambió?

### Antes ❌
- Solo se enviaba categoría (category-3)
- Muchos productos no encontraban resultados
- Ejemplo: "Gaming" no existe como categoría en Éxito

### Ahora ✅
- **Detección automática de marca** del nombre del producto
- **Filtros combinados**: categoría + marca
- **category-2** (no category-3)
- Genera exactamente los mismos filtros que DevTools

## 🔍 Ejemplos de Detección

| Producto | Marca Detectada | Categoría | Filtros Generados |
|----------|----------------|-----------|-------------------|
| AirPods 3 | `apple` | Audio | `category-2:audio` + `brand:apple` |
| iPhone 15 | `apple` | Celulares | `category-2:celulares` + `brand:apple` |
| Samsung Galaxy S24 | `samsung` | Celulares | `category-2:celulares` + `brand:samsung` |
| Motorola Edge 40 | `motorola` | Celulares | `category-2:celulares` + `brand:motorola` |
| JBL Charge 5 | `jbl` | Audio | `category-2:audio` + `brand:jbl` |
| MacBook Air M2 | `apple` | Computadores | `category-2:computadores` + `brand:apple` |

## 🧠 ¿Cómo funciona la detección?

### 1. Productos de Apple
El sistema reconoce estos productos como Apple:
- iPhone → `apple`
- iPad → `apple`
- AirPods → `apple`
- MacBook → `apple`
- iMac → `apple`
- Apple Watch → `apple`

### 2. Marcas conocidas
Lista de marcas que se detectan automáticamente:
- **Celulares**: Samsung, Motorola, Xiaomi, Huawei, OPPO, Realme
- **Computadores**: HP, Dell, Lenovo, ASUS, Acer
- **Electrodomésticos**: Kalley, Oster, Haceb, Whirlpool, Electrolux, Mabe, KitchenAid
- **Audio**: Bose, JBL, Sony
- **Cámaras**: Canon, Nikon, GoPro, DJI
- **Otros**: LG, Philips, Panasonic, Ring, Amazfit, Garmin, Fitbit

### 3. Fallback
Si no encuentra marca conocida, usa la **primera palabra** del nombre como marca.

## 📊 Payload Generado

### Ejemplo: AirPods 3 en categoría Audio

```json
{
  "operationName": "SearchQuery",
  "variables": {
    "first": 16,
    "after": "0",
    "sort": "price_asc",
    "term": "AirPods 3",
    "selectedFacets": [
      {
        "key": "category-2",
        "value": "audio"
      },
      {
        "key": "brand",
        "value": "apple"
      },
      {
        "key": "channel",
        "value": "{\"salesChannel\":\"1\",\"regionId\":\"\"}"
      },
      {
        "key": "locale",
        "value": "es-CO"
      }
    ]
  }
}
```

**Este payload es idéntico al que genera Éxito.com** ✅

## 🧪 Tests

### Verificar detección de marca
```bash
python scripts/tests/test_brand_detection.py
```

Este script prueba:
- Detección correcta de marca para AirPods, Motorola, Samsung, JBL
- Mapeo de categorías (Audio → audio, Celulares → celulares)
- Generación de payload correcto

### Probar scraping real
```bash
python scripts/tests/test_real_scraping.py
```

Este script hace búsquedas reales en Éxito para verificar que funciona end-to-end.

## ⚙️ Configuración

### Archivo: `config_sitios.json`
Ya está configurado para usar `category-2`:

```json
{
  "selectedFacets": [
    {
      "key": "category-2",
      "value": "{product_category}"
    }
  ]
}
```

### Archivo: `scrapers/graphql_scraper.py`
Contiene:
- `extract_brand()`: Detecta marca del nombre
- `map_category()`: Mapea categoría (Audio → audio)
- Lógica para agregar filtro de marca automáticamente

## 📝 ¿Necesitas agregar una marca?

Si encuentras productos que no detectan bien la marca:

1. Edita: `scrapers/graphql_scraper.py`
2. Agrega a `KNOWN_BRANDS`:
   ```python
   KNOWN_BRANDS = {
       'samsung', 'lg', 'sony', ...,
       'nueva_marca'  # ← Agregar aquí
   }
   ```

3. O agrega a `PRODUCT_TO_BRAND` si es producto específico:
   ```python
   PRODUCT_TO_BRAND = {
       'iphone': 'apple',
       'airpods': 'apple',
       'producto_especial': 'marca_real'  # ← Agregar aquí
   }
   ```

## 🎉 Beneficios

1. **Sin configuración manual**: No necesitas CSV de categorías
2. **Más resultados**: Los filtros combinados encuentran productos específicos
3. **Coincide con Éxito**: Genera exactamente los mismos filtros que el sitio
4. **Fácil de extender**: Solo agrega marcas nuevas al diccionario

## 📌 Resumen

**Ya no necesitas llenar el CSV de categorías manualmente**. El sistema:
- ✅ Detecta marca automáticamente
- ✅ Usa category-2 (correcto para Éxito)
- ✅ Genera filtros combinados categoría + marca
- ✅ Coincide exactamente con DevTools

**¡Listo para usar!** 🚀
