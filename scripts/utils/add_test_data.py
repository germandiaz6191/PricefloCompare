"""
Script para agregar productos y scrapear precios en tiempo real
Combina creación de productos + scraping en una sola ejecución
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

# Configurar UTF-8 para compatibilidad con emojis en Windows
# Debe ir ANTES de cualquier import que use print con emojis
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Obtener directorio raíz del proyecto (2 niveles arriba de este script)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# Cargar .env ANTES de importar database
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv no instalado, usar variables de sistema

# Ahora sí importar módulos que dependen de variables de entorno
from database import add_price_snapshot, get_products, get_stores
from scrapers.generic_scrapers import load_sites_config, scrape_price
from datetime import datetime

def scrape_and_save():
    """
    Obtiene productos de la BD y scrapea precios reales de todas las tiendas.
    Mucho más eficiente que correr add_test_data.py y scraper.py por separado.
    """
    products = get_products()
    stores = get_stores()

    if not products or not stores:
        print("❌ Primero ejecuta: python migrate_to_db.py")
        return

    # Verificar que el scraping esté habilitado o estemos en local
    enable_scraping = os.getenv("ENABLE_SCRAPING", "false").lower() == "true"
    is_local = not os.getenv("DATABASE_URL", "").startswith(("postgresql://", "postgres://"))

    if not enable_scraping and not is_local:
        print("⚠️  ENABLE_SCRAPING está desactivado en producción")
        print("💡 Si quieres scrapear desde local hacia producción, asegúrate de:")
        print("   1. Tener DATABASE_URL configurado con PostgreSQL de producción")
        print("   2. Ejecutar este script localmente")
        return

    print("🔍 Iniciando scraping de precios reales...")
    print(f"📦 Productos encontrados: {len(products)}")
    print(f"🏪 Tiendas encontradas: {len(stores)}")
    print("")

    # Cargar configuración de sitios
    try:
        sitios_config = load_sites_config()
    except Exception as e:
        print(f"❌ Error cargando config de sitios: {e}")
        return

    # Mapeo de nombres de tiendas a IDs
    store_name_to_id = {}
    for store in stores:
        # Normalizar nombre (Éxito → exito, Falabella → falabella)
        normalized = store['name'].lower().replace('é', 'e').strip()
        store_name_to_id[normalized] = store['id']
        # También guardar el nombre original
        store_name_to_id[store['name']] = store['id']

    total_saved = 0
    total_attempts = 0

    # Para cada producto, scrapear en todas las tiendas
    for product in products:
        product_name = product['name']
        product_category = product.get('category')
        product_id = product['id']

        print(f"\n{'='*60}")
        print(f"📱 Producto: {product_name}")
        print(f"   Categoría: {product_category or 'Sin categoría'}")
        print(f"{'='*60}")

        # Scrapear en cada sitio configurado
        for sitio_cfg in sitios_config:
            total_attempts += 1
            sitio_name = sitio_cfg['sitio']

            # Buscar el store_id correspondiente (normalizar para buscar)
            sitio_normalized = sitio_name.lower().replace('é', 'e').strip()
            store_id = store_name_to_id.get(sitio_normalized)
            if not store_id:
                print(f"⚠️  {sitio_name}: Tienda no encontrada en BD (saltando)")
                continue

            print(f"   🔍 Scrapeando en {sitio_name}...", end=" ")

            try:
                # Llamar al scraper
                result = scrape_price(sitio_cfg, product_name, product_category)

                if result and result.get('price') is not None:
                    title = result.get('title', product_name)
                    price = result['price']  # Ya es un integer
                    url = result.get('url', '')
                    score = result.get('score', 0)

                    # Detectar si la URL es problemática (URL del API en lugar del producto)
                    url_is_bad = url and ('graphql' in url.lower() or '/api/' in url.lower())
                    url_status = "⚠️  URL INCORRECTA (API GraphQL)" if url_is_bad else "✅ URL OK"

                    # Guardar en BD
                    add_price_snapshot(
                        product_id=product_id,
                        store_id=store_id,
                        price=price,
                        title=title,
                        url=url,
                        relevance_score=95
                    )

                    total_saved += 1
                    print(f"✅ ${price:,}  (score: {score}/100)")
                    print(f"      📝 Título: {title}")
                    print(f"      🔗 URL ({url_status}):")
                    print(f"         {url}")
                    if not url:
                        print(f"      ⚠️  URL vacía - el botón 'Ver en tienda' no funcionará")
                else:
                    print(f"❌ No encontrado")
                    if result:
                        print(f"      Score obtenido: {result.get('score', 0)}/100 (mínimo requerido: 60)")

            except Exception as e:
                print(f"❌ Error: {str(e)[:100]}")

    # Resumen final
    print(f"\n{'='*60}")
    print(f"✨ Scraping completado")
    print(f"{'='*60}")
    print(f"📊 Intentos totales: {total_attempts}")
    print(f"✅ Precios guardados: {total_saved}")
    print(f"❌ No encontrados: {total_attempts - total_saved}")
    print(f"💡 Tasa de éxito: {(total_saved/total_attempts*100):.1f}%" if total_attempts > 0 else "0%")
    print("")
    print("💡 Ahora prueba:")
    print("   http://localhost:8000/stats")
    print("   O ejecuta: python view_db.py")

if __name__ == "__main__":
    scrape_and_save()
