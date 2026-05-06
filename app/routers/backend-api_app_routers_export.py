from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
from app.database import get_db
from app.models import Product, StockIn, StockOut

router = APIRouter(prefix="/api/export", tags=["export"])


def create_excel(data: list, headers: list, title: str):
    wb = Workbook()
    ws = wb.active
    ws.title = title
    
    # Write headers
    ws.append(headers)
    
    # Write data
    for row in data:
        ws.append(row)
    
    # Auto adjust column width
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    return wb


@router.get("/products")
def export_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_deleted == False).order_by(desc(Product.id)).all()
    
    headers = ["ID", "商品名称", "规格", "单位", "进货价", "销售价", "库存", "预警库存", "创建时间"]
    data = [
        [
            p.id, p.name, p.spec, p.unit, p.cost_price, p.sale_price,
            p.stock, p.warning_stock, p.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ]
        for p in products
    ]
    
    wb = create_excel(data, headers, "商品列表")
    
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    filename = f"products_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/stock-in")
def export_stock_in(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(StockIn)
    
    if start_date:
        query = query.filter(StockIn.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(StockIn.created_at <= datetime.fromisoformat(end_date))
    
    records = query.order_by(desc(StockIn.created_at)).all()
    
    headers = ["ID", "商品名称", "数量", "单价", "总成本", "供应商", "备注", "入库时间"]
    data = [
        [
            r.id, r.product_name, r.quantity, r.unit_price, r.total_cost,
            r.supplier, r.remark, r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ]
        for r in records
    ]
    
    wb = create_excel(data, headers, "入库记录")
    
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    filename = f"stock_in_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/stock-out")
def export_stock_out(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(StockOut)
    
    if start_date:
        query = query.filter(StockOut.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(StockOut.created_at <= datetime.fromisoformat(end_date))
    
    records = query.order_by(desc(StockOut.created_at)).all()
    
    headers = ["ID", "商品名称", "数量", "销售单价", "销售额", "成本单价", "成本总额", "利润", "客户", "备注", "销售时间"]
    data = [
        [
            r.id, r.product_name, r.quantity, r.unit_price, r.total_amount,
            r.cost_price, r.cost_total, r.profit, r.customer, r.remark,
            r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ]
        for r in records
    ]
    
    wb = create_excel(data, headers, "销售记录")
    
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    filename = f"stock_out_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
