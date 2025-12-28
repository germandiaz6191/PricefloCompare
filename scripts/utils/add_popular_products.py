"""
Script para agregar productos populares a la base de datos
Basado en investigación de productos más vendidos en Colombia 2025
"""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from database import add_product

# Productos organizados por categoría
# Basado en: https://www.tiendanube.com/blog/productos-mas-vendidos-en-colombia/
# y https://www.eltiempo.com/tecnosfera/novedades-tecnologia/estos-seran-los-10-productos-que-mas-se-venderan-por-internet-en-2025-en-colombia-3409599

PRODUCTOS_POPULARES = {
    "Celulares": [
        # Smartphones más buscados
        "iPhone 15",
        "iPhone 15 Pro",
        "iPhone 14",
        "Samsung Galaxy S24",
        "Samsung Galaxy S23",
        "Samsung Galaxy A54",
        "Samsung Galaxy A34",
        "Xiaomi Redmi Note 13",
        "Xiaomi Redmi Note 12",
        "Motorola Edge 40",
        "Motorola G84",
        "OPPO Reno 11",
        "Realme 11 Pro",
    ],

    "Televisores": [
        # TVs más populares
        "Smart TV Samsung 55 pulgadas",
        "Smart TV LG 50 pulgadas",
        "Smart TV Samsung 43 pulgadas",
        "Smart TV LG 43 pulgadas",
        "Smart TV Samsung 65 pulgadas",
        "Smart TV TCL 50 pulgadas",
        "Smart TV Kalley 43 pulgadas",
        "TV Samsung QLED 55",
        "TV LG OLED 55",
        "TV Samsung Crystal UHD 50",
    ],

    "Computadores": [
        # Laptops y computadores
        "Portátil HP 15",
        "Portátil Lenovo IdeaPad",
        "Portátil ASUS VivoBook",
        "Portátil Dell Inspiron",
        "Portátil Acer Aspire 5",
        "MacBook Air M2",
        "MacBook Pro 14",
        "Portátil HP Pavilion",
        "Portátil Lenovo ThinkPad",
        "PC All in One HP",
    ],

    "Electrodomésticos": [
        # Electrodomésticos más vendidos
        "Nevera Samsung",
        "Nevera LG",
        "Lavadora Samsung",
        "Lavadora LG",
        "Nevera Mabe",
        "Lavadora Whirlpool",
        "Air Fryer Oster",
        "Air Fryer Kalley",
        "Microondas Samsung",
        "Licuadora Oster",
        "Aspiradora Robot",
        "Plancha de Vapor",
    ],

    "Gaming": [
        # Consolas y gaming
        "PlayStation 5",
        "PlayStation 5 Digital",
        "Xbox Series X",
        "Xbox Series S",
        "Nintendo Switch",
        "Nintendo Switch OLED",
        "Control PS5",
        "Control Xbox",
        "Audifonos Gamer",
        "Teclado Gamer",
        "Mouse Gamer",
        "Monitor Gamer 27",
    ],

    "Audio": [
        # Audio y accesorios
        "AirPods Pro",
        "AirPods 3",
        "Audifonos Samsung Buds",
        "JBL Flip 6",
        "JBL Charge 5",
        "Sony WH-1000XM5",
        "Bose QuietComfort",
        "Parlante Bluetooth JBL",
        "Soundbar Samsung",
        "Audifonos Inalambricos",
    ],

    "Smartwatches": [
        # Relojes inteligentes
        "Apple Watch Series 9",
        "Apple Watch SE",
        "Samsung Galaxy Watch 6",
        "Xiaomi Smart Band 8",
        "Amazfit GTS 4",
        "Garmin Forerunner",
        "Huawei Watch GT 4",
    ],

    "Tablets": [
        # Tablets más buscadas
        "iPad Air",
        "iPad 10",
        "iPad Pro 11",
        "Samsung Galaxy Tab S9",
        "Samsung Galaxy Tab A8",
        "Lenovo Tab M10",
        "Xiaomi Pad 6",
    ],

    "Hogar": [
        # Productos para el hogar
        "Colchón Doble",
        "Sofá Cama",
        "Juego de Comedor",
        "Mesa de Centro",
        "Escritorio para PC",
        "Silla Gamer",
        "Ventilador de Pie",
        "Ventilador de Torre",
        "Cafetera Oster",
        "Batidora KitchenAid",
    ],

    "Cámaras": [
        # Cámaras y fotografía
        "GoPro Hero 12",
        "Canon EOS Rebel T7",
        "Nikon D3500",
        "Sony Alpha A6400",
        "DJI Mini 3 Pro",
        "Ring Video Doorbell",
        "Cámara de Seguridad",
    ]
}

def agregar_productos_populares():
    """Agrega productos populares a la base de datos"""

    print("\n" + "="*70)
    print("📦 AGREGANDO PRODUCTOS POPULARES A LA BASE DE DATOS")
    print("="*70 + "\n")

    total_agregados = 0
    total_existentes = 0

    for categoria, productos in PRODUCTOS_POPULARES.items():
        print(f"\n📁 Categoría: {categoria}")
        print(f"   Total de productos: {len(productos)}")

        agregados_categoria = 0

        for producto in productos:
            try:
                # is_frequent=True para productos populares (actualizar cada 6 horas)
                product_id = add_product(
                    name=producto,
                    category=categoria,
                    is_frequent=True,
                    update_interval_hours=6
                )

                # Si el ID es bajo, probablemente es nuevo
                # (esto es una heurística simple)
                agregados_categoria += 1
                total_agregados += 1

            except Exception as e:
                print(f"   ⚠️  Error agregando '{producto}': {e}")

        print(f"   ✅ Productos procesados: {agregados_categoria}")

    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Total de productos agregados/actualizados: {total_agregados}")
    print(f"📁 Categorías: {len(PRODUCTOS_POPULARES)}")
    print("\n💡 Nota: Los productos duplicados se omiten automáticamente")
    print("="*70 + "\n")

    # Mostrar estadísticas por categoría
    print("\n📈 PRODUCTOS POR CATEGORÍA:\n")
    for categoria, productos in PRODUCTOS_POPULARES.items():
        print(f"   • {categoria:20s}: {len(productos):2d} productos")

    print("\n" + "="*70)
    print("✅ ¡Listo! Productos populares agregados a la base de datos")
    print("="*70 + "\n")

    print("🔄 Próximos pasos:")
    print("   1. Ejecutar: python add_test_data.py (para scrapear precios)")
    print("   2. O ejecutar scraper automático en Railway")
    print("   3. Los usuarios verán estos productos en epriceflo.com\n")


if __name__ == "__main__":
    agregar_productos_populares()
