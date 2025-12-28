"""
Test específico para scrapear Air Fryer Oster y Kalley
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

# Obtener directorio raíz del proyecto (2 niveles arriba: scripts/X/ -> scripts/ -> raíz)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
from database import add_price_snapshot, get_stores
from scrapers.generic_scrapers import load_sites_config, scrape_price

# Productos específicos a probar
test_products = [
    {"id": 40, "name": "Air Fryer Oster", "category": "Electrodomésticos"},
    {"id": 41, "name": "Air Fryer Kalley", "category": "Electrodomésticos"}
]

stores = get_stores()
sitios_config = load_sites_config()

# Mapeo de tiendas
store_name_to_id = {}
for store in stores:
    normalized = store['name'].lower().replace('é', 'e').strip()
    store_name_to_id[normalized] = store['id']
    store_name_to_id[store['name']] = store['id']

print("=" * 80)
print("🔍 TEST DE SCRAPING: AIR FRYER OSTER Y KALLEY")
print("=" * 80)

for product in test_products:
    product_name = product['name']
    product_category = product.get('category')
    product_id = product['id']

    print(f"\n{'='*80}")
    print(f"📱 Producto: {product_name}")
    print(f"   Categoría: {product_category}")
    print(f"{'='*80}")

    for sitio_cfg in sitios_config:
        sitio_name = sitio_cfg['sitio']
        sitio_normalized = sitio_name.lower().replace('é', 'e').strip()
        store_id = store_name_to_id.get(sitio_normalized)

        if not store_id:
            print(f"⚠️  {sitio_name}: Tienda no encontrada")
            continue

        print(f"\n   🔍 Scrapeando en {sitio_name}...")

        try:
            result = scrape_price(sitio_cfg, product_name, product_category)

            if result and result.get('price') is not None:
                title = result.get('title', product_name)
                price = result['price']
                url = result.get('url', '')

                add_price_snapshot(
                    product_id=product_id,
                    store_id=store_id,
                    price=price,
                    title=title,
                    url=url,
                    relevance_score=95
                )

                print(f"   ✅ ENCONTRADO: ${price:,} COP")
                print(f"      📝 Título: {title}")
                print(f"      🔗 URL: {url[:60]}...")
            else:
                print(f"   ❌ No encontrado")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:80]}")

print(f"\n{'='*80}")
print("✨ Test completado")
print("='*80}")
