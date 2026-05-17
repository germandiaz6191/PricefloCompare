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

## Correr el Job de Scraping por Entorno (Windows)

**`python job_scraper.py` sigue funcionando igual que siempre.** El wrapper
`run_job.ps1` es solo un atajo para cambiar de entorno sin tocar variables
manualmente — no reemplaza nada.

```
python job_scraper.py         → local SQLite  (igual que siempre)
.\run_job.ps1                 → local SQLite  (mismo resultado, via wrapper)
.\run_job.ps1 :pdn            → produccion    (wrapper setea DATABASE_URL y llama a python job_scraper.py)
```

### Local (SQLite)

```powershell
# Batch completo
python job_scraper.py

# Un producto específico (ignora el intervalo de 12h)
python job_scraper.py "Nevera Samsung 300L"
```

### Producción (PostgreSQL Supabase)

> **Primera vez:** Windows bloquea scripts `.ps1` por defecto. Habilitar una sola vez:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

```powershell
# Batch completo
.\run_job.ps1 :pdn

# Un producto específico en produccion
.\run_job.ps1 :pdn "Nevera Samsung 300L"
```

### Notas importantes

- `run_job.ps1` lee el `DATABASE_URL` del archivo `.env` local para `:pdn`.
- `run_job.ps1` está en `.gitignore` — no se sube a producción.
- `job_scraper.py` no fue modificado para entornos — es seguro desplegarlo a producción tal cual.
- En producción Railway inyecta `DATABASE_URL` automáticamente; el job se corre como `python job_scraper.py` sin flags.
- El job solo procesa productos cuyo `update_interval_hours` ya venció (default: 12h). Para forzar un producto sin esperar, pásalo por nombre.

### Ver precios guardados en la BD local

```powershell
python scripts/utils/view_db.py
```

---

**¿Todo listo?** Visita http://localhost:8000/docs para explorar la API
