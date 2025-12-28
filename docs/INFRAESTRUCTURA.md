# 🏗️ Infraestructura de ePriceFlo

Documento técnico que detalla la infraestructura completa del proyecto ePriceFlo.

---

## 📋 Resumen Ejecutivo

| Componente | Servicio | URL/Detalles |
|------------|----------|--------------|
| **🌐 Dominio** | Dominio Principal | `epriceflo.com` |
| **🚀 Backend/API** | Railway | Backend hosting |
| **🗄️ Base de Datos** | Supabase | PostgreSQL managed |
| **💻 Frontend** | Railway (Static) | Servido junto con la API |
| **📊 Analytics** | Google Analytics 4 | ID: `G-T57BY0R646` ✅ Activo |

---

## 🌐 Dominio

### epriceflo.com

- **Propietario**: Germán Díaz (@germandiaz6191)
- **Uso**: Sitio web principal de producción
- **URLs**:
  - `https://epriceflo.com` - Frontend principal
  - `https://epriceflo.com/docs` - Documentación automática de la API (FastAPI)
  - `https://epriceflo.com/api/...` - Endpoints de la API

### DNS y Configuración

El dominio está apuntando a Railway para servir tanto el frontend como la API.

---

## 🚀 Railway - Backend Hosting

### ¿Qué es Railway?

Railway es una plataforma de hosting moderna que simplifica el deployment de aplicaciones.

### Lo que está desplegado en Railway

1. **API FastAPI** (Python)
   - Archivo principal: `api.py`
   - Puerto: Asignado automáticamente por Railway (variable `$PORT`)
   - Start command: `bash start.sh`

2. **Frontend estático**
   - Servido por FastAPI desde `/frontend`
   - HTML, CSS, JavaScript vanilla

### Variables de Entorno en Railway

Railway inyecta automáticamente estas variables:

```bash
# Railway proporciona automáticamente
PORT=<puerto-asignado>              # Puerto dinámico
DATABASE_URL=<url-de-supabase>      # Conexión a Supabase (configurada manualmente)
```

### URLs de Railway

- **Dashboard**: `https://railway.app/dashboard`
- **Proyecto**: PricefloCompare
- **URL de producción**: `epriceflo.com` (dominio custom configurado)
- **URL interna Railway**: `*.railway.app` (también funciona)

### Configuración del Proyecto

Archivo de configuración: `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "bash start.sh",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Script de Inicio

`start.sh`:
```bash
#!/bin/bash
# Railway asigna PORT automáticamente, si no existe usa 8000
PORT=${PORT:-8000}

echo "🚀 Iniciando ePriceFlo API en puerto $PORT..."
uvicorn api:app --host 0.0.0.0 --port $PORT
```

### Plan

- **Plan Actual**: Hobby Plan (Gratis)
- **Límites**:
  - 500 horas/mes de ejecución
  - $5 USD de recursos gratis
  - Múltiples proyectos

---

## 🗄️ Supabase - Base de Datos PostgreSQL

### ¿Qué es Supabase?

Supabase es una alternativa open-source a Firebase que proporciona PostgreSQL managed.

### Configuración

- **Tipo**: PostgreSQL 15
- **Región**: (Verificar en dashboard de Supabase)
- **Acceso**: A través de `DATABASE_URL`

### Conexión

La variable `DATABASE_URL` tiene este formato:

```
postgresql://postgres.[project-id]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

Esta URL está configurada en Railway como variable de entorno.

### Estructura de Base de Datos

```
┌──────────────┐
│  countries   │  🌍 Países (CO, MX, CL, AR, PE)
└──────────────┘
       ↓
┌──────────────┐
│    stores    │  🏪 Tiendas (Éxito, Homecenter)
└──────────────┘  - country_code: VARCHAR(2)
       ↓          - currency: VARCHAR(3)
┌──────────────┐
│   products   │  📦 Productos (globales)
└──────────────┘
       ↓
┌──────────────┐
│price_snapshots│ 💰 Historial de precios
└──────────────┘
```

### Tablas Principales

1. **countries**: Configuración de países soportados
2. **stores**: Tiendas con país y moneda
3. **products**: Catálogo global de productos
4. **price_snapshots**: Histórico de precios por tienda

### Acceso a Supabase

- **Dashboard**: `https://supabase.com/dashboard`
- **SQL Editor**: Para ejecutar queries directamente
- **Table Editor**: Para ver y editar datos visualmente
- **API**: Supabase también proporciona API REST (no la usamos, usamos conexión PostgreSQL directa)

### Plan

- **Plan Actual**: Free Tier
- **Límites**:
  - 500 MB de base de datos
  - 1 GB de transferencia
  - 2 GB de almacenamiento de archivos
  - Proyectos ilimitados

---

## 🔄 Flujo de Deployment

### Desarrollo Local → Producción

```
1. Desarrollo Local
   ├── SQLite local (desarrollo)
   └── python api.py

2. Git Push
   ├── git push origin claude/...
   └── GitHub almacena código

3. Railway Auto-Deploy
   ├── Detecta cambios en GitHub
   ├── Build automático
   ├── Deploy automático
   └── Usa DATABASE_URL → Supabase

4. Supabase
   ├── PostgreSQL en la nube
   └── Datos persistentes

5. epriceflo.com
   └── Usuario accede al sitio
```

### Proceso de Deployment

```bash
# 1. Hacer cambios localmente
git add .
git commit -m "feat: nueva funcionalidad"
git push -u origin claude/branch-name

# 2. Railway detecta el push automáticamente
# 3. Railway hace build y deploy
# 4. El sitio se actualiza en epriceflo.com
```

**Tiempo de deployment**: ~2-3 minutos desde el push hasta que está live.

---

## 🔧 Configuración de Variables de Entorno

### En Railway

Configurar estas variables en Railway Dashboard → Variables:

```bash
# REQUERIDO
DATABASE_URL=postgresql://postgres.[project]:[pass]@...supabase.com:6543/postgres

# OPCIONAL
ENVIRONMENT=production
ALLOWED_ORIGINS=https://epriceflo.com,https://www.epriceflo.com
```

### En Local (Desarrollo)

Archivo `.env`:

```bash
# Usar SQLite local (por defecto)
# DATABASE_URL no es necesario para desarrollo local

# O conectar a Supabase desde local
DATABASE_URL=postgresql://postgres.[project]:[pass]@...supabase.com:6543/postgres

PORT=8000
ENVIRONMENT=development
```

---

## 📊 Monitoreo y Analytics

### Google Analytics 4

**Estado**: ✅ **Ya configurado y funcionando**

- **ID de Producción**: `G-T57BY0R646`
- **Archivo de configuración**: `frontend/analytics.js`
- **Incluido en**: `frontend/index.html` (línea 271)
- **Activación**: Automática cuando `hostname === 'epriceflo.com'`
- **Dashboard**: https://analytics.google.com

#### Eventos que se rastrean automáticamente:

1. **Page views**: Cada visita a una página
2. **view_item**: Cuando un usuario ve un producto
3. **price_comparison**: Cuando compara precios de productos
4. **store_click**: Cuando hace click en un enlace de tienda
5. **search**: Cuando busca productos

#### Verificar que funciona:

1. Ve a Google Analytics → Informes → Tiempo real
2. Visita `https://epriceflo.com`
3. Deberías verte como usuario activo

#### Documentación completa:

Ver: [`docs/ANALYTICS_Y_ADSENSE.md`](ANALYTICS_Y_ADSENSE.md) para:
- Guía completa de configuración
- Cuándo y cómo aplicar a Google AdSense
- Mejores posiciones para anuncios
- Plan de monetización paso a paso

### Railway Logs

Acceder a logs en tiempo real:

```bash
# Desde Railway Dashboard
Project → Deployments → View Logs

# O desde Railway CLI (si está instalado)
railway logs
```

---

## 🔒 Seguridad

### Variables Sensibles

❌ **NUNCA commitear**:
- `DATABASE_URL` con credenciales
- Tokens de API
- Secrets

✅ **Usar**:
- Variables de entorno en Railway
- `.env.example` como plantilla (sin valores reales)
- `.gitignore` para excluir `.env`

### HTTPS

- ✅ Railway proporciona HTTPS automáticamente
- ✅ Dominio custom `epriceflo.com` también usa HTTPS

---

## 💰 Costos

| Servicio | Plan | Costo Mensual |
|----------|------|---------------|
| Railway | Hobby Plan | **$0 USD** (con $5 de créditos) |
| Supabase | Free Tier | **$0 USD** |
| Dominio epriceflo.com | Registro anual | ~$12-15 USD/año |
| **TOTAL** | | **~$1-1.25 USD/mes** |

### Cuándo escalar

**Railway Hobby → Pro** ($20/mes):
- Más de 500 horas de ejecución
- Necesitas más de $5 USD de recursos
- Necesitas múltiples ambientes (staging, producción)

**Supabase Free → Pro** ($25/mes):
- Más de 500 MB de datos
- Necesitas backups diarios
- Más de 2 GB de archivos

---

## 🔄 Migraciones de Base de Datos

### Ejecutar Migraciones en Producción

#### Opción 1: Desde Local Conectado a Supabase

```bash
# 1. Configurar DATABASE_URL en .env apuntando a Supabase
DATABASE_URL="postgresql://postgres.[project]:[pass]@...supabase.com:6543/postgres"

# 2. Ejecutar migración
python migrate_countries.py
```

#### Opción 2: SQL Editor de Supabase

1. Ir a Supabase Dashboard → SQL Editor
2. Copiar el SQL de `INSTRUCCIONES_MIGRACION.md`
3. Ejecutar directamente en Supabase

#### ❌ NO Recomendado

No ejecutar migraciones directamente en Railway (no tiene acceso a scripts Python).

---

## 📞 Soporte y Enlaces

### Railway
- **Dashboard**: https://railway.app/dashboard
- **Documentación**: https://docs.railway.app
- **Community**: https://discord.gg/railway

### Supabase
- **Dashboard**: https://supabase.com/dashboard
- **Documentación**: https://supabase.com/docs
- **Community**: https://discord.supabase.com

### Repositorio
- **GitHub**: https://github.com/germandiaz6191/PricefloCompare
- **Issues**: https://github.com/germandiaz6191/PricefloCompare/issues

---

## 🎯 Resumen para Nuevos Desarrolladores

Si eres nuevo en el proyecto, esto es lo que necesitas saber:

1. **El sitio web** está en `epriceflo.com`
2. **El backend** está en Railway (se actualiza automáticamente con cada push)
3. **La base de datos** está en Supabase (PostgreSQL)
4. **Para desarrollo local**: Solo ejecuta `python api.py` (usa SQLite automáticamente)
5. **Para deployment**: Solo haz `git push` (Railway se encarga del resto)

---

**Última actualización**: 2025-12-28
**Autor**: Germán Díaz
**Proyecto**: ePriceFlo - Comparador de Precios
