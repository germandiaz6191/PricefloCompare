#!/usr/bin/env python3
"""
Inserta mapeos de categoría descubiertos en DevTools
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from database import get_db, _param_placeholder

print("="*80)
print("📊 INSERTAR MAPEOS DE CATEGORÍA DESCUBIERTOS")
print("="*80)

# Obtener ID de Éxito
with get_db() as conn:
    cursor = conn.cursor()
    ph = _param_placeholder()

    cursor.execute(f"SELECT id FROM stores WHERE name = {ph}", ("Éxito",))
    result = cursor.fetchone()

    if not result:
        print("❌ Tienda 'Éxito' no encontrada. Ejecuta migrate_to_db.py primero")
        sys.exit(1)

    if isinstance(result, dict):
        exito_id = result['id']
    else:
        exito_id = result[0]

# Mapeos descubiertos por el usuario
mappings = [
    # Audio: category-2:audio + marca
    {
        "category_name": "Audio",
        "filter_level": "category-2",
        "filter_value": "audio",
        "use_brand": 1,
        "note": "AirPods, JBL"
    },
    # Celulares: category-2:celulares + marca
    {
        "category_name": "Celulares",
        "filter_level": "category-2",
        "filter_value": "celulares",
        "use_brand": 1,
        "note": "iPhone, Samsung, Motorola"
    },
    # Smartwatches: category-2:reloj-inteligente + marca
    {
        "category_name": "Smartwatches",
        "filter_level": "category-2",
        "filter_value": "reloj-inteligente",
        "use_brand": 1,
        "note": "Apple Watch"
    },
    # Electrodomésticos (Air Fryer): Solo marca, SIN categoría
    # Para esto usamos filter_level vacío
    {
        "category_name": "Electrodomésticos",
        "filter_level": "",
        "filter_value": "",
        "use_brand": 1,
        "note": "Air Fryer - solo usa marca"
    },
    # Nota: Aspiradora Robot usa 3 niveles - necesita handling especial
]

print(f"\n📝 Insertando {len(mappings)} mapeos...\n")

with get_db() as conn:
    cursor = conn.cursor()
    ph = _param_placeholder()

    # Para SQLite usamos INSERT OR REPLACE
    # Para PostgreSQL usamos ON CONFLICT
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

    for mapping in mappings:
        cursor.execute(insert_sql, (
            exito_id,
            mapping["category_name"],
            mapping["filter_level"],
            mapping["filter_value"],
            mapping["use_brand"]
        ))

        status = "✅"
        if mapping["filter_level"] == "":
            status = "⚠️ "

        print(f"{status} {mapping['category_name']:20s} → {mapping['note']}")
        if mapping["filter_level"]:
            print(f"   Filtros: {mapping['filter_level']}:{mapping['filter_value']} + brand:{mapping['use_brand']}")
        else:
            print(f"   Filtros: solo brand (sin categoría)")
        print()

    conn.commit()

print("="*80)
print("✅ MAPEOS INSERTADOS")
print("="*80)
print("\n💡 Estos mapeos ahora se usarán automáticamente en el scraper")
print("   - La marca se detecta automáticamente del nombre")
print("   - La categoría se lee de esta tabla")
print("   - use_brand controla si se agrega filtro de marca")
print("="*80)
