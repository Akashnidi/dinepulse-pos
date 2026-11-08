"""Settings router – read and update restaurant settings."""
from fastapi import APIRouter
from app.database import get_conn
from app.schemas import SettingsOut, SettingsIn

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _load(conn) -> dict:
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    return {r["key"]: r["value"] for r in rows}


@router.get("", response_model=SettingsOut)
def get_settings():
    with get_conn() as conn:
        d = _load(conn)
    return SettingsOut(
        restaurant_name=d.get("restaurant_name", "DinePOS Restaurant"),
        address=d.get("address", ""),
        gstin=d.get("gstin", ""),
        tax_rate=float(d.get("tax_rate", 5)),
        printer_width=int(d.get("printer_width", 80)),
    )


@router.put("", response_model=SettingsOut)
def save_settings(body: SettingsIn):
    updates = {
        "restaurant_name": body.restaurant_name,
        "address": body.address,
        "gstin": body.gstin,
        "tax_rate": str(body.tax_rate),
        "printer_width": str(body.printer_width),
    }
    with get_conn() as conn:
        for k, v in updates.items():
            conn.execute(
                "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (k, v)
            )
        conn.commit()
    return SettingsOut(**{k: v for k, v in updates.items()},
                       tax_rate=body.tax_rate,
                       printer_width=body.printer_width)

