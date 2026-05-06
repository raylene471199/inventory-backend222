from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Product, StockOut
from app.schemas import StockOutCreate, StockOutResponse

router = APIRouter(prefix="/api/stock-out", tags=["stock-out"])


@router.get("", response_model=List[StockOutResponse])
def get_stock_out_records(
    skip: int = 0, 
    limit: int = 100, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    product_id: Optional[int] = None,
    customer: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(StockOut)
    
    if start_date:
        query = query.filter(StockOut.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(StockOut.created_at <= datetime.fromisoformat(end_date))
    if product_id:
        query = query.filter(StockOut.product_id == product_id)
    if customer:
        query = query.filter(StockOut.customer.contains(customer))
    
    return query.order_by(desc(StockOut.created_at)).offset(skip).limit(limit).all()


@router.post("", response_model=StockOutResponse)
def create_stock_out_record(record: StockOutCreate, db: Session = Depends(get_db)):
    # Check product exists and has enough stock
    product = db.query(Product).filter(Product.id == record.product_id, Product.is_deleted == False).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    if product.stock < record.quantity:
        raise HTTPException(status_code=400, detail=f"库存不足，当前库存: {product.stock}")
    
    # Calculate financials
    total_amount = record.quantity * record.unit_price
    cost_price = product.cost_price  # Get current cost price
    cost_total = record.quantity * cost_price
    profit = total_amount - cost_total
    
    # Create stock out record
    db_record = StockOut(
        product_id=record.product_id,
        product_name=product.name,
        quantity=record.quantity,
        unit_price=record.unit_price,
        total_amount=total_amount,
        cost_price=cost_price,
        cost_total=cost_total,
        profit=profit,
        customer=record.customer,
        remark=record.remark
    )
    
    # Reduce product stock
    product.stock -= record.quantity
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/{record_id}", response_model=StockOutResponse)
def get_stock_out_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(StockOut).filter(StockOut.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record
