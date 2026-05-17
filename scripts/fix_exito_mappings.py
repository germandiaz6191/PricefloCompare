"""
Elimina todos los category_mappings de Exito de la BD.
Esos mappings insertan category-3 facets que devuelven 0 resultados en la API.
"""
import sqlite3

conn = sqlite3.connect("data/prices.db")
store = conn.execute("SELECT id FROM stores WHERE name LIKE '%xito%'").fetchone()
if not store:
    print("No se encontro la tienda Exito")
    conn.close()
    exit(1)

store_id = store[0]
count = conn.execute("SELECT COUNT(*) FROM category_mappings WHERE store_id = ?", (store_id,)).fetchone()[0]
print(f"Eliminando {count} category_mappings de Exito (store_id={store_id})")

conn.execute("DELETE FROM category_mappings WHERE store_id = ?", (store_id,))
conn.commit()
conn.close()
print("Listo.")
