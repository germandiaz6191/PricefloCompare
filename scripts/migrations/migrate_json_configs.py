"""
Migra config_sitios.json y category_mapping.json a la base de datos.
Idempotente: se puede correr múltiples veces sin duplicar datos.

Uso:
    python scripts/migrations/migrate_json_configs.py

Antes de correr, ajustar DATABASE_URL en .env según donde quieras migrar:
- SQLite local: DATABASE_URL=data/prices.db (o no setearla)
- Supabase:     DATABASE_URL=postgresql://...
"""
import os
import sys
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from database import (
    get_db,
    add_store,
    update_store_country,
    add_category_mapping,
    IS_POSTGRES,
)
from scripts.migrations.migrate_countries import migrate_countries

CONFIG_SITIOS_PATH = os.path.join(project_root, "config_sitios.json")
CATEGORY_MAPPING_PATH = os.path.join(project_root, "category_mapping.json")

STORE_COLUMN_KEYS = {"sitio", "url", "fetch_method", "country_code", "currency"}


def _build_config_payload(site: dict) -> dict:
    """Quita los campos que viven como columnas y deja solo lo específico de scraping."""
    return {k: v for k, v in site.items() if k not in STORE_COLUMN_KEYS}


def migrate_sites():
    if not os.path.exists(CONFIG_SITIOS_PATH):
        print(f"⚠️  No existe {CONFIG_SITIOS_PATH}, salto migración de sitios.")
        return 0

    with open(CONFIG_SITIOS_PATH, "r", encoding="utf-8") as f:
        sites = json.load(f)

    migrated = 0
    for site in sites:
        name = site.get("sitio")
        url = site.get("url")
        fetch_method = site.get("fetch_method")
        country_code = site.get("country_code")
        currency = site.get("currency")

        if not (name and url and fetch_method):
            print(f"   ⚠️  Sitio incompleto, salto: {site}")
            continue

        config_payload = _build_config_payload(site)

        store_id = add_store(name, url, fetch_method, config_payload)

        if country_code and currency:
            update_store_country(store_id, country_code, currency)

        print(f"   ✅ {name} (id={store_id}, país={country_code}, método={fetch_method})")
        migrated += 1

    return migrated


def migrate_category_mappings():
    if not os.path.exists(CATEGORY_MAPPING_PATH):
        print(f"⚠️  No existe {CATEGORY_MAPPING_PATH}, salto mapeos.")
        return 0

    with open(CATEGORY_MAPPING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    mappings = data.get("mappings", {})
    if not mappings:
        print("   ℹ️  Archivo sin 'mappings', nada que hacer.")
        return 0

    target_store = "Éxito"
    migrated = 0
    for category, cfg in mappings.items():
        level = cfg.get("level", "category-3")
        value = cfg.get("value", category.lower())
        use_brand = cfg.get("use_brand", True)

        ok = add_category_mapping(target_store, category, level, value, use_brand)
        if ok:
            print(f"   ✅ {category} → {level}: {value}")
            migrated += 1
        else:
            print(f"   ⚠️  Tienda '{target_store}' no encontrada para {category}")

    return migrated


def main():
    print("=" * 70)
    print(f"📦 Migración JSON → BD ({'PostgreSQL' if IS_POSTGRES else 'SQLite'})")
    print("=" * 70)

    print("\n📍 Paso 1/3: Asegurar schema (tabla countries y columnas en stores)...")
    migrate_countries()

    print("\n📍 Paso 2/3: Migrar config_sitios.json → tabla 'stores'...")
    sites_count = migrate_sites()
    print(f"   📊 Total sitios migrados: {sites_count}")

    print("\n📍 Paso 3/3: Migrar category_mapping.json → tabla 'category_mappings'...")
    mappings_count = migrate_category_mappings()
    print(f"   📊 Total mapeos migrados: {mappings_count}")

    print("\n" + "=" * 70)
    print("✅ Migración completada.")
    print("=" * 70)
    print("\n💡 Siguiente paso: Verificar que el scraping siga funcionando:")
    print("   python scraper.py")
    print("\n🗑️  Si todo funciona, puedes borrar:")
    print("   - config_sitios.json")
    print("   - category_mapping.json")
    print("   - category_mapping_template.json")


if __name__ == "__main__":
    main()
