# ⚠️ INSTRUCCIONES IMPORTANTES - Migración de Países

## 🚨 Estado Actual: Funcionalidad Multi-País DESHABILITADA TEMPORALMENTE

Para evitar errores en producción mientras se ejecuta la migración de base de datos,
la funcionalidad de selector de países está **temporalmente deshabilitada**.

---

## 📋 Pasos para Activar Multi-País

### 1️⃣ Ejecutar Migración en Producción

Necesitas ejecutar el script de migración que crea las tablas y columnas necesarias:

```bash
# Opción A: Desde tu máquina local (conectado a Supabase)
# Asegúrate de tener DATABASE_URL configurado en .env apuntando a Supabase
python migrate_countries.py

# Opción B: Desde Supabase SQL Editor
# Ejecutar el script SQL manualmente (ver abajo)
```

#### Script SQL para Supabase (Opción B):

```sql
-- 1. Crear tabla countries
CREATE TABLE IF NOT EXISTS countries (
    code VARCHAR(2) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    locale VARCHAR(10) NOT NULL,
    flag_emoji VARCHAR(10),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Insertar países iniciales
INSERT INTO countries (code, name, currency, locale, flag_emoji, active) VALUES
('CO', 'Colombia', 'COP', 'es-CO', '🇨🇴', TRUE),
('MX', 'México', 'MXN', 'es-MX', '🇲🇽', FALSE),
('CL', 'Chile', 'CLP', 'es-CL', '🇨🇱', FALSE),
('AR', 'Argentina', 'ARS', 'es-AR', '🇦🇷', FALSE),
('PE', 'Perú', 'PEN', 'es-PE', '🇵🇪', FALSE)
ON CONFLICT (code) DO NOTHING;

-- 3. Agregar columnas a stores
ALTER TABLE stores ADD COLUMN IF NOT EXISTS country_code VARCHAR(2);
ALTER TABLE stores ADD COLUMN IF NOT EXISTS currency VARCHAR(3);

-- 4. Actualizar stores existentes a Colombia
UPDATE stores
SET country_code = 'CO', currency = 'COP'
WHERE country_code IS NULL OR country_code = '';

-- 5. Crear índice
CREATE INDEX IF NOT EXISTS idx_stores_country ON stores(country_code);

-- 6. Agregar foreign key constraint
ALTER TABLE stores
ADD CONSTRAINT fk_stores_country
FOREIGN KEY (country_code)
REFERENCES countries(code)
ON DELETE SET NULL;
```

### 2️⃣ Verificar que la Migración Funcionó

```sql
-- Verificar que countries tiene datos
SELECT * FROM countries;

-- Verificar que stores tiene country_code
SELECT id, name, country_code, currency FROM stores;
```

Deberías ver:
- ✅ 5 países en la tabla `countries`
- ✅ Todas las tiendas con `country_code = 'CO'`

### 3️⃣ Activar la Funcionalidad en el Frontend

Ahora que la base de datos está lista, necesitas **descomentar** las líneas de código:

#### Archivo: `frontend/app.js`

**Línea 586-588:**
```javascript
// Descomentar estas líneas:
// Inicializar selector de país
await initializeCountrySelector();
```

**Línea 751-754:**
```javascript
// Descomentar estas líneas:
if (selectedCountry) {
    url += `?country=${selectedCountry}`;
}
```

**Línea 845-848:**
```javascript
// Descomentar estas líneas:
if (selectedCountry) {
    url += `&country=${selectedCountry}`;
}
```

#### Archivo: `frontend/index.html`

**Línea 79-80:**
```html
<!-- Quitar el style="display: none;" -->
<!-- De: -->
<div class="country-selector-wrapper" style="display: none;">

<!-- A: -->
<div class="country-selector-wrapper">
```

### 4️⃣ Commitear y Pushear los Cambios

```bash
git add frontend/app.js frontend/index.html
git commit -m "feat: Activar selector de país después de migración"
git push origin claude/teleport-session-setup-019r42Bo2eeUcwaLfbn3p2ta
```

### 5️⃣ Verificar en Producción

1. Espera a que Railway despliegue los cambios
2. Ve a https://epriceflo.com
3. Deberías ver el selector de país: **🇨🇴 Colombia**
4. Al hacer clic, se abre el dropdown con la lista de países
5. Colombia es el único activo por ahora

---

## 🎯 Resumen del Flujo

```
Estado Actual:
├─ ❌ Selector de país oculto
├─ ❌ Filtros de país deshabilitados
└─ ✅ Aplicación funcionando normal (sin países)

Ejecutar migrate_countries.py ↓

Base de Datos Lista:
├─ ✅ Tabla countries creada
├─ ✅ Columna country_code en stores
└─ ✅ Datos migrados a Colombia

Descomentar código ↓

Funcionalidad Completa:
├─ ✅ Selector de país visible
├─ ✅ Filtros por país activos
└─ ✅ Listo para expansión internacional
```

---

## ⚡ Comando Rápido (Todo en Uno)

Si tienes acceso a la BD desde tu máquina local:

```bash
# 1. Ejecutar migración
python migrate_countries.py

# 2. Descomentar código (manualmente)
# Edita los archivos mencionados arriba

# 3. Commitear y pushear
git add frontend/app.js frontend/index.html
git commit -m "feat: Activar selector de país"
git push
```

---

## ❓ FAQ

### ¿Qué pasa si no ejecuto la migración?
- ✅ La aplicación seguirá funcionando normalmente
- ❌ No podrás usar el selector de países
- ❌ No podrás filtrar por país

### ¿Puedo ejecutar la migración en Railway directamente?
- ❌ No recomendado (Railway no tiene acceso a scripts Python directamente)
- ✅ Mejor opción: Ejecutar desde tu máquina local conectado a Supabase
- ✅ Alternativa: Copiar el SQL y ejecutarlo en Supabase SQL Editor

### ¿Los datos existentes se pierden?
- ✅ NO, todos los datos se preservan
- ✅ Las tiendas existentes se asignan automáticamente a Colombia ('CO')
- ✅ Los productos permanecen globales (sin cambios)

---

## 🆘 Si Algo Sale Mal

### Rollback de la migración:

```sql
-- Deshacer cambios (solo si es necesario)
ALTER TABLE stores DROP CONSTRAINT IF EXISTS fk_stores_country;
ALTER TABLE stores DROP COLUMN IF EXISTS country_code;
ALTER TABLE stores DROP COLUMN IF EXISTS currency;
DROP TABLE IF EXISTS countries;
```

### Restaurar funcionalidad (sin migración):

- El código ya está configurado para funcionar sin la migración
- Solo mantén las líneas comentadas
- La aplicación funcionará normalmente

---

**¿Listo para proceder?** Ejecuta la migración cuando estés listo. 🚀
