from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import (
    products_router,
    stock_in_router,
    stock_out_router,
    stats_router,
    export_router
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="商品进销存管理系统",
    description="简单的商品进销存管理系统API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products_router)
app.include_router(stock_in_router)
app.include_router(stock_out_router)
app.include_router(stats_router)
app.include_router(export_router)


@app.get("/")
def root():
    return {"message": "商品进销存管理系统 API", "docs": "/docs"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
