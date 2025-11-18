"""
Job de scraping que actualiza precios y guarda en base de datos
Se puede ejecutar manualmente o mediante cron
"""
import json
import time
from datetime import datetime
from typing import Dict, Optional

from database import (
    get_products_to_update,
    get_stores,
    add_price_snapshot,
    get_store_by_name,
    get_stats
)
from generic_scrapers import scrape_price


def scrape_and_save(product: Dict, store: Dict) -> bool:
    """
    Scrape un producto en una tienda y guarda el resultado
    Returns True si fue exitoso, False si hubo error
    """
    try:
        # Preparar config de la tienda (está como JSON)
        store_config = store['config']

        # Scrape usando la lógica existente
        result = scrape_price(
            sitio_config=store_config,
            product_name=product['name'],
            product_category=product.get('category')
        )

        if not result:
            print(f"   ⚠️  Sin resultados para {product['name']} en {store['name']}")
            return False

        # Verificar que tenemos precio
        precio = result.get('precio')
        if not precio:
            print(f"   ⚠️  Sin precio para {product['name']} en {store['name']}")
            return False

        # Guardar en base de datos
        add_price_snapshot(
            product_id=product['id'],
            store_id=store['id'],
            price=float(precio),
            title=result.get('titulo', product['name']),
            url=result.get('url'),
            relevance_score=result.get('score', 0)
        )

        print(f"   ✅ {product['name']} en {store['name']}: ${precio:,.0f}")
        return True

    except Exception as e:
        print(f"   ❌ Error {product['name']} - {store['name']}: {str(e)}")
        return False


def run_batch_update(delay_between_requests: float = 2.0):
    """
    Ejecuta actualización batch de todos los productos que lo necesiten

    Args:
        delay_between_requests: Segundos de espera entre requests (evitar bloqueos)
    """
    print("🚀 Iniciando actualización batch de precios...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Obtener productos a actualizar
    products = get_products_to_update()
    if not products:
        print("✨ No hay productos para actualizar en este momento")
        return

    # Obtener tiendas activas
    stores = get_stores(active_only=True)
    if not stores:
        print("❌ No hay tiendas activas configuradas")
        return

    print(f"📦 Actualizando {len(products)} productos en {len(stores)} tiendas")
    print(f"⏱️  Delay entre requests: {delay_between_requests}s")
    print()

    # Contadores
    total_attempts = 0
    total_success = 0
    total_failures = 0

    # Scrape cada producto en cada tienda
    for i, product in enumerate(products, 1):
        print(f"[{i}/{len(products)}] 📱 {product['name']}")
        if product.get('category'):
            print(f"         Categoría: {product['category']}")

        for store in stores:
            total_attempts += 1

            success = scrape_and_save(product, store)

            if success:
                total_success += 1
            else:
                total_failures += 1

            # Delay para evitar bloqueos
            if delay_between_requests > 0:
                time.sleep(delay_between_requests)

        print()  # Línea en blanco entre productos

    # Resumen
    print("="*70)
    print("📊 RESUMEN DE ACTUALIZACIÓN")
    print("="*70)
    print(f"Total de intentos: {total_attempts}")
    print(f"✅ Exitosos: {total_success} ({total_success/total_attempts*100:.1f}%)")
    print(f"❌ Fallidos: {total_failures} ({total_failures/total_attempts*100:.1f}%)")
    print()

    # Estadísticas generales
    stats = get_stats()
    print("📈 ESTADÍSTICAS GENERALES")
    print("="*70)
    print(f"Total de productos: {stats['total_products']}")
    print(f"Total de tiendas: {stats['total_stores']}")
    print(f"Total de snapshots: {stats['total_snapshots']}")
    print(f"Último scrape: {stats['last_scrape']}")
    print("="*70)

    print(f"\n✨ Actualización completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def update_single_product(product_name: str, delay_between_requests: float = 2.0):
    """
    Actualiza un producto específico en todas las tiendas

    Args:
        product_name: Nombre del producto a actualizar
        delay_between_requests: Segundos de espera entre requests
    """
    from database import get_db

    print(f"🔍 Buscando producto: {product_name}")

    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE name LIKE ?",
            (f"%{product_name}%",)
        ).fetchone()

        if not row:
            print(f"❌ Producto no encontrado: {product_name}")
            return

        product = dict(row)

    print(f"✅ Producto encontrado: {product['name']} (ID: {product['id']})")
    print()

    # Obtener tiendas activas
    stores = get_stores(active_only=True)

    total_success = 0
    total_failures = 0

    for store in stores:
        success = scrape_and_save(product, store)

        if success:
            total_success += 1
        else:
            total_failures += 1

        if delay_between_requests > 0:
            time.sleep(delay_between_requests)

    print()
    print(f"✅ Exitosos: {total_success}")
    print(f"❌ Fallidos: {total_failures}")


if __name__ == "__main__":
    import sys

    # Si se pasa un argumento, actualizar solo ese producto
    if len(sys.argv) > 1:
        product_name = " ".join(sys.argv[1:])
        update_single_product(product_name)
    else:
        # Actualización batch completa
        run_batch_update(delay_between_requests=2.0)
