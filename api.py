"""
API REST con FastAPI para PricefloCompare
Expone endpoints para consultar precios y productos
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import (
    get_products,
    get_product_by_id,
    get_latest_prices,
    get_price_history,
    get_stores,
    get_stats,
    get_db
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


# === ENDPOINTS ===

@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "PricefloCompare API",
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


@app.get("/products", response_model=List[Product])
def list_products(
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    limit: Optional[int] = Query(None, description="Limitar número de resultados")
):
    """
    Lista todos los productos

    - **category**: Filtrar por categoría (opcional)
    - **limit**: Número máximo de productos a retornar (opcional)
    """
    products = get_products(limit=limit, category=category)
    return products


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
        categories = conn.execute("""
            SELECT category, COUNT(*) as count
            FROM products
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """).fetchall()

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
        products = conn.execute("""
            SELECT * FROM products
            WHERE name LIKE ?
            ORDER BY is_frequent DESC, name ASC
            LIMIT ?
        """, (f"%{q}%", limit)).fetchall()

        return [dict(row) for row in products]


# === EJECUTAR SERVIDOR ===

if __name__ == "__main__":
    import uvicorn

    print("🚀 Iniciando PricefloCompare API...")
    print("📖 Documentación: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload en desarrollo
    )
