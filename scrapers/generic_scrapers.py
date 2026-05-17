import requests
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