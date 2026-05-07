from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api", tags=["sync"])

# 设备注册
class DeviceRegister(BaseModel):
    device_id: str
    device_name: str = ""

# 同步推送
class SyncPush(BaseModel):
    device_id: str
    data: Dict[str, Any]
    timestamp: int

# 同步拉取
class SyncPull(BaseModel):
    device_id: str
    last_sync_time: Optional[str] = None

# 共享数据存储（所有设备共用）
shared_data = {
    "products": [],
    "stockInList": [],
    "saleList": []
}

@router.post("/device/register")
def register_device(device: DeviceRegister):
    return {"success": True, "message": "设备注册成功"}

@router.post("/sync/push")
def sync_push(data: SyncPush):
    try:
        # 合并数据到共享存储
        if "products" in data.data and data.data["products"]:
            shared_data["products"] = data.data["products"]
        if "stockInList" in data.data and data.data["stockInList"]:
            shared_data["stockInList"] = data.data["stockInList"]
        if "saleList" in data.data and data.data["saleList"]:
            shared_data["saleList"] = data.data["saleList"]
        
        return {"success": True, "message": "数据上传成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.post("/sync/pull")
def sync_pull(data: SyncPull):
    try:
        return {
            "success": True,
            "pull_data": {
                "products": shared_data.get("products", []),
                "stockInList": shared_data.get("stockInList", []),
                "saleList": shared_data.get("saleList", [])
            },
            "last_update": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
