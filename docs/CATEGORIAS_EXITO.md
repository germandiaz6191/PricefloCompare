# 🏪 Categorías de Éxito - Referencia Rápida

Guía de categorías conocidas de Éxito.com para configurar correctamente.

---

## 🔍 Cómo Descubrir Categorías

### Método 1: Script Automático (Recomendado)

```bash
# Descubre categorías probando con productos de tu BD
python scripts/utils/discover_exito_categories.py
```

Esto:
- ✅ Prueba cada categoría con un producto ejemplo
- ✅ Muestra cuáles funcionan
- ✅ Sugiere ajustes

### Método 2: Verificación Manual

```bash
# Probar si una categoría funciona
python scripts/utils/verify_category.py "Teclado Gamer" --value accesorios-de-computador

# Con nivel diferente
python scripts/utils/verify_category.py "Samsung S24" --level category-2 --value tecnologia
```

### Método 3: DevTools (Manual)

1. Abre https://www.exito.com
2. Busca un producto
3. F12 → Network → Busca `SearchQuery`
4. Mira `selectedFacets` → copia el filtro

---

## 📋 Categorías Conocidas (category-3)

Basado en observación del sitio y pruebas:

| Categoría ePriceFlo | Valor Éxito | Estado | Producto de Prueba |
|---------------------|-------------|--------|--------------------|
| **Gaming** | `accesorios-de-computador` | ✅ Confirmado | Teclado Gamer |
| **Celulares** | `celulares` | ⚠️ Verificar | Samsung Galaxy S24 |
| **Smartphones** | `celulares` | ⚠️ Verificar | iPhone 15 |
| **Audio** | `audifonos` | ⚠️ Verificar | AirPods 3 |
| **Audífonos** | `audifonos` | ⚠️ Verificar | Sony WH-1000XM5 |
| **Computadores** | `portatiles` | ⚠️ Verificar | MacBook Air |
| **Laptops** | `portatiles` | ⚠️ Verificar | Dell Inspiron |
| **Tablets** | `tablets` | ⚠️ Verificar | iPad |
| **Televisores** | `televisores` | ⚠️ Verificar | Smart TV Samsung |
| **TV** | `televisores` | ⚠️ Verificar | LG OLED |
| **Electrodomésticos** | `electrodomesticos` | ⚠️ Verificar | Air Fryer |
| **Cocina** | `pequenos-electrodomesticos` | ⚠️ Verificar | Licuadora |
| **Lavadoras** | `lavado-y-secado` | ⚠️ Verificar | Lavadora LG |
| **Neveras** | `refrigeracion` | ⚠️ Verificar | Nevera Samsung |
| **Smartwatches** | `smartwatches` | ⚠️ Verificar | Apple Watch |
| **Relojes Inteligentes** | `smartwatches` | ⚠️ Verificar | Garmin |
| **Cámaras** | `camaras` | ⚠️ Verificar | Canon EOS |
| **Fotografía** | `camaras` | ⚠️ Verificar | Sony Alpha |
| **Hogar** | `hogar` | ⚠️ Verificar | Sofá |
| **Muebles** | `muebles` | ⚠️ Verificar | Mesa |
| **Decoración** | `decoracion` | ⚠️ Verificar | Espejo |

---

## 🔍 Categorías Posibles (category-2)

Categorías más generales (menos específicas):

| Valor | Descripción |
|-------|-------------|
| `tecnologia` | Electrónica general |
| `hogar` | Hogar y muebles |
| `electrodomesticos` | Electrodomésticos generales |
| `deporte` | Deportes |
| `belleza` | Belleza y cuidado personal |
| `juguetes` | Juguetes |
| `moda` | Ropa y accesorios |

---

## 🎯 Flujo de Trabajo Recomendado

### 1. Ejecutar descubrimiento automático
```bash
python scripts/utils/discover_exito_categories.py
```

### 2. Revisar resultados
Ver `category_discovery_results.json`

### 3. Verificar categorías específicas
```bash
# Para cada categoría que quieras confirmar
python scripts/utils/verify_category.py "Producto" --value "categoria-valor"
```

### 4. Agregar a BD las que funcionan
```sql
INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value)
VALUES (1, 'Gaming', 'category-3', 'accesorios-de-computador');
```

### 5. Probar scraper
```bash
python scripts/utils/add_test_data.py
```

---

## 💡 Tips

### Tip 1: Algunos productos pueden tener categorías múltiples
```
"Teclado Gamer" puede estar en:
- category-3: accesorios-de-computador
- category-4: teclados
```

### Tip 2: Valores con guiones
Éxito usa kebab-case:
- ✅ `accesorios-de-computador`
- ❌ `accesorios de computador`

### Tip 3: Plurales vs Singular
Éxito es inconsistente:
- `celulares` (plural)
- `television` (singular)
- `portatiles` (plural)

Prueba ambas formas.

### Tip 4: Si no encuentras la categoría correcta
Opciones:
1. Usa un nivel más general (category-2)
2. Omite el filtro de categoría (búsqueda amplia)
3. Usa términos más específicos en el nombre del producto

---

## 🔧 Agregar Nuevas Categorías

### Paso 1: Descubrir el valor
```bash
# Método A: Script
python scripts/utils/verify_category.py "Producto" --value "valor-a-probar"

# Método B: Manual
# 1. Buscar en exito.com
# 2. F12 → Network → SearchQuery
# 3. Copiar el valor de selectedFacets
```

### Paso 2: Agregar a BD
```sql
INSERT INTO category_mappings (store_id, category_name, filter_level, filter_value)
VALUES (1, 'NombreCategoria', 'category-3', 'valor-exacto');
```

### Paso 3: Verificar
```bash
python scripts/utils/add_test_data.py
# Revisar logs para ver si encuentra productos
```

---

## 📊 Estado de Verificación

| Estado | Significado |
|--------|-------------|
| ✅ Confirmado | Probado y funciona |
| ⚠️ Verificar | Pre-configurado, necesita prueba |
| ❌ No funciona | Probado y no retorna resultados |

**Meta**: Verificar todas las categorías ⚠️ y marcarlas como ✅ o ❌

---

**Última actualización**: 2025-12-28
**Contribuciones**: Si descubres nuevas categorías, agrégalas aquí
