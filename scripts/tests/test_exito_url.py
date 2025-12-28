"""
Test para verificar estructura del JSON de Éxito y path de linkText
"""
import requests
import json

# Configuración de Éxito
url = "https://www.exito.com/api/graphql"

variables = {
    "first": 16,
    "after": "0",
    "sort": "price_asc",
    "term": "AirPods",
    "selectedFacets": [
        {"key": "channel", "value": '{"salesChannel":"1","regionId":""}'},
        {"key": "locale", "value": "es-CO"}
    ]
}

query_params = {
    "operationName": "SearchQuery",
    "variables": json.dumps(variables, separators=(",", ":"))
}

from urllib.parse import urlencode
full_url = f"{url}?{urlencode(query_params)}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}

print("🔍 Consultando Éxito API...")
print(f"URL: {full_url[:100]}...")
print()

try:
    resp = requests.get(full_url, headers=headers, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    # Guardar respuesta completa
    with open("exito_airpods_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Respuesta guardada en: exito_airpods_response.json")
    print()

    # Intentar extraer el primer producto
    try:
        first_product = data["data"]["search"]["products"]["edges"][0]["node"]
        print("📦 PRIMER PRODUCTO:")
        print(f"   linkText: {first_product.get('linkText', 'NO ENCONTRADO')}")
        print(f"   productName: {first_product.get('productName', 'NO ENCONTRADO')}")
        print()

        # Intentar construir URL
        link_text = first_product.get('linkText')
        if link_text:
            product_url = f"https://www.exito.com/{link_text}/p"
            print(f"✅ URL construida: {product_url}")
        else:
            print("❌ No se pudo extraer linkText")

        # Mostrar estructura del item
        first_item = first_product.get("items", [{}])[0]
        print()
        print("📝 ESTRUCTURA DEL ITEM:")
        print(f"   name: {first_item.get('name', 'NO ENCONTRADO')}")

        sellers = first_item.get("sellers", [])
        if len(sellers) > 1:
            price = sellers[1].get("commertialOffer", {}).get("PriceWithoutDiscount")
            print(f"   precio: ${price:,} COP" if price else "   precio: NO ENCONTRADO")

    except (KeyError, IndexError) as e:
        print(f"❌ Error extrayendo datos: {e}")
        print("💡 Revisa exito_airpods_response.json para ver la estructura")

except Exception as e:
    print(f"❌ Error: {e}")
