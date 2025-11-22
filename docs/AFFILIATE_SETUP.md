# 🎯 Guía de Configuración del Sistema de Afiliados

Tu sitio YA ESTÁ LISTO para afiliados. Solo necesitas registrarte en programas y agregar tus códigos.

## ✅ Lo que YA está implementado:

1. ✅ Sistema automático de afiliados en `frontend/affiliate-config.js`
2. ✅ Botones "Ver en tienda" con tracking
3. ✅ Disclosure de transparencia en el footer
4. ✅ Atributo `rel="sponsored"` para SEO
5. ✅ Tracking de clics para estadísticas

---

## 🚀 Cómo Activar Afiliados (3 pasos)

### PASO 1: Regístrate en un Programa

**Opciones que funcionan en Colombia:**

#### Amazon Associates (Recomendado)
1. Ir a: https://affiliate-program.amazon.com/
2. Crear cuenta
3. Completar perfil (acepta bloggers/websites)
4. Te dan tu código (ejemplo: `priceflo-20`)

#### AliExpress Affiliate
1. Ir a: https://portals.aliexpress.com/
2. Registrarse
3. Copiar tu Tracking ID

---

### PASO 2: Agregar tu Código

Abre el archivo: `frontend/affiliate-config.js`

**Busca la tienda y cambia dos cosas:**

```javascript
// ANTES (deshabilitado):
'Amazon': {
    enabled: false,  // ← Cambiar a true
    code: '',        // ← Poner tu código aquí
    urlPattern: (url, code) => {
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}tag=${code}`;
    }
},

// DESPUÉS (habilitado):
'Amazon': {
    enabled: true,           // ✅ Cambiar aquí
    code: 'priceflo-20',    // ✅ Tu código aquí
    urlPattern: (url, code) => {
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}tag=${code}`;
    }
},
```

---

### PASO 3: ¡Listo! Ya Estás Ganando Comisiones

Ahora cuando alguien haga clic en "Ver en tienda", la URL llevará tu código de afiliado:

**Antes:**
```
https://www.amazon.com/dp/B08N5WRWNW
```

**Después:**
```
https://www.amazon.com/dp/B08N5WRWNW?tag=priceflo-20
```

El comercio trackea el clic y si compra → tú recibes comisión.

---

## 📊 Verificar que Funciona

### 1. Inspecciona el Botón "Ver en tienda"

Abre tu navegador:
1. Ir a `http://localhost:8000/app`
2. Click derecho en botón "Ver en tienda"
3. Inspeccionar elemento
4. Verificar que el `href` tiene tu código

**Debe verse así:**
```html
<a href="https://www.amazon.com/dp/XXXXX?tag=priceflo-20"
   target="_blank"
   rel="noopener noreferrer sponsored"
   class="btn-visit-store">
    Ver en tienda
</a>
```

### 2. Verifica en la Consola

Abre DevTools (F12) → Console

Deberías ver:
```
📊 Click tracked: Amazon - Product 1
```

---

## 🎨 Agregar Más Tiendas

### Si negociaste con Éxito:

```javascript
'Éxito': {
    enabled: true,                    // ✅ Activar
    code: 'TU_CODIGO_EXITO',         // ✅ Código que te dieron
    urlPattern: (url, code) => {
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}affiliate_id=${code}`;
    }
},
```

### Si es una red de afiliados (AWIN, ShareASale):

Algunas redes tienen su propio formato de URL. Ejemplo AWIN:

```javascript
'AWIN': {
    enabled: true,
    code: '12345',  // Tu Merchant ID
    urlPattern: (url, code) => {
        // AWIN redirige a través de su servidor
        return `https://www.awin1.com/cread.php?awinmid=${code}&awinaffid=TU_AFFILIATE_ID&clickref=&ued=${encodeURIComponent(url)}`;
    }
}
```

---

## 📈 Tracking y Estadísticas

### Ver Clics (Manual por ahora)

Los clics se registran en:
- Console del navegador (F12)
- Futuro: Dashboard en `/admin/stats`

### Implementar Dashboard de Ingresos

Más adelante puedes crear tabla en BD:

```sql
CREATE TABLE affiliate_clicks (
    id INTEGER PRIMARY KEY,
    store_name TEXT,
    product_id INTEGER,
    timestamp TEXT,
    converted INTEGER DEFAULT 0,
    revenue REAL
);
```

Y endpoint en API:

```python
@app.get("/admin/revenue")
def get_revenue_stats():
    # Total clics este mes
    # Total conversiones
    # Ingresos estimados
    pass
```

---

## ⚠️ Consideraciones Legales

### 1. Disclosure (YA ESTÁ IMPLEMENTADO)

El footer tiene el disclosure requerido:

> "💡 **Transparencia:** PricefloCompare puede recibir comisiones cuando compras a través de algunos de nuestros enlaces. Esto no afecta el precio que pagas y nos ayuda a mantener el servicio gratuito."

Esto cumple con FTC guidelines.

### 2. Atributo rel="sponsored" (YA ESTÁ)

Los links de afiliados tienen `rel="sponsored"` automáticamente para SEO.

### 3. Términos y Condiciones

Deberías crear `/terminos` con:
- Uso de links de afiliados
- Política de privacidad
- Cookies
- Limitación de responsabilidad

---

## 🔧 Troubleshooting

### Los enlaces no tienen mi código

**Causa:** `enabled: false` o `code` vacío

**Solución:**
```javascript
'TiendaX': {
    enabled: true,    // ✅ Debe ser true
    code: 'XXXXX',    // ✅ No debe estar vacío
    ...
}
```

### El código aparece dos veces en la URL

**Causa:** La URL ya tiene parámetros

**Solución:** El código ya maneja esto con:
```javascript
const separator = url.includes('?') ? '&' : '?';
```

Si la URL es: `https://tienda.com/producto?color=red`
Resultado: `https://tienda.com/producto?color=red&ref=TU_CODIGO` ✅

### No veo tracking en consola

**Causa:** El endpoint `/track/click` no existe todavía

**Solución:** Es normal, el tracking es opcional. Los links de afiliado funcionan igual.

---

## 📋 Checklist de Activación

Usa esta lista cuando te registres en un programa:

- [ ] Registrado en programa de afiliados
- [ ] Código recibido (email de confirmación)
- [ ] `enabled: true` en `affiliate-config.js`
- [ ] `code: 'MI_CODIGO'` agregado
- [ ] Probado en navegador (inspeccionar href)
- [ ] Verificado en consola (tracking)
- [ ] Primer clic de prueba realizado
- [ ] Verificado en dashboard del programa

---

## 💰 Programas Recomendados para Empezar

### 1. Amazon Associates ⭐
**Prioridad:** Alta
**Dificultad:** Fácil
**Link:** https://affiliate-program.amazon.com/

**Por qué:**
- Aprobación rápida
- Comisiones 1-10%
- Pago confiable
- Miles de productos

### 2. AliExpress Affiliate ⭐
**Prioridad:** Alta
**Dificultad:** Fácil
**Link:** https://portals.aliexpress.com/

**Por qué:**
- Muy usado en Colombia
- Comisiones 3-8%
- Cookie 30 días
- Productos baratos (alta conversión)

### 3. ShareASale
**Prioridad:** Media
**Dificultad:** Media
**Link:** https://www.shareasale.com/

**Por qué:**
- Red grande (+4,000 marcas)
- Comisiones variables
- Pago confiable

### 4. AWIN
**Prioridad:** Media
**Dificultad:** Media
**Link:** https://www.awin.com/

**Por qué:**
- AliExpress + otras marcas
- Global
- Bien pagado

---

## 🎯 Estrategia de Crecimiento

### Mes 1: Implementación
- [ ] Registrarse en Amazon y AliExpress
- [ ] Activar códigos en `affiliate-config.js`
- [ ] Agregar productos internacionales a tu BD

### Mes 2-3: Optimización
- [ ] A/B testing de CTAs
- [ ] Mejorar SEO
- [ ] Más categorías de productos

### Mes 4-6: Expansión
- [ ] Negociar con Éxito/Falabella (cuando tengas tráfico)
- [ ] Agregar más redes de afiliados
- [ ] Implementar dashboard de estadísticas

---

## 📞 Soporte

**¿Problemas?**
1. Verifica `affiliate-config.js` (enabled y code correctos)
2. Inspecciona el HTML generado
3. Revisa consola de errores (F12)

**¿Dudas sobre programas?**
- Cada programa tiene FAQ y soporte
- Contacta directamente al programa

---

## 🚀 Próximos Pasos

1. **HOY:** Registrarte en Amazon Associates
2. **MAÑANA:** Agregar tu código en `affiliate-config.js`
3. **ESTA SEMANA:** Primera comisión (aunque sea pequeña)

**¡Ya tienes todo listo para monetizar!** 💰
