from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Product, StockIn
from app.schemas import StockInCreate, StockInResponse

router = APIRouter(prefix="/api/stock-in", tags=["stock-in"])


@router.get("", response_model=List[StockInResponse])
def get_stock_in_records(
    skip: int = 0, 
    limit: int = 100, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    supplier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(StockIn)
    
    if start_date:
        query = query.filter(StockIn.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(StockIn.created_at <= datetime.fromisoformat(end_date))
    if supplier:
        query = query.filter(StockIn.supplier.contains(supplier))
    
    return query.order_by(desc(StockIn.created_at)).offset(skip).limit(limit).all()


@router.post("", response_model=StockInResponse)
def create_stock_in_record(record: StockInCreate, db: Session = Depends(get_db)):
    # Check product exists
    product = db.query(Product).filter(Product.id == record.product_id, Product.is_deleted == False).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # Calculate total cost
    total_cost = record.quantity * record.unit_price
    
    # Create stock in record
    db_record = StockIn(
        product_id=record.product_id,
        product_name=product.name,
        quantity=record.quantity,
        unit_price=record.unit_price,
        total_cost=total_cost,
        supplier=record.supplier,
        remark=record.remark
    )
    
    # Update product stock and cost_price
    product.stock += record.quantity
    product.cost_price = record.unit_price  # Update to latest purchase price
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/{record_id}", response_model=StockInResponse)
def get_stock_in_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(StockIn).filter(StockIn.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record
