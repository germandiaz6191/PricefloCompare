#!/usr/bin/env python3
"""
Prueba real de scraping con detección automática de marca
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from scrapers.generic_scrapers import scrape_price, load_sites_config

print("="*80)
print("🔍 PRUEBA REAL DE SCRAPING CON DETECCIÓN DE MARCA")
print("="*80)

# Cargar configuración de Éxito desde BD
sites = load_sites_config()
exito_config = next(s for s in sites if s["sitio"] == "Éxito")

# Casos de prueba
test_products = [
    {"name": "AirPods 3", "category": "Audio"},
    {"name": "Motorola Edge 40", "category": "Celulares"},
    {"name": "Samsung Galaxy S24", "category": "Celulares"}
]

for product in test_products:
    print(f"\n{'='*80}")
    print(f"📦 Producto: {product['name']}")
    print(f"📁 Categoría: {product['category']}")
    print(f"{'='*80}\n")

    result = scrape_price(exito_config, product['name'], product['category'])

    if result:
        print(f"\n✅ RESULTADO:")
        print(f"  Título: {result.get('title')}")
        print(f"  Precio: {result.get('price')}")
        print(f"  URL: {result.get('url')}")
        print(f"  Score: {result.get('score')}/100")
    else:
        print("\n❌ No se encontró resultado")

    print("\n" + "="*80)
