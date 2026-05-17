"""
Elimina el facet de categoria del config de Exito en la BD.
La categoria causa 0 resultados en la API de Exito.
"""
import sqlite3
import json

conn = sqlite3.connect("data/prices.db")
conn.row_factory = sqlite3.Row

row = conn.execute("SELECT id, name, config FROM stores WHERE name LIKE '%xito%'").fetchone()
if not row:
    print("No se encontro la tienda Exito")
    conn.close()
    exit(1)

print(f"Tienda: {row['name']} (id={row['id']})")
cfg = json.loads(row["config"])

facets = cfg.get("params", {}).get("variables", {}).get("selectedFacets", [])
print(f"Facets antes: {json.dumps(facets, ensure_ascii=False)}")

# Quitar facets de categoria (mantener channel y locale)
new_facets = [f for f in facets if "category" not in f.get("key", "")]
cfg["params"]["variables"]["selectedFacets"] = new_facets
print(f"Facets despues: {json.dumps(new_facets, ensure_ascii=False)}")

conn.execute(
    "UPDATE stores SET config = ? WHERE id = ?",
    (json.dumps(cfg, ensure_ascii=False), row["id"])
)
conn.commit()
conn.close()
print("Config actualizada correctamente.")
