#!/usr/bin/env python3
"""
Script para verificar si una categoría funciona en Éxito
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import requests
import json
from urllib.parse import urlencode

def test_category(product_name, category_level, category_value):
    """Prueba si una categoría retorna resultados en Éxito"""

    url = "https://www.exito.com/api/graphql"

    variables = {
        "first": 10,
        "after": "0",
        "sort": "score_desc",
        "term": product_name,
        "selectedFacets": [
            {"key": category_level, "value": category_value},
            {"key": "channel", "value": '{"salesChannel":"1","regionId":""}'},
            {"key": "locale", "value": "es-CO"}
        ]
    }

    query_params = {
        "operationName": "SearchQuery",
        "variables": json.dumps(variables, separators=(",", ":"))
    }

    full_url = f"{url}?{urlencode(query_params)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    print("="*80)
    print("🔍 VERIFICANDO CATEGORÍA EN ÉXITO")
    print("="*80)
    print(f"Producto: {product_name}")
    print(f"Filtro: {category_level} = {category_value}")
    print()

    try:
        resp = requests.get(full_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        products = data.get("data", {}).get("search", {}).get("products", {}).get("edges", [])
        total = len(products)

        if total > 0:
            print(f"✅ FUNCIONA - Encontrados {total} productos")
            print()
            print("Primeros 3 resultados:")
            for i, edge in enumerate(products[:3], 1):
                product = edge.get("node", {})
                item = product.get("items", [{}])[0]
                name = item.get("name", "Sin nombre")
                print(f"   {i}. {name}")

            print()
            print("💾 Para agregar a BD, ejecuta:")
            print(f"   INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value)")
            print(f"   VALUES (1, 'TuCategoria', '{category_level}', '{category_value}');")

        else:
            print("❌ NO FUNCIONA - Sin resultados")
            print()
            print("💡 Prueba:")
            print("   - Otro nivel (category-2, category-4, etc.)")
            print("   - Otro valor de categoría")
            print("   - Buscar manualmente en exito.com y ver F12 → Network")

    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("="*80)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verificar si una categoría funciona en Éxito")
    parser.add_argument("product", help="Nombre del producto a buscar")
    parser.add_argument("--level", default="category-3", help="Nivel de categoría (default: category-3)")
    parser.add_argument("--value", required=True, help="Valor de la categoría (ej: accesorios-de-computador)")

    args = parser.parse_args()

    test_category(args.product, args.level, args.value)
