#!/usr/bin/env python3
"""
Script de prueba para verificar detección de marca y filtros
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from scrapers.graphql_scraper import extract_brand, map_category
import json

print("="*80)
print("🧪 PRUEBA DE DETECCIÓN DE MARCA Y MAPEO DE CATEGORÍAS")
print("="*80)

# Casos de prueba basados en hallazgos del usuario
test_cases = [
    # Audio - Apple
    {
        "name": "AirPods 3",
        "category": "Audio",
        "expected_brand": "apple",
        "expected_category_level": "category-2",
        "expected_category_value": "audio"
    },
    # Celulares - Motorola
    {
        "name": "Motorola Edge 40",
        "category": "Celulares",
        "expected_brand": "motorola",
        "expected_category_level": "category-2",
        "expected_category_value": "celulares"
    },
    # Celulares - Samsung
    {
        "name": "Samsung Galaxy S24",
        "category": "Celulares",
        "expected_brand": "samsung",
        "expected_category_level": "category-2",
        "expected_category_value": "celulares"
    },
    # Audio - JBL
    {
        "name": "JBL Charge 5",
        "category": "Audio",
        "expected_brand": "jbl",
        "expected_category_level": "category-2",
        "expected_category_value": "audio"
    }
]

print("\n📋 Ejecutando casos de prueba...\n")

all_passed = True

for i, test in enumerate(test_cases, 1):
    print(f"Caso {i}: {test['name']} ({test['category']})")
    print("-" * 40)

    # Probar detección de marca
    detected_brand = extract_brand(test['name'])
    brand_ok = detected_brand == test['expected_brand']
    print(f"  Marca detectada: {detected_brand}")
    print(f"  Esperada: {test['expected_brand']}")
    print(f"  ✅ OK" if brand_ok else f"  ❌ FALLO")

    # Probar mapeo de categoría
    category_mapping = map_category(test['category'], "Éxito")
    category_level_ok = category_mapping['level'] == test['expected_category_level']
    category_value_ok = category_mapping['value'] == test['expected_category_value']

    print(f"  Categoría mapeada: {category_mapping['level']} = {category_mapping['value']}")
    print(f"  Esperada: {test['expected_category_level']} = {test['expected_category_value']}")
    print(f"  ✅ OK" if (category_level_ok and category_value_ok) else f"  ❌ FALLO")

    if not (brand_ok and category_level_ok and category_value_ok):
        all_passed = False

    print()

print("="*80)
if all_passed:
    print("✅ TODOS LOS CASOS DE PRUEBA PASARON")
else:
    print("❌ ALGUNOS CASOS FALLARON - Revisar configuración")
print("="*80)

# Simular payload completo
print("\n🔍 SIMULACIÓN DE PAYLOAD PARA ÉXITO")
print("="*80)
print("\nEjemplo: AirPods 3 (Audio)")
print("-" * 40)

simulated_facets = [
    {"key": "category-2", "value": "audio"},
    {"key": "brand", "value": "apple"},
    {"key": "channel", "value": "{\"salesChannel\":\"1\",\"regionId\":\"\"}"},
    {"key": "locale", "value": "es-CO"}
]

print(json.dumps(simulated_facets, indent=2, ensure_ascii=False))
print("\nEsto debería coincidir con el payload que encontraste en DevTools! ✅")
print("="*80)
