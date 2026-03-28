"""
database.py
-----------
Handles SQLite database initialization and connection management.
Creates the `products` table if it doesn't exist.
"""

import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "pricecompare.db"

logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database and create required tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                platform  TEXT    NOT NULL,
                price     REAL    NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Database initialized successfully.")


@contextmanager
def get_db():
    """Context manager that yields a sqlite3 connection and ensures it's closed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row        # enable column-name access
    try:
        yield conn
    except Exception as exc:
        conn.rollback()
        logger.error("Database error: %s", exc)
        raise
    finally:
        conn.close()


def save_product(name: str, platform: str, price: float):
    """
    Persist a product price entry.
    Avoids duplicates: skips insertion if the same name+platform combo
    was already stored within the last 60 seconds (same-session guard).
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM products
            WHERE name = ? AND platform = ?
              AND timestamp >= datetime('now', '-60 seconds')
        """, (name.lower(), platform))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO products (name, platform, price, timestamp)
                VALUES (?, ?, ?, ?)
            """, (name.lower(), platform, price, datetime.utcnow()))
            conn.commit()
            logger.debug("Saved: %s | %s | %s", name, platform, price)


def get_price_history(product_name: str) -> list[dict]:
    """
    Retrieve daily aggregated price history for a given product name.
    Returns a list of {"date": "YYYY-MM-DD", "price": float, "platform": str}.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                DATE(timestamp)      AS date,
                platform,
                ROUND(AVG(price), 2) AS price
            FROM products
            WHERE LOWER(name) LIKE ?
            GROUP BY DATE(timestamp), platform
            ORDER BY date ASC
        """, (f"%{product_name.lower()}%",))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
