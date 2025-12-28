"""
Ver qué productos hay en la BD y qué categorías tienen
"""
from database import get_products

products = get_products()

print("=" * 80)
print("📦 PRODUCTOS EN LA BASE DE DATOS")
print("=" * 80)

air_fryer_products = [p for p in products if 'fryer' in p['name'].lower() or 'freidora' in p['name'].lower()]

if air_fryer_products:
    print(f"\n🔍 Encontrados {len(air_fryer_products)} productos de Air Fryer/Freidora:\n")
    for p in air_fryer_products:
        print(f"ID: {p['id']}")
        print(f"   Nombre: {p['name']}")
        print(f"   Categoría: {p.get('category', 'Sin categoría')}")
        print(f"   Is Frequent: {p.get('is_frequent', False)}")
        print()
else:
    print("\n❌ No se encontraron productos de Air Fryer/Freidora")
    print("\nMostrando los primeros 5 productos:")
    for p in products[:5]:
        print(f"   - {p['name']} (Categoría: {p.get('category', 'Sin categoría')})")

print("=" * 80)
print(f"Total de productos en BD: {len(products)}")
print("=" * 80)
