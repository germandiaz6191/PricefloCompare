"""
Verifica que el title_xpath y price_xpath de Homecenter devuelvan
el mismo numero de elementos (1 por producto).
"""
from lxml import html

with open("Homecenter_resultado.html", "rb") as f:
    content = f.read()

tree = html.fromstring(content)

title_xpath = "//*[@id='title-pdp-link']/h2"
price_xpath = (
    "/html/body/div/div[2]/div/div[2]/div[3]/div[1]/div[1]/div[3]"
    "/div/div/div[5]/div/div/div[3]/div[1]/div[2]/div/div/span[1]"
)
url_xpath = "//*[@id='title-pdp-link']/@href"

titles = tree.xpath(title_xpath)
prices = tree.xpath(price_xpath)
urls = tree.xpath(url_xpath)

print(f"Titulos encontrados: {len(titles)}")
print(f"Precios encontrados: {len(prices)}")
print(f"URLs encontradas:    {len(urls)}")
print()

for i in range(min(5, len(titles))):
    t = titles[i].text_content().strip()[:60]
    p = prices[i].text_content().strip() if i < len(prices) else "(sin precio)"
    u = urls[i] if i < len(urls) else "(sin url)"
    print(f"[{i}] {t}")
    print(f"     Precio: {p}")
    print(f"     URL:    {u[:80]}")
    print()
