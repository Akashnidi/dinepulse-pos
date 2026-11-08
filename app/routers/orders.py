"""Orders router – place order, list, status update, token generation."""
from datetime import date as _date
from fastapi import APIRouter, HTTPException
from app.database import get_conn
from app.schemas import PlaceOrderIn, OrderOut, OrderItemOut, OrderStatusIn

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _next_token(conn, order_type: str) -> str:
    today = str(_date.today())
    prefix = "D" if order_type == "Dine-in" else "T"
    row = conn.execute(
        "SELECT count FROM token_counter WHERE date=?", (today,)
    ).fetchone()
    if row:
        new_count = row["count"] + 1
        conn.execute(
            "UPDATE token_counter SET count=? WHERE date=?", (new_count, today)
        )
    else:
        new_count = 1
        conn.execute(
            "INSERT INTO token_counter(date,count) VALUES(?,?)", (today, new_count)
        )
    return f"{prefix}-{new_count:03d}"


def _row_to_order(conn, order_row) -> OrderOut:
    items_rows = conn.execute(
        "SELECT id, item_id, name, price, quantity FROM order_items WHERE order_id=?",
        (order_row["id"],),
    ).fetchall()
    items = [
        OrderItemOut(
            **dict(r), line_total=round(r["price"] * r["quantity"], 2)
        )
        for r in items_rows
    ]
    return OrderOut(**dict(order_row), items=items)


@router.post("", response_model=OrderOut, status_code=201)
def place_order(body: PlaceOrderIn):
    # Fetch tax rate from settings
    with get_conn() as conn:
        setting = conn.execute(
            "SELECT value FROM settings WHERE key='tax_rate'"
        ).fetchone()
        tax_rate = float(setting["value"]) if setting else 5.0

        token = _next_token(conn, body.order_type)
        subtotal = round(sum(i.price * i.quantity for i in body.items), 2)
        tax_amount = round(subtotal * tax_rate / 100, 2)
        grand_total = round(subtotal + tax_amount, 2)

        cur = conn.execute(
            """INSERT INTO orders(token,order_type,subtotal,tax_amount,grand_total)
               VALUES(?,?,?,?,?)""",
            (token, body.order_type, subtotal, tax_amount, grand_total),
        )
        order_id = cur.lastrowid
        for item in body.items:
            conn.execute(
                """INSERT INTO order_items(order_id,item_id,name,price,quantity)
                   VALUES(?,?,?,?,?)""",
                (order_id, item.item_id, item.name, item.price, item.quantity),
            )
        conn.commit()
        order_row = conn.execute(
            "SELECT * FROM orders WHERE id=?", (order_id,)
        ).fetchone()
        return _row_to_order(conn, order_row)


@router.get("", response_model=list[OrderOut])
def list_orders(date: str | None = None, all_orders: bool = False):
    filter_date = date or str(_date.today())
    with get_conn() as conn:
        if all_orders:
            rows = conn.execute(
                "SELECT * FROM orders ORDER BY id DESC LIMIT 200"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM orders WHERE DATE(created_at)=? ORDER BY id DESC",
                (filter_date,),
            ).fetchall()
        return [_row_to_order(conn, r) for r in rows]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM orders WHERE id=?", (order_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Order not found")
        return _row_to_order(conn, row)


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status(order_id: int, body: OrderStatusIn):
    with get_conn() as conn:
        conn.execute(
            "UPDATE orders SET status=? WHERE id=?", (body.status, order_id)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM orders WHERE id=?", (order_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Order not found")
        return _row_to_order(conn, row)

