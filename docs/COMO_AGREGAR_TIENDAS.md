# 🏪 Cómo Agregar Nuevas Tiendas a ePriceFlo

Guía completa para investigar y configurar scrapers de nuevas tiendas colombianas.

---

## 📋 Tabla de Contenidos

1. [Investigación Manual de APIs](#investigación-manual-de-apis)
2. [Tiendas Colombianas Populares](#tiendas-colombianas-populares)
3. [Configuraciones Propuestas](#configuraciones-propuestas)
4. [Proceso de Prueba](#proceso-de-prueba)

---

## 🔍 Investigación Manual de APIs

### Paso 1: Abrir DevTools

1. Ve al sitio web de la tienda (ej: https://www.alkosto.com)
2. Abre las herramientas de desarrollador:
   - **Chrome/Edge**: `F12` o `Ctrl+Shift+I`
   - **Firefox**: `F12` o `Ctrl+Shift+I`
   - **Safari**: `Cmd+Option+I`

### Paso 2: Capturar Requests

1. Ve a la pestaña **Network** (Red)
2. Marca **Fetch/XHR** para filtrar solo peticiones AJAX
3. En el sitio, busca un producto (ej: "iPhone 15")
4. Observa las peticiones que aparecen

### Paso 3: Identificar el Endpoint

Busca peticiones que contengan:
- `/graphql` → GraphQL API (como Éxito)
- `/api/search` → REST API
- `/search?` → Query params
- Respuestas JSON con datos de productos

### Paso 4: Analizar la Petición

Haz clic en la petición y revisa:

**Headers:**
```
Request URL: https://www.tienda.com/api/graphql
Request Method: POST
Content-Type: application/json
```

**Payload (Body):**
```json
{
  "operationName": "ProductSearch",
  "variables": {
    "query": "iPhone 15",
    "limit": 20
  },
  "query": "query ProductSearch($query: String!) { ... }"
}
```

**Response:**
```json
{
  "data": {
    "products": [{
      "name": "iPhone 15 128GB",
      "price": 3999000,
      "url": "/iphone-15/p"
    }]
  }
}
```

### Paso 5: Extraer XPaths para Datos

Identifica las rutas para:
- **Nombre del producto**: `data.products[0].name`
- **Precio**: `data.products[0].price`
- **URL**: `data.products[0].url`

---

## 🏬 Tiendas Colombianas Populares

### 1. **Alkosto** 🔴
- **URL**: https://www.alkosto.com
- **Tipo**: Electrodomésticos, tecnología, hogar
- **Plataforma Probable**: VTEX o Custom
- **Método**: Investigar (GraphQL o REST)

### 2. **Falabella** 🟢
- **URL**: https://www.falabella.com.co
- **Tipo**: Multitienda (ropa, tecnología, hogar)
- **Presencia**: Colombia, Chile, Perú, Argentina
- **Plataforma Probable**: VTEX o Custom
- **Método**: Investigar (probablemente GraphQL)

### 3. **Ktronix** 🔵
- **URL**: https://www.ktronix.com
- **Tipo**: Tecnología y electrónica
- **Plataforma Probable**: VTEX (hermana de Éxito)
- **Método**: Probablemente GraphQL similar a Éxito

### 4. **Olimpica** 🟡
- **URL**: https://www.olimpica.com
- **Tipo**: Supermercado con electrónica
- **Método**: Investigar

### 5. **Mercado Libre Colombia** 🟠
- **URL**: https://www.mercadolibre.com.co
- **Tipo**: Marketplace
- **API**: Probablemente tiene API pública
- **Documentación**: https://developers.mercadolibre.com.co/

---

## ⚙️ Configuraciones Propuestas

### Configuración para Alkosto (Tentativa)

```json
{
  "sitio": "Alkosto",
  "country_code": "CO",
  "currency": "COP",
  "url": "https://www.alkosto.com/_v/segment/graphql/v1",
  "fetch_method": "graphql",
  "requires_url_variables": true,
  "base_product_url": "https://www.alkosto.com",
  "params": {
    "operationName": "productSearchV3",
    "variables": {
      "hideUnavailableItems": false,
      "skusFilter": "ALL",
      "simulationBehavior": "default",
      "installmentCriteria": "MAX_WITHOUT_INTEREST",
      "productOriginVtex": false,
      "map": "ft",
      "query": "{product_name}",
      "orderBy": "OrderByPriceDESC",
      "from": 0,
      "to": 9,
      "selectedFacets": []
    },
    "extensions": {
      "persistedQuery": {
        "version": 1,
        "sha256Hash": "HASH_A_INVESTIGAR"
      }
    }
  },
  "title_xpath": "data.productSearch.products[0].productName",
  "price_xpath": "data.productSearch.products[0].priceRange.sellingPrice.highPrice",
  "url_xpath": "data.productSearch.products[0].linkText"
}
```

**⚠️ Nota:** Requiere investigación manual para confirmar endpoint y hash.

### Configuración para Falabella (Tentativa)

```json
{
  "sitio": "Falabella",
  "country_code": "CO",
  "currency": "COP",
  "url": "https://www.falabella.com.co/s/browse/v1/search",
  "fetch_method": "rest",
  "base_product_url": "https://www.falabella.com.co",
  "params": {
    "Ntt": "{product_name}",
    "page": 1
  },
  "title_xpath": "results[0].displayName",
  "price_xpath": "results[0].prices.offerPrice",
  "url_xpath": "results[0].url"
}
```

**⚠️ Nota:** Requiere investigación manual para confirmar estructura.

### Configuración para Ktronix (Tentativa)

Ktronix es parte del Grupo Éxito, por lo que probablemente use VTEX con GraphQL similar:

```json
{
  "sitio": "Ktronix",
  "country_code": "CO",
  "currency": "COP",
  "url": "https://www.ktronix.com/api/graphql",
  "fetch_method": "graphql",
  "requires_url_variables": true,
  "base_product_url": "https://www.ktronix.com",
  "url_suffix": "/p",
  "params": {
    "operationName": "SearchQuery",
    "variables":{
      "first": 16,
      "after": "0",
      "sort": "price_asc",
      "term": "{product_name}",
      "selectedFacets": [
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
  },
  "title_xpath": "data.search.products.edges[0].node.items[0].name",
  "price_xpath": "data.search.products.edges[0].node.items[0].sellers[1].commertialOffer.PriceWithoutDiscount",
  "url_xpath": "data.search.products.edges[0].node.linkText"
}
```

**✅ Alta probabilidad de funcionar** (misma plataforma que Éxito).

---

## 🧪 Proceso de Prueba

### 1. Agregar configuración tentativa a `config_sitios.json`

```json
{
  "sitio": "NuevaTienda",
  "country_code": "CO",
  "currency": "COP",
  "url": "URL_INVESTIGADA",
  "fetch_method": "graphql",
  ...
}
```

### 2. Migrar la tienda a la BD

```bash
python migrate_to_db.py
```

### 3. Probar con un producto

```bash
python add_test_data.py
```

### 4. Revisar logs

Busca:
- ✅ `Mejor resultado: 'Producto' (score: 85/100)`
- ❌ `Error parseando respuesta JSON`
- ❌ `No se encontró ningún resultado relevante`

### 5. Ajustar configuración

Si falla:
1. Revisa el archivo `NuevaTienda_resultado.json` generado
2. Ajusta los `xpath` según la estructura real
3. Verifica el `url` y `params`
4. Intenta de nuevo

---

## 📝 Plantilla de Investigación

Usa esta plantilla para documentar tu investigación:

```markdown
## Investigación: [Nombre Tienda]

**Fecha**: 2025-XX-XX
**URL**: https://www.tienda.com
**Investigador**: [Tu nombre]

### Request Capturada

**Endpoint**:
**Método**: POST/GET
**Headers**:
```
Content-Type: application/json
```

**Payload**:
```json
{...}
```

**Response**:
```json
{...}
```

### XPaths Identificados

- **Nombre**: `data.products[0].name`
- **Precio**: `data.products[0].price`
- **URL**: `data.products[0].url`

### Configuración Propuesta

```json
{...}
```

### Resultado de Pruebas

- [ ] ✅ Respuesta JSON válida
- [ ] ✅ Extrae nombre correctamente
- [ ] ✅ Extrae precio correctamente
- [ ] ✅ Extrae URL correctamente
- [ ] ✅ Score de relevancia >= 60

### Notas

- [Observaciones adicionales]
```

---

## 🎯 Próximos Pasos Recomendados

1. **Investigar Ktronix** (alta prioridad - misma plataforma que Éxito)
2. **Investigar Alkosto** (muy popular en Colombia)
3. **Investigar Falabella** (expansión internacional)
4. **Investigar Mercado Libre** (tiene API pública oficial)

---

## 💡 Tips Importantes

1. **User-Agent**: Algunas tiendas bloquean requests sin User-Agent válido
2. **Rate Limiting**: No hagas demasiadas peticiones seguidas
3. **Headers**: Copia todos los headers importantes (referer, origin, etc.)
4. **Cookies**: Algunas APIs requieren cookies de sesión
5. **Permisos**: Respeta los términos de servicio de cada tienda

---

## 🔗 Referencias

- [VTEX GraphQL Docs](https://developers.vtex.com/docs/guides/graphql-in-vtex-io)
- [VTEX Store GraphQL](https://github.com/vtex-apps/store-graphql)
- [Mercado Libre API](https://developers.mercadolibre.com.co/)
