# 🎯 Configuración Rápida de Google AdSense

**Tiempo estimado:** 5 minutos (después de que Google apruebe tu cuenta)

---

## 📝 Paso 1: Obtener código de cliente AdSense

1. Ve a https://www.google.com/adsense
2. Regístrate/inicia sesión
3. Espera aprobación (1-3 días)
4. Ve a **Cuenta → Configuración**
5. Copia tu código: `ca-pub-XXXXXXXXXXXXXXXX`

---

## 🎨 Paso 2: Crear unidades de anuncio

1. En AdSense Dashboard → **Anuncios → Por unidad de anuncio**
2. Crea 4 unidades:

| Nombre | Tipo | Tamaño | ID (ejemplo) |
|--------|------|--------|--------------|
| PricefloCompare - Header | Display | 728x90 o Responsive | `1234567890` |
| PricefloCompare - Sidebar | Display | 300x250 | `1234567891` |
| PricefloCompare - Results | In-feed | Responsive | `1234567892` |
| PricefloCompare - Footer | Display | 728x90 o Responsive | `1234567893` |

3. **Copia el `data-ad-slot`** de cada una (son números de 10 dígitos)

---

## ⚙️ Paso 3: Configurar en tu proyecto

Abre `frontend/adsense-config.js` y edita:

```javascript
const ADSENSE_CONFIG = {
    // ========================================
    // ⬇️ CAMBIAR ESTOS VALORES ⬇️
    // ========================================
    enabled: true,  // Cambiar a true
    client: 'ca-pub-1234567890123456',  // TU código aquí

    slots: {
        header: '1234567890',       // ID Header
        sidebar: '1234567891',      // ID Sidebar
        betweenResults: '1234567892', // ID Results
        footer: '1234567893'        // ID Footer
    },
    // ========================================

    disabledDomains: [
        'localhost',
        '127.0.0.1',
        'priceflocompare-qa.vercel.app',  // QA
        'priceflocompare-dev.vercel.app'  // Dev
    ]
};
```

---

## ✅ Paso 4: Verificar

### Localmente (antes de deploy):

```bash
python api.py
# Abre: http://localhost:8000/app
```

Deberías ver **placeholders morados** (porque `localhost` está en `disabledDomains`)

### En producción (después de deploy):

1. Deploy a Vercel
2. Abre tu sitio
3. Deberías ver **anuncios reales** de Google
4. Si ves espacios vacíos, abre DevTools (F12) → Console para ver errores

---

## 🐛 Troubleshooting

### No veo anuncios

**Causa 1:** AdSense aún no aprobó tu cuenta
- **Solución:** Espera 1-3 días

**Causa 2:** Código de cliente incorrecto
- **Solución:** Verifica que copiaste bien `ca-pub-XXXXXXXX`

**Causa 3:** IDs de slots incorrectos
- **Solución:** Verifica los números de 10 dígitos

**Causa 4:** Bloqueador de anuncios activo
- **Solución:** Desactiva AdBlocker

**Causa 5:** Dominio está en `disabledDomains`
- **Solución:** Esto es intencional para QA/Local

### Veo error en consola

Abre DevTools (F12) → Console y busca errores:

```
❌ AdSense: Error cargando script
```
→ Código de cliente incorrecto

```
❌ AdSense: Contenedor ad-header no encontrado
```
→ Falta el contenedor HTML (no debería pasar)

---

## 💰 Cuándo empezaré a ganar dinero

- **Primeros días:** $0 (AdSense está aprendiendo)
- **Primera semana:** $0.10 - $2 USD (bajo tráfico inicial)
- **Primer mes:** $10 - $50 USD (con 1K-5K visitas)
- **3-6 meses:** $100 - $500 USD (con 10K-50K visitas)

**Pagos:**
- Mínimo para cobrar: $100 USD
- Método: Transferencia bancaria o cheque
- Frecuencia: Mensual (paga ~21 del mes siguiente)

---

## 🎯 Optimizar ingresos

1. **Más tráfico = más ingresos**
   - SEO (contenido de calidad)
   - Redes sociales
   - Publicidad pagada (Google Ads)

2. **Mejores posiciones**
   - Los ads "above the fold" (arriba) ganan más
   - Sidebar y header son los mejores
   - Entre resultados también funciona bien

3. **Responsive**
   - Asegúrate que los ads se vean bien en móvil
   - 60% del tráfico es móvil

4. **Contenido relevante**
   - Escribe sobre productos caros (electrodomésticos, tecnología)
   - Anuncios se ajustan al contenido

---

## 📊 Ver estadísticas

1. AdSense Dashboard → **Informes**
2. Métricas importantes:
   - **Page RPM:** Ganancia por 1,000 visitas
   - **CTR:** % de usuarios que hacen clic
   - **CPC:** Ganancia por clic

Típico en Colombia:
- RPM: $1 - $5 USD
- CTR: 1-2%
- CPC: $0.10 - $0.50 USD

---

## ❓ FAQ

**¿Puedo usar AdSense con links de afiliados?**
Sí, son complementarios.

**¿Cuántos ads puedo poner?**
Ilimitado, pero 3-4 es óptimo. Más puede molestar al usuario.

**¿AdSense funciona en Colombia?**
Sí, perfectamente.

**¿Necesito empresa registrada?**
No, puedes registrarte como persona natural.

**¿Me pueden banear?**
Sí, si:
- Haces clic en tus propios ads
- Tráfico falso/bots
- Contenido ilegal
- Pides a usuarios hacer clic

---

## 📚 Recursos

- **AdSense Help:** https://support.google.com/adsense
- **AdSense Policies:** https://support.google.com/adsense/answer/48182
- **Optimize Ads:** https://support.google.com/adsense/answer/9183549

---

**¡Listo! Ya tienes AdSense configurado** 🎉

Con 10,000 visitas/mes puedes esperar **$10-30 USD/mes** solo de AdSense.
Combínalo con afiliados para **$200-500 USD/mes** total.
