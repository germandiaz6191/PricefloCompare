# Comandos de referencia — PricefloCompare

## API / Servidor

```powershell
# Apuntando a Supabase (producción) — lee DATABASE_URL del .env
python api.py

# Apuntando a SQLite local — ignora el .env
$env:DATABASE_URL = ''
python api.py
```

## URLs locales

| Destino | URL |
|---|---|
| Frontend usuarios | http://localhost:8000 |
| Panel admin | http://localhost:8000/admin |
| Documentación API | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

## Job de scraping — por línea de comando

```powershell
# Batch completo → SQLite local
python job_scraper.py

# Producto específico → SQLite local
python job_scraper.py "Nevera Samsung 300L"

# Batch completo → Supabase producción
.\run_job.ps1 :pdn

# Producto específico → Supabase producción
.\run_job.ps1 :pdn "Nevera Samsung 300L"
```

> **Primera vez con run_job.ps1:** habilitar ejecución de scripts PS1 (una sola vez):
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

## Job de scraping — desde el admin (UI)

1. Abrir http://localhost:8000/admin
2. Tab **Scraping**
3. Seleccionar ambiente en el dropdown
4. Opcional: escribir nombre de producto (vacío = todos)
5. Clic en **Ejecutar**

## Agregar un nuevo ambiente de scraping

En `.env` agregar el nombre y label al final de `ENVIRONMENTS`:

```
ENVIRONMENTS=local:Local (SQLite),pdn:Producción (Supabase),nuevo:Mi Ambiente
```

Si el nuevo ambiente usa una BD distinta, agregar su URL en `.env`:

```
DATABASE_URL_NUEVO=postgresql://...
```

El dropdown en el admin lo tomará automáticamente sin cambios en código.

## Utilidades

```powershell
# Ver contenido de la BD local
python scripts/utils/view_db.py

# Backup de la BD
python scripts/utils/backup_db.py
```

## Variables de entorno clave

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Vacío = SQLite local, URL postgres = Supabase |
| `ENVIRONMENTS` | Lista de ambientes disponibles en el admin (clave:label separados por coma) |
| `ENABLE_SCRAPING` | Habilita/deshabilita el scraping |
| `PYTHONIOENCODING` | Setear `utf-8` en Windows para evitar errores de encoding |
