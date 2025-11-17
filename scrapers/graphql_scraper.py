import requests
import json
from scrapers.text_utils import calculate_relevance_score, format_price

def scrape_graphql(sitio_config, product_name, product_category=None):
    """
    Scraper para APIs GraphQL.

    Args:
        sitio_config: Configuración del sitio
        product_name: Nombre del producto a buscar
        product_category: Categoría opcional para filtrar (ej: "celulares", "electrodomesticos")
    """
    # Construir payload reemplazando {product_name} y {product_category}
    payload = sitio_config.get("params", {})
    payload_str = json.dumps(payload)
    payload_str = payload_str.replace("{product_name}", product_name)

    # Si hay categoría, reemplazar; si no, eliminar el facet de categoría
    if product_category:
        payload_str = payload_str.replace("{product_category}", product_category)
    else:
        # Parsear JSON para eliminar el facet de categoría
        temp_payload = json.loads(payload_str)
        if "variables" in temp_payload and "selectedFacets" in temp_payload["variables"]:
            # Filtrar facets que contengan {product_category}
            facets = temp_payload["variables"]["selectedFacets"]
            temp_payload["variables"]["selectedFacets"] = [
                f for f in facets if "{product_category}" not in json.dumps(f)
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
            best_result = {
                "sitio": sitio_config["sitio"],
                "busqueda": product_name,
                "url": url,
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