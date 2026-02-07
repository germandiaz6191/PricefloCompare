#!/usr/bin/env python3
"""
Migra los mapeos de categoría a la base de datos de producción (Supabase)
Ejecutar con DATABASE_URL configurado
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# Cargar .env para obtener DATABASE_URL
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from database import get_db, _param_placeholder

def migrate_category_mappings():
    """
    Inserta los 4 mapeos de categoría descubiertos a la BD de producción
    """
    database_url = os.getenv("DATABASE_URL", "")

    if not database_url.startswith(("postgresql://", "postgres://")):
        print("⚠️  DATABASE_URL no está configurado o no es PostgreSQL")
        print("💡 Este script está diseñado para migrar a Supabase (producción)")
        print()
        response = input("¿Continuar de todas formas en SQLite local? (s/n): ")
        if response.lower() != 's':
            print("Cancelado.")
            return

    print("="*80)
    print("📊 MIGRAR MAPEOS DE CATEGORÍA A PRODUCCIÓN")
    print("="*80)
    print(f"🗄️  Base de datos: {'Supabase (PostgreSQL)' if 'postgres' in database_url else 'SQLite local'}")
    print()

    # Mapeos a insertar
    mappings = [
        {
            "category_name": "Audio",
            "filter_level": "category-2",
            "filter_value": "audio",
            "use_brand": 1,
            "note": "AirPods, JBL, Bose"
        },
        {
            "category_name": "Celulares",
            "filter_level": "category-2",
            "filter_value": "celulares",
            "use_brand": 1,
            "note": "iPhone, Samsung, Motorola"
        },
        {
            "category_name": "Smartwatches",
            "filter_level": "category-2",
            "filter_value": "reloj-inteligente",
            "use_brand": 1,
            "note": "Apple Watch, Amazfit, Garmin"
        },
        {
            "category_name": "Electrodomésticos",
            "filter_level": "category-2",
            "filter_value": "electrodomesticos-hogar",
            "use_brand": 1,
            "note": "Air Fryer, Aspiradora, Lavadora"
        }
    ]

    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

        # Obtener ID de Éxito
        cursor.execute(f"SELECT id FROM stores WHERE name = {ph}", ("Éxito",))
        result = cursor.fetchone()

        if not result:
            print("❌ Tienda 'Éxito' no encontrada en la base de datos")
            print("💡 Asegúrate de haber ejecutado: python scripts/migrations/migrate_to_db.py")
            return

        exito_id = result['id'] if isinstance(result, dict) else result[0]
        print(f"✅ Tienda 'Éxito' encontrada (ID: {exito_id})")
        print()

        # Verificar si tabla existe
        try:
            cursor.execute("SELECT COUNT(*) FROM category_mappings")
            existing_count = cursor.fetchone()
            count = existing_count[0] if isinstance(existing_count, tuple) else existing_count['COUNT(*)']
            print(f"📊 Mapeos existentes en tabla: {count}")
        except Exception as e:
            print(f"❌ Error verificando tabla category_mappings: {e}")
            print("💡 Asegúrate de que Railway haya deployado el código más reciente")
            return

        print()
        print(f"📝 Insertando {len(mappings)} mapeos...")
        print()

        # SQL para insertar
        if ph == "%s":  # PostgreSQL
            insert_sql = f"""
            INSERT INTO category_mappings
            (store_id, category_name, filter_level, filter_value, use_brand)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            ON CONFLICT (store_id, category_name)
            DO UPDATE SET
                filter_level = EXCLUDED.filter_level,
                filter_value = EXCLUDED.filter_value,
                use_brand = EXCLUDED.use_brand
            """
        else:  # SQLite
            insert_sql = f"""
            INSERT OR REPLACE INTO category_mappings
            (store_id, category_name, filter_level, filter_value, use_brand)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """

        inserted = 0
        for mapping in mappings:
            try:
                cursor.execute(insert_sql, (
                    exito_id,
                    mapping["category_name"],
                    mapping["filter_level"],
                    mapping["filter_value"],
                    mapping["use_brand"]
                ))

                print(f"✅ {mapping['category_name']:20s} → {mapping['filter_level']}:{mapping['filter_value']}")
                print(f"   Productos: {mapping['note']}")
                print()
                inserted += 1
            except Exception as e:
                print(f"❌ Error insertando {mapping['category_name']}: {e}")

        conn.commit()

    print("="*80)
    print(f"✅ MIGRACIÓN COMPLETADA - {inserted}/{len(mappings)} mapeos insertados")
    print("="*80)
    print()
    print("💡 Próximos pasos:")
    print("   1. Ejecutar: python scripts/utils/add_test_data.py")
    print("      (con DATABASE_URL configurado para probar en producción)")
    print()
    print("   2. Verificar en epriceflo.com que los productos tengan precios")
    print("="*80)

if __name__ == "__main__":
    migrate_category_mappings()
