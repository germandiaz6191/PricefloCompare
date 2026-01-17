#!/usr/bin/env python3
"""
Importa mapeo de categorías desde CSV a la base de datos
"""
# IMPORTANTE: Agregar directorio raíz al path para imports
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from database import execute_query, is_postgres
import csv

def import_mappings(csv_file="categorias_mapeo.csv"):
    """Importa mapeos desde CSV a la base de datos"""

    print("="*80)
    print("📥 IMPORTANDO MAPEO DE CATEGORÍAS DESDE CSV")
    print("="*80)

    if not os.path.exists(csv_file):
        print(f"❌ Archivo no encontrado: {csv_file}")
        print("\n💡 Primero ejecuta: python scripts/utils/generate_category_template.py")
        return

    # Obtener ID de Éxito
    result = execute_query("SELECT id FROM stores WHERE name = ?", ("Éxito",), fetch=True)
    if not result:
        print("❌ Tienda 'Éxito' no encontrada en BD")
        print("💡 Ejecuta: python scripts/migrations/migrate_to_db.py")
        return

    exito_id = result[0]['id']

    # Leer CSV
    mappings = []
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category_name = row.get('Categoría Actual', '').strip()
            filter_level = row.get('Filtro Nivel (Éxito)', '').strip()
            filter_value = row.get('Filtro Valor (Éxito)', '').strip()
            status = row.get('Notas/Estado', '').strip()

            # Solo importar si tiene valor
            if category_name and filter_level and filter_value:
                mappings.append({
                    'category': category_name,
                    'level': filter_level,
                    'value': filter_value,
                    'status': status
                })

    if not mappings:
        print("❌ No se encontraron categorías para importar")
        print("💡 Asegúrate de haber llenado las columnas 'Filtro Nivel' y 'Filtro Valor'")
        return

    print(f"\n📦 Categorías a importar: {len(mappings)}")

    # Insertar en BD
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

    imported = 0
    for mapping in mappings:
        execute_query(
            insert_sql,
            (exito_id, mapping['category'], mapping['level'], mapping['value'])
        )
        status_emoji = mapping['status'][:2] if mapping['status'] else '  '
        print(f"   {status_emoji} {mapping['category']} → {mapping['level']}: {mapping['value']}")
        imported += 1

    print(f"\n✅ Importadas {imported} categorías")

    # Verificar
    print("\n📊 Verificando en BD...")
    result = execute_query("""
        SELECT category_name, filter_level, filter_value
        FROM category_mappings
        WHERE store_id = ?
        ORDER BY category_name
    """, (exito_id,), fetch=True)

    print(f"   Total en BD: {len(result) if result else 0} categorías")

    print("\n" + "="*80)
    print("✅ IMPORTACIÓN COMPLETADA")
    print("="*80)
    print("\n🚀 Próximo paso:")
    print("   python scripts/utils/add_test_data.py")
    print("\n   El scraper ahora usará las categorías importadas.")
    print("="*80)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Importar mapeo de categorías desde CSV")
    parser.add_argument("--file", default="categorias_mapeo.csv", help="Archivo CSV a importar")

    args = parser.parse_args()

    import_mappings(args.file)
