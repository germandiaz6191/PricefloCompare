# Guía de Separación del Frontend

Este documento explica cómo separar el frontend de PricefloCompare en un repositorio independiente y las consideraciones arquitectónicas.

## 📋 Tabla de Contenidos

1. [¿Deberías separar el frontend?](#deberías-separar-el-frontend)
2. [Arquitectura con Frontend Separado](#arquitectura-con-frontend-separado)
3. [Configuración de CORS](#configuración-de-cors)
4. [¿Necesitas un API Gateway?](#necesitas-un-api-gateway)
5. [Guía Paso a Paso](#guía-paso-a-paso)
6. [Deployment y Hosting](#deployment-y-hosting)
7. [Mejores Prácticas](#mejores-prácticas)

---

## ¿Deberías separar el frontend?

### ✅ Ventajas de Separar

- **Desarrollo independiente**: Frontend y backend pueden evolucionar por separado
- **Escalamiento independiente**: Servir frontend desde CDN, backend desde servidor
- **Equipos separados**: Diferentes equipos pueden trabajar sin conflictos
- **Deploy independiente**: Actualizar frontend sin redeployar backend
- **Diferentes tecnologías**: Puedes usar frameworks modernos (React, Vue, Next.js)
- **CDN y caché**: Frontend estático se sirve ultra-rápido desde CDN

### ❌ Desventajas

- **Mayor complejidad**: Dos repositorios, dos deploys, dos pipelines CI/CD
- **CORS**: Necesitas configurar correctamente Cross-Origin Resource Sharing
- **Variables de entorno**: URLs del backend deben configurarse por ambiente
- **Debugging más difícil**: Errores pueden ser frontend, backend, o red
- **Overhead inicial**: Setup inicial más complejo

### 🎯 Recomendación para PricefloCompare

**Para tu fase actual (MVP/emprendimiento):**

- ✅ **MANTÉN TODO EN UN REPO** hasta tener al menos 1000-5000 usuarios
- ✅ **Sirve el frontend desde FastAPI** como lo haces ahora
- ✅ **Simplifica el deployment** (un solo servidor)
- ✅ **Itera más rápido** sin complejidad extra

**Separa el frontend cuando:**

- Tengas más de 5000 usuarios activos
- Necesites escalar el frontend independientemente
- Quieras usar un framework complejo (React + Next.js, etc.)
- Tengas equipos separados para frontend/backend

---

## Arquitectura con Frontend Separado

### Arquitectura Actual (Monolito)

```
┌─────────────────────────────────────┐
│         PricefloCompare API         │
│  (FastAPI - Puerto 8000)            │
│                                     │
│  ┌────────────┐   ┌──────────────┐ │
│  │  Backend   │   │   Frontend   │ │
│  │  (Python)  │   │   (HTML/JS)  │ │
│  │            │   │              │ │
│  │  /products │   │  /app        │ │
│  │  /stores   │   │  /reports    │ │
│  │  /stats    │   │  /static/*   │ │
│  └────────────┘   └──────────────┘ │
│                                     │
│  ┌────────────┐                    │
│  │  Database  │                    │
│  │  (SQLite)  │                    │
│  └────────────┘                    │
└─────────────────────────────────────┘
```

**Ventajas:**
- Simple, todo en un servidor
- No hay problemas de CORS
- Fácil de deployar
- Un solo dominio

**Desventajas:**
- Difícil de escalar independientemente
- Frontend y backend acoplados

### Arquitectura Separada (Recomendada para escala)

```
┌─────────────────────┐        ┌─────────────────────┐
│   Frontend Repo     │        │   Backend Repo      │
│   (React/Vue/etc)   │        │   (FastAPI/Python)  │
│                     │        │                     │
│   Port 3000/5173    │◄──────►│   Port 8000         │
│   (Vite/Next.js)    │  HTTP  │   (Uvicorn)         │
│                     │  CORS  │                     │
│   - Componentes     │        │   - API Endpoints   │
│   - Estado          │        │   - DB Logic        │
│   - Routing         │        │   - Scraping        │
└─────────────────────┘        └─────────────────────┘
         │                              │
         │                              │
         ▼                              ▼
┌─────────────────────┐        ┌─────────────────────┐
│   Vercel/Netlify    │        │   Render/Railway    │
│   app.priceflo.com  │        │   api.priceflo.com  │
└─────────────────────┘        └─────────────────────┘
```

**Ventajas:**
- Frontend servido desde CDN global
- Backend escalable independiente
- Equipos pueden trabajar por separado

**Desventajas:**
- Necesitas configurar CORS
- Dos deploys separados
- Mayor complejidad

---

## Configuración de CORS

### ¿Qué es CORS?

CORS (Cross-Origin Resource Sharing) es un mecanismo de seguridad de navegadores que bloquea requests entre diferentes dominios.

**Ejemplo del problema:**
```
Frontend: https://app.priceflo.com (Puerto 3000)
Backend:  https://api.priceflo.com (Puerto 8000)

❌ Sin CORS: El navegador bloquea las peticiones
✅ Con CORS: El backend autoriza las peticiones del frontend
```

### Configuración Actual en PricefloCompare

En `api.py` ya tienes CORS configurado:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ INSEGURO para producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Configuración Recomendada para Producción

```python
# Para desarrollo local
ALLOWED_ORIGINS_DEV = [
    "http://localhost:3000",      # React/Vue dev server
    "http://localhost:5173",      # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Para producción
ALLOWED_ORIGINS_PROD = [
    "https://app.priceflo.com",
    "https://www.priceflo.com",
]

import os
environment = os.getenv("ENVIRONMENT", "development")

allowed_origins = ALLOWED_ORIGINS_DEV if environment == "development" else ALLOWED_ORIGINS_PROD

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### Variables de Entorno en el Frontend

Crea un archivo `.env` en el frontend:

```bash
# .env.development
VITE_API_URL=http://localhost:8000

# .env.production
VITE_API_URL=https://api.priceflo.com
```

En tu código JavaScript:

```javascript
// frontend/src/config.js
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export { API_URL };
```

---

## ¿Necesitas un API Gateway?

### ¿Qué es un API Gateway?

Un API Gateway es un servidor intermediario que:
- Recibe todas las requests del frontend
- Las redirige al backend apropiado
- Agrega funcionalidades como:
  - Rate limiting
  - Autenticación centralizada
  - Logging y monitoring
  - Caché
  - Load balancing

### Arquitectura con API Gateway

```
┌─────────────┐
│  Frontend   │
│             │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  API Gateway    │  ← Kong, AWS API Gateway, Nginx
│  (Puerto 443)   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│Backend │ │Backend │
│   #1   │ │   #2   │
└────────┘ └────────┘
```

### ¿Necesitas API Gateway para PricefloCompare?

**NO lo necesitas si:**
- ❌ Tienes menos de 100,000 usuarios
- ❌ Solo tienes un backend
- ❌ No necesitas rate limiting avanzado
- ❌ No tienes microservicios

**SÍ lo necesitas si:**
- ✅ Tienes múltiples microservicios
- ✅ Necesitas rate limiting por usuario
- ✅ Quieres caché centralizado
- ✅ Más de 1 millón de requests/día

### Recomendación

**Para tu caso actual:** ❌ **NO necesitas API Gateway**

**Usa solo:**
```
Frontend (Vercel) → Backend (Render/Railway)
```

**Considera API Gateway cuando:**
- Tengas más de 100K usuarios
- Necesites múltiples servicios (scraping separado, etc.)
- Quieras monetizar con rate limits por tier

**Opciones de API Gateway (futuro):**
- **Kong** (Open source, potente)
- **AWS API Gateway** (Managed, fácil)
- **Nginx** (DIY, más control)
- **Traefik** (Modern, containerizado)

---

## Guía Paso a Paso

### Opción 1: Mismo Repo, Carpetas Separadas (Recomendado para MVP)

```
PricefloCompare/
├── backend/
│   ├── api.py
│   ├── database.py
│   ├── scrapers/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

**Ventajas:**
- Todo versionado junto
- Fácil de sincronizar cambios
- Un solo repositorio

### Opción 2: Repositorios Completamente Separados

#### Crear Repo Backend: `PricefloCompare-API`

```bash
# Clonar repo actual
git clone <tu-repo> PricefloCompare-API
cd PricefloCompare-API

# Eliminar frontend
rm -rf frontend/
git add -A
git commit -m "Backend: Separar frontend"

# Actualizar api.py para CORS
# (Ver sección de CORS arriba)
```

#### Crear Repo Frontend: `PricefloCompare-App`

```bash
# Crear nuevo proyecto con Vite + React
npm create vite@latest PricefloCompare-App -- --template react

cd PricefloCompare-App

# Copiar archivos del frontend actual
# Adaptar a componentes React/Vue
```

### Migrar a React (Ejemplo)

**Tu código actual (Vanilla JS):**
```javascript
// frontend/app.js
async function loadProducts() {
    const response = await fetch(`${API_URL}/products`);
    const products = await response.json();
    displayProducts(products);
}
```

**En React:**
```jsx
// src/components/Products.jsx
import { useState, useEffect } from 'react';
import { API_URL } from '../config';

function Products() {
    const [products, setProducts] = useState([]);

    useEffect(() => {
        fetch(`${API_URL}/products`)
            .then(res => res.json())
            .then(data => setProducts(data));
    }, []);

    return (
        <div className="products-grid">
            {products.map(product => (
                <ProductCard key={product.id} product={product} />
            ))}
        </div>
    );
}
```

---

## Deployment y Hosting

### Backend (API)

**Opciones Recomendadas:**

1. **Render.com** (Fácil, free tier)
   ```yaml
   # render.yaml
   services:
     - type: web
       name: priceflo-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn api:app --host 0.0.0.0 --port $PORT
   ```

2. **Railway.app** (Muy simple)
   - Conecta GitHub repo
   - Auto-detecta Python
   - Deploy automático

3. **AWS/GCP** (Más control, más caro)
   - AWS Elastic Beanstalk
   - Google Cloud Run

### Frontend

**Opciones Recomendadas:**

1. **Vercel** (Mejor para Next.js/React)
   ```bash
   # Despliegue automático
   vercel
   ```

2. **Netlify** (Mejor para sitios estáticos)
   ```toml
   # netlify.toml
   [build]
     command = "npm run build"
     publish = "dist"
   ```

3. **Cloudflare Pages** (CDN global, gratis)
   - Push a GitHub
   - Auto-deploy

### Ejemplo de URLs

```
Production:
  Frontend: https://app.priceflo.com (Vercel)
  Backend:  https://api.priceflo.com (Render)

Staging:
  Frontend: https://staging.priceflo.com
  Backend:  https://api-staging.priceflo.com
```

---

## Mejores Prácticas

### 1. Variables de Entorno

**Backend (.env):**
```bash
DATABASE_URL=postgresql://...
ENVIRONMENT=production
ALLOWED_ORIGINS=https://app.priceflo.com
SECRET_KEY=your-secret-key
```

**Frontend (.env):**
```bash
VITE_API_URL=https://api.priceflo.com
VITE_ENVIRONMENT=production
```

### 2. Versionamiento de API

```python
# api.py
app = FastAPI(
    title="PricefloCompare API",
    version="1.0.0"  # Incrementa en breaking changes
)

# Endpoints versionados
@app.get("/v1/products")
@app.get("/v2/products")  # Nueva versión
```

### 3. Manejo de Errores

```javascript
// frontend
async function fetchProducts() {
    try {
        const res = await fetch(`${API_URL}/products`);

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }

        return await res.json();
    } catch (error) {
        console.error('Error fetching products:', error);
        // Mostrar mensaje al usuario
        showErrorToast('No se pudieron cargar los productos');
        return [];
    }
}
```

### 4. Testing

**Backend:**
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Frontend:**
```javascript
// tests/Products.test.jsx
import { render, screen } from '@testing-library/react';
import Products from './Products';

test('renders products', async () => {
    render(<Products />);
    const products = await screen.findAllByRole('article');
    expect(products).toHaveLength(5);
});
```

### 5. Monitoreo

```python
# api.py
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## Resumen y Decisión Final

### Para PricefloCompare HOY:

✅ **MANTÉN EL MONOLITO** (Backend + Frontend en un repo)

**Razones:**
1. Más rápido para iterar
2. Menos complejidad operacional
3. Un solo deploy
4. No hay necesidad real de separar aún

### Separa el Frontend CUANDO:

1. **Tengas más de 5,000 usuarios activos**
2. **Necesites optimización de CDN**
3. **Quieras usar framework complejo** (Next.js con SSR, etc.)
4. **Equipos separados de frontend/backend**

### Si decides separar, usa:

- **Frontend:** Vercel (Next.js) o Netlify (Vite)
- **Backend:** Render o Railway
- **NO uses API Gateway** (todavía)
- **Configura CORS correctamente**
- **Variables de entorno para URLs**

---

¿Preguntas? Consulta la [documentación de FastAPI](https://fastapi.tiangolo.com/) y [Vercel](https://vercel.com/docs).
