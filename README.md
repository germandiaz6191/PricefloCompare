# 🌍 ePriceFlo - Comparador de Precios Multi-País

Comparador profesional de precios para las principales tiendas de Latinoamérica.

[![Live Demo](https://img.shields.io/badge/demo-epriceflo.com-blue)](https://epriceflo.com)
[![Colombia](https://img.shields.io/badge/país-Colombia%20🇨🇴-green)]()
[![Platform](https://img.shields.io/badge/platform-Railway%20+%20Supabase-purple)]()

---

## 📋 Características

- ✅ **Soporte Multi-País**: Colombia, México, Chile, Argentina, Perú
- ✅ **Scraping Inteligente**: GraphQL y REST APIs
- ✅ **Paginación**: Navegación eficiente de productos
- ✅ **Categorías Dinámicas**: Top 4 categorías + dropdown
- ✅ **Selector de País**: Auto-detección con localStorage
- ✅ **Histórico de Precios**: Tracking temporal
- ✅ **API REST**: FastAPI con documentación automática

---

## 🚀 Quick Start

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/germandiaz6191/PricefloCompare.git
cd PricefloCompare

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### Ejecutar Localmente

```bash
# 1. Ejecutar migración inicial
python migrate_to_db.py

# 2. Migrar soporte de países
python migrate_countries.py

# 3. Iniciar API
python api.py
```

La aplicación estará disponible en:
- 🌐 Frontend: http://localhost:8000
- 📖 API Docs: http://localhost:8000/docs

---

## 🏪 Agregar Nuevas Tiendas

### Paso 1: Investigar la API

```bash
# Usar script de prueba
python test_tienda_api.py
```

**Documentación completa**: [COMO_AGREGAR_TIENDAS.md](docs/COMO_AGREGAR_TIENDAS.md)

### Paso 2: Agregar a config_sitios.json

```json
{
  "sitio": "NuevaTienda",
  "country_code": "CO",
  "currency": "COP",
  "url": "https://www.tienda.com/api/graphql",
  "fetch_method": "graphql",
  ...
}
```

### Paso 3: Migrar y Probar

```bash
python migrate_to_db.py
python add_test_data.py
```

---

## 📊 Arquitectura

### Backend
- **FastAPI**: API REST
- **PostgreSQL**: Producción (Supabase)
- **SQLite**: Desarrollo local
- **BeautifulSoup4**: HTML scraping
- **Requests**: GraphQL/REST

### Frontend
- **Vanilla JavaScript**: Sin frameworks
- **CSS Grid/Flexbox**: Layout responsivo
- **LocalStorage**: Persistencia de preferencias

### Deployment
- **Railway**: Backend hosting
- **Supabase**: PostgreSQL managed
- **Cloudflare**: CDN (opcional)

---

## 🗂️ Estructura del Proyecto

```
PricefloCompare/
├── api.py                          # API FastAPI
├── database.py                     # Abstracción de BD
├── config_sitios.json              # Config de tiendas activas
├── config_sitios_extended.json.example  # Tiendas adicionales
├── migrate_countries.py            # Migración multi-país
├── migrate_to_db.py                # Migración inicial
├── add_test_data.py                # Script de prueba
├── test_tienda_api.py             # Test de APIs
├── scrapers/
│   ├── graphql_scraper.py         # Scraper GraphQL
│   └── html_scraper.py            # Scraper HTML
├── frontend/
│   ├── index.html                 # Frontend principal
│   ├── app.js                     # Lógica JS
│   └── style.css                  # Estilos
└── docs/
    ├── COMO_AGREGAR_TIENDAS.md    # Guía de tiendas
    ├── MONETIZATION_GUIDE.md      # Monetización
    └── README_DB.md               # Base de datos
```

---

## 🌐 Endpoints API

### Países
- `GET /countries` - Lista de países
- `GET /countries/{code}` - Info de país
- `GET /detect-country` - Auto-detectar país

### Productos
- `GET /products?country=CO&page=1` - Productos paginados
- `GET /products/{id}` - Producto específico
- `GET /products/{id}/prices` - Precios actuales
- `GET /products/{id}/history` - Histórico de precios

### Categorías
- `GET /categories?country=CO` - Categorías por país

### Tiendas
- `GET /stores?country=CO` - Tiendas por país

**Documentación completa**: http://localhost:8000/docs

---

## 🗄️ Base de Datos

### Modelo de Datos

```sql
countries (🌍 Países)
    ↓
stores (🏪 Tiendas con country_code)
    ↓
price_snapshots (💰 Precios)
    ↓
products (📦 Productos globales)
```

**Ventajas**:
- Productos globales (no duplicados por país)
- Fácil expansión internacional
- Comparaciones multi-país futuras

---

## 🧪 Testing

### Probar Scraper de Tienda

```bash
python test_tienda_api.py
```

### Agregar Datos de Prueba

```bash
python add_test_data.py
```

### Verificar Migración

```bash
python migrate_to_db.py --verify
```

---

## 🌍 Países Soportados

| País | Código | Moneda | Estado | Tiendas |
|------|--------|--------|--------|---------|
| 🇨🇴 Colombia | CO | COP | ✅ Activo | Éxito, Homecenter |
| 🇲🇽 México | MX | MXN | ⏸️ Inactivo | - |
| 🇨🇱 Chile | CL | CLP | ⏸️ Inactivo | - |
| 🇦🇷 Argentina | AR | ARS | ⏸️ Inactivo | - |
| 🇵🇪 Perú | PE | PEN | ⏸️ Inactivo | - |

**Para activar un país**: Agregar tiendas y ejecutar:
```sql
UPDATE countries SET active = TRUE WHERE code = 'MX';
```

---

## 📝 Tiendas Configuradas

### ✅ Funcionando
- **Éxito** (CO) - GraphQL - VTEX
- **Homecenter** (CO) - HTML Scraping

### ⚠️ Pendiente de Prueba
- **Ktronix** (CO) - GraphQL - Config lista
- **Alkosto** (CO) - GraphQL - Requiere investigación
- **Falabella** (CO) - REST - Requiere investigación
- **Olimpica** (CO) - REST - Requiere investigación

Ver [config_sitios_extended.json.example](config_sitios_extended.json.example)

---

## 🔧 Variables de Entorno

```env
# Base de Datos
DATABASE_URL=postgresql://user:pass@host:port/db

# Opcional
PORT=8000
ENVIRONMENT=production
```

---

## 📚 Documentación Adicional

- [🏗️ Infraestructura](docs/INFRAESTRUCTURA.md) - Railway, Supabase, Dominio
- [🏪 Cómo Agregar Tiendas](docs/COMO_AGREGAR_TIENDAS.md)
- [📊 Analytics y AdSense](docs/ANALYTICS_Y_ADSENSE.md) - Google Analytics, Monetización
- [🔬 Análisis de Scrapers](docs/ANALISIS_SCRAPERS.md) - Detalles técnicos
- [📦 Productos Populares](docs/PRODUCTOS_POPULARES.md) - Investigación de mercado
- [🗄️ Base de Datos](docs/README_DB.md)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-tienda`
3. Commit cambios: `git commit -m 'feat: Agregar tienda X'`
4. Push: `git push origin feature/nueva-tienda`
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## 👨‍💻 Autor

**Germán Díaz**
- GitHub: [@germandiaz6191](https://github.com/germandiaz6191)
- Proyecto: [PricefloCompare](https://github.com/germandiaz6191/PricefloCompare)
- Web: [epriceflo.com](https://epriceflo.com)

---

## 🙏 Agradecimientos

- FastAPI por el framework
- VTEX por la plataforma de e-commerce
- Railway por el hosting
- Supabase por la base de datos

---

**⭐ Si te gusta el proyecto, dale una estrella en GitHub!**
