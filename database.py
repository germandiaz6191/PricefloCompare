"""
Sistema de base de datos dual para ePriceFlo
Soporta SQLite (local) y PostgreSQL (producción) automáticamente
"""
import json
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any

# Detectar tipo de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "data/prices.db")
IS_POSTGRES = DATABASE_URL.startswith(("postgresql://", "postgres://"))

# Importar dependencias según tipo de BD
if IS_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
        # Railway a veces usa postgres:// en lugar de postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    except ImportError:
        print("⚠️  psycopg2 no instalado. Instala: pip install psycopg2-binary")
        raise
else:
    import sqlite3

print(f"🗄️  Usando {'PostgreSQL' if IS_POSTGRES else 'SQLite'} como base de datos")


@contextmanager
def get_db():
    """Context manager para conexiones de BD (SQLite o PostgreSQL)"""
    if IS_POSTGRES:
        # PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        try:
            yield conn
        finally:
            conn.close()
    else:
        # SQLite
        os.makedirs(os.path.dirname(DATABASE_URL), exist_ok=True)
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


def init_db():
    """Crea las tablas si no existen"""
    with get_db() as conn:
        cursor = conn.cursor()

        if IS_POSTGRES:
            # SQL para PostgreSQL
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                is_frequent BOOLEAN DEFAULT FALSE,
                update_interval_hours INTEGER DEFAULT 12,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS stores (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                fetch_method TEXT NOT NULL,
                config JSONB,
                active BOOLEAN DEFAULT TRUE,
                affiliate_enabled BOOLEAN DEFAULT FALSE,
                affiliate_code TEXT,
                affiliate_url_pattern TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS price_snapshots (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
                price DECIMAL(10,2),
                title TEXT,
                url TEXT,
                relevance_score INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS search_not_found (
                id SERIAL PRIMARY KEY,
                search_term TEXT NOT NULL UNIQUE,
                search_count INTEGER DEFAULT 1,
                ignored BOOLEAN DEFAULT FALSE,
                first_searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_price_product_date ON price_snapshots(product_id, scraped_at DESC);
            CREATE INDEX IF NOT EXISTS idx_price_store_date ON price_snapshots(store_id, scraped_at DESC);
            CREATE INDEX IF NOT EXISTS idx_product_category ON products(category);
            CREATE INDEX IF NOT EXISTS idx_product_frequent ON products(is_frequent, update_interval_hours);
            CREATE INDEX IF NOT EXISTS idx_search_not_found_count ON search_not_found(search_count DESC, ignored);
            """)
        else:
            # SQL para SQLite
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                is_frequent INTEGER DEFAULT 0,
                update_interval_hours INTEGER DEFAULT 12,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                fetch_method TEXT NOT NULL,
                config TEXT,
                active INTEGER DEFAULT 1,
                affiliate_enabled INTEGER DEFAULT 0,
                affiliate_code TEXT,
                affiliate_url_pattern TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

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

            CREATE TABLE IF NOT EXISTS search_not_found (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_term TEXT NOT NULL UNIQUE,
                search_count INTEGER DEFAULT 1,
                ignored INTEGER DEFAULT 0,
                first_searched_at TEXT DEFAULT (datetime('now')),
                last_searched_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_price_product_date ON price_snapshots(product_id, scraped_at DESC);
            CREATE INDEX IF NOT EXISTS idx_price_store_date ON price_snapshots(store_id, scraped_at DESC);
            CREATE INDEX IF NOT EXISTS idx_product_category ON products(category);
            CREATE INDEX IF NOT EXISTS idx_product_frequent ON products(is_frequent, update_interval_hours);
            CREATE INDEX IF NOT EXISTS idx_search_not_found_count ON search_not_found(search_count DESC, ignored);
            """)

        conn.commit()
        print("✅ Base de datos inicializada")


def _fetch_all(cursor) -> List[Dict]:
    """Convierte resultados de cursor a lista de dicts (compatible con ambas BDs)"""
    if IS_POSTGRES:
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        return [dict(row) for row in cursor.fetchall()]


def _fetch_one(cursor) -> Optional[Dict]:
    """Convierte resultado de cursor a dict (compatible con ambas BDs)"""
    if IS_POSTGRES:
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    else:
        row = cursor.fetchone()
        return dict(row) if row else None


def _param_placeholder(index: int = 0) -> str:
    """Retorna placeholder correcto según BD (? para SQLite, %s para PostgreSQL)"""
    return "%s" if IS_POSTGRES else "?"


# === FUNCIONES DE PRODUCTOS ===

def get_products(limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict]:
    """Obtiene lista de productos"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if category:
            query += f" AND category = {_param_placeholder()}"
            params.append(category)

        query += " ORDER BY is_frequent DESC, name ASC"

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, params)
        return _fetch_all(cursor)


def get_product_by_id(product_id: int) -> Optional[Dict]:
    """Obtiene un producto por ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM products WHERE id = {_param_placeholder()}",
            (product_id,)
        )
        return _fetch_one(cursor)


def add_product(name: str, category: Optional[str] = None,
                is_frequent: bool = False, update_interval_hours: int = 12) -> int:
    """Agrega un nuevo producto"""
    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

        if IS_POSTGRES:
            cursor.execute(f"""
                INSERT INTO products (name, category, is_frequent, update_interval_hours)
                VALUES ({ph}, {ph}, {ph}, {ph})
                RETURNING id
            """, (name, category, is_frequent, update_interval_hours))
            product_id = cursor.fetchone()[0]
        else:
            cursor.execute(f"""
                INSERT INTO products (name, category, is_frequent, update_interval_hours)
                VALUES ({ph}, {ph}, {ph}, {ph})
            """, (name, category, 1 if is_frequent else 0, update_interval_hours))
            product_id = cursor.lastrowid

        conn.commit()
        return product_id


# === FUNCIONES DE TIENDAS ===

def get_stores(active_only: bool = True) -> List[Dict]:
    """Obtiene lista de tiendas"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM stores"
        if active_only:
            query += f" WHERE active = {1 if not IS_POSTGRES else 'TRUE'}"
        query += " ORDER BY name"

        cursor.execute(query)
        result = []
        for row in _fetch_all(cursor):
            store = dict(row)
            # Parsear config JSON solo en SQLite (PostgreSQL lo hace automáticamente)
            if not IS_POSTGRES and store.get('config'):
                store['config'] = json.loads(store['config'])
            result.append(store)
        return result


def get_store_by_name(name: str) -> Optional[Dict]:
    """Obtiene una tienda por nombre"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM stores WHERE name = {_param_placeholder()}",
            (name,)
        )
        store = _fetch_one(cursor)
        if store and not IS_POSTGRES and store.get('config'):
            store['config'] = json.loads(store['config'])
        return store


def add_store(name: str, url: str, fetch_method: str, config: Dict) -> int:
    """Agrega una nueva tienda"""
    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

        config_value = config if IS_POSTGRES else json.dumps(config, ensure_ascii=False)

        if IS_POSTGRES:
            cursor.execute(f"""
                INSERT INTO stores (name, url, fetch_method, config)
                VALUES ({ph}, {ph}, {ph}, {ph})
                ON CONFLICT (name) DO UPDATE SET
                    url = EXCLUDED.url,
                    fetch_method = EXCLUDED.fetch_method,
                    config = EXCLUDED.config
                RETURNING id
            """, (name, url, fetch_method, json.dumps(config)))
            store_id = cursor.fetchone()[0]
        else:
            cursor.execute(f"""
                INSERT OR REPLACE INTO stores (name, url, fetch_method, config)
                VALUES ({ph}, {ph}, {ph}, {ph})
            """, (name, url, fetch_method, config_value))
            store_id = cursor.lastrowid

        conn.commit()
        return store_id


# === FUNCIONES DE PRECIOS ===

def add_price_snapshot(product_id: int, store_id: int, price: float,
                       title: str, url: Optional[str] = None,
                       relevance_score: Optional[int] = None) -> int:
    """Agrega un snapshot de precio"""
    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

        if IS_POSTGRES:
            cursor.execute(f"""
                INSERT INTO price_snapshots
                (product_id, store_id, price, title, url, relevance_score)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                RETURNING id
            """, (product_id, store_id, price, title, url, relevance_score))
            snapshot_id = cursor.fetchone()[0]
        else:
            cursor.execute(f"""
                INSERT INTO price_snapshots
                (product_id, store_id, price, title, url, relevance_score)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            """, (product_id, store_id, price, title, url, relevance_score))
            snapshot_id = cursor.lastrowid

        conn.commit()
        return snapshot_id


def get_latest_prices(product_id: int) -> List[Dict]:
    """Obtiene los últimos precios de un producto en todas las tiendas"""
    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

        # Query compatible con ambas BDs
        cursor.execute(f"""
            SELECT DISTINCT ON (ps.product_id, ps.store_id)
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
            WHERE ps.product_id = {ph}
            ORDER BY ps.product_id, ps.store_id, ps.scraped_at DESC
        """ if IS_POSTGRES else f"""
            SELECT ps.*, p.name as product_name, p.category as product_category, s.name as store_name
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
            ) AND ps.product_id = {ph}
            ORDER BY s.name
        """, (product_id,))

        return _fetch_all(cursor)


def get_price_history(product_id: int, store_id: Optional[int] = None,
                     days: int = 30) -> List[Dict]:
    """Obtiene histórico de precios"""
    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

        if IS_POSTGRES:
            query = f"""
                SELECT ps.*, s.name as store_name
                FROM price_snapshots ps
                JOIN stores s ON ps.store_id = s.id
                WHERE ps.product_id = {ph}
                  AND ps.scraped_at >= NOW() - INTERVAL '{days} days'
            """
        else:
            query = f"""
                SELECT ps.*, s.name as store_name
                FROM price_snapshots ps
                JOIN stores s ON ps.store_id = s.id
                WHERE ps.product_id = {ph}
                  AND ps.scraped_at >= datetime('now', '-{days} days')
            """

        params = [product_id]

        if store_id:
            query += f" AND ps.store_id = {ph}"
            params.append(store_id)

        query += " ORDER BY ps.scraped_at DESC"

        cursor.execute(query, params)
        return _fetch_all(cursor)


def get_products_to_update() -> List[Dict]:
    """Obtiene productos que necesitan actualización según su intervalo"""
    with get_db() as conn:
        cursor = conn.cursor()

        if IS_POSTGRES:
            query = """
                SELECT DISTINCT p.*
                FROM products p
                WHERE
                    p.id NOT IN (SELECT DISTINCT product_id FROM price_snapshots)
                    OR
                    p.id IN (
                        SELECT ps.product_id
                        FROM price_snapshots ps
                        JOIN products p2 ON ps.product_id = p2.id
                        GROUP BY ps.product_id, p2.update_interval_hours
                        HAVING MAX(ps.scraped_at) < NOW() - (p2.update_interval_hours || ' hours')::INTERVAL
                    )
                ORDER BY p.is_frequent DESC, p.name
            """
        else:
            query = """
                SELECT DISTINCT p.*
                FROM products p
                WHERE
                    p.id NOT IN (SELECT DISTINCT product_id FROM price_snapshots)
                    OR
                    p.id IN (
                        SELECT ps.product_id
                        FROM price_snapshots ps
                        JOIN products p2 ON ps.product_id = p2.id
                        GROUP BY ps.product_id, p2.update_interval_hours
                        HAVING MAX(ps.scraped_at) < datetime('now', '-' || p2.update_interval_hours || ' hours')
                    )
                ORDER BY p.is_frequent DESC, p.name
            """

        cursor.execute(query)
        return _fetch_all(cursor)


def get_stats() -> Dict[str, Any]:
    """Obtiene estadísticas generales del sistema"""
    with get_db() as conn:
        cursor = conn.cursor()
        stats = {}

        # Total de productos
        cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = _fetch_one(cursor)['count']

        # Total de tiendas activas
        cursor.execute(f"SELECT COUNT(*) as count FROM stores WHERE active = {1 if not IS_POSTGRES else 'TRUE'}")
        stats['total_stores'] = _fetch_one(cursor)['count']

        # Total de snapshots
        cursor.execute("SELECT COUNT(*) as count FROM price_snapshots")
        stats['total_snapshots'] = _fetch_one(cursor)['count']

        # Último scrape
        cursor.execute("SELECT MAX(scraped_at) as last FROM price_snapshots")
        stats['last_scrape'] = _fetch_one(cursor)['last']

        # Productos por categoría
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM products
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """)
        stats['products_by_category'] = _fetch_all(cursor)

        return stats


# === FUNCIONES DE BÚSQUEDAS NO ENCONTRADAS ===

def record_search_not_found(search_term: str) -> None:
    """Registra una búsqueda que no tuvo resultados"""
    with get_db() as conn:
        cursor = conn.cursor()
        normalized_term = search_term.strip().lower()
        ph = _param_placeholder()

        if IS_POSTGRES:
            cursor.execute(f"""
                INSERT INTO search_not_found (search_term, search_count, last_searched_at)
                VALUES ({ph}, 1, NOW())
                ON CONFLICT(search_term) DO UPDATE SET
                    search_count = search_not_found.search_count + 1,
                    last_searched_at = NOW()
            """, (normalized_term,))
        else:
            cursor.execute(f"""
                INSERT INTO search_not_found (search_term, search_count, last_searched_at)
                VALUES ({ph}, 1, datetime('now'))
                ON CONFLICT(search_term) DO UPDATE SET
                    search_count = search_count + 1,
                    last_searched_at = datetime('now')
            """, (normalized_term,))

        conn.commit()


def get_search_not_found_report(limit: int = 50, include_ignored: bool = False) -> List[Dict]:
    """Obtiene reporte de búsquedas sin resultados, ordenado por cantidad"""
    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

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
            query += f" AND ignored = {0 if not IS_POSTGRES else 'FALSE'}"

        query += f"""
            ORDER BY search_count DESC, last_searched_at DESC
            LIMIT {ph}
        """

        cursor.execute(query, (limit,))
        return _fetch_all(cursor)


def toggle_ignore_search_not_found(search_id: int, ignored: bool = True) -> bool:
    """Marca/desmarca una búsqueda como ignorada"""
    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

        ignored_value = ignored if IS_POSTGRES else (1 if ignored else 0)

        cursor.execute(f"""
            UPDATE search_not_found
            SET ignored = {ph}
            WHERE id = {ph}
        """, (ignored_value, search_id))
        conn.commit()
        return cursor.rowcount > 0


def delete_search_not_found(search_id: int) -> bool:
    """Elimina un registro de búsqueda no encontrada"""
    with get_db() as conn:
        cursor = conn.cursor()
        ph = _param_placeholder()

        cursor.execute(f"""
            DELETE FROM search_not_found
            WHERE id = {ph}
        """, (search_id,))
        conn.commit()
        return cursor.rowcount > 0


# Inicializar BD al importar el módulo
init_db()
