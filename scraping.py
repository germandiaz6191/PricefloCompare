import requests
from bs4 import BeautifulSoup

def get_price_exito(product_name):
    url = f'https://www.exito.com/search?q={product_name.replace(" ", "+")}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error al acceder a Éxito: {response.status_code}"

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscar contenedor del producto y precio
    product_div = soup.find('div', class_='product-card')  # Selector probable
    if not product_div:
        return "Producto no encontrado en Éxito"

    price_span = product_div.find('span', class_='sr-only')  # Selector probable para precio
    if not price_span:
        return "Precio no encontrado en Éxito"
    
    return price_span.text.strip()

def get_price_homecenter(product_name):
    url = f'https://www.homecenter.com.co/homecenter-co/search?Ntt={product_name.replace(" ", "+")}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error al acceder a Homecenter: {response.status_code}"

    soup = BeautifulSoup(response.text, 'html.parser')
    
    product_div = soup.find('div', class_='product-item')  # Selector probable
    if not product_div:
        return "Producto no encontrado en Homecenter"

    price_span = product_div.find('span', class_='price-sales')  # Selector probable para precio
    if not price_span:
        return "Precio no encontrado en Homecenter"

    return price_span.text.strip()

if __name__ == "__main__":
    product = "taladro"
    print(f"Precio en Éxito: {get_price_exito(product)}")
    print(f"Precio en Homecenter: {get_price_homecenter(product)}")