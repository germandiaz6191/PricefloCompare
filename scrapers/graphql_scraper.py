import requests
import json
import os
from scrapers.text_utils import calculate_relevance_score, format_price

# Cargar mapeo de categorías
_category_mapping = None

def load_category_mapping():
    """Carga el mapeo de categorías desde category_mapping.json"""
    global _category_mapping
    if _category_mapping is None:
        mapping_file = os.path.join(os.path.dirname(__file__), "..", "category_mapping.json")
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _category_mapping = data.get("mappings", {})
        except FileNotFoundError:
            _category_mapping = {}  # Sin mapeo, usar categoría original
    return _category_mapping

def map_category(category):
    """
    Mapea una categoría de ePriceFlo a categoría de Éxito.
    Retorna dict con 'level' y 'value', o None si no hay categoría.
    """
    if not category:
        return None

    mapping = load_category_mapping()
    cat_data = mapping.get(category)

    if cat_data and isinstance(cat_data, dict):
        # Nuevo formato con level y value
        return {
            "level": cat_data.get("level", "category-3"),
            "value": cat_data.get("value", category.lower())
        }
    else:
        # Fallback: formato antiguo o sin mapeo
        return {
            "level": "category-3",
            "value": category.lower()
        }

def scrape_graphql(sitio_config, product_name, product_category=None):
    """
    Scraper para APIs GraphQL.

    Args:
        sitio_config: Configuración del sitio
        product_name: Nombre del producto a buscar
        product_category: Categoría opcional para filtrar (ej: "celulares", "electrodomesticos")
    """
    # Mapear categoría si existe
    category_mapped = None
    if product_category:
        category_mapped = map_category(product_category)
        if category_mapped:
            print(f"[Categoría mapeada]: {product_category} → {category_mapped['value']} (nivel: {category_mapped['level']})")

    # Construir payload reemplazando {product_name} y {product_category}
    payload = sitio_config.get("params", {})
    payload_str = json.dumps(payload)
    payload_str = payload_str.replace("{product_name}", product_name)

    # Si hay categoría mapeada, ajustar facet de categoría
    if category_mapped:
        # Parsear JSON para modificar el facet de categoría
        temp_payload = json.loads(payload_str)
        if "variables" in temp_payload and "selectedFacets" in temp_payload["variables"]:
            facets = temp_payload["variables"]["selectedFacets"]
            # Buscar y actualizar el facet de categoría
            for facet in facets:
                if "category" in facet.get("key", ""):
                    # Actualizar el key con el level correcto
                    facet["key"] = category_mapped["level"]
                    # Reemplazar el valor
                    if "{product_category}" in facet.get("value", ""):
                        facet["value"] = category_mapped["value"]
        payload_str = json.dumps(temp_payload)
    else:
        # Sin categoría: eliminar el facet de categoría
        temp_payload = json.loads(payload_str)
        if "variables" in temp_payload and "selectedFacets" in temp_payload["variables"]:
            facets = temp_payload["variables"]["selectedFacets"]
            temp_payload["variables"]["selectedFacets"] = [
                f for f in facets if "category" not in f.get("key", "")
            ]
        payload_str = json.dumps(temp_payload)

    payload_json = json.loads(payload_str)

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
            product_url = url  # Por defecto, URL de búsqueda
            url_path = sitio_config.get("url_xpath")
            if url_path:
                url_path_indexed = re.sub(r'\[0\]', f'[{index}]', url_path, count=1)
                link_text = extract_from_json(data, url_path_indexed)
                if link_text:
                    # Construir URL completa
                    base_url = sitio_config.get("base_product_url", "")
                    url_suffix = sitio_config.get("url_suffix", "")  # Sufijo opcional (ej: "/p" para Éxito)

                    if link_text.startswith('http'):
                        product_url = link_text
                    else:
                        # Construir URL base
                        if link_text.startswith('/'):
                            product_url = f"{base_url}{link_text}"
                        else:
                            product_url = f"{base_url}/{link_text}"

                        # Agregar sufijo si existe
                        if url_suffix:
                            product_url = f"{product_url}{url_suffix}"

                    print(f"[{sitio_config['sitio']}] URL del producto: {product_url}")

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