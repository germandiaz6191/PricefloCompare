"""
Encuentra el XPath correcto para precios en la pagina de resultados de Homecenter.
"""
from lxml import html

with open("Homecenter_resultado.html", "rb") as f:
    content = f.read()

tree = html.fromstring(content)

# Buscar elementos que contengan precios en formato colombiano (1.299.900)
import re
price_pattern = re.compile(r'\$\s*[\d\.]+|\b\d{1,3}(?:\.\d{3})+\b')

def find_price_elements(tree):
    for el in tree.iter():
        text = (el.text or "").strip()
        if price_pattern.search(text) and len(text) < 30:
            path = tree.getroottree().getpath(el)
            print(f"TEXT: {text!r:40s} | XPATH: {path}")

print("=== Elementos con precios ===")
find_price_elements(tree)

# Buscar por atributo data-price o clases comunes de precio
print("\n=== Elementos con data-price o clase price ===")
for el in tree.xpath('//*[@data-price]'):
    print(f"data-price={el.get('data-price')!r} | xpath={tree.getroottree().getpath(el)}")

for el in tree.xpath('//*[contains(@class,"price") or contains(@class,"Price")]'):
    text = el.text_content().strip()[:60]
    if text:
        print(f"class={el.get('class')!r:50s} text={text!r}")
