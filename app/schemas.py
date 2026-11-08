"""
Pydantic schemas for request / response validation.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ── Menu ──────────────────────────────────────────────────────────────────────
class CategoryOut(BaseModel):
    id: int
    name: str
    sort: int


class MenuItemOut(BaseModel):
    id: int
    category_id: int
    category: str
    name: str
    price: float
    image_url: Optional[str] = None
    is_active: bool


class MenuItemIn(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(gt=0)
    image_url: Optional[str] = None
    is_active: bool = True


# ── Orders ────────────────────────────────────────────────────────────────────
class CartItemIn(BaseModel):
    item_id: int
    name: str
    price: float
    quantity: int = Field(ge=1)


class PlaceOrderIn(BaseModel):
    order_type: str = Field(pattern="^(Dine-in|Takeaway)$")
    items: list[CartItemIn]


class OrderItemOut(BaseModel):
    id: int
    item_id: int
    name: str
    price: float
    quantity: int
    line_total: float


class OrderOut(BaseModel):
    id: int
    token: str
    order_type: str
    status: str
    subtotal: float
    tax_amount: float
    grand_total: float
    created_at: str
    items: list[OrderItemOut] = []


class OrderStatusIn(BaseModel):
    status: str = Field(pattern="^(Pending|Ready|Served|Cancelled)$")


# ── Settings ──────────────────────────────────────────────────────────────────
class SettingsOut(BaseModel):
    restaurant_name: str
    address: str
    gstin: str
    tax_rate: float
    printer_width: int


class SettingsIn(BaseModel):
    restaurant_name: str = Field(min_length=1, max_length=120)
    address: str = Field(max_length=240)
    gstin: str = Field(max_length=20)
    tax_rate: float = Field(ge=0, le=100)
    printer_width: int = Field(ge=58, le=80)


# ── Dashboard ─────────────────────────────────────────────────────────────────
class DashboardOut(BaseModel):
    total_orders: int
    total_revenue: float
    cancelled: int
    date: str

