# 📦 Productos Populares - ePriceFlo

Lista curada de productos más vendidos y buscados en Colombia para 2025.

---

## 🔍 Investigación

Basado en múltiples fuentes de mercado colombiano:

### Fuentes:
- [Productos más vendidos en Colombia - TiendaNube](https://www.tiendanube.com/blog/productos-mas-vendidos-en-colombia/)
- [Los 10 productos que más se venderán por internet en 2025 - El Tiempo](https://www.eltiempo.com/tecnosfera/novedades-tecnologia/estos-seran-los-10-productos-que-mas-se-venderan-por-internet-en-2025-en-colombia-3409599)
- [Productos más vendidos en Colombia 2025-2026 - AmericasMI](https://americasmi.com/insights/productos-mas-vendidos-colombia/)

### Estadísticas del Mercado (Q2 2025):
- 📊 **Ventas online**: COP $26.9 billones
- 📈 **Crecimiento**: +3% vs 2024
- 🛒 **Transacciones**: 224.3 millones
- 💼 **Retail**: +10.1% año tras año

---

## 📁 Categorías de Productos

### 1️⃣ **Celulares** (13 productos)
Los smartphones siguen siendo los productos más buscados en e-commerce colombiano.

**Marcas principales:**
- iPhone (3 modelos)
- Samsung Galaxy (5 modelos)
- Xiaomi Redmi (2 modelos)
- Motorola (2 modelos)
- OPPO, Realme

### 2️⃣ **Televisores** (10 productos)
Smart TVs son productos estrella, especialmente en tamaños 43-65 pulgadas.

**Marcas principales:**
- Samsung (5 modelos)
- LG (4 modelos)
- TCL, Kalley

**Tecnologías populares:**
- QLED
- OLED
- Crystal UHD

### 3️⃣ **Computadores** (10 productos)
Portátiles para trabajo remoto y estudio siguen en alta demanda.

**Marcas principales:**
- HP (3 modelos)
- Lenovo (2 modelos)
- ASUS, Dell, Acer
- Apple MacBook (2 modelos)

### 4️⃣ **Electrodomésticos** (12 productos)
**Categoría en auge**: Air Fryers son el producto estrella del 2025.

**Productos destacados:**
- Neveras (Samsung, LG, Mabe)
- Lavadoras (Samsung, LG, Whirlpool)
- Air Fryers (Oster, Kalley)
- Microondas, licuadoras, aspiradoras robot

### 5️⃣ **Gaming** (12 productos)
El gaming sigue creciendo en Colombia con consolas de última generación.

**Consolas:**
- PlayStation 5 (2 versiones)
- Xbox Series X/S
- Nintendo Switch (2 versiones)

**Accesorios:**
- Controles
- Audífonos gamer
- Periféricos (teclado, mouse)
- Monitores gamer

### 6️⃣ **Audio** (10 productos)
Audífonos inalámbricos y parlantes Bluetooth muy populares.

**Marcas principales:**
- Apple AirPods (2 modelos)
- Samsung Buds
- JBL (3 modelos)
- Sony, Bose

### 7️⃣ **Smartwatches** (7 productos)
Wearables en crecimiento constante.

**Marcas:**
- Apple Watch (2 modelos)
- Samsung Galaxy Watch
- Xiaomi, Amazfit, Garmin, Huawei

### 8️⃣ **Tablets** (7 productos)
Tablets para educación y entretenimiento.

**Marcas:**
- Apple iPad (3 modelos)
- Samsung Galaxy Tab (2 modelos)
- Lenovo, Xiaomi

### 9️⃣ **Hogar** (10 productos)
Muebles y electrodomésticos para el hogar.

**Productos:**
- Muebles (colchón, sofá, comedor)
- Escritorios y sillas gamer
- Ventiladores
- Pequeños electrodomésticos (cafetera, batidora)

### 🔟 **Cámaras** (7 productos)
Fotografía, videografía y seguridad.

**Productos:**
- GoPro
- Cámaras DSLR (Canon, Nikon, Sony)
- Drones (DJI)
- Cámaras de seguridad (Ring)

---

## 📊 Resumen Total

| Categoría | Cantidad | % del Total |
|-----------|----------|-------------|
| Celulares | 13 | 13.1% |
| Electrodomésticos | 12 | 12.1% |
| Gaming | 12 | 12.1% |
| Televisores | 10 | 10.1% |
| Computadores | 10 | 10.1% |
| Audio | 10 | 10.1% |
| Hogar | 10 | 10.1% |
| Smartwatches | 7 | 7.1% |
| Tablets | 7 | 7.1% |
| Cámaras | 7 | 7.1% |
| **TOTAL** | **98** | **100%** |

---

## 🚀 Cómo Agregar Estos Productos

### Opción 1: Usar el Script Automatizado

```bash
python add_popular_products.py
```

**Esto agregará:**
- ✅ 98 productos populares
- ✅ Organizados en 10 categorías
- ✅ Marcados como `is_frequent=True` (actualización cada 6 horas)
- ✅ Sin duplicados (verifica antes de insertar)

### Opción 2: Agregar Categoría Específica

Edita `add_popular_products.py` y comenta las categorías que no quieras:

```python
PRODUCTOS_POPULARES = {
    "Celulares": [...],    # ✅ Agregar
    # "Gaming": [...],     # ❌ No agregar
    "Televisores": [...],  # ✅ Agregar
}
```

### Opción 3: Agregar Productos Manualmente

```python
from database import add_product

add_product(
    name="iPhone 15 Pro Max",
    category="Celulares",
    is_frequent=True,
    update_interval_hours=6
)
```

---

## 🔄 Después de Agregar Productos

### 1. Scrapear Precios

```bash
python add_test_data.py
```

Esto buscará precios para los nuevos productos en todas las tiendas configuradas.

### 2. Verificar en la Base de Datos

```sql
-- Ver total de productos por categoría
SELECT category, COUNT(*) as total
FROM products
GROUP BY category
ORDER BY total DESC;

-- Ver productos frecuentes (más populares)
SELECT name, category, update_interval_hours
FROM products
WHERE is_frequent = TRUE
ORDER BY category, name;
```

### 3. Ver en Producción

Ve a https://epriceflo.com y verifica:
- ✅ Categorías con más productos
- ✅ Productos aparecen en búsqueda
- ✅ Precios se actualizan automáticamente

---

## 💡 Consejos

### Productos Frecuentes vs Normales

**Productos Frecuentes** (`is_frequent=True`):
- ✅ Se actualizan cada 6 horas
- ✅ Productos más buscados/vendidos
- ✅ Ejemplo: iPhone 15, PS5, Samsung S24

**Productos Normales** (`is_frequent=False`):
- ⏰ Se actualizan cada 12-24 horas
- 📦 Productos de nicho o menos demandados
- 📊 Ejemplo: Accesorios específicos, productos antiguos

### Agregar Más Productos

Para expandir la lista:

1. **Investiga tendencias:**
   - Google Trends Colombia
   - Mercado Libre más vendidos
   - Amazon best sellers

2. **Agrega a la lista:**
   ```python
   PRODUCTOS_POPULARES = {
       "NuevaCategoria": [
           "Producto 1",
           "Producto 2",
       ]
   }
   ```

3. **Ejecuta el script:**
   ```bash
   python add_popular_products.py
   ```

---

## 🎯 Próximos Pasos Recomendados

### A Corto Plazo:
1. ✅ Ejecutar `add_popular_products.py`
2. ✅ Scrapear precios con `add_test_data.py`
3. ✅ Verificar productos en producción

### A Mediano Plazo:
1. 📊 Agregar más tiendas (Ktronix, Alkosto)
2. 🔄 Configurar scraping automático (cron job)
3. 📈 Analizar qué productos tienen más búsquedas

### A Largo Plazo:
1. 🤖 Usar Google Trends API para detectar productos trending
2. 📊 Dashboard de productos más populares
3. 🔔 Alertas de cambios de precio

---

## 📚 Referencias

- [TiendaNube - Productos más vendidos en Colombia](https://www.tiendanube.com/blog/productos-mas-vendidos-en-colombia/)
- [El Tiempo - Top 10 productos internet 2025](https://www.eltiempo.com/tecnosfera/novedades-tecnologia/estos-seran-los-10-productos-que-mas-se-venderan-por-internet-en-2025-en-colombia-3409599)
- [360 Radio - Productos más vendidos según Mercado Libre](https://360radio.com.co/los-productos-mas-vendidos-en-colombia-en-2025-segun-mercado-libre/173725/)
- [AmericasMI - Insights productos Colombia](https://americasmi.com/insights/productos-mas-vendidos-colombia/)

---

**Actualizado**: Diciembre 2025
**Fuente de datos**: Investigación de mercado Colombia 2025
