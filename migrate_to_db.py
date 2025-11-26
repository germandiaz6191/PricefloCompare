"""
Script de migración de configuraciones JSON a base de datos
Migra config_sitios.json y config_productos.json a la base de datos
Soporta SQLite (local) y PostgreSQL (producción)
"""
# IMPORTANTE: Cargar .env ANTES de importar database
# porque database.py lee DATABASE_URL al importarse
import json
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv no instalado, usar variables de sistema

# Ahora sí importar módulos que dependen de variables de entorno
from database import add_store, add_product, get_db

def migrate_stores():
    """Migra config_sitios.json a la tabla stores"""
    config_file = 'config_sitios.json'

    if not os.path.exists(config_file):
        print(f"⚠️  {config_file} no encontrado")
        return 0

    with open(config_file, 'r', encoding='utf-8') as f:
        stores = json.load(f)

    count = 0
    for store in stores:
        try:
            store_id = add_store(
                name=store['sitio'],
                url=store['url'],
                fetch_method=store['fetch_method'],
                config=store  # Guardar toda la config como JSON
            )
            print(f"✅ Tienda migrada: {store['sitio']} (ID: {store_id})")
            count += 1
        except Exception as e:
            print(f"❌ Error migrando tienda {store.get('sitio', 'desconocido')}: {e}")

    return count


def migrate_products():
    """Migra config_productos.json a la tabla products"""
    config_file = 'config_productos.json'

    if not os.path.exists(config_file):
        print(f"⚠️  {config_file} no encontrado")
        return 0

    with open(config_file, 'r', encoding='utf-8') as f:
        products = json.load(f)

    count = 0
    for product in products:
        try:
            # Determinar intervalo de actualización
            is_frequent = product.get('frecuente', False)
            update_interval = 6 if is_frequent else 12

            product_id = add_product(
                name=product['nombre'],
                category=product.get('categoria'),
                is_frequent=is_frequent,
                update_interval_hours=update_interval
            )
            print(f"✅ Producto migrado: {product['nombre']} (ID: {product_id})")
            count += 1
        except Exception as e:
            print(f"❌ Error migrando producto {product.get('nombre', 'desconocido')}: {e}")

    return count


def verify_migration():
    """Verifica que la migración fue exitosa"""
    with get_db() as conn:
        # Contar registros
        stores_count = conn.execute("SELECT COUNT(*) as count FROM stores").fetchone()['count']
        products_count = conn.execute("SELECT COUNT(*) as count FROM products").fetchone()['count']

        print("\n" + "="*50)
        print("📊 RESUMEN DE MIGRACIÓN")
        print("="*50)
        print(f"Tiendas en BD: {stores_count}")
        print(f"Productos en BD: {products_count}")

        # Mostrar tiendas
        print("\n🏪 Tiendas:")
        stores = conn.execute("SELECT name, fetch_method FROM stores ORDER BY name").fetchall()
        for store in stores:
            print(f"  - {store['name']} ({store['fetch_method']})")

        # Mostrar productos por categoría
        print("\n📦 Productos por categoría:")
        categories = conn.execute("""
            SELECT category, COUNT(*) as count
            FROM products
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """).fetchall()

        for cat in categories:
            print(f"  - {cat['category']}: {cat['count']} productos")

        # Productos sin categoría
        no_cat = conn.execute("""
            SELECT COUNT(*) as count FROM products WHERE category IS NULL
        """).fetchone()['count']
        if no_cat > 0:
            print(f"  - Sin categoría: {no_cat} productos")

        print("="*50)


def main():
    """Ejecuta la migración completa"""
    # Detectar qué base de datos se está usando
    db_type = "PostgreSQL" if os.getenv("DATABASE_URL", "").startswith(("postgresql://", "postgres://")) else "SQLite"
    print(f"🚀 Iniciando migración de JSON a {db_type}...")
    print()

    # Migrar tiendas
    print("📍 Paso 1: Migrando tiendas...")
    stores_migrated = migrate_stores()
    print(f"   → {stores_migrated} tiendas migradas\n")

    # Migrar productos
    print("📍 Paso 2: Migrando productos...")
    products_migrated = migrate_products()
    print(f"   → {products_migrated} productos migrados\n")

    # Verificar
    print("📍 Paso 3: Verificando migración...")
    verify_migration()

    print("\n✨ Migración completada exitosamente!")

    # Mensaje según la base de datos usada
    if db_type == "PostgreSQL":
        print(f"\n💡 Datos migrados a PostgreSQL (producción)")
        print("💡 Ahora puedes ejecutar: python add_test_data.py")
    else:
        print(f"\n💡 Base de datos creada en: data/prices.db")
        print("💡 Ahora puedes ejecutar: python add_test_data.py")


if __name__ == "__main__":
    main()
