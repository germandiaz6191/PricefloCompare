#!/usr/bin/env python3
"""
Script para limpiar snapshots viejos de productos específicos y re-scrapear
Útil cuando las URLs están incorrectas y necesitas actualizarlas
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from database import get_db, add_price_snapshot, _param_placeholder
from scrapers.generic_scrapers import load_sites_config, scrape_price
import json

print("="*80)
print("🔄 LIMPIAR Y RE-SCRAPEAR PRODUCTOS ESPECÍFICOS")
print("="*80)

# Productos con URLs incorrectas que necesitan re-scraping
problem_products = [
    "AirPods 3",
    "AirPods Pro",
    # Agrega más productos aquí si es necesario
]

database_url = os.getenv("DATABASE_URL", "")
if database_url.startswith(("postgresql://", "postgres://")):
    print("🗄️  Conectado a: Supabase (Producción)")
else:
    print("🗄️  Conectado a: SQLite (Local)")

print(f"📦 Productos a re-scrapear: {len(problem_products)}")
print()

# Confirmar
response = input("¿Continuar con la limpieza y re-scraping? (s/n): ")
if response.lower() != 's':
    print("Cancelado.")
    sys.exit(0)

with get_db() as conn:
    cursor = conn.cursor()
    ph = _param_placeholder()

    for product_name in problem_products:
        print(f"\n{'='*80}")
        print(f"📱 Procesando: {product_name}")
        print(f"{'='*80}")

        # 1. Buscar producto en BD
        cursor.execute(f"SELECT id, name, category FROM products WHERE name = {ph}", (product_name,))
        product_row = cursor.fetchone()

        if not product_row:
            print(f"⚠️  Producto '{product_name}' no encontrado en BD")
            continue

        if isinstance(product_row, dict):
            product_id = product_row['id']
            category = product_row.get('category')
        else:
            product_id = product_row[0]
            product_name = product_row[1]
            category = product_row[2] if len(product_row) > 2 else None

        print(f"✅ Producto encontrado (ID: {product_id}, Categoría: {category})")

        # 2. Eliminar snapshots viejos de Éxito para este producto
        cursor.execute(f"""
            DELETE FROM price_snapshots
            WHERE product_id = {ph}
            AND store_id = (SELECT id FROM stores WHERE name = {ph})
        """, (product_id, "Éxito"))

        deleted = cursor.rowcount
        conn.commit()
        print(f"🗑️  Eliminados {deleted} snapshot(s) viejos de Éxito")

        # 3. Re-scrapear
        print(f"🔍 Re-scrapeando...")

        sitios_config = load_sites_config()
        exito_config = next((s for s in sitios_config if s['sitio'] == 'Éxito'), None)

        if not exito_config:
            print("❌ Configuración de Éxito no encontrada")
            continue

        try:
            result = scrape_price(exito_config, product_name, category)

            if result and result.get('price'):
                # Obtener store_id de Éxito
                cursor.execute(f"SELECT id FROM stores WHERE name = {ph}", ("Éxito",))
                store_row = cursor.fetchone()
                store_id = store_row['id'] if isinstance(store_row, dict) else store_row[0]

                # Guardar nuevo snapshot
                add_price_snapshot(
                    product_id=product_id,
                    store_id=store_id,
                    price=float(result['price']),
                    title=result.get('title', product_name),
                    url=result.get('url'),
                    relevance_score=result.get('score', 0)
                )

                print(f"✅ Precio: ${result['price']:,}")
                print(f"📝 Título: {result['title']}")

                url = result.get('url')
                if url:
                    if 'api/graphql' in url:
                        print(f"⚠️  URL: API URL (todavía incorrecta)")
                        print(f"   {url[:100]}...")
                    elif url.endswith('/p'):
                        print(f"✅ URL: Producto URL (correcta)")
                        print(f"   {url}")
                    else:
                        print(f"❓ URL: {url}")
                else:
                    print(f"⚠️  Sin URL")
            else:
                print(f"❌ No se encontró el producto en Éxito")

        except Exception as e:
            print(f"❌ Error: {e}")

print(f"\n{'='*80}")
print("✅ PROCESO COMPLETADO")
print(f"{'='*80}")
print("\n💡 Verifica los resultados:")
print("   python scripts/tests/verify_product_urls.py")
print(f"{'='*80}")
