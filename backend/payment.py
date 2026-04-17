"""
微信支付回调处理模块
支持多个业务线：安德森日历(AND-) 和 仓酷家(CKJ-)
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac
import base64
import json
import os
from datetime import datetime

router = APIRouter(prefix="/api/payment", tags=["payment"])

# 微信支付配置
WECHAT_MCH_ID = os.getenv("WECHAT_MCH_ID", "1743582175")
WECHAT_APIV3_KEY = os.getenv("WECHAT_APIV3_KEY", "")

class PaymentCallback(BaseModel):
    """微信支付回调数据模型"""
    id: str
    create_time: str
    resource_type: str
    event_type: str
    summary: str
    resource: dict

@router.post("/callback")
async def wechat_payment_callback(request: Request):
    """
    微信支付统一回调接口
    根据订单号前缀识别业务线：
    - AND- 开头：安德森日历
    - CKJ- 开头：仓酷家
    """
    try:
        # 获取回调数据
        body = await request.body()
        callback_data = json.loads(body)
        
        # 提取订单信息
        resource = callback_data.get("resource", {})
        ciphertext = resource.get("ciphertext", "")
        
        # TODO: 解密微信支付回调数据（需要实现解密逻辑）
        # 这里简化处理，实际需要使用APIv3密钥解密
        
        # 从解密后的数据中提取订单号
        # out_trade_no 格式: AND-xxx 或 CKJ-xxx
        out_trade_no = callback_data.get("out_trade_no", "")
        
        if not out_trade_no:
            return {"code": "FAIL", "message": "订单号不存在"}
        
        # 根据订单前缀识别业务线
        if out_trade_no.startswith("AND-"):
            # 安德森日历订单
            result = await handle_anderson_payment(callback_data, out_trade_no)
        elif out_trade_no.startswith("CKJ-"):
            # 仓酷家订单
            result = await handle_cangkujia_payment(callback_data, out_trade_no)
        else:
            return {"code": "FAIL", "message": "未知的订单类型"}
        
        return result
        
    except Exception as e:
        print(f"支付回调处理错误: {e}")
        return {"code": "FAIL", "message": str(e)}

async def handle_anderson_payment