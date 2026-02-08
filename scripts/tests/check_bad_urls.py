"""
Script para identificar productos con URLs incorrectas en la base de datos
"""
import os
import sys

# Agregar directorio raíz al path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# Cargar .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from database import get_db_connection

def check_bad_urls():
    """Identifica snapshots con URLs problemáticas"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar URLs que contengan 'graphql' o 'api' (probablemente incorrectas)
    query = """
        SELECT DISTINCT ON (ps.product_id, ps.store_id)
            p.name as product_name,
            s.name as store_name,
            ps.url,
            ps.scraped_at,
            ps.title
        FROM price_snapshots ps
        INNER JOIN products p ON ps.product_id = p.id
        INNER JOIN stores s ON ps.store_id = s.id
        WHERE s.name = 'Éxito'
        AND (ps.url LIKE '%graphql%' OR ps.url LIKE '%/api/%' OR ps.url IS NULL OR ps.url = '')
        ORDER BY ps.product_id, ps.store_id, ps.scraped_at DESC
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print("=" * 80)
    print("🔍 PRODUCTOS CON URLs INCORRECTAS EN ÉXITO")
    print("=" * 80)
    print()

    if not results:
        print("✅ No se encontraron productos con URLs incorrectas")
        return

    print(f"❌ Se encontraron {len(results)} productos con URLs problemáticas:\n")

    for row in results:
        product_name, store_name, url, scraped_at, title = row
        print(f"📦 Producto: {product_name}")
        print(f"   Título scrapeado: {title}")
        print(f"   🏪 Tienda: {store_name}")
        print(f"   🔗 URL problemática: {url[:100] if url else '(vacía)'}...")
        print(f"   📅 Fecha: {scraped_at}")
        print()

    print("=" * 80)
    print("💡 SOLUCIÓN:")
    print("=" * 80)
    print()
    print("Estos productos necesitan ser re-scrapeados. Opciones:")
    print()
    print("1. Re-scrapear TODO:")
    print("   DATABASE_URL='postgresql://...' python scripts/utils/add_test_data.py")
    print()
    print("2. Verificar si el producto existe en Éxito con ese nombre")
    print()
    print("3. Actualizar el nombre del producto si es diferente en Éxito")
    print()

    conn.close()

if __name__ == "__main__":
    check_bad_urls()
