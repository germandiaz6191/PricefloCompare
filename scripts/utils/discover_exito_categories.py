#!/usr/bin/env python3
"""
Script para descubrir categorías de Éxito automáticamente.
Busca productos en Éxito.com y extrae los filtros de categoría que se usan.
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import requests
import json
from database import get_products, execute_query, is_postgres
from collections import defaultdict

def discover_category_from_exito(search_term):
    """
    Busca un término en Éxito y extrae el filtro de categoría que retorna
    """
    url = "https://www.exito.com/api/graphql"

    variables = {
        "first": 5,
        "after": "0",
        "sort": "score_desc",
        "term": search_term,
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

    try:
        resp = requests.get(full_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Intentar extraer categorías de los facets retornados
        facets = data.get("data", {}).get("search", {}).get("facets", [])

        categories_found = []
        for facet in facets:
            if "categor" in facet.get("name", "").lower():
                values = facet.get("values", [])
                for val in values[:3]:  # Top 3 categorías
                    categories_found.append({
                        "facet_name": facet.get("name"),
                        "key": val.get("key"),
                        "name": val.get("name"),
                        "quantity": val.get("quantity", 0)
                    })

        # También intentar extraer de los productos retornados
        products = data.get("data", {}).get("search", {}).get("products", {}).get("edges", [])
        product_count = len(products)

        return {
            "search_term": search_term,
            "found_products": product_count,
            "categories": categories_found,
            "success": product_count > 0
        }

    except Exception as e:
        return {
            "search_term": search_term,
            "found_products": 0,
            "categories": [],
            "success": False,
            "error": str(e)
        }

def main():
    print("="*80)
    print("🔍 DESCUBRIMIENTO AUTOMÁTICO DE CATEGORÍAS DE ÉXITO")
    print("="*80)

    # Obtener productos de la BD agrupados por categoría
    products = get_products()

    categories = defaultdict(list)
    for p in products:
        cat = p.get('category', 'Sin categoría')
        if cat != 'Sin categoría':
            categories[cat].append(p['name'])

    print(f"\n📦 Encontradas {len(categories)} categorías en la BD")
    print(f"   Total de productos: {len(products)}")

    # Seleccionar un producto ejemplo por categoría
    results = {}

    print("\n" + "="*80)
    print("🔎 BUSCANDO PRODUCTOS EN ÉXITO...")
    print("="*80)

    for category, product_list in sorted(categories.items()):
        # Tomar el primer producto de cada categoría
        example_product = product_list[0]

        print(f"\n📁 Categoría: {category}")
        print(f"   Producto de prueba: {example_product}")
        print(f"   Buscando en Éxito...", end=" ")

        result = discover_category_from_exito(example_product)
        results[category] = result

        if result['success']:
            print(f"✅ {result['found_products']} productos encontrados")

            if result['categories']:
                print("   📊 Categorías detectadas:")
                for cat in result['categories']:
                    print(f"      - {cat['name']} (key: {cat['key']}, cantidad: {cat['quantity']})")
            else:
                print("   ⚠️ No se detectaron filtros de categoría en la respuesta")
        else:
            error = result.get('error', 'No encontrado')
            print(f"❌ {error}")

    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN")
    print("="*80)

    successful = [cat for cat, res in results.items() if res['success']]
    failed = [cat for cat, res in results.items() if not res['success']]

    print(f"\n✅ Categorías que encontraron productos: {len(successful)}/{len(results)}")
    print(f"❌ Categorías sin resultados: {len(failed)}")

    if failed:
        print("\n⚠️ Categorías que necesitan ajuste:")
        for cat in failed:
            print(f"   - {cat}: Prueba con otro término de búsqueda")

    # Sugerencias para actualizar BD
    print("\n" + "="*80)
    print("💡 PRÓXIMO PASO: VERIFICAR MANUALMENTE")
    print("="*80)
    print("\nPara cada categoría que encontró productos:")
    print("1. Abre https://www.exito.com")
    print("2. Busca el producto")
    print("3. F12 → Network → Busca 'SearchQuery'")
    print("4. Mira 'selectedFacets' → copia el filtro de categoría")
    print("5. Agrega a BD:")
    print()
    print("   INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value)")
    print("   VALUES (1, 'NombreCategoria', 'category-X', 'valor-encontrado');")
    print("="*80)

    # Guardar resultados en JSON
    output_file = "category_discovery_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultados guardados en: {output_file}")
    print("="*80)

if __name__ == "__main__":
    main()
