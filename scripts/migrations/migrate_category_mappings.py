"""
Migración: Agregar tabla de mapeo de categorías
Permite definir cómo se mapea cada categoría de ePriceFlo a cada tienda
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from database import execute_query, is_postgres
import json

def migrate_category_mappings():
    """Crea tabla category_mappings y migra datos existentes"""

    print("="*80)
    print("📊 MIGRACIÓN: Tabla de Mapeo de Categorías")
    print("="*80)

    # 1. Crear tabla
    print("\n📍 Paso 1: Crear tabla category_mappings...")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS category_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_id INTEGER NOT NULL,
        category_name VARCHAR(100) NOT NULL,
        filter_level VARCHAR(20) NOT NULL,
        filter_value VARCHAR(100) NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        UNIQUE(store_id, category_name)
    );
    """ if not is_postgres() else """
    CREATE TABLE IF NOT EXISTS category_mappings (
        id SERIAL PRIMARY KEY,
        store_id INTEGER NOT NULL,
        category_name VARCHAR(100) NOT NULL,
        filter_level VARCHAR(20) NOT NULL,
        filter_value VARCHAR(100) NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        UNIQUE(store_id, category_name)
    );
    """

    execute_query(create_table_sql)
    print("   ✅ Tabla category_mappings creada")

    # 2. Migrar datos del JSON existente
    print("\n📍 Paso 2: Migrar datos de category_mapping.json...")

    mapping_file = os.path.join(project_root, "category_mapping.json")
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        mappings = data.get("mappings", {})

        # Obtener ID de Éxito
        result = execute_query("SELECT id FROM stores WHERE name = ?", ("Éxito",), fetch=True)
        if not result:
            print("   ⚠️ Tienda 'Éxito' no encontrada. Ejecuta migrate_to_db.py primero")
            return

        exito_id = result[0]['id']

        # Insertar mappings
        ph = "%s" if is_postgres() else "?"
        insert_sql = f"""
        INSERT OR IGNORE INTO category_mappings
        (store_id, category_name, filter_level, filter_value)
        VALUES ({ph}, {ph}, {ph}, {ph})
        """ if not is_postgres() else f"""
        INSERT INTO category_mappings
        (store_id, category_name, filter_level, filter_value)
        VALUES ({ph}, {ph}, {ph}, {ph})
        ON CONFLICT (store_id, category_name) DO UPDATE SET
            filter_level = EXCLUDED.filter_level,
            filter_value = EXCLUDED.filter_value
        """

        count = 0
        for category, mapping in mappings.items():
            level = mapping.get("level", "category-3")
            value = mapping.get("value", category.lower())

            execute_query(insert_sql, (exito_id, category, level, value))
            count += 1
            print(f"   ✅ {category} → {level}: {value}")

        print(f"\n   📊 Total migrado: {count} categorías")
    else:
        print("   ⚠️ category_mapping.json no encontrado")

    # 3. Mostrar resumen
    print("\n📍 Paso 3: Verificar migración...")

    result = execute_query("""
        SELECT cm.category_name, cm.filter_level, cm.filter_value, s.name as store_name
        FROM category_mappings cm
        JOIN stores s ON cm.store_id = s.id
        ORDER BY s.name, cm.category_name
    """, fetch=True)

    print(f"\n   Total de mappings en BD: {len(result) if result else 0}")

    if result:
        print("\n   Ejemplo de mappings:")
        for row in result[:5]:
            print(f"   - {row['store_name']}: {row['category_name']} → {row['filter_level']}: {row['filter_value']}")
        if len(result) > 5:
            print(f"   ... y {len(result) - 5} más")

    print("\n" + "="*80)
    print("✅ MIGRACIÓN COMPLETADA")
    print("="*80)
    print("\n💡 Ahora puedes agregar/editar categorías directamente en la BD:")
    print("   - Tabla: category_mappings")
    print("   - Campos: store_id, category_name, filter_level, filter_value")
    print("\n📝 Ejemplo SQL para agregar una categoría:")
    print("   INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value)")
    print("   VALUES (1, 'Deportes', 'category-3', 'deportes');")
    print("="*80)

if __name__ == "__main__":
    migrate_category_mappings()
