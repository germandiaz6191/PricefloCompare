# 🚀 Guía de Deploy - PricefloCompare

Esta guía te llevará paso a paso para publicar tu aplicación en **Vercel** (gratis) con múltiples ambientes.

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configurar Google AdSense](#configurar-google-adsense)
3. [Deploy a Vercel](#deploy-a-vercel)
4. [Configurar Ambientes](#configurar-ambientes)
5. [Configurar Dominio Custom](#configurar-dominio-custom)
6. [Variables de Entorno](#variables-de-entorno)
7. [Verificar Deploy](#verificar-deploy)

---

## 1. Requisitos Previos

### Crear cuenta en Vercel

1. Ve a https://vercel.com
2. Click en "Sign Up"
3. Selecciona "Continue with GitHub"
4. Autoriza Vercel para acceder a tus repositorios

### Instalar Vercel CLI (Opcional)

```bash
npm install -g vercel
# o
pnpm install -g vercel
# o
yarn global add vercel
```

---

## 2. Configurar Google AdSense

### 2.1. Registrarse en AdSense

1. Ve a https://www.google.com/adsense
2. Click en **"Comenzar"**
3. Completa el formulario:
   - URL de tu sitio web (puedes usar tu dominio o `priceflocompare.vercel.app`)
   - Información de pago
   - Dirección postal

4. **IMPORTANTE:** Google necesita revisar tu sitio (toma 1-3 días)
5. Una vez aprobado, obtendrás tu **código de cliente**

### 2.2. Obtener tu código de cliente

1. En AdSense Dashboard → **"Cuenta" → "Configuración"**
2. Verás tu código en formato: `ca-pub-XXXXXXXXXXXXXXXX`
3. **Copia este código** (lo necesitarás en el paso siguiente)

### 2.3. Crear unidades de anuncio

1. En AdSense Dashboard → **"Anuncios" → "Por unidad de anuncio"**
2. Click en **"Crear nueva unidad de anuncio"**
3. Crea estas 4 unidades:

**Unidad 1: Header Banner**
- Nombre: `PricefloCompare - Header`
- Tipo: **Display**
- Tamaño: **Responsive** o `728x90`
- Click **"Crear"** y copia el `data-ad-slot` (ej: `1234567890`)

**Unidad 2: Sidebar**
- Nombre: `PricefloCompare - Sidebar`
- Tipo: **Display**
- Tamaño: **300x250** (Medium Rectangle)
- Click **"Crear"** y copia el `data-ad-slot`

**Unidad 3: Entre Resultados**
- Nombre: `PricefloCompare - Results`
- Tipo: **In-feed**
- Tamaño: **Responsive**
- Click **"Crear"** y copia el `data-ad-slot`

**Unidad 4: Footer**
- Nombre: `PricefloCompare - Footer`
- Tipo: **Display**
- Tamaño: **Responsive** o `728x90`
- Click **"Crear"** y copia el `data-ad-slot`

### 2.4. Configurar AdSense en tu proyecto

1. Abre el archivo `frontend/adsense-config.js`
2. Reemplaza los valores:

```javascript
const ADSENSE_CONFIG = {
    enabled: true,  // ⬅️ CAMBIAR A true
    client: 'ca-pub-XXXXXXXXXXXXXXXX',  // ⬅️ TU CÓDIGO AQUÍ

    slots: {
        header: '1234567890',       // ⬅️ ID del slot Header
        sidebar: '1234567891',      // ⬅️ ID del slot Sidebar
        betweenResults: '1234567892', // ⬅️ ID del slot Results
        footer: '1234567893'        // ⬅️ ID del slot Footer
    },
    // ...
};
```

3. **Guarda el archivo**

### 2.5. Verificar que funciona localmente (opcional)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python api.py

# Abrir en navegador
# http://localhost:8000/app
```

Verás placeholders de anuncios si `enabled: false` en local.

---

## 3. Deploy a Vercel

### Opción A: Deploy desde GitHub (Recomendado)

#### 3.1. Pushear código a GitHub

```bash
# Si aún no tienes repo remoto
git init
git add .
git commit -m "Initial commit with AdSense configured"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/PricefloCompare.git
git push -u origin main
```

#### 3.2. Importar proyecto en Vercel

1. Ve a https://vercel.com/dashboard
2. Click **"Add New..." → "Project"**
3. Selecciona tu repositorio **"PricefloCompare"**
4. Click **"Import"**

#### 3.3. Configurar proyecto

**Build & Development Settings:**
- Framework Preset: **Other**
- Root Directory: `./`
- Build Command: (dejar vacío)
- Output Directory: `frontend`
- Install Command: `pip install -r requirements.txt`

#### 3.4. Variables de entorno (opcional por ahora)

Por ahora no es necesario. Las configuraremos después.

#### 3.5. Deploy

1. Click **"Deploy"**
2. Espera 1-2 minutos
3. ✅ Tu sitio estará en: `https://priceflocompare.vercel.app`

---

### Opción B: Deploy con CLI

```bash
# Login
vercel login

# Deploy
vercel

# Seguir el wizard:
# - Set up and deploy? Yes
# - Which scope? (tu cuenta)
# - Link to existing project? No
# - Project name? priceflocompare
# - In which directory? ./
# - Override settings? No

# Deploy a producción
vercel --prod
```

---

## 4. Configurar Ambientes

Ahora vamos a configurar 3 ambientes:
- **Producción:** `priceflocompare.com` (o `.vercel.app`)
- **QA/Staging:** `priceflocompare-qa.vercel.app`
- **Preview:** Auto por cada PR

### 4.1. Crear branch staging

```bash
git checkout -b staging
git push origin staging
```

### 4.2. Configurar en Vercel Dashboard

1. Ve a tu proyecto en Vercel
2. **Settings → Git**
3. Configurar:

```
Production Branch: main ✓
```

4. En **"Preview Deployments"** → **"All branches"**

Ahora:
- Push a `main` → Deploy a producción
- Push a `staging` → Deploy a `priceflocompare-git-staging.vercel.app`
- Pull Request → Preview automático

---

## 5. Configurar Dominio Custom

### 5.1. Comprar dominio

1. Ve a **Namecheap.com** o **Cloudflare**
2. Busca: `priceflocompare.com`
3. Compra ($10-15 USD/año)

### 5.2. Agregar dominio en Vercel

1. En Vercel → Tu proyecto → **Settings → Domains**
2. Click **"Add Domain"**
3. Ingresa: `priceflocompare.com`
4. Vercel te dará DNS records:

```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### 5.3. Configurar DNS en Namecheap

1. En Namecheap → **Domain List → Manage**
2. Click **"Advanced DNS"**
3. Agregar records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | 76.76.21.21 | Automatic |
| CNAME | www | cname.vercel-dns.com | Automatic |

4. **Save Changes**
5. Esperar 5-30 minutos (propagación DNS)

### 5.4. Verificar SSL

1. En Vercel, espera a que aparezca ✅ junto al dominio
2. SSL se activa automáticamente (Let's Encrypt)
3. Visita `https://priceflocompare.com` (debe funcionar)

---

## 6. Variables de Entorno

### 6.1. Configurar en Vercel Dashboard

1. Vercel → Tu proyecto → **Settings → Environment Variables**
2. Agregar estas variables:

**Para PRODUCCIÓN:**

| Key | Value | Environment |
|-----|-------|-------------|
| `ENV` | `production` | Production |
| `GOOGLE_ADSENSE_CLIENT` | `ca-pub-XXXXXXXX` | Production |
| `ADSENSE_ENABLED` | `true` | Production |
| `CORS_ORIGINS` | `https://priceflocompare.com` | Production |

**Para STAGING/QA:**

| Key | Value | Environment |
|-----|-------|-------------|
| `ENV` | `staging` | Preview |
| `ADSENSE_ENABLED` | `false` | Preview |
| `CORS_ORIGINS` | `*` | Preview |

### 6.2. Variables locales (.env)

Crea archivo `.env` en la raíz:

```bash
cp .env.example .env
```

Edita `.env`:

```bash
ENV=local
GOOGLE_ADSENSE_CLIENT=ca-pub-XXXXXXXXXXXXXXXX
ADSENSE_ENABLED=false  # false en local para no afectar métricas
```

**IMPORTANTE:** `.env` ya está en `.gitignore` (nunca se sube a GitHub)

---

## 7. Verificar Deploy

### 7.1. Checklist de verificación

Abre tu sitio y verifica:

**✅ Frontend:**
- [ ] Sitio carga correctamente
- [ ] Logo se ve
- [ ] Búsqueda funciona
- [ ] Stats se cargan

**✅ AdSense:**
- [ ] Placeholder de ads visible (si `enabled: false` en local)
- [ ] Ads reales visibles (si `enabled: true` en prod)
- [ ] No hay errores en consola
- [ ] Badge de "Transparencia" en footer

**✅ API:**
- [ ] `/docs` muestra Swagger
- [ ] `/api/products` retorna JSON
- [ ] `/api/stats` funciona

**✅ Responsive:**
- [ ] Se ve bien en móvil
- [ ] Se ve bien en tablet
- [ ] Se ve bien en desktop

### 7.2. Ver logs

```bash
# Desde CLI
vercel logs

# O en Dashboard
# Vercel → Tu proyecto → Deployments → Click en deployment → Logs
```

### 7.3. Rollback si hay problemas

```bash
# CLI
vercel rollback

# O en Dashboard
# Deployments → Hover sobre versión anterior → "Promote to Production"
```

---

## 8. Workflow de Desarrollo

```bash
# 1. Desarrollar en local
git checkout -b feature/nueva-feature
# ... hacer cambios ...
python api.py  # Probar en localhost:8000

# 2. Commit y push
git add .
git commit -m "feat: nueva feature"
git push origin feature/nueva-feature

# 3. Crear Pull Request en GitHub
# → Vercel crea preview automático
# → Link aparece en el PR

# 4. Si todo está bien → Merge a staging
git checkout staging
git merge feature/nueva-feature
git push origin staging
# → Deploy automático a priceflocompare-git-staging.vercel.app

# 5. Testing en QA → Si pasa → Merge a main
git checkout main
git merge staging
git push origin main
# → Deploy automático a PRODUCCIÓN
```

---

## 9. Comandos Útiles

```bash
# Ver deployments
vercel ls

# Ver logs en tiempo real
vercel logs --follow

# Deploy manual
vercel --prod

# Eliminar deployment
vercel remove <deployment-url>

# Ver dominios
vercel domains ls

# Alias manual
vercel alias set <deployment-url> priceflocompare.com
```

---

## 10. Troubleshooting

### Los anuncios no se muestran

1. **Verifica que `enabled: true`** en `adsense-config.js`
2. **Verifica código de cliente** correcto
3. **Adblocker:** Desactiva tu bloqueador de anuncios
4. **Pendiente de aprobación:** Google tarda 1-3 días en aprobar
5. **Consola de errores:** Abre DevTools (F12) y revisa Console

### Build falla en Vercel

1. Revisa logs en Vercel Dashboard
2. Verifica `requirements.txt` tenga todas las dependencias
3. Verifica `vercel.json` esté bien configurado

### 404 en rutas

1. Verifica `vercel.json` tenga las rutas correctas
2. Verifica archivos estén en directorio correcto (`frontend/`)

### Base de datos SQLite no persiste

Vercel Serverless **NO soporta SQLite persistente**. Opciones:

1. **Railway** (gratis) con Postgres
2. **Supabase** (gratis) con Postgres
3. **PlanetScale** (gratis) con MySQL

Para migrar a Postgres:
```bash
# Instalar
pip install psycopg2-binary

# Variable de entorno en Vercel
DATABASE_URL=postgresql://user:pass@host:5432/db
```

---

## 11. Monitoreo y Analytics

### Google Analytics (Opcional)

1. Crear cuenta en https://analytics.google.com
2. Obtener ID: `G-XXXXXXXXXX`
3. Agregar a `frontend/index.html`:

```html
<head>
    <!-- ... -->
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
    </script>
</head>
```

### Vercel Analytics (Gratis)

1. Vercel → Tu proyecto → **Analytics → Enable**
2. ¡Listo! Métricas automáticas

---

## 12. Costos

```
Dominio .com: $12 USD/año
Vercel: $0 (hasta 100GB bandwidth)
AdSense: $0 (te pagan a ti)
SSL: $0 (Let's Encrypt incluido)

TOTAL: $12 USD/año (~$50,000 COP/año)
```

---

## 13. Siguiente Pasos

- [ ] Registrarse en programas de afiliados
- [ ] Crear contenido SEO (blog)
- [ ] Redes sociales (Instagram, TikTok)
- [ ] Configurar alertas de precio
- [ ] A/B testing de CTAs
- [ ] Migrar a DB PostgreSQL (si necesitas persistencia)

---

## 🎉 ¡Listo!

Tu aplicación ya está publicada con:
- ✅ Dominio profesional
- ✅ HTTPS automático
- ✅ Google AdSense configurado
- ✅ Ambientes de QA y producción
- ✅ Deploy automático por Git

**¿Preguntas?** Revisa la documentación de Vercel: https://vercel.com/docs

---

**Última actualización:** 2025-11-22
