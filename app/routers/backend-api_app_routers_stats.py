from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Product, StockIn, StockOut
from app.schemas import StatsSummary, TrendData, RankingItem

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def get_stats_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(StockOut)
    
    if start_date:
        query = query.filter(StockOut.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(StockOut.created_at <= datetime.fromisoformat(end_date))
    
    records = query.all()
    
    total_sales = sum(r.total_amount for r in records)
    total_cost = sum(r.cost_total for r in records)
    total_profit = total_sales - total_cost
    total_quantity = sum(r.quantity for r in records)
    order_count = len(records)
    
    profit_rate = (total_profit / total_sales * 100) if total_sales > 0 else 0
    
    return StatsSummary(
        total_sales=round(total_sales, 2),
        total_cost=round(total_cost, 2),
        total_profit=round(total_profit, 2),
        profit_rate=round(profit_rate, 2),
        total_quantity=total_quantity,
        order_count=order_count
    )


@router.get("/trend", response_model=List[TrendData])
def get_stats_trend(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    records = db.query(StockOut).filter(
        StockOut.created_at >= start_date,
        StockOut.created_at <= end_date
    ).all()
    
    # Group by date
    trend_dict = {}
    for record in records:
        date_str = record.created_at.strftime("%Y-%m-%d")
        if date_str not in trend_dict:
            trend_dict[date_str] = {"sales": 0, "cost": 0, "profit": 0, "quantity": 0}
        trend_dict[date_str]["sales"] += record.total_amount
        trend_dict[date_str]["cost"] += record.cost_total
        trend_dict[date_str]["profit"] += record.profit
        trend_dict[date_str]["quantity"] += record.quantity
    
    result = [
        TrendData(
            date=date,
            sales=round(data["sales"], 2),
            cost=round(data["cost"], 2),
            profit=round(data["profit"], 2),
            quantity=data["quantity"]
        )
        for date, data in sorted(trend_dict.items())
    ]
    
    return result


@router.get("/ranking", response_model=List[RankingItem])
def get_product_ranking(
    limit: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="profit", regex="^(profit|quantity|sales)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        StockOut.product_id,
        StockOut.product_name,
        func.sum(StockOut.quantity).label("quantity"),
        func.sum(StockOut.total_amount).label("sales"),
        func.sum(StockOut.profit).label("profit")
    ).group_by(StockOut.product_id, StockOut.product_name)
    
    if start_date:
        query = query.filter(StockOut.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(StockOut.created_at <= datetime.fromisoformat(end_date))
    
    if sort_by == "profit":
        query = query.order_by(desc("profit"))
    elif sort_by == "quantity":
        query = query.order_by(desc("quantity"))
    else:
        query = query.order_by(desc("sales"))
    
    results = query.limit(limit).all()
    
    return [
        RankingItem(
            product_id=r.product_id,
            product_name=r.product_name,
            quantity=r.quantity or 0,
            sales=round(r.sales or 0, 2),
            profit=round(r.profit or 0, 2)
        )
        for r in results
    ]
