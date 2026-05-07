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

# 模拟云端数据存储（实际应该用数据库）
cloud_data_store: Dict[str, Dict[str, Any]] = {}

# 注册设备
@router.post("/device/register")
def register_device(device: DeviceRegister):
    return {"success": True, "message": "设备注册成功"}

# 推送数据到云端
@router.post("/sync/push")
def sync_push(data: SyncPush):
    try:
        # 存储数据到云端
        cloud_data_store[data.device_id] = {
            "products": data.data.get("products", []),
            "stockInList": data.data.get("stockInList", []),
            "saleList": data.data.get("saleList", []),
            "last_update": datetime.now().isoformat()
        }
        return {"success": True, "message": "数据上传成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# 从云端拉取数据
@router.post("/sync/pull")
def sync_pull(data: SyncPull):
    try:
        device_data = cloud_data_store.get(data.device_id)
        if device_data:
            return {
                "success": True,
                "pull_data": {
                    "products": device_data.get("products", []),
                    "stockInList": device_data.get("stockInList", []),
                    "saleList": device_data.get("saleList", [])
                },
                "last_update": device_data.get("last_update")
            }
        else:
            return {
                "success": True,
                "pull_data": None,
                "message": "暂无数据"
            }
    except Exception as e:
        return {"success": False, "message": str(e)}
