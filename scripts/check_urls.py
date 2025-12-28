"""
Ver qué URLs están guardadas en la BD
"""
from database import get_price_snapshots

snapshots = get_price_snapshots(limit=5)

print("=" * 80)
print("🔗 URLs GUARDADAS EN LA BASE DE DATOS")
print("=" * 80)

for snap in snapshots:
    print(f"\nProducto ID: {snap.get('product_id')}")
    print(f"Tienda ID: {snap.get('store_id')}")
    print(f"Precio: ${snap.get('price'):,}")
    print(f"URL: {snap.get('url', 'Sin URL')[:100]}")
    print("-" * 80)
