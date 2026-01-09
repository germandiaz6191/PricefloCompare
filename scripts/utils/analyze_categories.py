#!/usr/bin/env python3
"""
Script para generar mapeo de categorías basado en productos existentes
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from database import get_products
from collections import defaultdict
import json

print("=" * 80)
print("📦 ANÁLISIS DE CATEGORÍAS - PRODUCTOS EN BD")
print("=" * 80)

products = get_products()

# Agrupar por categoría
categories = defaultdict(list)
for p in products:
    cat = p.get('category', 'Sin categoría')
    categories[cat].append(p['name'])

print(f"\nTotal de productos: {len(products)}")
print(f"Categorías únicas: {len(categories)}\n")

# Mostrar productos por categoría
for cat, prods in sorted(categories.items()):
    print(f"\n{'='*80}")
    print(f"📁 {cat} ({len(prods)} productos)")
    print('='*80)
    for i, prod in enumerate(prods[:10], 1):  # Mostrar primeros 10
        print(f"   {i}. {prod}")
    if len(prods) > 10:
        print(f"   ... y {len(prods) - 10} más")

# Generar template para mapeo
print("\n" + "="*80)
print("🗺️ TEMPLATE PARA MAPEO DE CATEGORÍAS")
print("="*80)
print("\nInstrucciones:")
print("1. Para cada categoría, busca en Éxito.com productos de esa categoría")
print("2. Inspecciona la petición GraphQL (F12 -> Network -> Buscar 'SearchQuery')")
print("3. Busca el filtro 'selectedFacets' con key 'category-X'")
print("4. Anota el valor y el nivel (category-2, category-3, etc.)")
print("\nEjemplo encontrado:")
print("  Categoría: Gaming")
print("  Producto: Teclado Gamer")
print("  Filtro Éxito: category-3 = 'accesorios-de-computador'")
print("\n" + "="*80)

# Template JSON para completar
template = {
    "comment": "Mapeo de categorías ePriceFlo a filtros de Éxito",
    "instructions": {
        "1": "Busca en Éxito.com un producto de cada categoría",
        "2": "Abre DevTools (F12) -> Network -> Buscar 'SearchQuery'",
        "3": "Copia el valor del filtro selectedFacets con key 'category-X'",
        "4": "Actualiza el mapping abajo con el nivel y valor correcto"
    },
    "mappings": {}
}

# Generar estructura para cada categoría
for cat in sorted(categories.keys()):
    if cat != 'Sin categoría':
        template["mappings"][cat] = {
            "exito_level": "category-3",  # ← ACTUALIZAR (category-2, category-3, etc.)
            "exito_value": "COMPLETAR",   # ← ACTUALIZAR con el valor de Éxito
            "example_product": categories[cat][0],  # Producto ejemplo para buscar
            "notes": ""
        }

# Guardar template
output_file = "category_mapping_template.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2, ensure_ascii=False)

print(f"\n✅ Template generado en: {output_file}")
print("\n📝 Próximo paso:")
print(f"   1. Edita {output_file}")
print("   2. Para cada categoría, busca en Éxito y completa:")
print("      - exito_level: El nivel de categoría (category-2, category-3, etc.)")
print("      - exito_value: El valor exacto del filtro")
print("   3. Ejecuta: python scripts/utils/apply_category_mapping.py")
print("="*80)
