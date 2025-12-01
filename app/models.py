# app/models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    product_id: str = Field(index=True, unique=True)
    available_stocks: int
    price_per_unit: float
    tax_percent: float

class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)

class Purchase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_amount: float = 0.0
    paid_amount: float = 0.0

class PurchaseItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    purchase_id: Optional[int] = Field(default=None, foreign_key="purchase.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    product_code: str
    qty: int
    unit_price: float
    tax_percent: float
    line_total: float

class Denomination(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: int
    count: int
