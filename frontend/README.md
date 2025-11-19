# Frontend de PricefloCompare

Frontend web simple y funcional para el comparador de precios.

## 🎨 Características

- ✅ **Responsive** - Funciona en desktop y móvil
- ✅ **Búsqueda en tiempo real**
- ✅ **Filtrado por categorías**
- ✅ **Estadísticas en vivo**
- ✅ **Mejor precio destacado**
- ✅ **Sin dependencias** - Vanilla JS, HTML, CSS

## 🚀 Cómo Usar

### Opción 1: Servido por la API (Recomendado)

```bash
# Iniciar la API (sirve automáticamente el frontend)
python api.py

# Abrir en el navegador:
http://localhost:8000/app
```

### Opción 2: Servidor Local Independiente

```bash
# Con Python
cd frontend
python -m http.server 8080

# Abrir en el navegador:
http://localhost:8080
```

**IMPORTANTE:** Asegúrate de que la API esté corriendo en `http://localhost:8000`

## 📁 Estructura

```
frontend/
├── index.html    # Estructura HTML
├── app.js        # Lógica de la aplicación
└── style.css     # Estilos
```

## 🔧 Configuración

### Cambiar URL de la API

Edita `app.js` línea 2:

```javascript
// Desarrollo local
const API_URL = 'http://localhost:8000';

// Producción
const API_URL = 'https://tu-api.railway.app';
```

## 🎯 Funcionalidades

### 1. **Vista de Productos**
- Muestra todos los productos con sus precios
- Ordenados por mejor precio primero
- Indica con 🏆 el precio más bajo

### 2. **Búsqueda**
- Busca productos por nombre
- Actualización en tiempo real

### 3. **Filtro por Categorías**
- Filtra productos por categoría
- Muestra cantidad de productos por categoría

### 4. **Estadísticas**
- Total de productos
- Total de tiendas
- Total de comparaciones de precios

### 5. **Histórico de Precios**
- Click en "📊 Ver histórico" para ver evolución

## 🎨 Personalización

### Cambiar Colores

Edita `style.css` líneas 9-16:

```css
:root {
    --primary: #2563eb;      /* Color principal */
    --secondary: #10b981;    /* Color secundario */
    --danger: #ef4444;       /* Color de error */
    /* ... más colores */
}
```

### Agregar Logo

Agrega a `index.html` en el header:

```html
<header>
    <img src="logo.png" alt="Logo" style="width: 100px;">
    <h1>💰 PricefloCompare</h1>
</header>
```

## 📱 Responsive

El frontend es totalmente responsive:
- **Desktop:** Grid de 3 columnas
- **Tablet:** Grid de 2 columnas
- **Mobile:** Grid de 1 columna

## 🔄 Flujo de Datos

```
Usuario → Frontend (app.js)
           ↓
       API REST (FastAPI)
           ↓
     Base de Datos SQLite
```

## 🚀 Deploy del Frontend

### Opción A: Con la API (Mismo servidor)

Ya está configurado. La API sirve el frontend automáticamente.

### Opción B: Frontend Separado (Netlify/Vercel)

```bash
# 1. Subir carpeta frontend/ a GitHub
# 2. Conectar con Netlify/Vercel
# 3. Actualizar API_URL en app.js con la URL de tu API
```

**Ventaja:** Frontend gratis en Netlify/Vercel, API en Railway/Render.

## 🐛 Troubleshooting

### "Error al cargar productos"

**Causa:** API no está corriendo.

**Solución:**
```bash
# Verificar que la API esté corriendo
curl http://localhost:8000/health

# Si no responde, iniciar API
python api.py
```

### "Sin precios disponibles"

**Causa:** Base de datos vacía.

**Solución:**
```bash
# Ejecutar scraping
python scrape_and_save.py

# Verificar datos
python view_db.py
```

### CORS Error

**Causa:** API no permite el origen del frontend.

**Solución:** La API ya tiene CORS configurado para `*` (todos los orígenes). Si necesitas restringir:

```python
# api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://tu-dominio.com"],
    ...
)
```

## 📊 Próximas Mejoras

Ideas para extender el frontend:

- [ ] Gráficas de evolución de precios (Chart.js)
- [ ] Sistema de alertas ("avísame si baja de X")
- [ ] Favoritos guardados en localStorage
- [ ] Compartir productos por URL
- [ ] Modo oscuro
- [ ] PWA (Progressive Web App)
- [ ] Notificaciones push

## 💡 Convertir a React/Vue

Si quieres usar un framework:

```bash
# React
npx create-react-app priceflo-frontend
# Copiar lógica de app.js a componentes React

# Vue
npm create vue@latest priceflo-frontend
# Copiar lógica de app.js a componentes Vue
```

La API ya está lista para consumir desde cualquier framework.

---

**¿Dudas?** Consulta la [documentación de la API](http://localhost:8000/docs)
