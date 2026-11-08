"""Menu router – categories and items CRUD (with image_url support)."""
from fastapi import APIRouter, HTTPException
from app.database import get_conn
from app.schemas import CategoryOut, MenuItemOut, MenuItemIn

router = APIRouter(prefix="/api/menu", tags=["menu"])

_ITEM_SELECT = """
    SELECT m.id, m.category_id, c.name as category,
           m.name, m.price, m.image_url, m.is_active
    FROM menu_items m JOIN categories c ON c.id = m.category_id
"""


@router.get("/categories", response_model=list[CategoryOut])
def list_categories():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, sort FROM categories ORDER BY sort"
        ).fetchall()
    return [dict(r) for r in rows]


@router.get("/items", response_model=list[MenuItemOut])
def list_items(category_id: int | None = None, search: str | None = None):
    sql = _ITEM_SELECT + " WHERE 1=1"
    params: list = []
    if category_id:
        sql += " AND m.category_id = ?"
        params.append(category_id)
    if search:
        sql += " AND m.name LIKE ?"
        params.append(f"%{search}%")
    sql += " ORDER BY c.sort, m.sort"
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


@router.post("/items", response_model=MenuItemOut, status_code=201)
def create_item(body: MenuItemIn):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO menu_items(category_id,name,price,image_url,is_active) VALUES(?,?,?,?,?)",
            (body.category_id, body.name, body.price, body.image_url, int(body.is_active)),
        )
        conn.commit()
        row = conn.execute(
            _ITEM_SELECT + " WHERE m.id=?", (cur.lastrowid,)
        ).fetchone()
    return dict(row)


@router.put("/items/{item_id}", response_model=MenuItemOut)
def update_item(item_id: int, body: MenuItemIn):
    with get_conn() as conn:
        conn.execute(
            "UPDATE menu_items SET category_id=?,name=?,price=?,image_url=?,is_active=? WHERE id=?",
            (body.category_id, body.name, body.price, body.image_url, int(body.is_active), item_id),
        )
        conn.commit()
        row = conn.execute(
            _ITEM_SELECT + " WHERE m.id=?", (item_id,)
        ).fetchone()
    if not row:
        raise HTTPException(404, "Item not found")
    return dict(row)


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
        conn.commit()
