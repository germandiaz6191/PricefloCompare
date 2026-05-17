"""
Actualiza el price_xpath de Homecenter al correcto para pagina de listado.
Usa div[1] para tomar siempre el precio final (no el original cuando hay descuento).
"""
import sqlite3
import json
from lxml import html

# Verificar primero en el HTML
with open("Homecenter_resultado.html", "rb") as f:
    content = f.read()
tree = html.fromstring(content)

title_xpath = "//*[@id='title-pdp-link']/h2"
price_xpath = (
    "/html/body/div/div[2]/div/div[2]/div[3]/div[1]/div[1]/div[3]"
    "/div/div/div[5]/div/div/div[3]/div[1]/div[2]/div[1]/div/span[1]"
)
titles = tree.xpath(title_xpath)
prices = tree.xpath(price_xpath)
print(f"Titulos: {len(titles)}, Precios: {len(prices)} -> {'OK' if len(titles) == len(prices) else 'MISMATCH'}")

# Guardar en BD
conn = sqlite3.connect("data/prices.db")
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT id, config FROM stores WHERE name = 'Homecenter'").fetchone()
cfg = json.loads(row["config"])
cfg["price_xpath"] = price_xpath
conn.execute("UPDATE stores SET config = ? WHERE id = ?", (json.dumps(cfg, ensure_ascii=False), row["id"]))
conn.commit()
conn.close()
print(f"price_xpath actualizado: {price_xpath}")
