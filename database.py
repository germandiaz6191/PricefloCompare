"""
Sistema de base de datos SQLite para PricefloCompare
Soporta migración futura a PostgreSQL con mínimos cambios
"""
import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

DATABASE_URL = "data/prices.db"

@contextmanager
def get_db():
    """Context manager para conexiones SQLite"""
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(DATABASE_URL), exist_ok=True)

    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Crea las tablas si no existen"""
    with get_db() as conn:
        conn.executescript("""
        -- Tabla de productos
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            is_frequent INTEGER DEFAULT 0,  -- SQLite usa INTEGER para BOOLEAN
            update_interval_hours INTEGER DEFAULT 12,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        -- Tabla de tiendas
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            fetch_method TEXT NOT NULL,  -- 'html' o 'graphql'
            config TEXT,  -- JSON como TEXT
            active INTEGER DEFAULT 1,
            affiliate_enabled INTEGER DEFAULT 0,  -- Si tiene afiliado configurado
            affiliate_code TEXT,  -- Código de afiliado
            affiliate_url_pattern TEXT,  -- Patrón de URL (ej: "?tag={code}")
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Tabla de snapshots de precios
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            store_id INTEGER NOT NULL,
            price REAL,
            title TEXT,
            url TEXT,
            relevance_score INTEGER,
            scraped_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
        );

        -- Índices para mejorar performance de queries
        CREATE INDEX IF NOT EXISTS idx_price_product_date
            ON price_snapshots(product_id, scraped_at DESC);

        CREATE INDEX IF NOT EXISTS idx_price_store_date
            ON price_snapshots(store_id, scraped_at DESC);

        CREATE INDEX IF NOT EXISTS idx_product_category
            ON products(category);

        CREATE INDEX IF NOT EXISTS idx_product_frequent
            ON products(is_frequent, update_interval_hours);

        -- Tabla de búsquedas sin resultados (para tracking)
        CREATE TABLE IF NOT EXISTS search_not_found (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT NOT NULL UNIQUE,
            search_count INTEGER DEFAULT 1,
            ignored INTEGER DEFAULT 0,  -- Si el usuario lo marca como ignorado
            first_searched_at TEXT DEFAULT (datetime('now')),
            last_searched_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_search_not_found_count
            ON search_not_found(search_count DESC, ignored);

        -- Vista de últimos precios por producto/tienda
        CREATE VIEW IF NOT EXISTS latest_prices AS
        SELECT
            ps.id,
            ps.product_id,
            ps.store_id,
            ps.price,
            ps.title,
            ps.url,
            ps.relevance_score,
            ps.scraped_at,
            p.name as product_name,
            p.category as product_category,
            s.name as store_name
        FROM price_snapshots ps
        INNER JOIN products p ON ps.product_id = p.id
        INNER JOIN stores s ON ps.store_id = s.id
        WHERE ps.id IN (
            SELECT ps2.id
            FROM price_snapshots ps2
            WHERE ps2.product_id = ps.product_id
              AND ps2.store_id = ps.store_id
            ORDER BY ps2.scraped_at DESC
            LIMIT 1
        )
        ORDER BY ps.scraped_at DESC;
        """)
        conn.commit()
        print("✅ Base de datos inicializada")


# === FUNCIONES DE PRODUCTOS ===

def get_products(limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict]:
    """Obtiene lista de productos"""
    with get_db() as conn:
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY is_frequent DESC, name ASC"

        if limit:
            query += f" LIMIT {limit}"

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_product_by_id(product_id: int) -> Optional[Dict]:
    """Obtiene un producto por ID"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()
        return dict(row) if row else None


def add_product(name: str, category: Optional[str] = None,
                is_frequent: bool = False, update_interval_hours: int = 12) -> int:
    """Agrega un nuevo producto"""
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO products (name, category, is_frequent, update_interval_hours)
            VALUES (?, ?, ?, ?)
        """, (name, category, 1 if is_frequent else 0, update_interval_hours))
        conn.commit()
        return cursor.lastrowid


# === FUNCIONES DE TIENDAS ===

def get_stores(active_only: bool = True) -> List[Dict]:
    """Obtiene lista de tiendas"""
    with get_db() as conn:
        query = "SELECT * FROM stores"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY name"

        rows = conn.execute(query).fetchall()
        result = []
        for row in rows:
            store = dict(row)
            # Parsear config JSON
            if store.get('config'):
                store['config'] = json.loads(store['config'])
            result.append(store)
        return result


def get_store_by_name(name: str) -> Optional[Dict]:
    """Obtiene una tienda por nombre"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM stores WHERE name = ?",
            (name,)
        ).fetchone()
        if row:
            store = dict(row)
            if store.get('config'):
                store['config'] = json.loads(store['config'])
            return store
        return None


def add_store(name: str, url: str, fetch_method: str, config: Dict) -> int:
    """Agrega una nueva tienda"""
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT OR REPLACE INTO stores (name, url, fetch_method, config)
            VALUES (?, ?, ?, ?)
        """, (name, url, fetch_method, json.dumps(config, ensure_ascii=False)))
        conn.commit()
        return cursor.lastrowid


# === FUNCIONES DE PRECIOS ===

def add_price_snapshot(product_id: int, store_id: int, price: float,
                       title: str, url: Optional[str] = None,
                       relevance_score: Optional[int] = None) -> int:
    """Agrega un snapshot de precio"""
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO price_snapshots
            (product_id, store_id, price, title, url, relevance_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, store_id, price, title, url, relevance_score))
        conn.commit()
        return cursor.lastrowid


def get_latest_prices(product_id: int) -> List[Dict]:
    """Obtiene los últimos precios de un producto en todas las tiendas"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM latest_prices
            WHERE product_id = ?
            ORDER BY store_name
        """, (product_id,)).fetchall()
        return [dict(row) for row in rows]


def get_price_history(product_id: int, store_id: Optional[int] = None,
                     days: int = 30) -> List[Dict]:
    """Obtiene histórico de precios"""
    with get_db() as conn:
        query = """
            SELECT ps.*, s.name as store_name
            FROM price_snapshots ps
            JOIN stores s ON ps.store_id = s.id
            WHERE ps.product_id = ?
              AND ps.scraped_at >= datetime('now', '-' || ? || ' days')
        """
        params = [product_id, days]

        if store_id:
            query += " AND ps.store_id = ?"
            params.append(store_id)

        query += " ORDER BY ps.scraped_at DESC"

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_products_to_update() -> List[Dict]:
    """Obtiene productos que necesitan actualización según su intervalo"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT DISTINCT p.*
            FROM products p
            WHERE
                -- Productos que nunca se han scrapeado
                p.id NOT IN (SELECT DISTINCT product_id FROM price_snapshots)
                OR
                -- O productos cuyo último scrape fue hace más de su intervalo
                p.id IN (
                    SELECT ps.product_id
                    FROM price_snapshots ps
                    JOIN products p2 ON ps.product_id = p2.id
                    GROUP BY ps.product_id, p2.update_interval_hours
                    HAVING MAX(ps.scraped_at) < datetime('now', '-' || p2.update_interval_hours || ' hours')
                )
            ORDER BY p.is_frequent DESC, p.name
        """).fetchall()
        return [dict(row) for row in rows]


def get_stats() -> Dict[str, Any]:
    """Obtiene estadísticas generales del sistema"""
    with get_db() as conn:
        stats = {}

        # Total de productos
        stats['total_products'] = conn.execute(
            "SELECT COUNT(*) as count FROM products"
        ).fetchone()['count']

        # Total de tiendas activas
        stats['total_stores'] = conn.execute(
            "SELECT COUNT(*) as count FROM stores WHERE active = 1"
        ).fetchone()['count']

        # Total de snapshots
        stats['total_snapshots'] = conn.execute(
            "SELECT COUNT(*) as count FROM price_snapshots"
        ).fetchone()['count']

        # Último scrape
        last_scrape = conn.execute(
            "SELECT MAX(scraped_at) as last FROM price_snapshots"
        ).fetchone()['last']
        stats['last_scrape'] = last_scrape

        # Productos por categoría
        categories = conn.execute("""
            SELECT category, COUNT(*) as count
            FROM products
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """).fetchall()
        stats['products_by_category'] = [dict(row) for row in categories]

        return stats


# === FUNCIONES DE BÚSQUEDAS NO ENCONTRADAS ===

def record_search_not_found(search_term: str) -> None:
    """Registra una búsqueda que no tuvo resultados"""
    with get_db() as conn:
        # Normalizar el término de búsqueda (lowercase, trim)
        normalized_term = search_term.strip().lower()

        # Intentar insertar o actualizar
        conn.execute("""
            INSERT INTO search_not_found (search_term, search_count, last_searched_at)
            VALUES (?, 1, datetime('now'))
            ON CONFLICT(search_term) DO UPDATE SET
                search_count = search_count + 1,
                last_searched_at = datetime('now')
        """, (normalized_term,))
        conn.commit()


def get_search_not_found_report(limit: int = 50, include_ignored: bool = False) -> List[Dict]:
    """Obtiene reporte de búsquedas sin resultados, ordenado por cantidad"""
    with get_db() as conn:
        query = """
            SELECT
                id,
                search_term,
                search_count,
                ignored,
                first_searched_at,
                last_searched_at
            FROM search_not_found
            WHERE 1=1
        """

        if not include_ignored:
            query += " AND ignored = 0"

        query += """
            ORDER BY search_count DESC, last_searched_at DESC
            LIMIT ?
        """

        rows = conn.execute(query, (limit,)).fetchall()
        return [dict(row) for row in rows]


def toggle_ignore_search_not_found(search_id: int, ignored: bool = True) -> bool:
    """Marca/desmarca una búsqueda como ignorada"""
    with get_db() as conn:
        cursor = conn.execute("""
            UPDATE search_not_found
            SET ignored = ?
            WHERE id = ?
        """, (1 if ignored else 0, search_id))
        conn.commit()
        return cursor.rowcount > 0


def delete_search_not_found(search_id: int) -> bool:
    """Elimina un registro de búsqueda no encontrada"""
    with get_db() as conn:
        cursor = conn.execute("""
            DELETE FROM search_not_found
            WHERE id = ?
        """, (search_id,))
        conn.commit()
        return cursor.rowcount > 0


# Inicializar BD al importar el módulo
init_db()
