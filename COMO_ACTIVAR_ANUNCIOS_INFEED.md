# 📍 Cómo activar anuncios IN-FEED (Entre resultados)

Has elegido la **mejor posición** para anuncios: **IN-FEED** (entre resultados de búsqueda)

---

## ✅ ¿Por qué es la mejor posición?

### **Ventajas:**
- ⭐⭐⭐⭐⭐ CTR: 2-4% (el más alto)
- Se ve natural, como parte del contenido
- **No interrumpe** la experiencia del usuario
- **No molesta** - usuarios lo esperan
- Funciona perfecto en móvil y desktop

### **Ejemplo visual:**
```
┌─────────────────────────┐
│ Producto 1              │
│ Nevera Samsung          │
│ $1,200,000              │
└─────────────────────────┘

┌─────────────────────────┐
│ Producto 2              │
│ Lavadora LG             │
│ $850,000                │
└─────────────────────────┘

┌─────────────────────────┐
│ Producto 3              │
│ Microondas Whirlpool    │
│ $350,000                │
└─────────────────────────┘

╔═════════════════════════╗  👈 ANUNCIO IN-FEED AQUÍ
║ 📢 ANUNCIO              ║
║ (Se ve como un producto)║
╚═════════════════════════╝

┌─────────────────────────┐
│ Producto 4              │
│ Licuadora Oster         │
│ $180,000                │
└─────────────────────────┘
```

---

## 📋 Pasos para activar (cuando tengas AdSense aprobado)

### **Paso 1: Crear unidad de anuncio IN-FEED en AdSense**

1. Ve a: https://adsense.google.com
2. Menú → **Anuncios** → **Por unidad de anuncio**
3. Click **"Nueva unidad de anuncio"**
4. Selecciona: **"In-feed"** (anuncios en el feed)
5. Configura el diseño:
   
   **Opciones recomendadas:**
   - **Tamaño de imagen:** 1x1 (cuadrado) o 16:9 (horizontal)
   - **Color de fondo:** Blanco (#FFFFFF) - igual que tus tarjetas de producto
   - **Color de texto:** Gris oscuro (#0F172A) - igual que tu diseño
   - **Fuente:** System (para que coincida con tu sitio)
   - **Responsive:** ✅ SÍ

6. **Vista previa:** Asegúrate que se vea similar a tus tarjetas de producto
7. Click **"Crear"**
8. **Copia el SLOT ID** (formato: `1234567890`)

---

### **Paso 2: Configurar el slot ID en tu código**

Edita `frontend/adsense-config.js` línea 27:

```javascript
slots: {
    header: '1234567890',       // Banner superior
    sidebar: '1234567891',      // Sidebar derecho
    betweenResults: 'TU_SLOT_ID_INFEED_AQUI',  // 👈 PEGA AQUÍ
    footer: '1234567893'        // Footer
},
```

---

### **Paso 3: Activar AdSense**

Edita `frontend/adsense-config.js` línea 17:

```javascript
enabled: true,  // 👈 Cambiar de false a true
client: 'ca-pub-XXXXXXXXXX',  // 👈 Tu código de cliente de AdSense
```

---

### **Paso 4: Ya está implementado - funciona automáticamente** ✅

El código YA está listo en `frontend/app.js`. Cuando muestres resultados de búsqueda, automáticamente:

1. Muestra productos 1, 2, 3
2. **Inserta anuncio IN-FEED** (después del 3er producto)
3. Continúa con productos 4, 5, 6...
4. **Inserta otro anuncio** (después del 6to producto)
5. Y así sucesivamente...

**No necesitas programar nada**, solo:
- Activar AdSense (`enabled: true`)
- Pegar el slot ID
- Deploy a producción

---

## 🎨 Personalización avanzada (opcional)

### **Cambiar frecuencia de anuncios:**

Si quieres cambiar cuándo aparecen los anuncios (cada 3, 5, 7 productos), edita `frontend/app.js`:

**Busca esta línea:**
```javascript
if ((index + 1) % 3 === 0) {  // Cada 3 productos
    // Insertar anuncio in-feed
}
```

**Opciones:**
- `% 3` → Cada 3 productos (recomendado)
- `% 5` → Cada 5 productos (menos intrusivo)
- `% 7` → Cada 7 productos (muy espaciado)

**Mi recomendación:** Déjalo en `% 3` (cada 3 productos) para maximizar ingresos sin molestar.

---

## 📊 Monitorear rendimiento

Una vez activado, monitorea en Google AdSense:

### **Métricas clave:**
- **CTR (Click-through rate):** Meta: 2-4%
- **RPM (Revenue per 1000 impressions):** Meta: $1-5 USD
- **Impresiones:** Cuántas veces se vio el anuncio
- **Clicks:** Cuántas veces hicieron click

### **Si el CTR es bajo (<1%):**
- Ajusta colores del anuncio para que coincidan mejor con tu diseño
- Cambia la frecuencia (cada 5 productos en vez de 3)
- Prueba diferentes tamaños de imagen (1x1 vs 16:9)

### **Si el CTR es alto (>4%):**
- ¡Perfecto! No cambies nada
- Considera agregar un segundo anuncio in-feed cada 10 productos

---

## ⚠️ Errores comunes a evitar

### ❌ NO hagas esto:
1. **Muchos anuncios:** No pongas un anuncio cada 2 productos (Google te penaliza)
2. **Anuncios al inicio:** No pongas anuncio antes del 1er producto
3. **Solo in-feed:** Considera también header banner para más ingresos

### ✅ SÍ haz esto:
1. **Empieza con pocos:** Solo in-feed al principio, mide resultados
2. **Colores consistentes:** Que el anuncio se vea parte del diseño
3. **Monitorea métricas:** Revisa AdSense semanalmente

---

## 🎯 Plan de activación recomendado

### **Semana 1: Solo IN-FEED**
- Activa SOLO anuncios in-feed (cada 3 productos)
- Monitorea CTR y feedback de usuarios
- Meta: CTR > 2%

### **Semana 2: Agregar HEADER**
- Si in-feed funciona bien, agrega header banner
- Monitorea si el CTR del in-feed baja
- Si baja mucho, quita el header

### **Semana 3: Optimizar**
- Ajusta frecuencia según métricas
- Prueba diferentes estilos de anuncio
- Maximiza RPM

---

## 📞 Próximos pasos

**Cuando tengas AdSense aprobado:**
1. Lee esta guía completa
2. Crea unidad in-feed en AdSense Dashboard
3. Copia el slot ID
4. Activa en `adsense-config.js`
5. Deploy a producción
6. Verifica que funciona (abre el sitio y busca productos)
7. Monitorea métricas en AdSense

**Si tienes dudas**, vuelve a leer esta guía o checa la documentación oficial:
https://support.google.com/adsense/answer/9274017

---

✅ **El código está listo**. Solo falta que tengas AdSense aprobado y configures el slot ID.
