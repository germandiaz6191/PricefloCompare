"""
Script de migración para agregar soporte multi-país
Agrega tabla countries y modifica stores para soportar múltiples países
"""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from database import get_db, IS_POSTGRES

def migrate_countries():
    """Migración para agregar soporte de países"""

    print("🌍 Iniciando migración de países...")

    with get_db() as conn:
        cursor = conn.cursor()

        try:
            # 1. Crear tabla countries
            print("\n📋 Creando tabla 'countries'...")
            if IS_POSTGRES:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS countries (
                        code VARCHAR(2) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        currency VARCHAR(3) NOT NULL,
                        locale VARCHAR(10) NOT NULL,
                        flag_emoji VARCHAR(10),
                        active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS countries (
                        code TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        currency TEXT NOT NULL,
                        locale TEXT NOT NULL,
                        flag_emoji TEXT,
                        active INTEGER DEFAULT 1,
                        created_at TEXT DEFAULT (datetime('now'))
                    );
                """)
            print("   ✅ Tabla 'countries' creada")

            # 2. Insertar países iniciales (empezando con Colombia)
            print("\n🇨🇴 Insertando países iniciales...")
            ph = '%s' if IS_POSTGRES else '?'

            countries = [
                ('CO', 'Colombia', 'COP', 'es-CO', '🇨🇴', True),
                ('MX', 'México', 'MXN', 'es-MX', '🇲🇽', False),  # Desactivado por ahora
                ('CL', 'Chile', 'CLP', 'es-CL', '🇨🇱', False),
                ('AR', 'Argentina', 'ARS', 'es-AR', '🇦🇷', False),
                ('PE', 'Perú', 'PEN', 'es-PE', '🇵🇪', False),
            ]

            for country in countries:
                try:
                    if IS_POSTGRES:
                        cursor.execute(f"""
                            INSERT INTO countries (code, name, currency, locale, flag_emoji, active)
                            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                            ON CONFLICT (code) DO NOTHING
                        """, country)
                    else:
                        cursor.execute(f"""
                            INSERT OR IGNORE INTO countries (code, name, currency, locale, flag_emoji, active)
                            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                        """, country)
                    print(f"   ✅ {country[1]} ({country[0]})")
                except Exception as e:
                    print(f"   ⚠️  Error insertando {country[1]}: {e}")

            # 3. Verificar si stores ya tiene las columnas
            print("\n🏪 Verificando estructura de tabla 'stores'...")

            cursor.execute("SELECT * FROM stores LIMIT 0")
            existing_columns = [desc[0] for desc in cursor.description]

            has_country_code = 'country_code' in existing_columns
            has_currency = 'currency' in existing_columns

            # 4. Agregar columnas a stores si no existen
            if not has_country_code:
                print("   Agregando columna 'country_code' a stores...")
                if IS_POSTGRES:
                    cursor.execute("ALTER TABLE stores ADD COLUMN country_code VARCHAR(2)")
                else:
                    cursor.execute("ALTER TABLE stores ADD COLUMN country_code TEXT")
                print("   ✅ Columna 'country_code' agregada")
            else:
                print("   ℹ️  Columna 'country_code' ya existe")

            if not has_currency:
                print("   Agregando columna 'currency' a stores...")
                if IS_POSTGRES:
                    cursor.execute("ALTER TABLE stores ADD COLUMN currency VARCHAR(3)")
                else:
                    cursor.execute("ALTER TABLE stores ADD COLUMN currency TEXT")
                print("   ✅ Columna 'currency' agregada")
            else:
                print("   ℹ️  Columna 'currency' ya existe")

            # 5. Actualizar stores existentes a Colombia (solo si no tienen país asignado)
            print("\n🔄 Actualizando tiendas existentes...")
            cursor.execute(f"""
                UPDATE stores
                SET country_code = 'CO', currency = 'COP'
                WHERE country_code IS NULL OR country_code = ''
            """)

            if IS_POSTGRES:
                cursor.execute("SELECT COUNT(*) FROM stores WHERE country_code = 'CO'")
                count = cursor.fetchone()[0]
            else:
                cursor.execute("SELECT COUNT(*) FROM stores WHERE country_code = 'CO'")
                count = cursor.fetchone()[0]

            print(f"   ✅ {count} tienda(s) configurada(s) para Colombia")

            # 6. Crear índice para mejorar performance
            print("\n📊 Creando índices...")
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_stores_country ON stores(country_code)")
                print("   ✅ Índice 'idx_stores_country' creado")
            except Exception as e:
                print(f"   ℹ️  Índice ya existe o error: {e}")

            # 7. Agregar foreign key constraint (solo PostgreSQL)
            if IS_POSTGRES:
                print("\n🔗 Agregando constraint de foreign key...")
                try:
                    cursor.execute("""
                        ALTER TABLE stores
                        ADD CONSTRAINT fk_stores_country
                        FOREIGN KEY (country_code)
                        REFERENCES countries(code)
                    """)
                    print("   ✅ Foreign key constraint agregado")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate" in str(e):
                        print("   ℹ️  Constraint ya existe")
                    else:
                        print(f"   ⚠️  Error agregando constraint: {e}")

            conn.commit()
            print("\n✅ Migración completada exitosamente!")

            # Mostrar resumen
            print("\n" + "="*50)
            print("📊 RESUMEN DE MIGRACIÓN")
            print("="*50)

            cursor.execute("SELECT code, name, active FROM countries ORDER BY active DESC, name")
            if IS_POSTGRES:
                countries_data = cursor.fetchall()
                print("\n🌍 Países disponibles:")
                for code, name, active in countries_data:
                    status = "✅ Activo" if active else "⏸️  Inactivo"
                    print(f"   {code} - {name}: {status}")
            else:
                countries_data = cursor.fetchall()
                print("\n🌍 Países disponibles:")
                for row in countries_data:
                    code, name, active = row[0], row[1], row[2]
                    status = "✅ Activo" if active else "⏸️  Inactivo"
                    print(f"   {code} - {name}: {status}")

            cursor.execute("SELECT name, country_code FROM stores WHERE country_code IS NOT NULL")
            if IS_POSTGRES:
                stores_data = cursor.fetchall()
                print("\n🏪 Tiendas configuradas:")
                for name, country in stores_data:
                    print(f"   {name} → {country}")
            else:
                stores_data = cursor.fetchall()
                print("\n🏪 Tiendas configuradas:")
                for row in stores_data:
                    name, country = row[0], row[1]
                    print(f"   {name} → {country}")

            print("\n" + "="*50)

        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error durante la migración: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    migrate_countries()
