#!/usr/bin/env python3
"""
Aplica el mapeo de categorías verificado al sistema
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import json

print("="*80)
print("🔧 APLICAR MAPEO DE CATEGORÍAS")
print("="*80)

# 1. Leer template con mappings
template_file = os.path.join(project_root, "category_mapping_template.json")
if not os.path.exists(template_file):
    print(f"❌ No se encontró: {template_file}")
    print("💡 Primero ejecuta: python scripts/utils/analyze_categories.py")
    sys.exit(1)

with open(template_file, 'r', encoding='utf-8') as f:
    template = json.load(f)

mappings = template.get("mappings", {})

# Verificar que no haya valores sin completar
incomplete = []
for cat, data in mappings.items():
    if data.get("exito_value") in ["COMPLETAR", ""]:
        incomplete.append(f"{cat} ({data['example_product']})")

if incomplete:
    print("\n⚠️  Categorías sin completar:")
    for cat in incomplete:
        print(f"   - {cat}")
    print("\n💡 Edita category_mapping_template.json y completa los valores faltantes")
    print("   Instrucciones en el archivo.")
    sys.exit(1)

# 2. Generar category_mapping.json simplificado para el scraper
output_mapping = {}
for cat, data in mappings.items():
    output_mapping[cat] = {
        "level": data["exito_level"],
        "value": data["exito_value"]
    }

output_file = os.path.join(project_root, "category_mapping.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "comment": "Mapeo de categorías ePriceFlo a filtros de Éxito (GENERADO AUTOMÁTICAMENTE)",
        "mappings": output_mapping
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ category_mapping.json actualizado")
print(f"   Ubicación: {output_file}")

# 3. Actualizar config_sitios.json para usar category-3
config_file = os.path.join(project_root, "config_sitios.json")
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Buscar configuración de Éxito y actualizar
updated = False
for sitio in config:
    if sitio.get("sitio") == "Éxito":
        # Actualizar el level de categoría a category-3
        if "params" in sitio and "variables" in sitio["params"]:
            facets = sitio["params"]["variables"].get("selectedFacets", [])
            for facet in facets:
                if "category" in facet.get("key", ""):
                    old_key = facet["key"]
                    facet["key"] = "category-3"  # Usar category-3 por defecto
                    print(f"   📝 Éxito: {old_key} → category-3")
                    updated = True

if updated:
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"   ✅ config_sitios.json actualizado")

# 4. Resumen
print("\n" + "="*80)
print("✅ MAPEO APLICADO EXITOSAMENTE")
print("="*80)
print("\nCambios realizados:")
print(f"   1. category_mapping.json generado con {len(output_mapping)} categorías")
print("   2. config_sitios.json actualizado a category-3")
print("\nPróximo paso:")
print("   python scripts/utils/add_test_data.py")
print("\nEl scraper ahora usará:")
print("   - Nivel: category-3 (en vez de category-2)")
print("   - Valores correctos de Éxito por categoría")
print("="*80)
