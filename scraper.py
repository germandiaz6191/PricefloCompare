import json
from datetime import datetime, timedelta
from scrapers.generic_scrapers import load_sites_config, scrape_price

def load_products_config(path="config_productos.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def should_update(product, last_updates, freq_days):
    last_update = last_updates.get(product["nombre"])
    if not last_update:
        return True
    last_time = datetime.fromisoformat(last_update)
    return datetime.now() - last_time >= timedelta(days=freq_days)

def batch_update():
    sitios = load_sites_config()
    productos = load_products_config()

    try:
        with open("last_updates.json", "r", encoding="utf-8") as f:
            last_updates = json.load(f)
    except FileNotFoundError:
        last_updates = {}

    for producto in productos:
        if producto.get("frecuente", False) or should_update(producto, last_updates, producto.get("dias_actualizacion", 1)):
            categoria = producto.get("categoria")  # Obtener categoría opcional
            for sitio_ref in producto["sitios"]:
                sitio_cfg = next((s for s in sitios if s["sitio"] == sitio_ref["sitio"]), None)
                if sitio_cfg:
                    precio = scrape_price(sitio_cfg, producto["nombre"], categoria)
                    if precio:
                        print(f"{producto['nombre']} en {sitio_cfg['sitio']}: {precio}")
                        last_updates[producto["nombre"]] = datetime.now().isoformat()
                    else:
                        print(f"{producto['nombre']} en {sitio_cfg['sitio']}: No encontrado")

    with open("last_updates.json", "w", encoding="utf-8") as f:
        json.dump(last_updates, f, indent=2, ensure_ascii=False)

def on_demand(product_name, product_category=None):
    """
    Búsqueda on-demand de un producto.

    Args:
        product_name: Nombre del producto
        product_category: Categoría opcional (ej: "celulares", "electrodomesticos")
    """
    sitios = load_sites_config()
    for sitio_cfg in sitios:
        result = scrape_price(sitio_cfg, product_name, product_category)
        if result is not None:
            title = result.get("title") or "Título no disponible"
            price = result.get("price") or "Precio no disponible"
            print(f"{product_name} en {sitio_cfg['sitio']}: nombre encontrado {title}, precio {price}")
        else:
            print(f"{product_name} en {sitio_cfg['sitio']}: No encontrado")

if __name__ == "__main__":
    modo = input("¿Modo? (batch/on-demand): ").strip().lower()
    if modo == "batch":
        batch_update()
    else:
        nombre = input("Ingrese nombre de producto: ").strip()
        print("Categorías disponibles: celulares, electrodomesticos, hogar, deportes, etc.")
        print("(Usar categoría mejora precisión al filtrar accesorios y productos relacionados)")
        categoria = input("Ingrese categoría (opcional, presione Enter para omitir): ").strip()
        categoria = categoria if categoria else None
        on_demand(nombre, categoria)