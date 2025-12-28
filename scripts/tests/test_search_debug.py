"""
Script de debug para probar búsquedas en Éxito y ver qué resultados retorna
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

# Obtener directorio raíz del proyecto (2 niveles arriba: scripts/X/ -> scripts/ -> raíz)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
import json
from scrapers.graphql_scraper import scrape_graphql

# Cargar configuración de Éxito
with open('config_sitios.json', 'r', encoding='utf-8') as f:
    configs = json.load(f)

exito_config = configs[0]  # Éxito es el primero

# Productos a probar
test_products = [
    "Air Fryer Oster",
    "Air Fryer Kalley",
    "Freidora de Aire Oster",
    "Freidora Oster"
]

print("=" * 80)
print("🔍 TEST DE BÚSQUEDAS EN ÉXITO")
print("=" * 80)

for product in test_products:
    print(f"\n{'='*80}")
    print(f"🔎 Buscando: '{product}'")
    print("="*80)

    result = scrape_graphql(exito_config, product)

    if result:
        print(f"\n✅ ENCONTRADO:")
        print(f"   Título: {result['title']}")
        print(f"   Precio: ${result['price']:,} COP")
        print(f"   URL: {result['url']}")
    else:
        print(f"\n❌ NO SE ENCONTRÓ RESULTADO RELEVANTE")

    print()

print("\n" + "="*80)
print("💡 SUGERENCIAS:")
print("="*80)
print("1. Si los productos se encuentran con 'Freidora' pero no con 'Air Fryer',")
print("   considera actualizar los nombres en la base de datos.")
print("2. Si aparecen en los logs pero con score bajo (<60), considera bajar")
print("   el threshold de relevancia en text_utils.py")
print("="*80)
