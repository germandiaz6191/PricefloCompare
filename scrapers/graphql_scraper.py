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

    # Sin mapeo en BD: no filtrar por categoria (evita 0 resultados con valores invalidos)
    _category_mapping_cache[cache_key] = None
    return None

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

    def _build_payload(include_brand):
        """Construye el payload GraphQL. include_brand=False omite el facet brand."""
        payload_local = sitio_config.get("params", {})
        payload_str_local = json.dumps(payload_local)
        payload_str_local = payload_str_local.replace("{product_name}", product_name)
        temp = json.loads(payload_str_local)

        if "variables" in temp and "selectedFacets" in temp["variables"]:
            facets_local = temp["variables"]["selectedFacets"]

            if category_mapped and category_mapped.get("level"):
                category_facet_found = False
                for facet in facets_local:
                    if "category" in facet.get("key", ""):
                        facet["key"] = category_mapped["level"]
                        facet["value"] = category_mapped["value"]
                        category_facet_found = True
                        break
                if not category_facet_found:
                    facets_local.insert(0, {
                        "key": category_mapped["level"],
                        "value": category_mapped["value"]
                    })
            else:
                temp["variables"]["selectedFacets"] = [
                    f for f in facets_local if "category" not in f.get("key", "")
                ]
                facets_local = temp["variables"]["selectedFacets"]

            if brand and include_brand:
                brand_facet_exists = any(f.get("key") == "brand" for f in facets_local)
                if not brand_facet_exists:
                    has_category = category_mapped and category_mapped.get("level")
                    insert_pos = 1 if has_category else 0
                    facets_local.insert(insert_pos, {
                        "key": "brand",
                        "value": brand
                    })
                    print(f"[Filtro de marca agregado]: brand = {brand}")
        return temp

    payload_json = _build_payload(use_brand_filter)

    base_url = sitio_config["url"]

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

    def _request_and_iterate(payload):
        """Hace el request GraphQL y itera resultados. Devuelve best_result o None."""
        url_local = base_url
        try:
            if sitio_config.get("requires_url_variables", False):
                from urllib.parse import urlencode
                operation_name = payload.get("operationName")
                variables = payload.get("variables", {})
                query_params = {
                    "operationName": operation_name,
                    "variables": json.dumps(variables, separators=(",", ":"))
                }
                url_local = f"{url_local}?{urlencode(query_params)}"
                resp = requests.get(url_local, headers=headers, timeout=10)
            else:
                resp = requests.post(url_local, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Conexion con {sitio_config['sitio']}: {e}")
            print("URL:", url_local)
            print("Payload JSON:", json.dumps(payload, indent=2, ensure_ascii=False))
            return None

        debug_filename = f"{sitio_config['sitio']}_resultado.json"
        try:
            with open(debug_filename, "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"[DEBUG] Respuesta guardada en: {debug_filename}")
        except Exception:
            pass

        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando respuesta JSON de {sitio_config['sitio']}: {e}")
            print(f"[DEBUG] Content-Type: {resp.headers.get('Content-Type', 'desconocido')}")
            print(f"[DEBUG] Status: {resp.status_code}")
            print(resp.text[:500])
            return None

        import re
        title_path = sitio_config.get("title_xpath")
        price_path = sitio_config.get("price_xpath")
        if not title_path:
            return None

        best = None
        best_s = 0
        for index in range(10):
            title_path_indexed = re.sub(r'\[0\]', f'[{index}]', title_path, count=1)
            price_path_indexed = re.sub(r'\[0\]', f'[{index}]', price_path, count=1) if price_path else None

            title = extract_from_json(data, title_path_indexed)
            if not title:
                break

            score, is_relevant = calculate_relevance_score(product_name, title)
            print(f"[{sitio_config['sitio']}] Resultado {index}: '{title}' - Score: {score}/100")

            if is_relevant and score > best_s:
                price = extract_from_json(data, price_path_indexed) if price_path_indexed else None

                if price is None and price_path_indexed and 'sellers[1]' in price_path_indexed:
                    fallback_path = price_path_indexed.replace('sellers[1]', 'sellers[0]')
                    price = extract_from_json(data, fallback_path)
                    if price is not None:
                        print(f"[{sitio_config['sitio']}] [INFO] Precio obtenido de sellers[0] (fallback): {price}")

                product_url = None
                url_path = sitio_config.get("url_xpath")
                if url_path:
                    url_path_indexed = re.sub(r'\[0\]', f'[{index}]', url_path, count=1)
                    link_text = extract_from_json(data, url_path_indexed)

                    if link_text:
                        product_base = sitio_config.get("base_product_url", "")
                        url_suffix = sitio_config.get("url_suffix", "")
                        if link_text.startswith('http'):
                            product_url = link_text
                        else:
                            if link_text.startswith('/'):
                                product_url = f"{product_base}{link_text}"
                            else:
                                product_url = f"{product_base}/{link_text}"
                            if url_suffix:
                                product_url = f"{product_url}{url_suffix}"
                        print(f"[{sitio_config['sitio']}] URL del producto: {product_url}")
                    else:
                        product_id_path = f"data.search.products.edges[{index}].node.productId"
                        product_id = extract_from_json(data, product_id_path)
                        if not product_id:
                            item_id_path = f"data.search.products.edges[{index}].node.items[0].itemId"
                            product_id = extract_from_json(data, item_id_path)

                        if product_id and sitio_config['sitio'] == "Éxito":
                            import unicodedata
                            slug = title.lower()
                            slug = ''.join(c for c in unicodedata.normalize('NFD', slug)
                                         if unicodedata.category(c) != 'Mn')
                            slug = re.sub(r'[^a-z0-9]+', '-', slug)
                            slug = slug.strip('-')
                            product_base = sitio_config.get("base_product_url", "https://www.exito.com")
                            product_url = f"{product_base}/{slug}-{product_id}-mp/p"
                            print(f"[{sitio_config['sitio']}] [WARN] linkText no encontrado - URL construida: {product_url}")
                        else:
                            print(f"[{sitio_config['sitio']}] [WARN] No se pudo construir URL del producto")

                if product_url and ('graphql' in product_url.lower() or '/api/' in product_url.lower()):
                    print(f"[{sitio_config['sitio']}] [BLOCK] URL del API detectada, descartando: {product_url[:80]}...")
                    product_url = None

                best = {
                    "sitio": sitio_config["sitio"],
                    "busqueda": product_name,
                    "url": product_url,
                    "title_path": title_path_indexed,
                    "price_path": price_path_indexed,
                    "title": title,
                    "price": format_price(str(price)) if price else None,
                    "score": score
                }
                best_s = score

        return best

    best_result = _request_and_iterate(payload_json)

    # Fallback: si no hubo resultados con filtro de marca, reintentar sin marca
    if best_result is None and brand and use_brand_filter:
        print(f"[{sitio_config['sitio']}] [RETRY] Sin resultados con brand={brand}, reintentando sin filtro de marca")
        best_result = _request_and_iterate(_build_payload(False))

    if best_result:
        url_debug = best_result.get('url') or '(sin URL)'
        print(f"[{sitio_config['sitio']}] [OK] Mejor resultado: '{best_result['title']}' (score: {best_result['score']}/100)")
        print(f"[{sitio_config['sitio']}] [URL] URL que se guardara en BD: {url_debug}")
        return best_result
    else:
        print(f"[{sitio_config['sitio']}] [ERROR] No se encontro ningun resultado relevante (score >= 60)")
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