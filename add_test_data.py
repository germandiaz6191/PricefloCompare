"""
Script para agregar datos de prueba a la BD
Útil si el scraping da 403
"""
from database import add_price_snapshot, get_products, get_stores
from datetime import datetime

def add_test_data():
    """Agrega datos de prueba a la base de datos"""

    products = get_products()
    stores = get_stores()

    if not products or not stores:
        print("❌ Primero ejecuta: python migrate_to_db.py")
        return

    print("📝 Agregando datos de prueba...")

    # Mapeo de store_id a nombre de tienda
    store_names = {store['id']: store['name'] for store in stores}

    # Función para generar URL realista según la tienda
    def generate_store_url(product_id, store_id, title):
        store_name = store_names.get(store_id, "")
        # Crear slug del producto (minúsculas, sin espacios)
        slug = title.lower().replace(" ", "-").replace("kg", "kg").replace("l", "l")
        # Remover caracteres especiales
        import re
        slug = re.sub(r'[^a-z0-9-]', '', slug)

        if "Éxito" in store_name or "exito" in store_name.lower():
            # URL estilo Éxito: https://www.exito.com/{slug}/p
            return f"https://www.exito.com/{slug}/p"
        elif "Homecenter" in store_name or "homecenter" in store_name.lower():
            # URL estilo Homecenter: https://www.homecenter.com.co/homecenter-co/product/{id}/{slug}
            return f"https://www.homecenter.com.co/homecenter-co/product/{product_id * 100000}/{slug}"
        elif "Falabella" in store_name or "falabella" in store_name.lower():
            # URL estilo Falabella: https://www.falabella.com.co/falabella-co/product/{id}/{slug}
            return f"https://www.falabella.com.co/falabella-co/product/{product_id * 100000}/{slug}"
        else:
            # URL genérica para otras tiendas
            return f"https://{store_name.lower().replace(' ', '')}.com.co/{slug}"

    # Datos de ejemplo (precios ficticios)
    test_prices = [
        # Lavadora LG 17Kg
        {"product_id": 1, "store_id": 1, "price": 1299000, "title": "Lavadora LG 17Kg Carga Superior Silver"},
        {"product_id": 1, "store_id": 2, "price": 1349000, "title": "Lavadora LG 17 Kg Automática"},

        # Nevera Samsung 300L
        {"product_id": 2, "store_id": 1, "price": 1899000, "title": "Nevera Samsung 300L No Frost Plateada"},
        {"product_id": 2, "store_id": 2, "price": 1849000, "title": "Refrigerador Samsung 300 Litros"},

        # iPhone 16
        {"product_id": 3, "store_id": 1, "price": 4299000, "title": "iPhone 16 128GB Negro"},
        {"product_id": 3, "store_id": 2, "price": 4399000, "title": "Apple iPhone 16 128GB Black"},
    ]

    for data in test_prices:
        try:
            # Generar URL realista
            product_url = generate_store_url(
                data['product_id'],
                data['store_id'],
                data['title']
            )

            add_price_snapshot(
                product_id=data['product_id'],
                store_id=data['store_id'],
                price=data['price'],
                title=data['title'],
                url=product_url,
                relevance_score=95
            )
            print(f"✅ Agregado: {data['title']} - ${data['price']:,.0f}")
            print(f"   🔗 URL: {product_url}")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✨ Datos de prueba agregados")
    print("💡 Ahora prueba: http://localhost:8000/stats")
    print("💡 O ejecuta: python view_db.py")

if __name__ == "__main__":
    add_test_data()
