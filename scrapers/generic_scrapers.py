import requests
from lxml import html
import json
from urllib.parse import urlencode
from scrapers.graphql_scraper import scrape_graphql  # nuevo módulo
from scrapers.text_utils import calculate_relevance_score, normalize_text, format_price

def load_sites_config(path="config_sitios.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def scrape_price(sitio_config, product_name):
    method = sitio_config.get("fetch_method", "html")

    if method == "html":
        return scrape_html(sitio_config, product_name)
    elif method == "graphql":
        return scrape_graphql(sitio_config, product_name)
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

    # Extraer título
    title_xpath = sitio_config.get("title_xpath")
    title_text = None
    if title_xpath:
        elements = tree.xpath(title_xpath)
        if elements:
            title_text = elements[0].text_content().strip()
            print(f"[{sitio_config['sitio']}] Primer título encontrado: '{title_text}'")

            # Calcular score de relevancia
            score, is_relevant = calculate_relevance_score(product_name, title_text)
            print(f"[{sitio_config['sitio']}] Score de relevancia: {score}/100")

            if not is_relevant:
                print(f"[{sitio_config['sitio']}] Primer resultado no es relevante (score < 60)")
                return None
        else:
            print(f"[{sitio_config['sitio']}] No se encontró ningún título con el xpath '{title_xpath}'")
            return None

    # Extraer precio
    price_xpath = sitio_config.get("price_xpath")
    price_text = None
    if price_xpath:
        price_elements = tree.xpath(price_xpath)
        if price_elements:
            price_text = price_elements[0].text_content().strip()
            price_text = format_price(price_text)

    if title_text:
        return {
            "sitio": sitio_config["sitio"],
            "busqueda": product_name,
            "url": url,
            "title_xpath": title_xpath,
            "price_xpath": price_xpath,
            "title": title_text,
            "price": price_text
        }

    return None