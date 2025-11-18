# PricefloCompare - Sistema de Base de Datos y API

Sistema completo de scraping de precios con base de datos SQLite y API REST.

## 🎯 Características

- ✅ **Base de datos SQLite** - Cero costos, fácil de usar
- ✅ **API REST con FastAPI** - Endpoints para consultar precios
- ✅ **Job automático** - Actualización periódica de precios
- ✅ **Backup automático** - Copias de seguridad con rotación
- ✅ **Docker ready** - Deploy con un comando
- ✅ **Escalable** - Migración fácil a PostgreSQL

## 📁 Estructura del Proyecto

```
PricefloCompare/
├── database.py           # Sistema de base de datos SQLite
├── api.py               # API REST con FastAPI
├── job_scraper.py       # Job de scraping automático
├── migrate_to_db.py     # Migración desde JSON
├── backup_db.py         # Sistema de backups
├── manage.sh            # Script de gestión
├── requirements.txt     # Dependencias Python
├── Dockerfile           # Imagen Docker
├── docker-compose.yml   # Orquestación de servicios
│
├── data/
│   └── prices.db        # Base de datos SQLite
├── backups/             # Backups automáticos
└── logs/                # Logs de sistema
```

## 🚀 Instalación Rápida

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd PricefloCompare

# 2. Setup inicial (migrar configs JSON)
./manage.sh setup

# 3. Iniciar todos los servicios
./manage.sh docker-up

# 4. Ver logs
./manage.sh docker-logs
```

**¡Listo!** La API estará en `http://localhost:8000`

### Opción 2: Sin Docker (Desarrollo Local)

```bash
# 1. Setup inicial
./manage.sh setup

# 2. Iniciar API (Terminal 1)
./manage.sh api

# 3. Ejecutar scraping manual (Terminal 2)
./manage.sh scrape
```

## 📊 Uso de la Base de Datos

### Migración Inicial

Si tienes `config_sitios.json` y `config_productos.json`:

```bash
python migrate_to_db.py
```

Esto creará:
- Tabla `products` con todos los productos
- Tabla `stores` con todas las tiendas
- Tabla `price_snapshots` (vacía, se llena con scraping)

### Ejecutar Scraping

```bash
# Actualizar todos los productos que necesiten actualización
python job_scraper.py

# Actualizar un producto específico
python job_scraper.py "iPhone 16"
```

### Crear Backups

```bash
# Crear backup manual
python backup_db.py

# Listar backups disponibles
python backup_db.py list

# Restaurar desde backup
python backup_db.py restore prices_backup_20250118_120000.db
```

## 🌐 API REST

### Documentación Interactiva

Una vez iniciada la API, visita:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### 1. Listar Productos

```bash
# Todos los productos
curl http://localhost:8000/products

# Filtrar por categoría
curl http://localhost:8000/products?category=celulares

# Limitar resultados
curl http://localhost:8000/products?limit=10
```

#### 2. Obtener Precios de un Producto

```bash
# Últimos precios (con detalle del producto)
curl http://localhost:8000/products/1

# Solo precios
curl http://localhost:8000/products/1/prices

# Histórico de 30 días
curl http://localhost:8000/products/1/history?days=30
```

#### 3. Buscar Productos

```bash
curl "http://localhost:8000/search?q=iphone"
```

#### 4. Estadísticas

```bash
curl http://localhost:8000/stats
```

Respuesta:
```json
{
  "total_products": 10,
  "total_stores": 2,
  "total_snapshots": 45,
  "last_scrape": "2025-01-18 12:00:00",
  "products_by_category": [
    {"category": "celulares", "count": 3},
    {"category": "electrodomesticos", "count": 7}
  ]
}
```

## ⚙️ Configuración

### Intervalos de Actualización

En la base de datos, cada producto tiene:

- `is_frequent`: Si es `1`, se actualiza más seguido
- `update_interval_hours`: Horas entre actualizaciones

```python
# Ejemplo: Producto frecuente (cada 6 horas)
is_frequent = 1
update_interval_hours = 6

# Producto normal (cada 12 horas)
is_frequent = 0
update_interval_hours = 12
```

### Agregar Nuevos Productos

```python
from database import add_product

product_id = add_product(
    name="Samsung Galaxy S24",
    category="celulares",
    is_frequent=True,
    update_interval_hours=6
)
```

### Agregar Nuevas Tiendas

```python
from database import add_store

store_config = {
    "sitio": "Alkosto",
    "url": "https://www.alkosto.com/...",
    "fetch_method": "html",
    "params": {...},
    "title_xpath": "...",
    "price_xpath": "..."
}

store_id = add_store(
    name="Alkosto",
    url=store_config["url"],
    fetch_method="html",
    config=store_config
)
```

## 🐳 Docker

### Servicios Disponibles

El `docker-compose.yml` incluye 3 servicios:

1. **api** - API REST (puerto 8000)
2. **scraper** - Job que ejecuta cada 12 horas
3. **backup** - Backup automático cada 24 horas

### Comandos Docker

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f api
docker-compose logs -f scraper

# Detener servicios
docker-compose down

# Reconstruir imágenes
docker-compose build

# Reiniciar un servicio específico
docker-compose restart api
```

### Volumes Persistentes

Los datos se persisten en:
- `./data` - Base de datos SQLite
- `./backups` - Backups automáticos
- `./logs` - Logs de sistema

## 📈 Escalabilidad

### Capacidad Actual (SQLite)

- ✅ 10,000+ productos
- ✅ 10+ tiendas
- ✅ Millones de snapshots históricos
- ✅ <50ms response time
- ✅ $0 costo

### Migración a PostgreSQL

Cuando necesites más escala:

```bash
# 1. Exportar SQLite
sqlite3 data/prices.db .dump > backup.sql

# 2. Editar backup.sql
# - Reemplazar AUTOINCREMENT por SERIAL
# - Reemplazar datetime('now') por NOW()

# 3. Importar a PostgreSQL
psql -U user -d prices < backup.sql

# 4. Actualizar database.py
# Cambiar sqlite3 por psycopg2 o SQLAlchemy
```

## 🔧 Troubleshooting

### Error: "database is locked"

SQLite no soporta múltiples escrituras simultáneas. Soluciones:

```bash
# Opción 1: Usar un solo job de scraping
# Opción 2: Migrar a PostgreSQL
# Opción 3: Aumentar timeout en database.py
```

### API no inicia

```bash
# Verificar que el puerto 8000 esté libre
lsof -i :8000

# Verificar logs
docker-compose logs api
```

### Scraping falla con 403

```bash
# Aumentar delay entre requests en job_scraper.py
run_batch_update(delay_between_requests=5.0)  # 5 segundos
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-18T12:00:00",
  "database": "connected",
  "last_scrape": "2025-01-18 11:45:00"
}
```

### Logs

```bash
# Scraper
tail -f logs/scraper.log

# Backup
tail -f logs/backup.log

# Docker
docker-compose logs -f
```

## 🚀 Deploy en Producción

### Railway (Gratis)

```bash
# 1. Instalar Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Iniciar proyecto
railway init

# 4. Deploy
railway up

# 5. Configurar volúmenes persistentes en dashboard
```

### Render (Gratis)

1. Conectar repositorio GitHub
2. Crear "Web Service"
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python api.py`
5. Agregar "Disk" para persistir `data/`

### DigitalOcean App Platform

1. Conectar repositorio
2. Seleccionar Dockerfile
3. Configurar persistent volumes
4. Deploy

## 🔐 Seguridad

### API Pública

Para exponer la API públicamente:

```python
# api.py - Agregar rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/products")
@limiter.limit("10/minute")
def list_products():
    ...
```

### Backups Seguros

```bash
# Encriptar backups
gpg -c backups/prices_backup_20250118.db

# Subir a S3/Google Cloud
aws s3 cp backups/ s3://mybucket/backups/ --recursive
```

## 📚 Recursos

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLite Docs**: https://sqlite.org/docs.html
- **Docker Compose**: https://docs.docker.com/compose/

## 🤝 Contribuir

1. Fork el repositorio
2. Crear feature branch
3. Commit cambios
4. Push a branch
5. Crear Pull Request

## 📝 Licencia

[Tu licencia aquí]

---

**Hecho con ❤️ para PricefloCompare**
