# 🚀 Inicio Rápido - PricefloCompare

## ⚡ Opción 1: Docker (Más Rápido)

```bash
# 1. Migrar datos (solo primera vez)
python3 migrate_to_db.py

# 2. Iniciar todo
docker-compose up -d

# 3. Ver API
open http://localhost:8000/docs
```

## 💻 Opción 2: Local (Desarrollo)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Migrar datos
python3 migrate_to_db.py

# 3. Iniciar API (Terminal 1)
python3 api.py

# 4. En otro terminal: ejecutar scraping
python3 job_scraper.py
```

## 📝 Usando el Script de Gestión

```bash
# Hacer ejecutable (solo primera vez)
chmod +x manage.sh

# Setup completo
./manage.sh setup

# Ver comandos disponibles
./manage.sh help
```

## 🎯 Primeros Pasos

### 1. Ver productos disponibles
```bash
curl http://localhost:8000/products | python3 -m json.tool
```

### 2. Ejecutar primer scraping
```bash
python3 job_scraper.py
```

### 3. Ver precios actualizados
```bash
curl http://localhost:8000/products/1 | python3 -m json.tool
```

### 4. Ver estadísticas
```bash
curl http://localhost:8000/stats | python3 -m json.tool
```

## 📚 Documentación Completa

- **Documentación API**: http://localhost:8000/docs
- **Guía completa**: Ver [README_DB.md](README_DB.md)

## ✅ Verificación

```bash
# Health check
curl http://localhost:8000/health

# Debe responder:
# {"status": "healthy", "timestamp": "...", ...}
```

## 🆘 Problemas Comunes

### Puerto 8000 ocupado
```bash
# Cambiar puerto en api.py línea final:
uvicorn.run("api:app", host="0.0.0.0", port=8001)
```

### Base de datos no existe
```bash
python3 migrate_to_db.py
```

### Dependencias faltantes
```bash
pip install -r requirements.txt
```

---

**¿Todo listo?** Visita http://localhost:8000/docs para explorar la API 🎉
