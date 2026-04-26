"""
微信支付v3 API - Native扫码支付
仓酷家V8.1 商业化变现模块5.2
"""

from fastapi import APIRouter, Request, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Subscription
import os
import time
import random
import string
import json
from datetime import datetime, timedelta
import httpx
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
from jose import jwt, JWTError

# JWT 配置（与 auth.py 保持一致）
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-min-32-characters-long")
JWT_ALGORITHM = "HS256"

def get_user_id_from_token(authorization: str) -> str:
    """从 Authorization Header 解析 JWT 获取 user_id"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证信息")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的认证信息")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token无效")

router = APIRouter(prefix="/api/payment", tags=["payment"])
user_router = APIRouter(prefix="/api/user", tags=["user"])

# 微信支付v3配置
WECHAT_MCHID = os.getenv("WECHAT_MCHID", "1743582175")
WECHAT_APPID = os.getenv("WECHAT_APPID", "wx3e00623c71d93a65")
WECHAT_APIV3_KEY = os.getenv("WECHAT_APIV3_KEY", "")
WECHAT_NOTIFY_URL = os.getenv("WECHAT_NOTIFY_URL", "https://www.cangkujia666.com/api/payment/callback")
WECHAT_CERT_PATH = os.getenv("WECHAT_CERT_PATH", "/var/www/cangkujia/backend/certs/apiclient_cert.pem")
WECHAT_KEY_PATH = os.getenv("WECHAT_KEY_PATH", "/var/www/cangkujia/backend/certs/apiclient_key.pem")

# 定价映射（单位：分）
PRICE_MAP = {
    "monthly": 1990,      # ¥19.9
    "quarterly": 4900,    # ¥49
    "halfyear": 8900,     # ¥89
    "yearly": 16800       # ¥168
}

# 时长映射（天数）
DURATION_MAP = {
    "monthly": 30,
    "quarterly": 90,
    "halfyear": 180,
    "yearly": 365
}

PLAN_NAME_MAP = {
    "monthly": "仓酷家Pro版-月付",
    "quarterly": "仓酷家Pro版-季付",
    "halfyear": "仓酷家Pro版-半年",
    "yearly": "仓酷家Pro版-年付"
}


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    plan_type: str  # monthly, quarterly, halfyear, yearly
    # user_id 不再从请求体获取，改为从 JWT Header 解析


class OrderStatusResponse(BaseModel):
    """订单状态响应"""
    order_no: str
    status: str
    plan_type: Optional[str] = None
    paid_at: Optional[str] = None
    amount: Optional[int] = None


def generate_order_no() -> str:
    """生成订单号：CKJ-2026-{timestamp}-{random4位}"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"CKJ-2026-{timestamp}-{random_num}"


def generate_nonce_str(length=32) -> str:
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_wechat_pay_signature(method: str, url: str, body: str, nonce_str: str, timestamp: str) -> str:
    """
    生成微信支付v3签名
    签名格式：HTTP请求方法\n请求URL\n请求时间戳\n随机字符串\n请求体\n
    注意：GET请求body为空字符串
    """
    message = f"{method}\n{url}\n{timestamp}\n{nonce_str}\n{body}\n"
    
    # 加载商户私钥
    try:
        with open(WECHAT_KEY_PATH, 'r') as f:
            private_key = serialization.load_pem_private_key(
                f.read().encode(),
                password=None
            )
    except Exception as e:
        print(f"加载私钥失败: {e}")
        # 开发环境返回模拟签名
        return "MOCK_SIGNATURE"
    
    # 使用私钥签名
    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    return base64.b64encode(signature).decode('utf-8')


def get_authorization_header(method: str, url: str, body: str = "") -> str:
    """生成Authorization请求头"""
    nonce_str = generate_nonce_str()
    timestamp = str(int(time.time()))
    
    signature = get_wechat_pay_signature(method, url, body, nonce_str, timestamp)
    
    # 序列号（从证书中提取，这里简化处理）
    serial_no = "MOCK_SERIAL_NO"  # 实际应从证书中提取
    
    return f'WECHATPAY2-SHA256-RSA2048 mchid="{WECHAT_MCHID}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{timestamp}",serial_no="{serial_no}"'


@router.get("/config")
async def get_payment_config():
    """
    获取支付配置（4档定价）
    返回定价配置供前端动态渲染
    """
    return {
        "code": 0,
        "data": {
            "pricing_options": [
                {
                    "id": "monthly",
                    "name": "月付",
                    "price": 1990,  # 单位：分
                    "price_yuan": 19.9,
                    "period": "月",
                    "monthly_price": None,
                    "recommended": False,
                    "best_value": False
                },
                {
                    "id": "quarterly",
                    "name": "季付",
                    "price": 4900,
                    "price_yuan": 49,
                    "period": "季",
                    "monthly_price": 16.3,
                    "recommended": False,
                    "best_value": False
                },
                {
                    "id": "halfyear",
                    "name": "半年",
                    "price": 8900,
                    "price_yuan": 89,
                    "period": "半年",
                    "monthly_price": 14.8,
                    "recommended": True,
                    "best_value": False
                },
                {
                    "id": "yearly",
                    "name": "年付",
                    "price": 16800,
                    "price_yuan": 168,
                    "period": "年",
                    "monthly_price": 14,
                    "recommended": False,
                    "best_value": True
                }
            ]
        }
    }


@router.post("/create-order")
async def create_order(
    request: CreateOrderRequest,
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """
    创建支付订单
    调用微信支付v3 Native统一下单API
    从 Authorization Header 解析 JWT 获取 user_id
    """
    try:
        # 从 JWT 获取 user_id 并转换为 int
        user_id = int(get_user_id_from_token(authorization))

        # 验证plan_type
        if request.plan_type not in PRICE_MAP:
            raise HTTPException(status_code=400, detail="无效的套餐类型")
        
        # 生成订单号
        order_no = generate_order_no()
        amount = PRICE_MAP[request.plan_type]
        description = PLAN_NAME_MAP[request.plan_type]
        
        # 创建订单记录
        new_order = Order(
            order_no=order_no,
            user_id=user_id,
            amount=amount / 100,  # 转换为元存储
            status="pending",
            product_name=description,
            description=f"用户{user_id}购买{description}",
            created_at=datetime.now()
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # 构建微信支付v3请求
        url = "/v3/pay/transactions/native"
        request_body = {
            "mchid": WECHAT_MCHID,
            "out_trade_no": order_no,
            "appid": WECHAT_APPID,
            "description": description,
            "notify_url": WECHAT_NOTIFY_URL,
            "amount": {
                "total": amount,
                "currency": "CNY"
            }
        }
        
        body_json = json.dumps(request_body, ensure_ascii=False)
        authorization = get_authorization_header("POST", url, body_json)
        
        # 调用微信支付API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.mch.weixin.qq.com{url}",
                    content=body_json,
                    headers={
                        "Authorization": authorization,
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    timeout=30.0
                )
                
                result = response.json()
                print(f"微信支付响应: {result}")
                
                if response.status_code == 200 and "code_url" in result:
                    # 返回成功
                    return {
                        "code": 0,
                        "message": "订单创建成功",
                        "data": {
                            "order_no": order_no,
                            "code_url": result["code_url"],
                            "amount": amount,
                            "plan_type": request.plan_type
                        }
                    }
                else:
                    # 微信返回错误
                    error_msg = result.get("message", "微信下单失败")
                    print(f"微信下单失败: {error_msg}")
                    raise HTTPException(status_code=500, detail=f"微信下单失败: {error_msg}")

        except Exception as e:
            print(f"调用微信支付API失败: {e}")
            raise HTTPException(status_code=500, detail=f"支付服务异常: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"创建订单失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/order-status")
async def get_order_status(order_no: str, db: Session = Depends(get_db)):
    """查询订单状态"""
    try:
        order = db.query(Order).filter(Order.order_no == order_no).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        return {
            "code": 0,
            "data": {
                "order_no": order.order_no,
                "status": order.status,
                "plan_type": None,  # 需要从订单描述中解析
                "paid_at": order.paid_at.isoformat() if order.paid_at else None,
                "amount": int(order.amount * 100) if order.amount else 0
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def decrypt_wechat_callback(associated_data: str, nonce: str, ciphertext: str) -> dict:
    """
    解密微信支付回调数据
    使用Node.js子进程调用crypto.createDecipheriv（复用安德森日历成熟方案）
    
    原因：Python的cryptography库AESGCM与微信GCM密文格式不兼容
    解决方案：通过Node.js子进程调用crypto.createDecipheriv进行解密
    """
    import subprocess
    
    try:
        # 调用Node.js解密脚本
        result = subprocess.run(
            ['node', '/var/www/cangkujia/backend/decrypt_wechat.js', WECHAT_APIV3_KEY, associated_data, nonce, ciphertext],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Node.js解密失败: {result.stderr}")
            return {}
        
        return json.loads(result.stdout)
        
    except Exception as e:
        print(f"解密失败: {e}")
        import traceback
        traceback.print_exc()
        return {}


@router.post("/callback")
@router.post("/wechat-callback")
async def wechat_callback(request: Request, db: Session = Depends(get_db)):
    """
    微信支付回调接口
    接收微信支付的异步通知
    """
    try:
        # 获取请求体
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        print(f"收到微信支付回调: {json.dumps(data, ensure_ascii=False)[:500]}")
        
        # 提取加密数据
        resource = data.get('resource', {})
        associated_data = resource.get('associated_data', '')
        nonce = resource.get('nonce', '')
        ciphertext = resource.get('ciphertext', '')
        
        # 解密数据
        decrypted_data = decrypt_wechat_callback(associated_data, nonce, ciphertext)
        
        if not decrypted_data:
            return {"code": "FAIL", "message": "解密失败"}
        
        print(f"解密后的数据: {json.dumps(decrypted_data, ensure_ascii=False)}")
        
        # 提取订单信息
        out_trade_no = decrypted_data.get('out_trade_no', '')
        transaction_id = decrypted_data.get('transaction_id', '')
        trade_state = decrypted_data.get('trade_state', '')
        amount_info = decrypted_data.get('amount', {})
        total_fee = amount_info.get('total', 0)
        success_time = decrypted_data.get('success_time', '')
        
        print(f"订单号: {out_trade_no}, 状态: {trade_state}")
        
        # 查询订单
        order = db.query(Order).filter(Order.order_no == out_trade_no).first()
        
        if not order:
            print(f"订单不存在: {out_trade_no}")
            return {"code": "SUCCESS", "message": "成功"}  # 返回成功避免微信重复通知
        
        # 处理支付成功
        if trade_state == "SUCCESS":
            # 更新订单状态
            order.status = "paid"
            order.transaction_id = transaction_id
            order.paid_amount = total_fee / 100  # 分转元
            if success_time:
                try:
                    order.paid_at = datetime.fromisoformat(success_time.replace('Z', '+00:00'))
                except:
                    order.paid_at = datetime.now()
            else:
                order.paid_at = datetime.now()
            
            # 根据product_name/description映射plan_type和天数
            plan_map = {
                'monthly': ('monthly', 30), '月付': ('monthly', 30),
                'quarterly': ('quarterly', 90), '季付': ('quarterly', 90),
                'halfyear': ('halfyear', 180), '半年': ('halfyear', 180),
                'yearly': ('yearly', 365), '年付': ('yearly', 365), '年度': ('yearly', 365)
            }
            
            plan_type = None
            days = 365
            search_text = f"{order.product_name or ''} {order.description or ''}".lower()
            for key, (ptype, d) in plan_map.items():
                if key in search_text:
                    plan_type, days = ptype, d
                    break
            
            # 如果没匹配到，从PLAN_NAME_MAP再试一次
            if not plan_type:
                for pt, name in PLAN_NAME_MAP.items():
                    if name in order.product_name:
                        plan_type = pt
                        break
            
            if not plan_type:
                plan_type = "yearly"  # 默认年付
                days = 365
            
            now = datetime.now()
            expire_at = now + timedelta(days=days)
            
            # 标记用户旧订阅为replaced
            old_subs = db.query(Subscription).filter_by(user_id=order.user_id, status='active').all()
            for sub in old_subs:
                sub.status = 'replaced'
                sub.updated_at = now
            
            # 创建新订阅
            new_sub = Subscription(
                user_id=order.user_id,
                plan_type=plan_type,
                status='active',
                started_at=now,
                expire_at=expire_at,
                order_no=out_trade_no
            )
            db.add(new_sub)
            
            db.commit()
            print(f"支付成功处理完成: {out_trade_no}, 用户: {order.user_id}, 套餐: {plan_type}, 过期时间: {expire_at}")
            
        else:
            # 支付失败或其他状态
            order.status = "failed"
            order.fail_reason = f"trade_state: {trade_state}"
            db.commit()
            print(f"支付未成功: {out_trade_no}, 状态: {trade_state}")
        
        return {"code": "SUCCESS", "message": "成功"}
        
    except Exception as e:
        print(f"回调处理错误: {e}")
        import traceback
        traceback.print_exc()
        return {"code": "SUCCESS", "message": "成功"}  # 返回成功避免微信重复通知


@user_router.get("/subscription")
async def get_user_subscription(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户订阅状态
    返回格式：{status: 'active'|'expired'|'free', plan: plan_type|null, expire_at: ISOString|null, started_at: ISOString|null}
    """
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            return {
                "status": "free",
                "plan": None,
                "expire_at": None,
                "started_at": None
            }
        
        # 检查是否过期
        now = datetime.now()
        if subscription.expire_at and subscription.expire_at < now:
            if subscription.status != 'expired':
                subscription.status = 'expired'
                db.commit()
            return {
                "status": "expired",
                "plan": subscription.plan_type,
                "expire_at": subscription.expire_at.isoformat() if subscription.expire_at else None,
                "started_at": subscription.started_at.isoformat() if subscription.started_at else None
            }
        
        return {
            "status": subscription.status,
            "plan": subscription.plan_type,
            "expire_at": subscription.expire_at.isoformat() if subscription.expire_at else None,
            "started_at": subscription.started_at.isoformat() if subscription.started_at else None
        }
        
    except Exception as e:
        print(f"获取订阅状态失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
