#!/usr/bin/env python3
"""
Genera plantilla CSV para mapear categorías manualmente
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from database import get_products, get_stores
import csv
from collections import defaultdict

print("="*80)
print("📋 GENERANDO PLANTILLA DE MAPEO DE CATEGORÍAS")
print("="*80)

# 1. Obtener productos y agrupar por categoría
products = get_products()
categories = defaultdict(list)

for p in products:
    cat = p.get('category', 'Sin categoría')
    if cat != 'Sin categoría':
        categories[cat].append(p['name'])

print(f"\n📦 Productos encontrados: {len(products)}")
print(f"📁 Categorías únicas: {len(categories)}")

# 2. Obtener tiendas
stores = get_stores()
store_names = [s['name'] for s in stores]

print(f"🏪 Tiendas configuradas: {', '.join(store_names)}")

# 3. Generar CSV
output_file = "categorias_mapeo.csv"

with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)

    # Header
    headers = [
        'Categoría Actual',
        'Productos',
        'Cantidad Productos',
        'Filtro Nivel (Éxito)',
        'Filtro Valor (Éxito)',
        'Notas/Estado'
    ]
    writer.writerow(headers)

    # Filas por categoría
    for category in sorted(categories.keys()):
        product_list = categories[category]
        all_products = ', '.join(product_list)  # TODOS los productos

        writer.writerow([
            category,                  # Categoría Actual
            all_products,              # Productos (TODOS)
            len(product_list),         # Cantidad Productos
            'category-3',              # Filtro Nivel (pre-llenado)
            '',                        # Filtro Valor (VACÍO - para llenar)
            ''                         # Notas/Estado
        ])

print(f"\n✅ Plantilla generada: {output_file}")
print("\n" + "="*80)
print("📝 INSTRUCCIONES PARA LLENAR")
print("="*80)
print("""
1. Abre el archivo en Excel/Google Sheets: categorias_mapeo.csv

2. Para cada categoría:
   a) Ve a https://www.exito.com
   b) Busca uno de los productos de ejemplo
   c) Abre DevTools (F12) → Network → Busca "SearchQuery"
   d) Mira "selectedFacets" → copia el valor del filtro de categoría
   e) Llena las columnas:
      - "Filtro Nivel (Éxito)": category-2, category-3, etc.
      - "Filtro Valor (Éxito)": el valor exacto (ej: accesorios-de-computador)
      - "Notas/Estado": ✅ Confirmado / ❌ No encontrado / ⚠️ Dudoso

3. Guarda el archivo

4. Ejecuta: python scripts/utils/import_category_mapping.py

Esto importará todos los mapeos a la base de datos automáticamente.
""")
print("="*80)

# 4. Generar también un Excel con ejemplo ya llenado
print("\n💡 Generando ejemplo pre-llenado (categorias_mapeo_ejemplo.csv)...")

example_file = "categorias_mapeo_ejemplo.csv"
with open(example_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    # Ejemplo con Gaming ya llenado
    writer.writerow([
        'Gaming',
        'Teclado Gamer, Mouse Gamer, Audifonos Gamer',
        '12',
        'category-3',
        'accesorios-de-computador',
        '✅ Confirmado - Funciona perfecto'
    ])

    # Ejemplo con categoría sin confirmar
    writer.writerow([
        'Celulares',
        'Samsung Galaxy S24, iPhone 15, Xiaomi Redmi Note 13',
        '13',
        'category-3',
        'celulares',
        '⚠️ Por verificar'
    ])

print(f"✅ Ejemplo generado: {example_file}")
print("\nArchivos creados:")
print(f"  📄 {output_file} - Para que lo llenes")
print(f"  📄 {example_file} - Ejemplo de cómo llenarlo")
print("="*80)
