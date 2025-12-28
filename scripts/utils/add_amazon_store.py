"""
Script para agregar Amazon como tienda al comparador

Amazon estará DESACTIVADA por defecto.
Actívala cuando:
1. Te registres en Amazon Associates
2. Obtengas tu código de afiliado
3. Actualices la BD con tu código
"""
from database import get_db
import json

def add_amazon_store():
    """Agrega Amazon a la base de datos como tienda desactivada"""

    # Configuración de Amazon para scraping
    # (Similar a Éxito/Homecenter pero para Amazon)
    amazon_config = {
        "sitio": "Amazon",
        "search_url_template": "https://www.amazon.com/s?k={product_name}",
        "title_xpath": "//span[@class='a-size-medium a-color-base a-text-normal']",
        "price_xpath": "//span[@class='a-price-whole']",
        "url_xpath": "//a[@class='a-link-normal s-no-outline']/@href",
        "base_product_url": "https://www.amazon.com"
    }

    with get_db() as conn:
        # Verificar si Amazon ya existe
        existing = conn.execute(
            "SELECT id FROM stores WHERE name = 'Amazon'"
        ).fetchone()

        if existing:
            print("⚠️  Amazon ya existe en la base de datos")
            print(f"   ID: {existing['id']}")

            # Mostrar configuración actual
            store = conn.execute(
                "SELECT * FROM stores WHERE name = 'Amazon'"
            ).fetchone()

            print(f"\nConfiguración actual:")
            print(f"   Activa: {'Sí' if store['active'] else 'No'}")
            print(f"   Afiliado habilitado: {'Sí' if store['affiliate_enabled'] else 'No'}")
            print(f"   Código afiliado: {store['affiliate_code'] or '(sin configurar)'}")

            return

        # Insertar Amazon
        cursor = conn.execute("""
            INSERT INTO stores (
                name,
                url,
                fetch_method,
                config,
                active,
                affiliate_enabled,
                affiliate_code,
                affiliate_url_pattern
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Amazon",
            "https://www.amazon.com",
            "html",  # Método de scraping
            json.dumps(amazon_config, ensure_ascii=False),
            0,  # Desactivada por defecto
            0,  # Afiliado deshabilitado
            None,  # Sin código aún
            "?tag={code}"  # Patrón de Amazon Associates
        ))

        conn.commit()
        store_id = cursor.lastrowid

        print("✅ Amazon agregada exitosamente a la base de datos")
        print(f"\n📦 Detalles:")
        print(f"   ID: {store_id}")
        print(f"   Nombre: Amazon")
        print(f"   Estado: Desactivada (no aparecerá en comparaciones)")
        print(f"   Afiliado: Deshabilitado (sin código)")

        print(f"\n🚀 Para activar Amazon:")
        print(f"   1. Regístrate en Amazon Associates: https://affiliate-program.amazon.com/")
        print(f"   2. Obtén tu código (ej: 'priceflo-20')")
        print(f"   3. Ejecuta: python activate_amazon_affiliate.py TU_CODIGO")

        print(f"\n💡 Para agregar productos de Amazon:")
        print(f"   Usa add_test_data.py o agrega manualmente a la tabla 'products'")

if __name__ == "__main__":
    add_amazon_store()
