import os
import re
import requests
from datetime import datetime, timedelta
from lxml import html
import json
from urllib.parse import urlencode
from scrapers.graphql_scraper import scrape_graphql  # nuevo módulo
from scrapers.text_utils import calculate_relevance_score, normalize_text, format_price

def load_sites_config(path=None):
    """
    Carga la configuración de sitios desde la BD (tabla 'stores').
    El parámetro 'path' se mantiene por compatibilidad pero se ignora.
    """
    from database import get_stores

    stores = get_stores(active_only=True)
    sites = []
    for store in stores:
        config = store.get("config") or {}
        if isinstance(config, str):
            config = json.loads(config)

        site = dict(config)
        site["sitio"] = store["name"]
        site["url"] = store["url"]
        site["fetch_method"] = store["fetch_method"]
        if store.get("country_code"):
            site["country_code"] = store["country_code"]
        if store.get("currency"):
            site["currency"] = store["currency"]
        sites.append(site)

    return sites

def scrape_price(sitio_config, product_name, product_category=None):
    """
    Scraper principal que enruta a HTML o GraphQL según configuración.

    Args:
        sitio_config: Configuración del sitio
        product_name: Nombre del producto a buscar
        product_category: Categoría opcional para filtrar búsqueda
    """
    method = sitio_config.get("fetch_method", "html")

    if method == "html":
        return scrape_html(sitio_config, product_name)
    elif method == "graphql":
        return scrape_graphql(sitio_config, product_name, product_category)
    elif method == "nextjs":
        return scrape_nextjs(sitio_config, product_name)
    elif method == "vtex_rest":
        return scrape_vtex_rest(sitio_config, product_name)
    elif method == "mercadolibre":
        return scrape_mercadolibre(sitio_config, product_name)
    else:
        print(f"Método de fetch desconocido para {sitio_config['sitio']}")
        return None

def scrape_html(sitio_config, product_name):
    # Construir parámetros dinámicamente desde config_sitios.json
    params = {k: (v.replace("{product_name}", product_name) if isinstance(v, str) else v)
              for k, v in sitio_config.get("params", {}).items()}
    params_str = {str(k): str(v) for k, v in params.items()}
    print("Params para URL:", params_str)

    url = f'{sitio_config["url"]}?{urlencode(params_str)}'
    print(f"Consultando: {url}")

    # Headers más completos para evitar detección de bot
    # Nota: Accept-Encoding se omite para que requests lo maneje automáticamente
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error de conexión con {sitio_config['sitio']}: {e}")
        return None

    tree = html.fromstring(resp.content)

    # Guardar HTML para debug
    filename = f"{sitio_config['sitio']}_resultado.html"
    with open(filename, "wb") as f:
        f.write(resp.content)
    print(f"HTML guardado en: {filename}")

    # Extraer títulos (todos los resultados) y elegir el de mejor score
    title_xpath = sitio_config.get("title_xpath")
    price_xpath = sitio_config.get("price_xpath")
    url_xpath = sitio_config.get("url_xpath")

    if not title_xpath:
        return None

    title_elements = tree.xpath(title_xpath)
    if not title_elements:
        print(f"[{sitio_config['sitio']}] No se encontró ningún título con el xpath '{title_xpath}'")
        return None

    url_elements = tree.xpath(url_xpath) if url_xpath else []
    price_elements = tree.xpath(price_xpath) if price_xpath else []

    max_results = min(15, len(title_elements))
    best_idx = -1
    best_score = -1
    best_title = None
    for i in range(max_results):
        txt = title_elements[i].text_content().strip()
        score, is_relevant = calculate_relevance_score(product_name, txt)
        print(f"[{sitio_config['sitio']}] Resultado {i}: '{txt[:70]}' - Score: {score}/100")
        if is_relevant and score > best_score:
            best_score = score
            best_idx = i
            best_title = txt

    if best_idx < 0:
        print(f"[{sitio_config['sitio']}] [ERROR] Ningun resultado relevante (score >= 60) en top {max_results}")
        return None

    title_text = best_title
    print(f"[{sitio_config['sitio']}] [OK] Mejor resultado [idx={best_idx}]: '{title_text}' (score: {best_score}/100)")

    # Extraer URL en el mismo índice
    product_url = None
    if best_idx < len(url_elements):
        raw_url = url_elements[best_idx]
        product_url = raw_url if isinstance(raw_url, str) else raw_url.text_content().strip()
        if product_url and not product_url.startswith('http'):
            base_url = sitio_config.get("base_product_url", "")
            product_url = base_url + product_url
        print(f"[{sitio_config['sitio']}] URL del producto: {product_url}")

    # Extraer precio: preferir el del mismo índice; fallback al único si el xpath devuelve 1 sólo
    price_text = None
    if best_idx < len(price_elements):
        price_text = format_price(price_elements[best_idx].text_content().strip())
    elif len(price_elements) == 1:
        price_text = format_price(price_elements[0].text_content().strip())
    elif price_xpath:
        print(f"[{sitio_config['sitio']}] ⚠️ price_xpath devolvió {len(price_elements)} elementos; precio no extraído")

    return {
        "sitio": sitio_config["sitio"],
        "busqueda": product_name,
        "url": product_url or url,
        "title_xpath": title_xpath,
        "price_xpath": price_xpath,
        "title": title_text,
        "price": price_text,
        "score": best_score
    }


def scrape_nextjs(sitio_config, product_name):
    """
    Scraper para sitios Next.js que embeben resultados de búsqueda en un <script>
    con JSON en props.pageProps (o ruta configurable).
    """
    params = {k: (v.replace("{product_name}", product_name) if isinstance(v, str) else v)
              for k, v in sitio_config.get("params", {}).items()}
    params_str = {str(k): str(v) for k, v in params.items()}
    url = f'{sitio_config["url"]}?{urlencode(params_str)}'
    print(f"Consultando: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-CO,es;q=0.9",
        "Connection": "keep-alive",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error de conexión con {sitio_config['sitio']}: {e}")
        return None

    try:
        tree = html.fromstring(resp.content.decode("utf-8", errors="replace"))
    except Exception:
        tree = html.fromstring(resp.content)

    # Buscar __NEXT_DATA__ por id (robusto), fallback a script_index
    next_data = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if next_data:
        script_text = next_data[0]
    else:
        script_index = sitio_config.get("script_index", 0)
        scripts = tree.xpath("//script/text()")
        if script_index >= len(scripts):
            print(f"[{sitio_config['sitio']}] Script index {script_index} no encontrado ({len(scripts)} scripts)")
            return None
        script_text = scripts[script_index]

    try:
        data = json.loads(script_text)
    except json.JSONDecodeError as e:
        print(f"[{sitio_config['sitio']}] Error parseando JSON del script: {e}")
        return None

    # Navegar hasta el array de resultados por la ruta configurada
    data_path = sitio_config.get("data_path", "props.pageProps.results")
    obj = data
    for key in data_path.split("."):
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            obj = None
        if obj is None:
            print(f"[{sitio_config['sitio']}] Path '{data_path}' no encontrado en JSON")
            return None

    results = obj if isinstance(obj, list) else []
    if not results:
        print(f"[{sitio_config['sitio']}] Sin productos en '{data_path}'")
        return None

    title_field = sitio_config.get("title_field", "displayName")
    url_field   = sitio_config.get("url_field", "url")
    price_type  = sitio_config.get("price_type", "internetPrice")

    # Elegir el resultado con mejor score de relevancia
    best_idx, best_score, best_title = -1, -1, None
    for i, item in enumerate(results[:15]):
        title = item.get(title_field, "")
        if not title:
            continue
        score, is_relevant = calculate_relevance_score(product_name, title)
        print(f"[{sitio_config['sitio']}] Resultado {i}: '{title[:70]}' - Score: {score}/100")
        if is_relevant and score > best_score:
            best_score, best_idx, best_title = score, i, title

    if best_idx < 0:
        print(f"[{sitio_config['sitio']}] Sin resultados relevantes (score >= 60)")
        return None

    item = results[best_idx]
    product_url = item.get(url_field)

    # Extraer precio por tipo preferido, con fallback al primero disponible
    price = None
    for p in item.get("prices", []):
        if p.get("type") == price_type:
            raw = p.get("price", [])
            if raw:
                price = format_price(str(raw[0]))
            break
    if not price:
        for p in item.get("prices", []):
            raw = p.get("price", [])
            if raw:
                price = format_price(str(raw[0]))
                break

    print(f"[{sitio_config['sitio']}] [OK] '{best_title}' - Precio: {price}")

    return {
        "sitio": sitio_config["sitio"],
        "busqueda": product_name,
        "title": best_title,
        "price": price,
        "url": product_url,
        "score": best_score,
    }


def scrape_vtex_rest(sitio_config, product_name):
    """
    Scraper para tiendas VTEX usando la API REST de catálogo.
    El término de búsqueda va en el path de la URL, no como query param.
    """
    search_term = product_name.replace(" ", "%20")
    url = f'{sitio_config["url"]}{search_term}'
    from_idx = sitio_config.get("from", 0)
    to_idx = sitio_config.get("to", 49)
    print(f"Consultando: {url}?_from={from_idx}&_to={to_idx}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "es-CO,es;q=0.9",
    }

    try:
        resp = requests.get(url, params={"_from": from_idx, "_to": to_idx}, headers=headers, timeout=15)
        resp.raise_for_status()
        products = resp.json()
    except requests.RequestException as e:
        print(f"Error de conexión con {sitio_config['sitio']}: {e}")
        return None
    except Exception as e:
        print(f"[{sitio_config['sitio']}] Error parseando respuesta: {e}")
        return None

    if not products:
        print(f"[{sitio_config['sitio']}] Sin resultados")
        return None

    base_domain = sitio_config.get("base_domain", "")

    best_idx, best_score, best_title = -1, -1, None
    for i, p in enumerate(products[:15]):
        title = p.get("productName", "")
        if not title:
            continue
        score, is_relevant = calculate_relevance_score(product_name, title)
        print(f"[{sitio_config['sitio']}] Resultado {i}: '{title[:70]}' - Score: {score}/100")
        if is_relevant and score > best_score:
            best_score, best_idx, best_title = score, i, title

    if best_idx < 0:
        print(f"[{sitio_config['sitio']}] Sin resultados relevantes (score >= 60)")
        return None

    p = products[best_idx]
    items = p.get("items", [])
    price = None

    if items:
        sellers = items[0].get("sellers", [])
        seller = next((s for s in sellers if s.get("sellerDefault")), sellers[0] if sellers else None)
        if seller:
            offer = seller.get("commertialOffer", {})
            if offer.get("IsAvailable"):
                price_raw = offer.get("Price") or offer.get("PriceWithoutDiscount")
                if price_raw:
                    price = format_price(str(int(price_raw)))

    link = p.get("link", "")
    product_url = link if link.startswith("http") else f"{base_domain}{link}" if link else None

    print(f"[{sitio_config['sitio']}] [OK] '{best_title}' - Precio: {price}")

    return {
        "sitio": sitio_config["sitio"],
        "busqueda": product_name,
        "title": best_title,
        "price": price,
        "url": product_url,
        "score": best_score,
    }


# Cache de token para Mercado Libre (evita llamar oauth en cada scrape)
_ml_token_cache: dict = {"token": None, "expires_at": None}


def _get_ml_token(client_id: str, client_secret: str) -> str:
    now = datetime.now()
    if _ml_token_cache["token"] and _ml_token_cache["expires_at"] and now < _ml_token_cache["expires_at"]:
        return _ml_token_cache["token"]

    resp = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data={"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    _ml_token_cache["token"] = data["access_token"]
    _ml_token_cache["expires_at"] = now + timedelta(seconds=data.get("expires_in", 21600) - 300)
    return _ml_token_cache["token"]


def scrape_mercadolibre(sitio_config, product_name):
    """
    Scraper para Mercado Libre via API REST oficial con OAuth2.
    Requiere ML_CLIENT_ID y ML_CLIENT_SECRET en .env.
    """
    client_id = os.environ.get("ML_CLIENT_ID") or sitio_config.get("client_id")
    client_secret = os.environ.get("ML_CLIENT_SECRET") or sitio_config.get("client_secret")
    site_id = sitio_config.get("site_id", "MCO")

    if not client_id or not client_secret:
        print(f"[{sitio_config['sitio']}] Faltan ML_CLIENT_ID y ML_CLIENT_SECRET en .env")
        return None

    try:
        token = _get_ml_token(client_id, client_secret)
    except Exception as e:
        print(f"[{sitio_config['sitio']}] Error obteniendo token: {e}")
        return None

    try:
        resp = requests.get(
            f"https://api.mercadolibre.com/sites/{site_id}/search",
            params={"q": product_name, "limit": sitio_config.get("limit", 50)},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[{sitio_config['sitio']}] Error de conexión: {e}")
        return None

    results = data.get("results", [])
    if not results:
        print(f"[{sitio_config['sitio']}] Sin resultados")
        return None

    best_idx, best_score, best_title = -1, -1, None
    for i, r in enumerate(results[:15]):
        title = r.get("title", "")
        score, is_relevant = calculate_relevance_score(product_name, title)
        print(f"[{sitio_config['sitio']}] Resultado {i}: '{title[:70]}' - Score: {score}/100")
        if is_relevant and score > best_score:
            best_score, best_idx, best_title = score, i, title

    if best_idx < 0:
        print(f"[{sitio_config['sitio']}] Sin resultados relevantes (score >= 60)")
        return None

    r = results[best_idx]
    price = format_price(str(int(r["price"]))) if r.get("price") else None

    print(f"[{sitio_config['sitio']}] [OK] '{best_title}' - Precio: {price}")

    return {
        "sitio": sitio_config["sitio"],
        "busqueda": product_name,
        "title": best_title,
        "price": price,
        "url": r.get("permalink"),
        "score": best_score,
    }