"""
API REST con FastAPI para PricefloCompare
Expone endpoints para consultar precios y productos
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
import re
import subprocess
import sys
import threading

from dotenv import load_dotenv
load_dotenv()

from database import (
    get_products,
    count_products,
    get_product_by_id,
    get_latest_prices,
    get_price_history,
    get_stores,
    get_stats,
    get_db,
    record_search_not_found,
    get_search_not_found_report,
    toggle_ignore_search_not_found,
    delete_search_not_found,
    get_countries,
    get_country,
    get_stores_by_country,
    get_products_by_country,
    count_products_by_country,
    add_product,
    update_product,
    delete_product,
    add_store,
    get_store_by_id,
    update_store,
    delete_store,
    get_stores_for_product,
    set_product_stores,
)

# Crear app FastAPI
app = FastAPI(
    title="PricefloCompare API",
    description="API para comparación de precios entre tiendas",
    version="1.0.0"
)

# Configurar CORS (permite requests desde navegadores)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === MODELOS PYDANTIC ===

class Product(BaseModel):
    id: int
    name: str
    category: Optional[str]
    is_frequent: int
    update_interval_hours: int
    created_at: str
    updated_at: str


class Store(BaseModel):
    id: int
    name: str
    url: str
    fetch_method: str
    active: int
    country_code: Optional[str] = None
    currency: Optional[str] = None
    country_name: Optional[str] = None
    flag_emoji: Optional[str] = None


class Country(BaseModel):
    code: str
    name: str
    currency: str
    locale: str
    flag_emoji: Optional[str] = None
    active: bool = True


class PriceSnapshot(BaseModel):
    id: int
    product_id: int
    store_id: int
    price: float
    title: str
    url: Optional[str]
    relevance_score: Optional[int]
    scraped_at: str
    store_name: Optional[str] = None
    product_name: Optional[str] = None


class LatestPrice(BaseModel):
    store_name: str
    price: float
    title: str
    url: Optional[str]
    scraped_at: str
    relevance_score: Optional[int]
    is_stale: bool = False


class ProductWithPrices(BaseModel):
    product: Product
    prices: List[LatestPrice]
    last_update: str
    is_stale: bool


class SearchNotFound(BaseModel):
    id: int
    search_term: str
    search_count: int
    ignored: int
    first_searched_at: str
    last_searched_at: str


class SearchNotFoundRequest(BaseModel):
    search_term: str


class IgnoreSearchRequest(BaseModel):
    ignored: bool = True


class PaginatedProducts(BaseModel):
    """Respuesta paginada de productos"""
    items: List[Product]
    total: int
    page: int
    page_size: int
    total_pages: int


# === ENDPOINTS ===

@app.get("/api")
def api_info():
    """Información de la API"""
    return {
        "message": "ePriceFlo API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/products",
            "product_detail": "/products/{id}",
            "product_prices": "/products/{id}/prices",
            "product_history": "/products/{id}/history",
            "stores": "/stores",
            "stats": "/stats"
        },
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check para monitoreo"""
    try:
        stats = get_stats()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "last_scrape": stats.get('last_scrape')
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/products", response_model=PaginatedProducts)
def list_products(
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    country: Optional[str] = Query(None, description="Filtrar por código de país (ej: 'CO')"),
    page: int = Query(1, ge=1, description="Número de página (inicia en 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Productos por página (máximo 100)")
):
    """
    Lista productos con paginación

    - **category**: Filtrar por categoría (opcional)
    - **country**: Filtrar por código de país (opcional, ej: 'CO')
    - **page**: Número de página (por defecto: 1)
    - **page_size**: Productos por página (por defecto: 20, máximo: 100)

    Retorna:
    - **items**: Lista de productos de la página actual
    - **total**: Total de productos (con filtros aplicados)
    - **page**: Página actual
    - **page_size**: Productos por página
    - **total_pages**: Total de páginas disponibles
    """
    # Calcular offset
    offset = (page - 1) * page_size

    # Si se especifica país, usar funciones de filtrado por país
    if country:
        country = country.upper()
        # Verificar que el país existe
        country_info = get_country(country)
        if not country_info:
            raise HTTPException(status_code=404, detail=f"País '{country}' no encontrado")

        products = get_products_by_country(
            country_code=country,
            limit=page_size,
            offset=offset,
            category=category
        )
        total = count_products_by_country(country_code=country, category=category)
    else:
        # Sin filtro de país, usar funciones normales
        products = get_products(limit=page_size, offset=offset, category=category)
        total = count_products(category=category)

    # Calcular total de páginas
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@app.get("/products/{product_id}", response_model=ProductWithPrices)
def get_product_detail(
    product_id: int,
    max_age_hours: int = Query(6, description="Edad máxima de datos en horas")
):
    """
    Obtiene detalle de un producto con sus últimos precios

    - **product_id**: ID del producto
    - **max_age_hours**: Considera los datos "stale" si son más viejos que esto
    """
    # Obtener producto
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Obtener últimos precios
    prices_data = get_latest_prices(product_id)

    if not prices_data:
        return ProductWithPrices(
            product=Product(**product),
            prices=[],
            last_update="Nunca",
            is_stale=True
        )

    # Convertir a modelo LatestPrice
    prices = []
    last_update = None

    for price_row in prices_data:
        scraped_at = datetime.fromisoformat(price_row['scraped_at'])

        if not last_update or scraped_at > last_update:
            last_update = scraped_at

        # Verificar si está stale
        age_hours = (datetime.now() - scraped_at).total_seconds() / 3600
        is_stale = age_hours > max_age_hours

        prices.append(LatestPrice(
            store_name=price_row['store_name'],
            price=price_row['price'],
            title=price_row['title'],
            url=price_row['url'],
            scraped_at=price_row['scraped_at'],
            relevance_score=price_row['relevance_score'],
            is_stale=is_stale
        ))

    # Determinar si el conjunto completo está stale
    overall_stale = all(p.is_stale for p in prices) if prices else True

    return ProductWithPrices(
        product=Product(**product),
        prices=prices,
        last_update=last_update.isoformat() if last_update else "Nunca",
        is_stale=overall_stale
    )


@app.get("/products/{product_id}/prices", response_model=List[LatestPrice])
def get_product_prices(
    product_id: int,
    max_age_hours: int = Query(6, description="Edad máxima de datos en horas")
):
    """
    Obtiene solo los precios más recientes de un producto

    - **product_id**: ID del producto
    - **max_age_hours**: Marca precios como stale si son más viejos
    """
    # Verificar que el producto existe
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    prices_data = get_latest_prices(product_id)

    prices = []
    for price_row in prices_data:
        scraped_at = datetime.fromisoformat(price_row['scraped_at'])
        age_hours = (datetime.now() - scraped_at).total_seconds() / 3600
        is_stale = age_hours > max_age_hours

        prices.append(LatestPrice(
            store_name=price_row['store_name'],
            price=price_row['price'],
            title=price_row['title'],
            url=price_row['url'],
            scraped_at=price_row['scraped_at'],
            relevance_score=price_row['relevance_score'],
            is_stale=is_stale
        ))

    return prices


@app.get("/products/{product_id}/history", response_model=List[PriceSnapshot])
def get_product_price_history(
    product_id: int,
    store_id: Optional[int] = Query(None, description="Filtrar por tienda específica"),
    days: int = Query(30, description="Días de histórico a obtener", ge=1, le=365)
):
    """
    Obtiene el histórico de precios de un producto

    - **product_id**: ID del producto
    - **store_id**: ID de tienda específica (opcional, por defecto todas)
    - **days**: Número de días hacia atrás (1-365, por defecto 30)
    """
    # Verificar que el producto existe
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    history = get_price_history(product_id, store_id=store_id, days=days)

    return [PriceSnapshot(**row) for row in history]


@app.get("/stores", response_model=List[Store])
def list_stores(active_only: bool = Query(True, description="Solo tiendas activas")):
    """
    Lista todas las tiendas

    - **active_only**: Si es True, solo retorna tiendas activas
    """
    stores = get_stores(active_only=active_only)

    # Remover el campo 'config' que es muy grande
    return [
        {k: v for k, v in store.items() if k != 'config'}
        for store in stores
    ]


@app.get("/affiliate-config")
def get_affiliate_configuration():
    """
    Obtiene la configuración de afiliados para todas las tiendas

    Retorna solo las tiendas que tienen afiliados habilitados,
    con su código y patrón de URL para el frontend.
    """
    with get_db() as conn:
        stores = conn.execute("""
            SELECT name, affiliate_code, affiliate_url_pattern
            FROM stores
            WHERE affiliate_enabled = 1
            AND affiliate_code IS NOT NULL
        """).fetchall()

        config = {}
        for store in stores:
            config[store['name']] = {
                'enabled': True,
                'code': store['affiliate_code'],
                'url_pattern': store['affiliate_url_pattern']
            }

        return config


@app.get("/stats")
def get_statistics():
    """
    Obtiene estadísticas generales del sistema

    Incluye totales de productos, tiendas, snapshots y categorías
    """
    return get_stats()


@app.get("/categories")
def get_categories(country: Optional[str] = Query(None, description="Filtrar por código de país (ej: 'CO')")):
    """
    Lista todas las categorías disponibles con conteo de productos

    - **country**: Filtrar por código de país (opcional, ej: 'CO')
    """
    with get_db() as conn:
        cursor = conn.cursor()
        from database import _fetch_all, _param_placeholder

        ph = _param_placeholder()

        if country:
            country = country.upper()
            # Verificar que el país existe
            country_info = get_country(country)
            if not country_info:
                raise HTTPException(status_code=404, detail=f"País '{country}' no encontrado")

            # Contar categorías solo de productos disponibles en ese país
            cursor.execute(f"""
                SELECT p.category, COUNT(DISTINCT p.id) as count
                FROM products p
                INNER JOIN price_snapshots ps ON ps.product_id = p.id
                INNER JOIN stores s ON ps.store_id = s.id
                WHERE p.category IS NOT NULL
                  AND s.country_code = {ph}
                GROUP BY p.category
                ORDER BY count DESC
            """, (country,))
        else:
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM products
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
            """)

        categories = _fetch_all(cursor)

        return [
            {"category": row['category'], "count": row['count']}
            for row in categories
        ]


@app.get("/search")
def search_products(
    q: str = Query(..., description="Término de búsqueda", min_length=2),
    limit: int = Query(10, description="Número máximo de resultados", ge=1, le=100)
):
    """
    Busca productos por nombre

    - **q**: Término de búsqueda (mínimo 2 caracteres)
    - **limit**: Número máximo de resultados (1-100, por defecto 10)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        from database import _param_placeholder, _fetch_all, IS_POSTGRES

        ph = _param_placeholder()

        if IS_POSTGRES:
            query = f"""
                SELECT * FROM products
                WHERE name ILIKE {ph}
                ORDER BY is_frequent DESC, name ASC
                LIMIT {ph}
            """
        else:
            query = f"""
                SELECT * FROM products
                WHERE name LIKE {ph}
                ORDER BY is_frequent DESC, name ASC
                LIMIT {ph}
            """

        cursor.execute(query, (f"%{q}%", limit))
        products = _fetch_all(cursor)

        return [dict(row) for row in products]


# === REPORTES Y ANALYTICS ===

@app.post("/reports/search-not-found", status_code=201)
def register_search_not_found(request: SearchNotFoundRequest):
    """
    Registra una búsqueda que no tuvo resultados

    - **search_term**: Término que se buscó sin resultados
    """
    try:
        record_search_not_found(request.search_term)
        return {"message": "Búsqueda registrada", "search_term": request.search_term}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/not-found", response_model=List[SearchNotFound])
def get_not_found_report(
    limit: int = Query(50, description="Número de resultados (máx 200)", ge=1, le=200),
    include_ignored: bool = Query(False, description="Incluir búsquedas ignoradas")
):
    """
    Obtiene el reporte de búsquedas sin resultados (Top 50 por defecto)

    - **limit**: Número de resultados a retornar (1-200, por defecto 50)
    - **include_ignored**: Si incluir o no las búsquedas marcadas como ignoradas

    Retorna la lista ordenada por cantidad de búsquedas descendente
    """
    try:
        results = get_search_not_found_report(limit=limit, include_ignored=include_ignored)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/reports/not-found/{search_id}")
def update_search_not_found_status(
    search_id: int,
    request: IgnoreSearchRequest
):
    """
    Marca o desmarca una búsqueda como ignorada

    - **search_id**: ID de la búsqueda
    - **ignored**: True para ignorar, False para reactivar
    """
    success = toggle_ignore_search_not_found(search_id, request.ignored)
    if not success:
        raise HTTPException(status_code=404, detail="Búsqueda no encontrada")

    status = "ignorada" if request.ignored else "reactivada"
    return {"message": f"Búsqueda {status}", "id": search_id, "ignored": request.ignored}


@app.delete("/reports/not-found/{search_id}")
def delete_not_found_entry(search_id: int):
    """
    Elimina completamente un registro de búsqueda no encontrada

    - **search_id**: ID de la búsqueda a eliminar
    """
    success = delete_search_not_found(search_id)
    if not success:
        raise HTTPException(status_code=404, detail="Búsqueda no encontrada")

    return {"message": "Búsqueda eliminada", "id": search_id}


# === ENDPOINTS DE PAÍSES ===

@app.get("/countries", response_model=List[Country])
def list_countries(active_only: bool = Query(True, description="Solo países activos")):
    """
    Obtiene la lista de países disponibles

    - **active_only**: Si True, solo devuelve países activos (default: True)
    """
    countries = get_countries(active_only=active_only)
    return [Country(**c) for c in countries]


@app.get("/countries/{country_code}", response_model=Country)
def get_country_info(country_code: str):
    """
    Obtiene información de un país específico

    - **country_code**: Código ISO del país (ej: 'CO', 'MX', 'CL')
    """
    country = get_country(country_code.upper())
    if not country:
        raise HTTPException(status_code=404, detail="País no encontrado")

    return Country(**country)


@app.get("/stores", response_model=List[Store])
def list_stores_filtered(
    country: Optional[str] = Query(None, description="Filtrar por código de país (ej: 'CO')"),
    active_only: bool = Query(True, description="Solo tiendas activas")
):
    """
    Obtiene la lista de tiendas, opcionalmente filtradas por país

    - **country**: Código de país para filtrar (opcional)
    - **active_only**: Si True, solo devuelve tiendas activas (default: True)
    """
    if country:
        country = country.upper()
        # Verificar que el país existe
        country_info = get_country(country)
        if not country_info:
            raise HTTPException(status_code=404, detail=f"País '{country}' no encontrado")

        stores = get_stores_by_country(country_code=country, active_only=active_only)
    else:
        stores = get_stores_by_country(country_code=None, active_only=active_only)

    return [Store(**s) for s in stores]


@app.get("/detect-country")
async def detect_country_by_ip():
    """
    Intenta detectar el país del usuario basándose en su IP

    Nota: Funcionalidad básica. En producción usar servicio como ipapi.co o geoip2
    """
    # Por ahora retornar Colombia por defecto
    # En producción, usar la IP del cliente para detectar el país real
    return {
        "country_code": "CO",
        "country_name": "Colombia",
        "currency": "COP",
        "flag_emoji": "🇨🇴",
        "detected_by": "default",
        "message": "País detectado por defecto. Puedes cambiarlo en el selector."
    }


# === ADMIN: MODELOS ===

class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    is_frequent: bool = False
    update_interval_hours: int = 12


class ProductUpdate(BaseModel):
    name: str
    category: Optional[str] = None
    is_frequent: bool = False
    update_interval_hours: int = 12


class StoreCreate(BaseModel):
    name: str
    url: str
    fetch_method: str
    config: dict
    active: bool = True


class StoreUpdate(BaseModel):
    name: str
    url: str
    fetch_method: str
    config: dict
    active: bool = True


class StoreTestRequest(BaseModel):
    product_name: str
    product_category: Optional[str] = None


# === ADMIN: PRODUCTOS ===

@app.get("/admin/products", response_model=PaginatedProducts)
def admin_list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None, min_length=1),
    store_id: Optional[int] = Query(None),
):
    """Lista productos con paginación y filtros para admin"""
    offset = (page - 1) * page_size
    products = get_products(limit=page_size, offset=offset, category=category, search=search, store_id=store_id)
    total = count_products(category=category, search=search, store_id=store_id)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return {"items": products, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@app.post("/admin/products", status_code=201)
def admin_create_product(data: ProductCreate):
    """Crea un nuevo producto"""
    product_id = add_product(
        name=data.name,
        category=data.category,
        is_frequent=data.is_frequent,
        update_interval_hours=data.update_interval_hours
    )
    product = get_product_by_id(product_id)
    return product


@app.put("/admin/products/{product_id}")
def admin_update_product(product_id: int, data: ProductUpdate):
    """Actualiza un producto"""
    if not get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    ok = update_product(
        product_id=product_id,
        name=data.name,
        category=data.category,
        is_frequent=data.is_frequent,
        update_interval_hours=data.update_interval_hours
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Error actualizando producto")
    return get_product_by_id(product_id)


@app.delete("/admin/products/{product_id}")
def admin_delete_product(product_id: int):
    """Elimina un producto y todos sus snapshots"""
    if not get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    delete_product(product_id)
    return {"message": "Producto eliminado", "id": product_id}


# === ADMIN: TIENDAS ===

@app.get("/admin/stores")
def admin_list_stores():
    """Lista todas las tiendas incluyendo config completo"""
    return get_stores(active_only=False)


@app.get("/admin/stores/{store_id}")
def admin_get_store(store_id: int):
    """Obtiene una tienda por ID con config completo"""
    store = get_store_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


@app.post("/admin/stores", status_code=201)
def admin_create_store(data: StoreCreate):
    """Crea una nueva tienda"""
    store_id = add_store(
        name=data.name,
        url=data.url,
        fetch_method=data.fetch_method,
        config=data.config
    )
    return get_store_by_id(store_id)


@app.put("/admin/stores/{store_id}")
def admin_update_store(store_id: int, data: StoreUpdate):
    """Actualiza una tienda incluyendo su config de scraping"""
    if not get_store_by_id(store_id):
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    ok = update_store(
        store_id=store_id,
        name=data.name,
        url=data.url,
        fetch_method=data.fetch_method,
        config=data.config,
        active=data.active
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Error actualizando tienda")
    return get_store_by_id(store_id)


@app.delete("/admin/stores/{store_id}")
def admin_delete_store(store_id: int):
    """Elimina una tienda"""
    if not get_store_by_id(store_id):
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    delete_store(store_id)
    return {"message": "Tienda eliminada", "id": store_id}


@app.get("/admin/products/{product_id}/stores")
def admin_get_product_stores(product_id: int):
    """Retorna los IDs de tiendas asignadas a un producto"""
    if not get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"store_ids": get_stores_for_product(product_id)}


@app.put("/admin/products/{product_id}/stores")
def admin_set_product_stores(product_id: int, data: dict):
    """Reemplaza las tiendas asignadas a un producto"""
    if not get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    store_ids = data.get("store_ids", [])
    set_product_stores(product_id, store_ids)
    return {"product_id": product_id, "store_ids": store_ids}


@app.post("/admin/stores/{store_id}/test")
def admin_test_store(store_id: int, data: StoreTestRequest):
    """Prueba el scraping de una tienda con un producto dado"""
    store = get_store_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")

    from scrapers.generic_scrapers import scrape_price
    store_config = {
        **store['config'],
        'url': store['url'],
        'sitio': store['name'],
        'fetch_method': store['fetch_method']
    }
    try:
        result = scrape_price(
            sitio_config=store_config,
            product_name=data.product_name,
            product_category=data.product_category
        )
        if result:
            return {"success": True, "result": result}
        return {"success": False, "result": None, "message": "Sin resultados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === SCRAPING JOB ===

_scrape_job: dict = {
    "running": False,
    "started_at": None,
    "env_key": None,
    "product": None,
    "last_run": None,
    "last_result": None,
    "process": None,
}
_scrape_lock = threading.Lock()


def _parse_environments() -> list:
    raw = os.environ.get("ENVIRONMENTS", "")
    envs = []
    for item in raw.split("|"):          # | como separador, permite comas en labels
        item = item.strip()
        if ":" in item:
            key, label = item.split(":", 1)
            envs.append({"key": key.strip(), "label": label.strip()})
    return envs


def _job_thread(cmd: list, sub_env: dict, cwd: str):
    try:
        proc = subprocess.Popen(
            cmd,
            env=sub_env,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        with _scrape_lock:
            _scrape_job["process"] = proc

        try:
            stdout, stderr = proc.communicate(timeout=3600)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

        output = (stdout or "") + (stderr or "")

        # Leer resultado estructurado si job_scraper lo emitió
        result_m = re.search(r'__JOB_RESULT__(.+?)__JOB_RESULT__', output)
        if result_m:
            import json as _json
            try:
                job_data = _json.loads(result_m.group(1))
                success = job_data.get("success")
                failed = job_data.get("failed")
            except Exception:
                success = failed = None
        else:
            success = failed = None

        result = {
            "success": success,
            "failed": failed,
            "output": output[-4000:],
            "exit_code": proc.returncode,
        }
    except Exception as e:
        result = {"success": None, "failed": None, "output": str(e), "exit_code": -1}

    with _scrape_lock:
        _scrape_job["running"] = False
        _scrape_job["process"] = None
        _scrape_job["last_run"] = datetime.now().isoformat()
        _scrape_job["last_result"] = result


class ScrapeRunRequest(BaseModel):
    env: str
    product: Optional[str] = None


@app.get("/api/scrape/environments")
def list_scrape_environments():
    """Lista los ambientes disponibles para correr el job (leídos de ENVIRONMENTS en .env)"""
    return _parse_environments()


@app.get("/api/scrape/status")
def scrape_status():
    """Estado actual del job de scraping"""
    with _scrape_lock:
        return {
            "running": _scrape_job["running"],
            "started_at": _scrape_job["started_at"],
            "env_key": _scrape_job["env_key"],
            "product": _scrape_job["product"],
            "last_run": _scrape_job["last_run"],
            "last_result": _scrape_job["last_result"],
        }


@app.post("/api/scrape/run")
def run_scrape_job(data: ScrapeRunRequest):
    """Dispara el job de scraping en el ambiente indicado"""
    valid_keys = {e["key"] for e in _parse_environments()}
    if data.env not in valid_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Ambiente '{data.env}' no configurado en ENVIRONMENTS"
        )

    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    if data.env == "local":
        sub_env.pop("DATABASE_URL", None)
    else:
        specific_url = os.environ.get(f"DATABASE_URL_{data.env.upper()}")
        if specific_url:
            sub_env["DATABASE_URL"] = specific_url

    cwd = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable, os.path.join(cwd, "job_scraper.py")]
    if data.product and data.product.strip():
        cmd.append(data.product.strip())

    with _scrape_lock:
        if _scrape_job["running"]:
            raise HTTPException(status_code=409, detail="Ya hay un job corriendo")
        _scrape_job["running"] = True
        _scrape_job["started_at"] = datetime.now().isoformat()
        _scrape_job["env_key"] = data.env
        _scrape_job["product"] = data.product or None
        _scrape_job["last_result"] = None
        started_at = _scrape_job["started_at"]

    threading.Thread(target=_job_thread, args=(cmd, sub_env, cwd), daemon=True).start()

    return {
        "message": "Job iniciado",
        "env": data.env,
        "product": data.product or "todos",
        "started_at": started_at,
    }


@app.delete("/api/scrape/run")
def cancel_scrape_job():
    """Cancela el job de scraping en curso"""
    with _scrape_lock:
        if not _scrape_job["running"]:
            raise HTTPException(status_code=409, detail="No hay job corriendo")
        proc = _scrape_job.get("process")

    if proc:
        try:
            proc.terminate()
        except Exception:
            pass

    with _scrape_lock:
        _scrape_job["running"] = False
        _scrape_job["process"] = None
        _scrape_job["last_run"] = datetime.now().isoformat()
        _scrape_job["last_result"] = {
            "success": None, "failed": None,
            "output": "Cancelado manualmente.", "exit_code": -2,
        }
    return {"message": "Job cancelado"}


# === FRONTEND ESTÁTICO ===

# Montar archivos estáticos del frontend (si existe el directorio)
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_frontend():
        """Sirve el frontend HTML en la raíz"""
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/reports")
    async def serve_reports():
        """Sirve la página de reportes"""
        return FileResponse(os.path.join(frontend_path, "reports.html"))

    @app.get("/admin")
    async def serve_admin():
        """Sirve la página de administración"""
        return FileResponse(os.path.join(frontend_path, "admin.html"))


# === EJECUTAR SERVIDOR ===

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("Iniciando PricefloCompare API...")
    print("=" * 70)
    print("\n  App:   http://localhost:8000")
    print("  Admin: http://localhost:8000/admin")
    print("  Docs:  http://localhost:8000/docs")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload en desarrollo
    )
