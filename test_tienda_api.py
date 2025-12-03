"""
Script de prueba para investigar y testear APIs de tiendas
Permite probar configuraciones de scraping antes de agregarlas a config_sitios.json
"""
import json
import sys
import requests
from pprint import pprint

def test_graphql_api(config, product_name="iPhone 15"):
    """
    Prueba un endpoint GraphQL con una configuración dada

    Args:
        config: Diccionario con configuración de tienda
        product_name: Nombre del producto a buscar
    """
    print(f"\n{'='*70}")
    print(f"🔍 Probando {config['sitio']} - GraphQL API")
    print(f"{'='*70}\n")

    # Preparar la petición
    url = config['url']
    params = config['params'].copy()

    # Reemplazar placeholders
    if config.get('requires_url_variables'):
        # Convertir params a JSON string, reemplazar, y convertir de vuelta
        params_str = json.dumps(params)
        params_str = params_str.replace('{product_name}', product_name)
        params = json.loads(params_str)

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    print(f"📡 Endpoint: {url}")
    print(f"📦 Buscando: {product_name}\n")

    try:
        # Hacer la petición
        response = requests.post(url, json=params, headers=headers, timeout=10)

        print(f"✅ Status Code: {response.status_code}")
        print(f"📏 Response Size: {len(response.text)} bytes\n")

        if response.status_code == 200:
            try:
                data = response.json()

                # Guardar respuesta para debug
                filename = f"{config['sitio']}_test_resultado.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"💾 Respuesta guardada en: {filename}\n")

                # Intentar extraer datos usando los xpaths configurados
                print("🔎 Intentando extraer datos...\n")

                title_xpath = config.get('title_xpath')
                price_xpath = config.get('price_xpath')
                url_xpath = config.get('url_xpath')

                if title_xpath:
                    title = extract_from_json(data, title_xpath)
                    print(f"   📝 Nombre: {title}")

                if price_xpath:
                    price = extract_from_json(data, price_xpath)
                    print(f"   💰 Precio: {price}")

                if url_xpath:
                    product_url = extract_from_json(data, url_xpath)
                    base_url = config.get('base_product_url', '')
                    url_suffix = config.get('url_suffix', '')

                    if product_url:
                        if not product_url.startswith('http'):
                            if product_url.startswith('/'):
                                product_url = f"{base_url}{product_url}"
                            else:
                                product_url = f"{base_url}/{product_url}"
                            if url_suffix:
                                product_url = f"{product_url}{url_suffix}"

                    print(f"   🔗 URL: {product_url}")

                print(f"\n{'='*70}")
                print("✅ Test completado exitosamente!")
                print(f"{'='*70}\n")

                return True

            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                print(f"Contenido de respuesta (primeros 500 chars):")
                print(response.text[:500])
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Timeout - La petición tardó más de 10 segundos")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición: {e}")
        return False


def test_rest_api(config, product_name="iPhone 15"):
    """
    Prueba un endpoint REST con una configuración dada

    Args:
        config: Diccionario con configuración de tienda
        product_name: Nombre del producto a buscar
    """
    print(f"\n{'='*70}")
    print(f"🔍 Probando {config['sitio']} - REST API")
    print(f"{'='*70}\n")

    # Preparar la petición
    url = config['url']
    params = config['params'].copy()

    # Reemplazar placeholders
    for key, value in params.items():
        if isinstance(value, str) and '{product_name}' in value:
            params[key] = value.replace('{product_name}', product_name)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    print(f"📡 Endpoint: {url}")
    print(f"📦 Params: {params}\n")

    try:
        # Hacer la petición GET
        response = requests.get(url, params=params, headers=headers, timeout=10)

        print(f"✅ Status Code: {response.status_code}")
        print(f"📏 Response Size: {len(response.text)} bytes\n")

        if response.status_code == 200:
            try:
                data = response.json()

                # Guardar respuesta para debug
                filename = f"{config['sitio']}_test_resultado.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"💾 Respuesta guardada en: {filename}\n")

                # Intentar extraer datos
                print("🔎 Intentando extraer datos...\n")

                title_xpath = config.get('title_xpath')
                price_xpath = config.get('price_xpath')
                url_xpath = config.get('url_xpath')

                if title_xpath:
                    title = extract_from_json(data, title_xpath)
                    print(f"   📝 Nombre: {title}")

                if price_xpath:
                    price = extract_from_json(data, price_xpath)
                    print(f"   💰 Precio: {price}")

                if url_xpath:
                    product_url = extract_from_json(data, url_xpath)
                    print(f"   🔗 URL: {product_url}")

                print(f"\n{'='*70}")
                print("✅ Test completado exitosamente!")
                print(f"{'='*70}\n")

                return True

            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Timeout - La petición tardó más de 10 segundos")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición: {e}")
        return False


def extract_from_json(data, path):
    """Extrae un valor de un diccionario JSON usando una ruta tipo 'a.b[0].c'"""
    parts = path.replace('[', '.').replace(']', '').split('.')
    current = data

    for part in parts:
        if not part:
            continue

        try:
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]
        except (KeyError, IndexError, TypeError):
            return None

    return current


# === CONFIGURACIONES DE PRUEBA ===

# Configuración de Ktronix (alta probabilidad de funcionar)
KTRONIX_CONFIG = {
    "sitio": "Ktronix",
    "country_code": "CO",
    "currency": "COP",
    "url": "https://www.ktronix.com/api/graphql",
    "fetch_method": "graphql",
    "requires_url_variables": True,
    "base_product_url": "https://www.ktronix.com",
    "url_suffix": "/p",
    "params": {
        "operationName": "SearchQuery",
        "variables": {
            "first": 16,
            "after": "0",
            "sort": "price_asc",
            "term": "{product_name}",
            "selectedFacets": [
                {
                    "key": "channel",
                    "value": "{\"salesChannel\":\"1\",\"regionId\":\"\"}"
                },
                {
                    "key": "locale",
                    "value": "es-CO"
                }
            ]
        }
    },
    "title_xpath": "data.search.products.edges[0].node.items[0].name",
    "price_xpath": "data.search.products.edges[0].node.items[0].sellers[0].commertialOffer.Price",
    "url_xpath": "data.search.products.edges[0].node.linkText"
}


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TEST DE APIS DE TIENDAS - ePriceFlo")
    print("="*70)

    # Mostrar opciones
    print("\nOpciones:")
    print("1. Probar Ktronix (recomendado - similar a Éxito)")
    print("2. Probar configuración personalizada (edita el código)\n")

    opcion = input("Selecciona una opción (1-2): ").strip()

    if opcion == "1":
        product = input("\nNombre del producto a buscar [iPhone 15]: ").strip() or "iPhone 15"
        test_graphql_api(KTRONIX_CONFIG, product)

    elif opcion == "2":
        print("\n⚠️  Edita el archivo test_tienda_api.py y agrega tu configuración")
        print("Luego ejecuta de nuevo el script")

    else:
        print("❌ Opción inválida")
