import requests
from bs4 import BeautifulSoup

def buscar_producto_exito(product_name):
    # URL construida con parámetros que diste
    base_url = "https://www.exito.com/s"
    params = {
        "q": product_name,
        "sort": "price_asc",
        "page": "0"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Error Éxito: {response.status_code}"

    soup = BeautifulSoup(response.text, 'html.parser')

    # Selector del producto (ajusta según inspecciones)
    product_div = soup.find('div', class_='product-card')
    if not product_div:
        return "Producto no encontrado en Éxito"

    price_span = product_div.find('span', class_='sr-only')
    if not price_span:
        return "Precio no encontrado en Éxito"

    return price_span.text.strip()