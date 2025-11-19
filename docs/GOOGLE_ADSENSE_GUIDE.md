# 💰 Guía Completa de Google AdSense

Google AdSense es la forma MÁS FÁCIL de monetizar mientras creces. No requiere tráfico mínimo y te pagan solo por mostrar anuncios.

---

## 📋 ¿Qué es Google AdSense?

**Cómo funciona:**
1. Google muestra anuncios en tu sitio
2. Te pagan por **impresiones** (CPM) y **clics** (CPC)
3. Google optimiza automáticamente qué anuncios mostrar
4. Pago mensual (mínimo $100 USD para cobrar)

**Ingresos típicos en Colombia:**
- **CPM:** $1-3 USD por cada 1,000 impresiones
- **CPC:** $0.10-0.50 USD por clic
- **CTR:** 1-2% (de 100 visitantes, 1-2 hacen clic)

**Ejemplo:**
```
10,000 visitas/mes:
- 10,000 impresiones × $2 CPM = $20 USD
- 150 clics × $0.20 CPC = $30 USD
Total: $50 USD/mes
```

---

## 🚀 Registro en Google AdSense (15 minutos)

### PASO 1: Requisitos Previos

**Antes de registrarte necesitas:**

✅ **Sitio web publicado y funcionando**
- Dominio propio (recomendado) o subdominio
- Contenido original (no copias)
- Política de privacidad
- Al menos 10-15 páginas/productos

⚠️ **NO aceptan:**
- Localhost
- IPs (192.168.x.x)
- Sitios sin HTTPS
- Contenido ilegal/adulto

**Opciones para publicar rápido:**

1. **Vercel (GRATIS, 5 minutos):**
   ```bash
   npm install -g vercel
   vercel
   ```
   Te da: `https://priceflo-compare.vercel.app`

2. **Netlify (GRATIS):**
   - Conectar GitHub repo
   - Deploy automático
   - Te da: `https://priceflo.netlify.app`

3. **Railway (GRATIS):**
   - Deploy de FastAPI + frontend
   - Base de datos incluida

---

### PASO 2: Crear Cuenta AdSense

1. **Ir a:** https://www.google.com/adsense/

2. **Hacer clic en "Comenzar"**

3. **Completar formulario:**
   - URL de tu sitio: `https://tu-sitio.vercel.app`
   - Email de Google
   - País: Colombia
   - ¿Recibir consejos?: Sí (recomendado)

4. **Aceptar términos y condiciones**

5. **Conectar cuenta de pago:**
   - Nombre completo
   - Dirección en Colombia
   - Teléfono

6. **Verificar número de teléfono** (SMS)

---

### PASO 3: Verificar tu Sitio

Google te dará un **código de verificación** que debes pegar en tu sitio.

**Ejemplo del código:**
```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456"
     crossorigin="anonymous"></script>
```

**Dónde pegarlo en PricefloCompare:**

Abre `frontend/index.html` y agrégalo en el `<head>`:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PricefloCompare</title>

    <!-- Google AdSense Verificación -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-TU_ID_AQUI"
         crossorigin="anonymous"></script>

    <link rel="stylesheet" href="/static/style.css">
</head>
```

**Guardar y hacer deploy:**
```bash
git add frontend/index.html
git commit -m "Añadir verificación de AdSense"
git push
```

---

### PASO 4: Esperar Aprobación

- **Tiempo:** 1-3 días (a veces hasta 2 semanas)
- **Recibirás email** cuando estés aprobado
- Mientras tanto, **genera tráfico y contenido**

**Para aumentar chances de aprobación:**
- Agrega más productos (al menos 20-30)
- Crea blog con guías ("Mejores lavadoras 2025")
- Política de privacidad (ver template abajo)
- Términos y condiciones
- Página "Sobre nosotros"

---

## 📍 Dónde Colocar los Anuncios

### Ubicaciones con Mejor Rendimiento:

**1. Banner superior (Leaderboard 728x90)**
```
┌──────────────────────────────────┐
│        [ ANUNCIO BANNER ]        │
└──────────────────────────────────┘
┌──────────────────────────────────┐
│         Header / Logo            │
│     Barra de búsqueda            │
└──────────────────────────────────┘
```

**2. Entre resultados (cada 3-5 productos)**
```
┌──────────┐  ┌──────────┐  ┌──────────┐
│Producto 1│  │Producto 2│  │Producto 3│
└──────────┘  └──────────┘  └──────────┘

┌────────────────────────────────────┐
│      [ ANUNCIO RESPONSIVE ]        │
└────────────────────────────────────┘

┌──────────┐  ┌──────────┐  ┌──────────┐
│Producto 4│  │Producto 5│  │Producto 6│
└──────────┘  └──────────┘  └──────────┘
```

**3. Sidebar (300x250 o 300x600)**
```
┌─────────────┐  ┌──────────┐
│             │  │          │
│  Productos  │  │ ANUNCIO  │
│             │  │ 300x250  │
│             │  │          │
└─────────────┘  └──────────┘
```

**4. Antes del footer**

---

## 💻 Implementación en PricefloCompare

### Código de Anuncio Básico

```html
<!-- Anuncio Responsive (se adapta a cualquier tamaño) -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-TU_ID_AQUI"
     data-ad-slot="TU_SLOT_AQUI"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
```

---

### Anuncio en Header (Banner Superior)

Edita `frontend/index.html`:

```html
<body>
    <div class="container">
        <!-- Anuncio Header -->
        <div class="ad-banner-top">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-TU_ID"
                 crossorigin="anonymous"></script>
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-TU_ID"
                 data-ad-slot="TU_SLOT"
                 data-ad-format="horizontal"
                 data-full-width-responsive="true"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({});
            </script>
        </div>

        <!-- Hero Header -->
        <header class="hero">
        ...
```

Estilos en `frontend/style.css`:

```css
.ad-banner-top {
    max-width: 1200px;
    margin: 0 auto 20px;
    padding: 16px;
    background: var(--gray-50);
    border-radius: 8px;
    text-align: center;
}

.ad-banner-top ins {
    display: block !important;
}
```

---

### Anuncio Entre Productos

Modifica `frontend/app.js` en la función `displayProducts()`:

```javascript
async function displayProducts(products) {
    const grid = document.getElementById('products');

    for (let i = 0; i < products.length; i++) {
        const product = products[i];

        // Crear card del producto
        const card = await createProductCard(product);
        grid.appendChild(card);

        // Insertar anuncio cada 3 productos
        if ((i + 1) % 3 === 0 && i < products.length - 1) {
            const adContainer = document.createElement('div');
            adContainer.className = 'ad-in-feed';
            adContainer.innerHTML = `
                <ins class="adsbygoogle"
                     style="display:block"
                     data-ad-client="ca-pub-TU_ID"
                     data-ad-slot="TU_SLOT"
                     data-ad-format="fluid"
                     data-ad-layout-key="-6t+ed+2i-1n-4w"></ins>
                <script>
                     (adsbygoogle = window.adsbygoogle || []).push({});
                </script>
            `;
            grid.appendChild(adContainer);
        }
    }
}
```

Estilos:

```css
.ad-in-feed {
    grid-column: 1 / -1; /* Ocupa todo el ancho */
    margin: 20px 0;
    padding: 20px;
    background: var(--gray-50);
    border-radius: 12px;
    min-height: 250px;
}
```

---

### Anuncio en Sidebar (Desktop)

```html
<!-- En index.html, dentro de .container -->
<div class="main-content">
    <div class="content-left">
        <!-- Productos aquí -->
        <div id="products" class="products-grid"></div>
    </div>

    <aside class="sidebar-right">
        <!-- Anuncio Sticky -->
        <div class="ad-sidebar">
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-TU_ID"
                 data-ad-slot="TU_SLOT"
                 data-ad-format="rectangle"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({});
            </script>
        </div>
    </aside>
</div>
```

CSS:

```css
.main-content {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 24px;
    max-width: 1400px;
    margin: 0 auto;
}

.sidebar-right {
    position: sticky;
    top: 20px;
    height: fit-content;
}

.ad-sidebar {
    background: var(--gray-50);
    padding: 16px;
    border-radius: 12px;
    min-height: 600px;
}

@media (max-width: 1024px) {
    .main-content {
        grid-template-columns: 1fr;
    }

    .sidebar-right {
        display: none; /* Ocultar en móvil */
    }
}
```

---

## ⚠️ Políticas de AdSense (IMPORTANTE)

### ❌ Prohibido:

1. **Hacer clic en tus propios anuncios**
   - Google te banea permanentemente
   - Usa VPN/incógnito tampoco funciona (te detectan)

2. **Pedir clics**
   - "Haz clic en los anuncios"
   - "Apóyanos haciendo clic"

3. **Colocar más de 3 anuncios por página**
   - Máximo 3 anuncios display
   - 1 anuncio de búsqueda
   - 2 enlaces patrocinados

4. **Contenido prohibido:**
   - Adulto, violencia, drogas
   - Productos falsificados
   - Copyright infringement

### ✅ Permitido:

- Anuncios + afiliados (Amazon, etc.)
- Múltiples sitios en la misma cuenta
- Anuncios responsive
- Auto ads (Google decide dónde colocarlos)

---

## 📊 Optimización para Más Ingresos

### 1. Auto Ads (Recomendado)

Deja que Google decida dónde colocar anuncios:

```html
<head>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-TU_ID"
         crossorigin="anonymous"></script>

    <!-- Auto Ads -->
    <script>
        (adsbygoogle = window.adsbygoogle || []).push({
            google_ad_client: "ca-pub-TU_ID",
            enable_page_level_ads: true
        });
    </script>
</head>
```

### 2. Formatos con Mejor CPM

- **Responsive Display:** Se adapta, mayor fill rate
- **Large Rectangle (336x280):** Alto CTR
- **Leaderboard (728x90):** Visible en header
- **Medium Rectangle (300x250):** El más común

### 3. Tráfico de Calidad

AdSense paga más por:
- Usuarios de USA/Europa/Canada ($5-10 CPM)
- Usuarios de Colombia ($1-3 CPM)
- Tráfico orgánico (SEO) > tráfico de redes sociales
- Desktop > Mobile (generalmente)

---

## 💸 Pagos y Retiros

### Configurar Método de Pago

**En Colombia puedes usar:**

1. **Transferencia Bancaria** (Western Union)
   - Comisión: ~$3-5 USD
   - Tiempo: 7-10 días hábiles
   - Requisito: Cuenta bancaria colombiana

2. **Cheque (No recomendado)**
   - Demora 4-6 semanas
   - Costos altos de cobro

**Configuración:**
1. AdSense → Pagos → Métodos de pago
2. Agregar método de pago
3. Verificar con depósito de prueba ($1-2 USD)

### Umbral de Pago

- **Mínimo:** $100 USD
- **Frecuencia:** Mensual (entre el 21-26 de cada mes)
- **Acumulativo:** Si no llegas a $100, se acumula para el próximo mes

**Ejemplo:**
```
Enero: $40 USD (no se paga)
Febrero: $60 USD → Total $100 USD → ¡Pago!
```

---

## 🔧 Verificación de Dirección (PIN)

**Cuando llegues a $10 USD**, Google enviará un PIN por correo postal a tu dirección.

1. **Esperar carta** (4-6 semanas a Colombia)
2. **Ingresar PIN** en AdSense → Pagos
3. **Verificado** → Ya puedes recibir pagos

**Si no llega:**
- Pedir reenvío (hasta 3 veces)
- Verificación online (después de 4 meses)

---

## 📈 Proyección de Ingresos

### Escenario Conservador

| Visitas/mes | Impresiones | Clics | CPM | CPC | Total/mes |
|-------------|-------------|-------|-----|-----|-----------|
| 1,000 | 1,000 | 15 | $2 | $0.20 | $5 |
| 5,000 | 5,000 | 75 | $2 | $0.20 | $25 |
| 10,000 | 10,000 | 150 | $2 | $0.20 | $50 |
| 25,000 | 25,000 | 375 | $2 | $0.20 | $125 |
| 50,000 | 50,000 | 750 | $2.5 | $0.25 | $313 |
| 100,000 | 100,000 | 1,500 | $3 | $0.30 | $750 |

### Factores que Aumentan CPM

✅ Nicho de tecnología/electrodomésticos (tu caso): +20-30%
✅ Usuarios logged in (Google sabe más): +15%
✅ Sitio HTTPS: +10%
✅ Velocidad rápida: +5-10%
✅ Contenido original: +20%

---

## 🚀 Plan de Acción

### Esta Semana

- [ ] Publicar sitio en Vercel/Netlify
- [ ] Registrarse en AdSense
- [ ] Agregar código de verificación
- [ ] Crear política de privacidad

### Siguiente Semana

- [ ] Esperar aprobación
- [ ] Implementar primer anuncio (header)
- [ ] Monitorear rendimiento

### Primer Mes

- [ ] Optimizar ubicaciones
- [ ] Probar Auto Ads
- [ ] Llegar a $10 (PIN)

---

## 📄 Template de Política de Privacidad

Crea `frontend/privacy.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Política de Privacidad - PricefloCompare</title>
</head>
<body>
    <h1>Política de Privacidad</h1>

    <h2>Google AdSense</h2>
    <p>Este sitio utiliza Google AdSense, un servicio de publicidad de Google Inc.</p>

    <p>Google utiliza cookies para mostrar anuncios basados en visitas previas del usuario.</p>

    <p>Puedes desactivar las cookies de publicidad personalizada en:
    <a href="https://www.google.com/settings/ads">Configuración de anuncios de Google</a></p>

    <h2>Cookies</h2>
    <p>Utilizamos cookies para mejorar tu experiencia y para mostrar publicidad relevante.</p>

    <h2>Datos Recopilados</h2>
    <ul>
        <li>Páginas visitadas</li>
        <li>Productos buscados</li>
        <li>Ubicación aproximada (país/ciudad)</li>
    </ul>

    <h2>Contacto</h2>
    <p>Para preguntas sobre esta política: contacto@priceflo.com</p>
</body>
</html>
```

Agregar link en footer de `index.html`:

```html
<a href="/privacy.html">Política de Privacidad</a>
```

---

## ✅ Checklist de Implementación

**Antes de aplicar:**
- [ ] Sitio publicado con dominio
- [ ] HTTPS habilitado
- [ ] Política de privacidad
- [ ] Al menos 10-15 productos
- [ ] Contenido original (no copias)

**Durante aprobación:**
- [ ] Código de verificación instalado
- [ ] Sitio activo y funcionando
- [ ] Tráfico orgánico (aunque sea poco)

**Después de aprobación:**
- [ ] Primer anuncio en header
- [ ] Auto Ads activado
- [ ] Monitorear reportes diarios
- [ ] Optimizar ubicaciones

---

## 🎯 Resumen

**AdSense es ideal para ti porque:**
- ✅ No requiere tráfico mínimo (aunque más es mejor)
- ✅ Ingresos pasivos desde el día 1
- ✅ Complementa perfectamente a afiliados
- ✅ Google optimiza automáticamente
- ✅ Pagos confiables cada mes

**Proyección realista:**
```
Mes 1-3:    1,000-5,000 visitas  →  $5-25 USD/mes
Mes 4-6:    5,000-10,000 visitas → $25-50 USD/mes
Mes 7-12:   10,000-25,000 visitas → $50-150 USD/mes
Año 2:      25,000-100,000 visitas → $150-750 USD/mes
```

**Combinado con afiliados:**
```
AdSense: $100/mes
Afiliados: $300/mes
Total: $400/mes ($1,650,000 COP/mes) 🎉
```

---

**¿Preguntas?** Lee la [documentación oficial de AdSense](https://support.google.com/adsense/)
