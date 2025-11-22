# Sistema de Afiliados Configurable por Base de Datos

## 🎯 Ventajas

✅ **NO necesitas editar código** - Todo se configura desde la BD
✅ **Éxito y Homecenter siguen funcionando normal** - Sin cambios
✅ **Amazon lista para activar** - Solo ejecuta un script cuando tengas el código
✅ **Escalable** - Agrega más tiendas fácilmente

---

## 📦 Setup Inicial

### 1. Migrar Base de Datos (Solo una vez)

Agrega las columnas de afiliados a tu BD existente:

```bash
python migrate_affiliate_fields.py
```

Output esperado:
```
🔄 Ejecutando 3 migraciones...
   - ALTER TABLE stores ADD COLUMN affiliate_enabled INTEGER DEFAULT 0
   - ALTER TABLE stores ADD COLUMN affiliate_code TEXT
   - ALTER TABLE stores ADD COLUMN affiliate_url_pattern TEXT
✅ Migración completada exitosamente
```

---

### 2. Agregar Amazon (Opcional)

Amazon está lista para agregar cuando quieras:

```bash
python add_amazon_store.py
```

Esto agrega Amazon a la BD pero **DESACTIVADA**:
- No aparecerá en comparaciones
- No hace scraping
- Lista para activar cuando tengas código de afiliado

---

## 🔑 Activar Afiliados

### Cuando consigas tu código de Amazon Associates:

```bash
python activate_amazon_affiliate.py TU_CODIGO_AQUI
```

**Ejemplo:**
```bash
python activate_amazon_affiliate.py priceflo-20
```

Output:
```
✅ Afiliado de Amazon activado exitosamente

📊 Configuración:
   Código de afiliado: priceflo-20
   Patrón de URL: https://amazon.com/...?tag=priceflo-20
   Amazon activa para scraping: No

🎉 ¡Listo! Ahora todos los links a Amazon tendrán tu código de afiliado
```

---

## 🏪 Configurar Otras Tiendas

### Para Éxito, Homecenter, Falabella (cuando negocies):

**Opción 1: SQL directo**

```sql
UPDATE stores
SET affiliate_enabled = 1,
    affiliate_code = 'TU_CODIGO_EXITO',
    affiliate_url_pattern = '?affiliate_id={code}'
WHERE name = 'Éxito';
```

**Opción 2: Script Python**

```python
from database import get_db

with get_db() as conn:
    conn.execute("""
        UPDATE stores
        SET affiliate_enabled = 1,
            affiliate_code = ?,
            affiliate_url_pattern = ?
        WHERE name = ?
    """, ('TU_CODIGO', '?ref={code}', 'Homecenter'))
    conn.commit()

print("✅ Afiliado de Homecenter activado")
```

---

## 🔍 Verificar Configuración

### Ver todas las tiendas con afiliados activos:

```python
from database import get_db

with get_db() as conn:
    stores = conn.execute("""
        SELECT name, affiliate_code, affiliate_url_pattern, active
        FROM stores
        WHERE affiliate_enabled = 1
    """).fetchall()

    for store in stores:
        print(f"{store['name']}: {store['affiliate_code']}")
```

---

## 🌐 Cómo Funciona el Frontend

El frontend ahora carga la configuración automáticamente desde la API:

```
1. Usuario visita /app
2. JavaScript llama GET /affiliate-config
3. API retorna tiendas con affiliate_enabled = 1
4. Frontend aplica códigos automáticamente a botones
5. Usuario hace clic → URL tiene código de afiliado → $$$
```

**Ejemplo de respuesta del API:**

```json
{
  "Amazon": {
    "enabled": true,
    "code": "priceflo-20",
    "url_pattern": "?tag={code}"
  }
}
```

**URL generada:**
```
Original:  https://www.amazon.com/dp/B08N5WRWNW
Afiliado:  https://www.amazon.com/dp/B08N5WRWNW?tag=priceflo-20
```

---

## 📊 Esquema de Base de Datos

```sql
CREATE TABLE stores (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    fetch_method TEXT,  -- 'html', 'graphql'
    config TEXT,        -- JSON config para scraping
    active INTEGER DEFAULT 1,

    -- Campos de afiliados (nuevos)
    affiliate_enabled INTEGER DEFAULT 0,
    affiliate_code TEXT,
    affiliate_url_pattern TEXT,

    created_at TEXT
);
```

**Ejemplos de datos:**

| name | active | affiliate_enabled | affiliate_code | affiliate_url_pattern |
|------|--------|-------------------|----------------|----------------------|
| Éxito | 1 | 0 | NULL | NULL |
| Homecenter | 1 | 0 | NULL | NULL |
| Amazon | 0 | 1 | priceflo-20 | ?tag={code} |

---

## 🚀 Flujo Completo

### Escenario 1: Solo Éxito y Homecenter (Ahora)

```
1. Éxito y Homecenter activas, sin afiliado
2. Productos se scrappean normal
3. Botones "Ver en tienda" con URLs normales
4. ✅ Todo funciona como antes
```

### Escenario 2: Agregas Amazon con Afiliado

```
1. python add_amazon_store.py (Amazon desactivada)
2. python activate_amazon_affiliate.py priceflo-20
3. Agregas productos de Amazon a la BD
4. Botones de Amazon tienen tu código de afiliado
5. ✅ Empiezas a ganar comisiones
```

### Escenario 3: Negociaste CPA con Éxito

```
1. UPDATE stores SET affiliate_enabled = 1, affiliate_code = 'CODIGO_EXITO'
2. Botones de Éxito ahora tienen tu código
3. ✅ Tracking de clics y comisiones
```

---

## 📁 Archivos Creados

| Archivo | Propósito |
|---------|-----------|
| `migrate_affiliate_fields.py` | Agregar columnas a BD existente |
| `add_amazon_store.py` | Agregar Amazon a la BD |
| `activate_amazon_affiliate.py` | Activar afiliado de Amazon |
| `api.py` | Endpoint `/affiliate-config` |
| `frontend/affiliate-config.js` | Cargar config desde API |

---

## ⚠️ Importante

### ✅ Éxito y Homecenter NO se ven afectados

Tus tiendas actuales siguen funcionando exactamente igual:
- Scraping funciona
- Precios se actualizan
- Links normales (sin afiliado)

### 🔄 Migración es segura

El script `migrate_affiliate_fields.py`:
- Solo AGREGA columnas
- NO modifica datos existentes
- NO borra nada
- Puedes ejecutarlo múltiples veces (es idempotente)

### 📈 Amazon cuando quieras

Amazon solo se activa cuando TÚ ejecutes los scripts:
1. `add_amazon_store.py` - Agregar tienda (desactivada)
2. `activate_amazon_affiliate.py` - Activar afiliado

Hasta entonces, **cero impacto** en tu sistema actual.

---

## 🎯 Ventajas de este Enfoque

1. **No tocar código** - Todo se configura por BD
2. **Éxito/Homecenter intactos** - Sin riesgo
3. **Amazon lista** - Cuando tengas código
4. **Escalable** - Fácil agregar más tiendas
5. **Centralizado** - Un solo lugar de configuración
6. **Flexible** - Activa/desactiva sin deploy

---

## 📞 Preguntas Frecuentes

**Q: ¿Afecta mis tiendas actuales?**
A: NO. Éxito y Homecenter siguen igual.

**Q: ¿Necesito código para probar?**
A: NO. Puedes agregar Amazon y activar después.

**Q: ¿Puedo desactivar afiliado?**
A: SÍ. `UPDATE stores SET affiliate_enabled = 0`

**Q: ¿Funciona sin Amazon?**
A: SÍ. Amazon es opcional.

**Q: ¿Puedo tener múltiples afiliados?**
A: SÍ. Cada tienda tiene su propio código.

---

## ✅ Resumen

```bash
# 1. Migrar BD (solo una vez)
python migrate_affiliate_fields.py

# 2. Agregar Amazon (opcional)
python add_amazon_store.py

# 3. Cuando tengas código de Amazon
python activate_amazon_affiliate.py priceflo-20

# ¡Listo! Ya estás monetizando 🎉
```

**Éxito y Homecenter:** Funcionando normal ✅
**Amazon:** Lista para activar cuando quieras ✅
**Código:** NO necesitas editarlo ✅
