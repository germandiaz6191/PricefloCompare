"""
Migración: Agregar campos de afiliados a tabla stores

Ejecutar una sola vez para agregar los nuevos campos a BD existente.
"""
import sqlite3
import os

DATABASE_URL = "data/prices.db"

def migrate():
    """Agrega columnas de afiliados a stores si no existen"""

    if not os.path.exists(DATABASE_URL):
        print("❌ Base de datos no existe aún")
        print("💡 Ejecuta primero: python -c 'from database import init_db; init_db()'")
        return

    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Verificar si las columnas ya existen
    cursor.execute("PRAGMA table_info(stores)")
    columns = [col[1] for col in cursor.fetchall()]

    migrations_needed = []

    if 'affiliate_enabled' not in columns:
        migrations_needed.append(
            "ALTER TABLE stores ADD COLUMN affiliate_enabled INTEGER DEFAULT 0"
        )

    if 'affiliate_code' not in columns:
        migrations_needed.append(
            "ALTER TABLE stores ADD COLUMN affiliate_code TEXT"
        )

    if 'affiliate_url_pattern' not in columns:
        migrations_needed.append(
            "ALTER TABLE stores ADD COLUMN affiliate_url_pattern TEXT"
        )

    if not migrations_needed:
        print("✅ Las columnas de afiliados ya existen. No se necesita migración.")
        conn.close()
        return

    # Ejecutar migraciones
    print(f"🔄 Ejecutando {len(migrations_needed)} migraciones...")

    for sql in migrations_needed:
        print(f"   - {sql}")
        cursor.execute(sql)

    conn.commit()
    conn.close()

    print("✅ Migración completada exitosamente")
    print("\nAhora puedes:")
    print("1. Agregar Amazon con: python add_amazon_store.py")
    print("2. Configurar afiliados desde la BD")

if __name__ == "__main__":
    migrate()
