"""Dashboard router – today's stats."""
from datetime import date as _date
from fastapi import APIRouter
from app.database import get_conn
from app.schemas import DashboardOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def dashboard(date: str | None = None):
    target = date or str(_date.today())
    with get_conn() as conn:
        row = conn.execute(
            """SELECT
                COUNT(*) as total_orders,
                COALESCE(SUM(CASE WHEN status!='Cancelled' THEN grand_total ELSE 0 END),0) as total_revenue,
                COALESCE(SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END),0) as cancelled
               FROM orders WHERE DATE(created_at)=?""",
            (target,),
        ).fetchone()
    return DashboardOut(
        total_orders=row["total_orders"],
        total_revenue=round(row["total_revenue"], 2),
        cancelled=row["cancelled"],
        date=target,
    )

