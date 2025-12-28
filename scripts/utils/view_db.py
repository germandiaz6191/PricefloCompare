"""
Script para explorar la base de datos SQLite
"""
from database import get_products, get_stores, get_stats, get_latest_prices
import json

def show_db_content():
    print("=" * 70)
    print("📊 CONTENIDO DE LA BASE DE DATOS")
    print("=" * 70)

    # Estadísticas generales
    stats = get_stats()
    print("\n📈 ESTADÍSTICAS:")
    print(f"  Total productos: {stats['total_products']}")
    print(f"  Total tiendas: {stats['total_stores']}")
    print(f"  Total snapshots: {stats['total_snapshots']}")
    print(f"  Último scrape: {stats['last_scrape']}")

    # Productos
    print("\n📦 PRODUCTOS:")
    products = get_products()
    for p in products:
        print(f"  [{p['id']}] {p['name']}")
        print(f"      Categoría: {p['category']}")
        print(f"      Frecuente: {'Sí' if p['is_frequent'] else 'No'}")
        print(f"      Intervalo: {p['update_interval_hours']}h")

        # Últimos precios de este producto
        prices = get_latest_prices(p['id'])
        if prices:
            print(f"      Precios actuales:")
            for price in prices:
                print(f"        - {price['store_name']}: ${price['price']:,.0f}")
                print(f"          Título: {price['title'][:50]}...")
                print(f"          Scraped: {price['scraped_at']}")
        else:
            print(f"      ⚠️  Sin precios registrados")
        print()

    # Tiendas
    print("\n🏪 TIENDAS:")
    stores = get_stores()
    for s in stores:
        print(f"  [{s['id']}] {s['name']}")
        print(f"      URL: {s['url']}")
        print(f"      Método: {s['fetch_method']}")
        print(f"      Activa: {'Sí' if s['active'] else 'No'}")
        print()

    print("=" * 70)

if __name__ == "__main__":
    show_db_content()
