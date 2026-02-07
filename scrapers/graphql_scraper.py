import requests
import json
import os
from scrapers.text_utils import calculate_relevance_score, format_price

# Importar función de BD para category mapping
try:
    from database import get_category_mapping
    USE_DB_MAPPING = True
except ImportError:
    USE_DB_MAPPING = False

# Cache de mapeo de categorías (para evitar queries repetidas)
_category_mapping_cache = {}

# Marcas conocidas (en minúsculas para búsqueda case-insensitive)
KNOWN_BRANDS = {
    'samsung', 'lg', 'sony', 'motorola', 'xiaomi', 'huawei', 'oppo', 'realme',
    'hp', 'dell', 'lenovo', 'asus', 'acer',
    'kalley', 'oster', 'haceb', 'whirlpool', 'electrolux', 'mabe', 'bose', 'jbl',
    'kitchenaid', 'ninja', 'philips', 'panasonic', 'canon', 'nikon', 'gopro', 'dji',
    'ring', 'amazfit', 'garmin', 'fitbit', 'microsoft', 'logitech', 'razer'
}

# Mapeo de productos a marcas (cuando el nombre del producto no contiene la marca directamente)
PRODUCT_TO_BRAND = {
    'iphone': 'apple',
    'ipad': 'apple',
    'airpods': 'apple',
    'macbook': 'apple',
    'imac': 'apple',
    'mac': 'apple',
    'watch': 'apple',  # Apple Watch
    'xbox': 'microsoft',
    'playstation': 'sony',
    'ps5': 'sony',
    'ps4': 'sony',
    'nintendo': 'nintendo',
    'switch': 'nintendo'
}

def extract_brand(product_name):
    """
    Extrae la marca del nombre del producto.
    Busca palabras conocidas o la primera palabra del nombre.
    Retorna la marca en minúsculas o None.
    """
    if not product_name:
        return None

    # Normalizar nombre (minúsculas)
    name_lower = product_name.lower()
    words = name_lower.split()

    # 1. Buscar productos que mapean a marcas específicas
    for word in words:
        clean_word = ''.join(c for c in word if c.isalnum())
        if clean_word in PRODUCT_TO_BRAND:
            return PRODUCT_TO_BRAND[clean_word]

    # 2. Buscar marca conocida en el nombre
    for word in words:
        clean_word = ''.join(c for c in word if c.isalnum())
        if clean_word in KNOWN_BRANDS:
            return clean_word

    # 3. Si no se encuentra marca conocida, usar primera palabra como marca
    if words:
        first_word = ''.join(c for c in words[0] if c.isalnum())
        if len(first_word) >= 2:  # Evitar palabras muy cortas
            return first_word

    return None

def map_category(category, store_name="Éxito"):
    """
    Mapea una categoría de ePriceFlo a categoría de tienda.
    Lee desde la BD (tabla category_mappings).
    Retorna dict con 'level' y 'value', o None si no hay categoría.
    """
    if not category:
        return None

    # Usar cache
    cache_key = f"{store_name}:{category}"
    if cache_key in _category_mapping_cache:
        return _category_mapping_cache[cache_key]

    # Intentar obtener de BD
    if USE_DB_MAPPING:
        try:
            mapping = get_category_mapping(store_name, category)
            if mapping:
                _category_mapping_cache[cache_key] = mapping
                return mapping
        except Exception:
            # Tabla no existe o error de BD - usar fallback silenciosamente
            pass

    # Fallback: usar category-2 con categoría en minúsculas (patrón descubierto)
    fallback = {
        "level": "category-2",
        "value": category.lower()
    }
    _category_mapping_cache[cache_key] = fallback
    return fallback

def scrape_graphql(sitio_config, product_name, product_category=None):
    """
    Scraper para APIs GraphQL.

    Args:
        sitio_config: Configuración del sitio
        product_name: Nombre del producto a buscar
        product_category: Categoría opcional para filtrar (ej: "celulares", "electrodomesticos")
    """
    # Extraer marca del nombre del producto
    brand = extract_brand(product_name)
    if brand:
        print(f"[Marca detectada]: {brand}")

    # Mapear categoría si existe
    category_mapped = None
    use_brand_filter = True  # Por defecto sí usar marca
    if product_category:
        store_name = sitio_config.get("sitio", "Éxito")
        category_mapped = map_category(product_category, store_name)
        if category_mapped:
            # Verificar si este mapeo usa filtro de marca
            use_brand_filter = category_mapped.get('use_brand', True)

            if category_mapped['level']:  # Si tiene categoría
                print(f"[Categoría mapeada]: {product_category} → {category_mapped['value']} (nivel: {category_mapped['level']})")
            else:  # Si no tiene categoría (solo marca)
                print(f"[Categoría mapeada]: {product_category} → solo marca (sin categoría)")

    # Construir payload reemplazando {product_name} y {product_category}
    payload = sitio_config.get("params", {})
    payload_str = json.dumps(payload)
    payload_str = payload_str.replace("{product_name}", product_name)

    # Parsear payload para modificar facets
    temp_payload = json.loads(payload_str)

    if "variables" in temp_payload and "selectedFacets" in temp_payload["variables"]:
        facets = temp_payload["variables"]["selectedFacets"]

        # 1. Actualizar o agregar facet de categoría
        if category_mapped and category_mapped.get("level"):  # Solo si tiene nivel de categoría
            category_facet_found = False
            for facet in facets:
                if "category" in facet.get("key", ""):
                    # Actualizar facet existente
                    facet["key"] = category_mapped["level"]
                    facet["value"] = category_mapped["value"]
                    category_facet_found = True
                    break

            # Si no existía, agregarlo al inicio (después del term)
            if not category_facet_found:
                facets.insert(0, {
                    "key": category_mapped["level"],
                    "value": category_mapped["value"]
                })
        else:
            # Sin categoría: eliminar facet de categoría
            temp_payload["variables"]["selectedFacets"] = [
                f for f in facets if "category" not in f.get("key", "")
            ]
            facets = temp_payload["variables"]["selectedFacets"]

        # 2. Agregar facet de marca si se detectó Y se debe usar
        if brand and use_brand_filter:
            # Verificar si ya existe facet de marca
            brand_facet_exists = any(f.get("key") == "brand" for f in facets)
            if not brand_facet_exists:
                # Insertar después de categoría (posición 1) o al inicio
                has_category = category_mapped and category_mapped.get("level")
                insert_pos = 1 if has_category else 0
                facets.insert(insert_pos, {
                    "key": "brand",
                    "value": brand
                })
                print(f"[Filtro de marca agregado]: brand = {brand}")

    payload_json = temp_payload

    url = sitio_config["url"]

    # Headers más completos para evitar detección de bot
    # Nota: Accept-Encoding se omite para que requests lo maneje automáticamente
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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

    try:
        if sitio_config.get("requires_url_variables", False):
            # === Caso GET con variables en la URL (ej: Éxito) ===
            from urllib.parse import urlencode

            operation_name = payload_json.get("operationName")
            variables = payload_json.get("variables", {})

            query_params = {
                "operationName": operation_name,
                "variables": json.dumps(variables, separators=(",", ":"))
            }
            url = f"{url}?{urlencode(query_params)}"

            resp = requests.get(url, headers=headers, timeout=10)

        else:
            # === Caso estándar: POST con body JSON ===
            resp = requests.post(url, json=payload_json, headers=headers, timeout=10)
        
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error de conexión con {sitio_config['sitio']}: {e}")
        print("=== Detalles de la petición fallida ===")
        print("URL:", url)
        print("Headers:", headers)
        print("Payload JSON:", json.dumps(payload_json, indent=2, ensure_ascii=False))
        print("=======================================")
        return None

    # Guardar respuesta para debug
    debug_filename = f"{sitio_config['sitio']}_resultado.json"
    try:
        with open(debug_filename, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"[DEBUG] Respuesta guardada en: {debug_filename}")
    except Exception:
        pass  # Ignorar errores al guardar debug

    # Intentar parsear JSON
    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando respuesta JSON de {sitio_config['sitio']}: {e}")
        print(f"[DEBUG] Content-Type recibido: {resp.headers.get('Content-Type', 'desconocido')}")
        print(f"[DEBUG] Status code: {resp.status_code}")
        print(f"[DEBUG] Respuesta recibida (primeros 500 chars):")
        print(resp.text[:500])
        print("=== Posible causa: ===")
        print("- El sitio puede estar devolviendo HTML en lugar de JSON")
        print("- Puede ser una página de error o desafío de Cloudflare")
        print("- Verifica si el sitio ha cambiado su API")
        return None

    # Buscar en múltiples resultados (hasta 10) para encontrar el más relevante
    best_result = None
    best_score = 0

    # Intentar extraer múltiples productos de la respuesta
    max_results = 10
    for index in range(max_results):
        # Reemplazar [0] con [index] en los paths
        title_path = sitio_config.get("title_xpath")
        price_path = sitio_config.get("price_xpath")

        if not title_path:
            break

        # Reemplazar el índice en el path (ej: edges[0] -> edges[1])
        import re
        title_path_indexed = re.sub(r'\[0\]', f'[{index}]', title_path, count=1)
        price_path_indexed = re.sub(r'\[0\]', f'[{index}]', price_path, count=1) if price_path else None

        title = extract_from_json(data, title_path_indexed)

        if not title:
            # No hay más resultados
            break

        # Calcular score de relevancia
        score, is_relevant = calculate_relevance_score(product_name, title)

        print(f"[{sitio_config['sitio']}] Resultado {index}: '{title}' - Score: {score}/100")

        # Guardar el mejor resultado encontrado
        if is_relevant and score > best_score:
            price = extract_from_json(data, price_path_indexed) if price_path_indexed else None

            # Extraer URL del producto si está configurada
            product_url = None
            url_path = sitio_config.get("url_xpath")

            if url_path:
                url_path_indexed = re.sub(r'\[0\]', f'[{index}]', url_path, count=1)
                link_text = extract_from_json(data, url_path_indexed)

                if link_text:
                    # Caso 1: linkText existe - usar método normal
                    base_url = sitio_config.get("base_product_url", "")
                    url_suffix = sitio_config.get("url_suffix", "")

                    if link_text.startswith('http'):
                        product_url = link_text
                    else:
                        if link_text.startswith('/'):
                            product_url = f"{base_url}{link_text}"
                        else:
                            product_url = f"{base_url}/{link_text}"

                        if url_suffix:
                            product_url = f"{product_url}{url_suffix}"

                    print(f"[{sitio_config['sitio']}] URL del producto: {product_url}")
                else:
                    # Caso 2: linkText NO existe - construir URL alternativa
                    # Intentar obtener productId
                    product_id_path = f"data.search.products.edges[{index}].node.productId"
                    product_id = extract_from_json(data, product_id_path)

                    if not product_id:
                        # Intentar itemId como alternativa
                        item_id_path = f"data.search.products.edges[{index}].node.items[0].itemId"
                        product_id = extract_from_json(data, item_id_path)

                    if product_id and sitio_config['sitio'] == "Éxito":
                        # Construir URL con patrón de Éxito: {slug}-{productId}-mp/p
                        # Crear slug del título
                        import unicodedata
                        slug = title.lower()
                        # Remover acentos
                        slug = ''.join(c for c in unicodedata.normalize('NFD', slug)
                                     if unicodedata.category(c) != 'Mn')
                        # Reemplazar espacios y caracteres especiales
                        slug = re.sub(r'[^a-z0-9]+', '-', slug)
                        # Remover guiones al inicio/final
                        slug = slug.strip('-')

                        base_url = sitio_config.get("base_product_url", "https://www.exito.com")
                        product_url = f"{base_url}/{slug}-{product_id}-mp/p"
                        print(f"[{sitio_config['sitio']}] ⚠️ linkText no encontrado - URL construida: {product_url}")
                    else:
                        # Si no podemos construir URL, dejar como None
                        print(f"[{sitio_config['sitio']}] ⚠️ No se pudo construir URL del producto")

            best_result = {
                "sitio": sitio_config["sitio"],
                "busqueda": product_name,
                "url": product_url,
                "title_path": title_path_indexed,
                "price_path": price_path_indexed,
                "title": title,
                "price": format_price(str(price)) if price else None,
                "score": score
            }
            best_score = score

    if best_result:
        print(f"[{sitio_config['sitio']}] ✅ Mejor resultado: '{best_result['title']}' (score: {best_score}/100)")
        return best_result
    else:
        print(f"[{sitio_config['sitio']}] ❌ No se encontró ningún resultado relevante (score >= 60)")
        return None

def extract_from_json(data, path):
    """
    Extrae un valor de un diccionario JSON usando una ruta tipo 'a.b[0].c'
    e imprime en qué parte falla si no encuentra algo.
    """
    try:
        keys = path.split(".")
        current = data
        for key in keys:
            # Si el key es un índice de lista (ej: items[0])
            if "[" in key and "]" in key:
                key_name = key.split("[")[0]
                index = int(key.split("[")[1].replace("]", ""))
                
                if key_name not in current:
                    print(f"[DEBUG] No se encontró clave '{key_name}' en la ruta: {path}")
                    return None
                if not isinstance(current[key_name], list):
                    print(f"[DEBUG] '{key_name}' no es una lista en la ruta: {path}")
                    return None
                if index >= len(current[key_name]):
                    print(f"[DEBUG] Índice {index} fuera de rango para '{key_name}' en la ruta: {path}")
                    return None
                
                current = current[key_name][index]
            
            # Si es clave normal
            else:
                if key not in current:
                    print(f"[DEBUG] No se encontró clave '{key}' en la ruta: {path}")
                    return None
                current = current[key]
        
        return current

    except Exception as e:
        print(f"[DEBUG] Error al extraer ruta '{path}': {e}")
        return None