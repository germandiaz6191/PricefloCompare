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
    delete_search_not_found
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
    page: int = Query(1, ge=1, description="Número de página (inicia en 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Productos por página (máximo 100)")
):
    """
    Lista productos con paginación

    - **category**: Filtrar por categoría (opcional)
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

    # Obtener productos y total
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
def get_categories():
    """
    Lista todas las categorías disponibles con conteo de productos
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM products
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """)

        from database import _fetch_all
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


# === EJECUTAR SERVIDOR ===

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🚀 Iniciando PricefloCompare API...")
    print("=" * 70)
    print("\n📱 APLICACIÓN:")
    print("   http://localhost:8000/app")
    print("\n📖 DOCUMENTACIÓN API:")
    print("   http://localhost:8000/docs")
    print("\n🔍 ENDPOINTS:")
    print("   http://localhost:8000/products")
    print("   http://localhost:8000/stats")
    print("   http://localhost:8000/health")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload en desarrollo
    )
