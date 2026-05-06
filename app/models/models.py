from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    spec = Column(String(50), default="")
    unit = Column(String(20), default="个")
    cost_price = Column(Float, default=0.0)
    sale_price = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    warning_stock = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class StockIn(Base):
    __tablename__ = "stock_in"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_cost = Column(Float, default=0.0)
    supplier = Column(String(100), default="")
    remark = Column(String(500), default="")
    created_at = Column(DateTime, default=func.now())


class StockOut(Base):
    __tablename__ = "stock_out"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, default=0.0)
    cost_price = Column(Float, default=0.0)
    cost_total = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    customer = Column(String(100), default="")
    remark = Column(String(500), default="")
    created_at = Column(DateTime, default=func.now())
