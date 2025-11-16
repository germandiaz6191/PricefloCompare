import requests
from bs4 import BeautifulSoup

def buscar_producto_homecenter(product_name):
    base_url = "https://www.homecenter.com.co/homecenter-co/search"
    params = {
        "Ntt": product_name,
        "currentpage": "1",
        "sortBy": "derived.price.event.search.10,asc"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Error Homecenter: {response.status_code}"

    soup = BeautifulSoup(response.text, 'html.parser')

    product_div = soup.find('div', class_='product-item')
    if not product_div:
        return "Producto no encontrado en Homecenter"

    price_span = product_div.find('span', class_='price-sales')
    if not price_span:
        return "Precio no encontrado en Homecenter"

    return price_span.text.strip()