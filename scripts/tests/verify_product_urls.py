#!/usr/bin/env python3
"""
Script para probar la construcción de URLs de productos de Éxito
Especialmente para productos sin linkText
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from database import get_db

print("="*80)
print("🔗 VERIFICACIÓN DE URLs DE PRODUCTOS")
print("="*80)

# Ver últimos 10 productos scrapeados de Éxito
with get_db() as conn:
    cursor = conn.cursor()

    query = """
        SELECT
            p.name as product_name,
            ps.title as scraped_title,
            ps.price,
            ps.url,
            s.name as store_name,
            ps.scraped_at
        FROM price_snapshots ps
        JOIN products p ON ps.product_id = p.id
        JOIN stores s ON ps.store_id = s.id
        WHERE s.name = 'Éxito'
        ORDER BY ps.scraped_at DESC
        LIMIT 10
    """

    cursor.execute(query)
    results = cursor.fetchall()

    if not results:
        print("\n⚠️ No hay productos scrapeados de Éxito en la BD")
        print("💡 Ejecuta: python scripts/utils/add_test_data.py")
        sys.exit(0)

    print(f"\n📊 Últimos {len(results)} productos scrapeados de Éxito:\n")

    for i, row in enumerate(results, 1):
        if isinstance(row, dict):
            product = row['product_name']
            title = row['scraped_title']
            price = row['price']
            url = row['url']
        else:
            product, title, price, url, store, scraped = row

        print(f"{i}. {product}")
        print(f"   Título: {title}")
        print(f"   Precio: ${price:,.0f}")

        # Verificar URL
        if not url:
            print(f"   URL: ❌ Sin URL")
        elif 'api/graphql' in url:
            print(f"   URL: ❌ URL de API (incorrecto)")
            print(f"        {url[:100]}...")
        elif url.endswith('/p'):
            print(f"   URL: ✅ URL de producto válida")
            print(f"        {url}")
        else:
            print(f"   URL: ⚠️ URL desconocida")
            print(f"        {url}")

        print()

print("="*80)
print("💡 URLs correctas de Éxito deben terminar en '/p'")
print("   Ejemplo: https://www.exito.com/iphone-16-128-gb-negro-104670578-mp/p")
print("="*80)
