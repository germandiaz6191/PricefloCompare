"""
Script que ejecuta scraping usando la lógica de main.py
PERO guarda los resultados en la base de datos

Usar este script si main.py funciona pero job_scraper.py da 403
"""
import json
from scrapers.generic_scrapers import load_sites_config, scrape_price
from database import get_products, get_stores, add_price_snapshot

def scrape_all_and_save():
    """
    Scrape todos los productos en todas las tiendas y guarda en BD
    Usa la misma lógica que main.py pero persiste en BD
    """
    print("🚀 Iniciando scraping con guardado en BD...")
    print("=" * 70)

    # Cargar desde BD
    products = get_products()
    stores_db = get_stores(active_only=True)

    # Cargar config de sitios para scraping
    sites_config = load_sites_config()

    total_success = 0
    total_failures = 0

    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{len(products)}] 📱 {product['name']}")
        if product.get('category'):
            print(f"         Categoría: {product['category']}")

        for store_db in stores_db:
            # Buscar config del sitio
            site_config = next(
                (s for s in sites_config if s['sitio'] == store_db['name']),
                None
            )

            if not site_config:
                print(f"   ⚠️  Config no encontrada para {store_db['name']}")
                continue

            try:
                # Scrape (igual que main.py)
                result = scrape_price(
                    sitio_config=site_config,
                    product_name=product['name'],
                    product_category=product.get('category')
                )

                if result and result.get('price'):
                    # Guardar en BD
                    add_price_snapshot(
                        product_id=product['id'],
                        store_id=store_db['id'],
                        price=float(result['price']) if result['price'] else 0,
                        title=result.get('title', product['name']),
                        url=result.get('url'),
                        relevance_score=result.get('score', 0)
                    )

                    print(f"   ✅ {store_db['name']}: ${result['price']}")
                    total_success += 1
                else:
                    print(f"   ⚠️  {store_db['name']}: Sin resultados")
                    total_failures += 1

            except Exception as e:
                print(f"   ❌ {store_db['name']}: {str(e)}")
                total_failures += 1

            # Pequeño delay entre requests
            import time
            time.sleep(2)

    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print(f"✅ Exitosos: {total_success}")
    print(f"❌ Fallidos: {total_failures}")
    print(f"Total: {total_success + total_failures}")
    print()
    print("💡 Para ver los datos guardados: python view_db.py")
    print("=" * 70)

if __name__ == "__main__":
    scrape_all_and_save()
