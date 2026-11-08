"""
Database bootstrap: creates tables, seeds demo menu, provides a connection factory.
Paths are PyInstaller-safe (sys._MEIPASS for bundled assets, ProgramData for data).
"""
import os
import sqlite3
import sys
from pathlib import Path


def get_data_dir() -> Path:
    """
    Persistent data directory – survives app updates.
    Dev mode  : project root
    Frozen exe: C:\\ProgramData\\RestaurantPOS
    """
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "RestaurantPOS"
    else:
        base = Path(__file__).resolve().parent.parent  # project root
    base.mkdir(parents=True, exist_ok=True)
    return base


DB_PATH = get_data_dir() / "pos_data.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=FULL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


# ── Schema ────────────────────────────────────────────────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL UNIQUE,
    sort INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS menu_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name        TEXT    NOT NULL,
    price       REAL    NOT NULL,
    image_url   TEXT,
    is_active   INTEGER DEFAULT 1,
    sort        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    token        TEXT    NOT NULL,
    order_type   TEXT    NOT NULL CHECK(order_type IN ('Dine-in','Takeaway')),
    status       TEXT    NOT NULL DEFAULT 'Pending'
                         CHECK(status IN ('Pending','Ready','Served','Cancelled')),
    subtotal     REAL    NOT NULL,
    tax_amount   REAL    NOT NULL,
    grand_total  REAL    NOT NULL,
    created_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now','localtime'))
);

CREATE TABLE IF NOT EXISTS order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    item_id    INTEGER NOT NULL REFERENCES menu_items(id),
    name       TEXT    NOT NULL,
    price      REAL    NOT NULL,
    quantity   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS token_counter (
    date  TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0
);
"""

SEED_SETTINGS = {
    "restaurant_name": "DinePOS Restaurant",
    "address": "MG Road, Bengaluru - 560001",
    "gstin": "29ABCDE1234F125",
    "tax_rate": "5",
    "printer_width": "80",
}

SEED_MENU = {
    "Starters":    [("Veg Soup", 90), ("Chicken Soup", 120), ("Paneer Tikka", 220), ("Chicken Tikka", 260)],
    "Main Course": [("Dal Makhani", 180), ("Paneer Butter Masala", 220), ("Chicken Curry", 240), ("Fish Fry", 280)],
    "Biryani":     [("Veg Biryani", 180), ("Chicken Biryani", 240), ("Mutton Biryani", 320)],
    "Beverages":   [("Lassi", 60), ("Masala Chai", 30), ("Cold Coffee", 80), ("Fresh Lime Soda", 50)],
    "Desserts":    [("Gulab Jamun", 80), ("Ice Cream", 100), ("Kheer", 90)],
}


def init_db():
    with get_conn() as conn:
        conn.executescript(DDL)

        # Non-destructive migration: add image_url if upgrading from older schema
        try:
            conn.execute("ALTER TABLE menu_items ADD COLUMN image_url TEXT")
            conn.commit()
        except Exception:
            pass  # column already exists

        # Settings
        for k, v in SEED_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (k, v)
            )

        # Categories + Menu items (only on first run)
        for sort_idx, (cat_name, items) in enumerate(SEED_MENU.items()):
            conn.execute(
                "INSERT OR IGNORE INTO categories(name,sort) VALUES(?,?)",
                (cat_name, sort_idx),
            )
            cat_id = conn.execute(
                "SELECT id FROM categories WHERE name=?", (cat_name,)
            ).fetchone()["id"]
            for item_sort, (item_name, price) in enumerate(items):
                conn.execute(
                    "INSERT OR IGNORE INTO menu_items(category_id,name,price,sort) VALUES(?,?,?,?)",
                    (cat_id, item_name, price, item_sort),
                )
        conn.commit()

