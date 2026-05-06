from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Product Schemas
class ProductBase(BaseModel):
    name: str
    spec: str = ""
    unit: str = "个"
    cost_price: float = 0.0
    sale_price: float = 0.0
    stock: int = 0
    warning_stock: int = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None
    stock: Optional[int] = None
    warning_stock: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# StockIn Schemas
class StockInBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    supplier: str = ""
    remark: str = ""


class StockInCreate(StockInBase):
    pass


class StockInResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_cost: float
    supplier: str
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True


# StockOut Schemas
class StockOutBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    customer: str = ""
    remark: str = ""


class StockOutCreate(StockOutBase):
    pass


class StockOutResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    cost_price: float
    cost_total: float
    profit: float
    customer: str
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True


# Stats Schemas
class StatsSummary(BaseModel):
    total_sales: float
    total_cost: float
    total_profit: float
    profit_rate: float
    total_quantity: int
    order_count: int


class TrendData(BaseModel):
    date: str
    sales: float
    cost: float
    profit: float
    quantity: int


class RankingItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    sales: float
    profit: float
