# 🔬 Análisis Técnico de Scrapers - ePriceFlo

Documento técnico que explica cómo funcionan los scrapers de Éxito y Homecenter.

---

## 📋 Tabla de Contenidos

1. [Arquitectura General](#arquitectura-general)
2. [Scraper GraphQL (Éxito)](#scraper-graphql-éxito)
3. [Scraper HTML (Homecenter)](#scraper-html-homecenter)
4. [Sistema de Relevancia](#sistema-de-relevancia)
5. [Extracción de Datos](#extracción-de-datos)
6. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 🏗️ Arquitectura General

### Flujo del Sistema

```
Usuario busca "iPhone 15"
         ↓
┌────────────────────────┐
│ generic_scrapers.py    │
│ scrape_price()         │
└────────────────────────┘
         ↓
    ¿fetch_method?
         ↓
    ┌────┴────┐
    ↓         ↓
GraphQL      HTML
(Éxito)   (Homecenter)
```

### Archivo de Configuración: `config_sitios.json`

```json
[
  {
    "sitio": "Éxito",
    "country_code": "CO",
    "currency": "COP",
    "url": "https://www.exito.com/api/graphql",
    "fetch_method": "graphql",
    ...
  },
  {
    "sitio": "Homecenter",
    "country_code": "CO",
    "currency": "COP",
    "url": "https://www.homecenter.com.co/homecenter-co/search",
    "fetch_method": "html",
    ...
  }
]
```

---

## 🔷 Scraper GraphQL (Éxito)

### 1. Configuración Completa

```json
{
  "sitio": "Éxito",
  "country_code": "CO",
  "currency": "COP",
  "url": "https://www.exito.com/api/graphql",
  "fetch_method": "graphql",
  "requires_url_variables": true,
  "base_product_url": "https://www.exito.com",
  "url_suffix": "/p",
  "params": {
    "operationName": "SearchQuery",
    "variables": {
      "first": 16,
      "after": "0",
      "sort": "price_asc",
      "term": "{product_name}",
      "selectedFacets": [
        {
          "key": "category-2",
          "value": "{product_category}"
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
  },
  "title_xpath": "data.search.products.edges[0].node.items[0].name",
  "price_xpath": "data.search.products.edges[0].node.items[0].sellers[1].commertialOffer.PriceWithoutDiscount",
  "url_xpath": "data.search.products.edges[0].node.linkText"
}
```

### 2. Cómo Funciona

#### Paso 1: Construcción del Payload

```python
# 1. Cargar configuración
payload = sitio_config.get("params", {})

# 2. Convertir a string para reemplazo
payload_str = json.dumps(payload)

# 3. Reemplazar placeholders
payload_str = payload_str.replace("{product_name}", "iPhone 15")
# Resultado: "term": "iPhone 15"
```

**Ejemplo de payload resultante:**
```json
{
  "operationName": "SearchQuery",
  "variables": {
    "first": 16,
    "after": "0",
    "sort": "price_asc",
    "term": "iPhone 15",
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
}
```

#### Paso 2: Construcción de la Request

**Tipo de Request: GET con variables en URL**

```python
# Éxito usa requires_url_variables: true
# Esto significa que las variables van en la URL, no en el body

operation_name = "SearchQuery"
variables = {
  "first": 16,
  "after": "0",
  "sort": "price_asc",
  "term": "iPhone 15",
  ...
}

# Construir URL
query_params = {
    "operationName": operation_name,
    "variables": json.dumps(variables, separators=(",", ":"))
}

url_final = f"https://www.exito.com/api/graphql?{urlencode(query_params)}"
```

**URL resultante (codificada):**
```
https://www.exito.com/api/graphql?operationName=SearchQuery&variables=%7B%22first%22%3A16%2C%22after%22%3A%220%22%2C%22sort%22%3A%22price_asc%22%2C%22term%22%3A%22iPhone%2015%22%2C...
```

#### Paso 3: Headers

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
    "Origin": "https://www.exito.com",
    "Referer": "https://www.exito.com/",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}
```

**Por qué estos headers:**
- **User-Agent**: Simula un navegador Chrome en Windows
- **Accept**: Indica que espera JSON
- **Origin/Referer**: Indica que viene del sitio web de Éxito
- **Sec-Fetch-***: Headers de seguridad del navegador

#### Paso 4: Hacer la Petición

```python
resp = requests.get(url_final, headers=headers, timeout=10)
```

#### Paso 5: Respuesta JSON de Éxito

```json
{
  "data": {
    "search": {
      "products": {
        "edges": [
          {
            "node": {
              "linkText": "iphone-15-128gb-5g-esim-negro-103747083-mp",
              "items": [
                {
                  "name": "iPhone 15 128GB Negro 5G eSIM",
                  "sellers": [
                    {},
                    {
                      "commertialOffer": {
                        "Price": 3999000,
                        "PriceWithoutDiscount": 4299000
                      }
                    }
                  ]
                }
              ]
            }
          },
          {
            "node": {
              "linkText": "iphone-15-pro-256gb...",
              ...
            }
          }
        ]
      }
    }
  }
}
```

#### Paso 6: Extracción de Datos con JSON Paths

**Sistema de JSON Paths:**
```python
title_xpath = "data.search.products.edges[0].node.items[0].name"
```

**Cómo se procesa:**
```python
data["data"]["search"]["products"]["edges"][0]["node"]["items"][0]["name"]
# Resultado: "iPhone 15 128GB Negro 5G eSIM"
```

**Path del precio:**
```python
price_xpath = "data.search.products.edges[0].node.items[0].sellers[1].commertialOffer.PriceWithoutDiscount"

data["data"]["search"]["products"]["edges"][0]["node"]["items"][0]["sellers"][1]["commertialOffer"]["PriceWithoutDiscount"]
# Resultado: 4299000
```

**Path de la URL:**
```python
url_xpath = "data.search.products.edges[0].node.linkText"

data["data"]["search"]["products"]["edges"][0]["node"]["linkText"]
# Resultado: "iphone-15-128gb-5g-esim-negro-103747083-mp"
```

#### Paso 7: Construcción de URL del Producto

```python
link_text = "iphone-15-128gb-5g-esim-negro-103747083-mp"
base_url = "https://www.exito.com"
url_suffix = "/p"

# Construir URL
if link_text.startswith('/'):
    product_url = f"{base_url}{link_text}"
else:
    product_url = f"{base_url}/{link_text}"

# Agregar sufijo
if url_suffix:
    product_url = f"{product_url}{url_suffix}"

# Resultado:
# https://www.exito.com/iphone-15-128gb-5g-esim-negro-103747083-mp/p
```

#### Paso 8: Sistema de Múltiples Resultados

Éxito devuelve hasta 16 productos. El scraper evalúa los primeros 10:

```python
for index in range(10):  # Evaluar hasta 10 resultados
    # Reemplazar [0] con [index] en los paths
    title_path = "data.search.products.edges[0].node.items[0].name"
    title_path_indexed = "data.search.products.edges[1].node.items[0].name"  # index=1

    title = extract_from_json(data, title_path_indexed)

    if not title:
        break  # No hay más resultados

    # Calcular score de relevancia
    score, is_relevant = calculate_relevance_score("iPhone 15", title)

    # Guardar el mejor resultado
    if is_relevant and score > best_score:
        best_result = {
            "title": title,
            "price": price,
            "url": product_url,
            "score": score
        }
        best_score = score
```

**Ejemplo de evaluación:**
```
[Éxito] Resultado 0: 'iPhone 15 128GB Negro 5G eSIM' - Score: 95/100
[Éxito] Resultado 1: 'iPhone 15 Pro 256GB Titanio' - Score: 85/100
[Éxito] Resultado 2: 'iPhone 14 128GB Negro' - Score: 70/100
[Éxito] Resultado 3: 'Cable USB-C para iPhone 15' - Score: 55/100
[Éxito] ✅ Mejor resultado: 'iPhone 15 128GB Negro 5G eSIM' (score: 95/100)
```

---

## 🔶 Scraper HTML (Homecenter)

### 1. Configuración Completa

```json
{
  "sitio": "Homecenter",
  "country_code": "CO",
  "currency": "COP",
  "url": "https://www.homecenter.com.co/homecenter-co/search",
  "fetch_method": "html",
  "base_product_url": "https://www.homecenter.com.co",
  "params": {
    "Ntt": "{product_name}",
    "currentpage": "1",
    "sortBy": "derived.price.event.search.10,asc"
  },
  "title_xpath": "//*[@id='title-pdp-link']/h2",
  "price_xpath": "//*[@id='__next']/div[2]/div[1]/div[4]/div[3]/div[1]/div[1]/div[3]/div[1]/div/div[6]/div/div[4]/div/div",
  "url_xpath": "//*[@id='title-pdp-link']/@href"
}
```

### 2. Cómo Funciona

#### Paso 1: Construcción de Parámetros

```python
params = {
    "Ntt": "{product_name}",
    "currentpage": "1",
    "sortBy": "derived.price.event.search.10,asc"
}

# Reemplazar placeholder
params_replaced = {
    "Ntt": "iPhone 15",
    "currentpage": "1",
    "sortBy": "derived.price.event.search.10,asc"
}
```

#### Paso 2: Construcción de URL

```python
from urllib.parse import urlencode

url_base = "https://www.homecenter.com.co/homecenter-co/search"
url_final = f"{url_base}?{urlencode(params_replaced)}"

# Resultado:
# https://www.homecenter.com.co/homecenter-co/search?Ntt=iPhone+15&currentpage=1&sortBy=derived.price.event.search.10%2Casc
```

#### Paso 3: Headers

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
}
```

**Diferencias con GraphQL:**
- **Accept**: Espera HTML en lugar de JSON
- **Upgrade-Insecure-Requests**: Indica que es una navegación normal
- **Sec-Fetch-Dest**: "document" en lugar de "empty"

#### Paso 4: Hacer la Petición

```python
resp = requests.get(url_final, headers=headers, timeout=10)
```

#### Paso 5: Respuesta HTML de Homecenter

```html
<!DOCTYPE html>
<html>
<body>
  <div id="__next">
    <div>
      <div>
        <div id="title-pdp-link">
          <h2>iPhone 15 128GB Negro</h2>
          <a href="/iphone-15-128gb/p/12345">Ver producto</a>
        </div>
        <div>
          <!-- Varios divs anidados -->
          <div>
            <div>
              <div>$4.299.000</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
```

#### Paso 6: Parsear HTML con lxml

```python
from lxml import html

tree = html.fromstring(resp.content)
```

**Estructura del árbol:**
```
<tree>
  └─ <body>
      └─ <div id="__next">
          └─ ...
              └─ <div id="title-pdp-link">
                  ├─ <h2>iPhone 15 128GB Negro</h2>
                  └─ <a href="/iphone-15-128gb/p/12345">
```

#### Paso 7: Extracción con XPath

**XPath del título:**
```python
title_xpath = "//*[@id='title-pdp-link']/h2"

# Explicación del XPath:
# //*          → Buscar en cualquier lugar del documento
# [@id='...']  → Elemento con id='title-pdp-link'
# /h2          → Hijo <h2> de ese elemento

elements = tree.xpath(title_xpath)
# Resultado: [<Element h2>]

title_text = elements[0].text_content().strip()
# Resultado: "iPhone 15 128GB Negro"
```

**XPath del precio:**
```python
price_xpath = "//*[@id='__next']/div[2]/div[1]/div[4]/div[3]/div[1]/div[1]/div[3]/div[1]/div/div[6]/div/div[4]/div/div"

# Explicación:
# //*[@id='__next']  → div con id='__next'
# /div[2]            → segundo div hijo
# /div[1]            → primer div hijo
# /div[4]            → cuarto div hijo
# ... (navegación profunda en el árbol)

price_elements = tree.xpath(price_xpath)
price_text = price_elements[0].text_content().strip()
# Resultado: "$4.299.000"

# Formatear precio
price_formatted = format_price(price_text)
# Resultado: 4299000 (número)
```

**XPath de la URL (atributo):**
```python
url_xpath = "//*[@id='title-pdp-link']/@href"

# El /@href extrae el atributo href directamente
url_elements = tree.xpath(url_xpath)
# Resultado: ["/iphone-15-128gb/p/12345"]

product_url = url_elements[0]
# Resultado: "/iphone-15-128gb/p/12345"

# Construir URL completa
if not product_url.startswith('http'):
    base_url = "https://www.homecenter.com.co"
    product_url = base_url + product_url

# Resultado final:
# https://www.homecenter.com.co/iphone-15-128gb/p/12345
```

#### Paso 8: Guardar HTML para Debug

```python
filename = "Homecenter_resultado.html"
with open(filename, "wb") as f:
    f.write(resp.content)

print(f"HTML guardado en: {filename}")
```

---

## 📊 Sistema de Relevancia

Ambos scrapers usan un sistema de scoring para validar resultados.

### Cómo Funciona

```python
def calculate_relevance_score(search_term, result_title):
    """
    Calcula qué tan relevante es un resultado

    Args:
        search_term: "iPhone 15"
        result_title: "iPhone 15 128GB Negro 5G eSIM"

    Returns:
        (score, is_relevant)
        score: 0-100
        is_relevant: score >= 60
    """
```

### Criterios de Scoring

1. **Palabras clave presentes** (+10 puntos por palabra)
   ```python
   search_term = "iPhone 15"
   result_title = "iPhone 15 128GB Negro"

   "iphone" en "iphone 15 128gb negro" → +10
   "15" en "iphone 15 128gb negro" → +10
   Score parcial: 20
   ```

2. **Orden de palabras** (+20 puntos si están en orden)
   ```python
   "iPhone 15" aparece en ese orden → +20
   Score parcial: 40
   ```

3. **Match exacto** (+40 puntos adicionales)
   ```python
   "iPhone 15" == "iPhone 15 128GB Negro" → No
   "iPhone 15" in "iPhone 15 128GB Negro" → Sí (+20 más)
   Score final: 60+
   ```

### Umbrales

- **Score >= 60**: Resultado relevante ✅
- **Score < 60**: Resultado NO relevante ❌

### Ejemplos

```python
search_term = "iPhone 15"

# Caso 1: Match perfecto
result = "iPhone 15 128GB"
score = 95/100 → ✅ RELEVANTE

# Caso 2: Match bueno
result = "Apple iPhone 15 Negro"
score = 85/100 → ✅ RELEVANTE

# Caso 3: Match parcial
result = "iPhone 14 Pro Max"
score = 40/100 → ❌ NO RELEVANTE

# Caso 4: Match malo
result = "Cable USB-C para iPhone"
score = 25/100 → ❌ NO RELEVANTE
```

---

## 🔧 Extracción de Datos

### JSON Path Extractor (GraphQL)

```python
def extract_from_json(data, path):
    """
    Extrae valor de JSON usando notación de punto

    Path: "data.search.products.edges[0].node.items[0].name"
    """

    keys = path.split(".")
    current = data

    for key in keys:
        if "[" in key and "]" in key:
            # Procesar índices de array
            key_name = key.split("[")[0]  # "edges"
            index = int(key.split("[")[1].replace("]", ""))  # 0

            current = current[key_name][index]
        else:
            # Procesar claves normales
            current = current[key]

    return current
```

**Ejemplo paso a paso:**

```python
data = {
    "data": {
        "search": {
            "products": {
                "edges": [
                    {
                        "node": {
                            "items": [
                                {
                                    "name": "iPhone 15"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
}

path = "data.search.products.edges[0].node.items[0].name"

# Procesamiento:
current = data
current = data["data"]
current = data["data"]["search"]
current = data["data"]["search"]["products"]
current = data["data"]["search"]["products"]["edges"][0]
current = data["data"]["search"]["products"]["edges"][0]["node"]
current = data["data"]["search"]["products"]["edges"][0]["node"]["items"][0]
current = data["data"]["search"]["products"]["edges"][0]["node"]["items"][0]["name"]

# Resultado: "iPhone 15"
```

### XPath Extractor (HTML)

```python
# XPath simple (texto)
xpath = "//*[@id='title']/h2"
elements = tree.xpath(xpath)
text = elements[0].text_content().strip()

# XPath de atributo
xpath = "//*[@id='product-link']/@href"
url = tree.xpath(xpath)[0]  # Devuelve string directamente

# XPath con índices
xpath = "//div[@class='products']/div[1]/h2"
#                                     ↑
#                                 primer div
```

---

## 🧪 Ejemplos Prácticos

### Ejemplo 1: Buscar iPhone 15 en Éxito

**Input:**
```python
product_name = "iPhone 15"
```

**Request URL:**
```
https://www.exito.com/api/graphql?operationName=SearchQuery&variables=%7B%22first%22%3A16%2C%22after%22%3A%220%22%2C%22sort%22%3A%22price_asc%22%2C%22term%22%3A%22iPhone%2015%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D
```

**Response (simplificado):**
```json
{
  "data": {
    "search": {
      "products": {
        "edges": [
          {
            "node": {
              "linkText": "iphone-15-128gb-negro-103747083-mp",
              "items": [{
                "name": "iPhone 15 128GB Negro 5G eSIM",
                "sellers": [{}, {
                  "commertialOffer": {
                    "PriceWithoutDiscount": 4299000
                  }
                }]
              }]
            }
          }
        ]
      }
    }
  }
}
```

**Output:**
```python
{
    "sitio": "Éxito",
    "title": "iPhone 15 128GB Negro 5G eSIM",
    "price": 4299000,
    "url": "https://www.exito.com/iphone-15-128gb-negro-103747083-mp/p",
    "score": 95
}
```

### Ejemplo 2: Buscar Nevera Samsung en Homecenter

**Input:**
```python
product_name = "Nevera Samsung"
```

**Request URL:**
```
https://www.homecenter.com.co/homecenter-co/search?Ntt=Nevera+Samsung&currentpage=1&sortBy=derived.price.event.search.10%2Casc
```

**Response (HTML simplificado):**
```html
<div id="title-pdp-link">
  <h2>Nevera Samsung 350 Litros No Frost</h2>
  <a href="/nevera-samsung-350l/p/54321"></a>
</div>
<div>
  ...
  <div>$1.899.000</div>
</div>
```

**Output:**
```python
{
    "sitio": "Homecenter",
    "title": "Nevera Samsung 350 Litros No Frost",
    "price": 1899000,
    "url": "https://www.homecenter.com.co/nevera-samsung-350l/p/54321",
    "score": 88
}
```

---

## 📝 Notas Importantes

### Debug Mode

Ambos scrapers guardan las respuestas para debug:

**GraphQL:**
```python
# Guarda JSON
"Éxito_resultado.json"
```

**HTML:**
```python
# Guarda HTML
"Homecenter_resultado.html"
```

Puedes abrir estos archivos para ver la respuesta completa.

### Manejo de Errores

1. **Timeout** (10 segundos)
2. **HTTP errors** (404, 500, etc.)
3. **JSON parse errors**
4. **XPath no encuentra elementos**
5. **Score de relevancia bajo** (< 60)

### Limitaciones Conocidas

**Homecenter:**
- XPath muy específico y frágil
- Si cambia la estructura HTML, deja de funcionar
- Requiere actualización manual del XPath

**Éxito:**
- Más robusto (estructura JSON consistente)
- Puede cambiar la operación GraphQL
- Depende de que la API sea pública

---

## 🎯 Conclusiones

### Éxito (GraphQL)
**✅ Ventajas:**
- Estructura JSON consistente
- Datos estructurados
- Más robusto a cambios visuales
- Múltiples resultados evaluados

**❌ Desventajas:**
- Requiere entender GraphQL
- Más complejo de configurar
- API puede cambiar

### Homecenter (HTML)
**✅ Ventajas:**
- Simple de entender
- No requiere API
- Funciona con cualquier sitio HTML

**❌ Desventajas:**
- XPath frágil
- Se rompe con cambios de HTML
- Más difícil encontrar selectores correctos
- Solo evalúa primer resultado

---

**Creado**: Diciembre 2025
**Autor**: Análisis técnico de scrapers ePriceFlo
**Archivos analizados**:
- `scrapers/graphql_scraper.py`
- `scrapers/generic_scrapers.py`
- `config_sitios.json`
