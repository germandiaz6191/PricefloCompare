"""
Diagnostico: prueba la API de Exito con distintos facets para encontrar
combinacion que devuelva resultados.
"""
import requests
import json
from urllib.parse import urlencode

URL = "https://www.exito.com/api/graphql"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
    "Origin": "https://www.exito.com",
    "Referer": "https://www.exito.com/",
}

def search(term, facets, label):
    variables = {
        "first": 5,
        "after": "0",
        "sort": "price_asc",
        "term": term,
        "selectedFacets": facets
    }
    params = {
        "operationName": "SearchQuery",
        "variables": json.dumps(variables, separators=(",", ":"))
    }
    url = f"{URL}?{urlencode(params)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        data = resp.json()
        edges = data.get("data", {}).get("search", {}).get("products", {}).get("edges", [])
        total = data.get("data", {}).get("search", {}).get("products", {}).get("pageInfo", {}).get("totalCount", 0)
        print(f"[{label}] totalCount={total}, edges={len(edges)}")
        for i, e in enumerate(edges[:3]):
            name = e.get("node", {}).get("items", [{}])[0].get("name", "?")
            print(f"  {i}: {name[:80]}")
    except Exception as ex:
        print(f"[{label}] ERROR: {ex}")
    print()

BASE_FACETS = [
    {"key": "channel", "value": "{\"salesChannel\":\"1\",\"regionId\":\"\"}"},
    {"key": "locale", "value": "es-CO"}
]

print("=== Prueba 1: Sin categoria, solo term ===")
search("Nevera Samsung", BASE_FACETS, "sin-cat")

print("=== Prueba 2: category-2 electrodomesticos ===")
search("Nevera Samsung", [{"key": "category-2", "value": "electrodomesticos"}] + BASE_FACETS, "cat2-electro")

print("=== Prueba 3: category-3 electrodomesticos ===")
search("Nevera Samsung", [{"key": "category-3", "value": "electrodomesticos"}] + BASE_FACETS, "cat3-electro")

print("=== Prueba 4: iPhone 16, sin categoria ===")
search("iPhone 16", BASE_FACETS, "iphone-sin-cat")

print("=== Prueba 5: iPhone 16, category-2 celulares ===")
search("iPhone 16", [{"key": "category-2", "value": "celulares"}] + BASE_FACETS, "iphone-cat2")

print("=== Prueba 6: Lavadora LG, sin categoria ===")
search("Lavadora LG 17Kg", BASE_FACETS, "lavadora-sin-cat")
