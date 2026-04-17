from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import hashlib
import xml.etree.ElementTree as ET
import os
import hmac
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models import Order
import httpx
import time
import random
import string

router = APIRouter(prefix="/api/payment", tags=["payment"])

# 微信支付配置
WECHAT_MCH_ID = os.getenv("WECHAT_MCH_ID", "1743582175")
WECHAT_APIV3_KEY = os.getenv("WECHAT_APIV3_KEY", "")
WECHAT_APPID = os.getenv("WECHAT_APPID", "")
WECHAT_NOTIFY_URL = "https://cangkujia666.com/api/payment/callback"

# 微信支付API基础URL
WECHAT_PAY_BASE_URL = "https://api.mch.weixin.qq.com"

class PaymentCallback(BaseModel):
    """微信支付回调数据模型"""
    appid: str
    mch_id: str
    out_trade_no: str
    transaction_id: Optional[str] = None
    total_fee: Optional[int] = None
    result_code: Optional[str] = None
    return_code: Optional[str] = None
    time_end: Optional[str] = None
    sign: Optional[str] = None

class CreateOrderRequest(BaseModel):
    """创建订单请求模型"""
    user_id: int
    amount: float
    product_name: str = "仓酷家服务"
    description: Optional[str] = ""
    openid: Optional[str] = None  # 微信用户openid（JSAPI支付需要）

def generate_nonce_str(length=32):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_sign(params: dict, api_key: str) -> str:
    """
    生成微信支付签名
    微信签名算法：将参数按ASCII码排序，拼接成字符串，最后加上&key=api_key，然后MD5加密
    """
    # 过滤空值和sign字段
    filtered_params = {k: v for k, v in params.items() if v is not None and k != 'sign'}
    
    # 按ASCII码排序并拼接
    sorted_params = sorted(filtered_params.items())
    string_a = '&'.join([f"{k}={v}" for k, v in sorted_params])
    
    # 拼接key
    string_sign_temp = f"{string_a}&key={api_key}"
    
    # MD5加密并转大写
    sign = hashlib.md5(string_sign_temp.encode('utf-8')).hexdigest().upper()
    
    return sign

def verify_wechat_sign(data: dict, api_key: str) -> bool:
    """
    验证微信支付签名
    """
    # 获取sign字段
    sign = data.get('sign')
    if not sign:
        return False
    
    # 复制数据用于验证
    verify_data = data.copy()
    verify_data.pop('sign', None)
    
    # 计算签名
    calculated_sign = generate_sign(verify_data, api_key)
    
    return calculated_sign == sign

def dict_to_xml(data: dict) -> str:
    """将字典转换为XML字符串"""
    xml_parts = ["<xml>"]
    for key, value in data.items():
        xml_parts.append(f"<{key}><![CDATA[{value}]]></{key}>")
    xml_parts.append("</xml>")
    return ''.join(xml_parts)

def parse_wechat_xml(xml_data: str) -> dict:
    """解析微信支付回调的XML数据"""
    root = ET.fromstring(xml_data)
    data = {}
    for child in root:
        data[child.tag] = child.text
    return data

def generate_response_xml(return_code: str, return_msg: str) -> str:
    """生成返回给微信的XML响应"""
    return f"""<xml>
<return_code><![CDATA[{return_code}]]></return_code>
<return_msg><![CDATA[{return_msg}]]></return_msg>
</xml>"""

async def wechat_unified_order(
    order_no: str,
    amount: float,
    description: str,
    openid: str = None,
    trade_type: str = "NATIVE"
) -> dict:
    """
    调用微信统一下单API
    
    Args:
        order_no: 商户订单号
        amount: 订单金额（元）
        description: 商品描述
        openid: 微信用户openid（JSAPI支付需要）
        trade_type: 交易类型（NATIVE-扫码支付，JSAPI-公众号支付）
    
    Returns:
        dict: 微信支付返回的结果
    """
    try:
        # 构建请求参数
        params = {
            "appid": WECHAT_APPID,
            "mch_id": WECHAT_MCH_ID,
            "nonce_str": generate_nonce_str(),
            "body": description,
            "out_trade_no": order_no,
            "total_fee": int(amount * 100),  # 转换为分
            "spbill_create_ip": "150.158.45.157",  # 服务器IP
            "notify_url": WECHAT_NOTIFY_URL,
            "trade_type": trade_type,
        }
        
        # JSAPI支付需要openid
        if trade_type == "JSAPI" and openid:
            params["openid"] = openid
        
        # 生成签名
        params["sign"] = generate_sign(params, WECHAT_APIV3_KEY)
        
        # 转换为XML
        xml_data = dict_to_xml(params)
        
        print(f"统一下单请求: {xml_data}")
        
        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{WECHAT_PAY_BASE_URL}/pay/unifiedorder",
                content=xml_data,
                headers={"Content-Type": "application/xml"},
                timeout=30.0
            )
        
        # 解析响应
        result = parse_wechat_xml(response.text)
        print(f"统一下单响应: {result}")
        
        # 验证返回签名
        if not verify_wechat_sign(result, WECHAT_APIV3_KEY):
            print("警告: 响应签名验证失败")
        
        return result
        
    except Exception as e:
        print(f"统一下单请求失败: {e}")
        import traceback
        traceback.print_exc()
        return {"return_code": "FAIL", "return_msg": str(e)}

def generate_jsapi_params(prepay_id: str) -> dict:
    """
    生成JSAPI支付参数（用于前端调起微信支付）
    """
    params = {
        "appId": WECHAT_APPID,
        "timeStamp": str(int(time.time())),
        "nonceStr": generate_nonce_str(),
        "package": f"prepay_id={prepay_id}",
        "signType": "MD5",
    }
    
    # 生成支付签名
    params["paySign"] = generate_sign(params, WECHAT_APIV3_KEY)
    
    return params

@router.post("/callback")
async def wechat_payment_callback(request: Request, db: Session = Depends(get_db)):
    """
    微信支付回调接口
    微信在用户支付完成后会主动调用此接口通知支付结果
    支持多业务线：CKJ-开头为仓酷家订单，AND-开头为安德森日历订单
    """
    try:
        # 获取原始XML数据
        body = await request.body()
        xml_data = body.decode('utf-8')
        
        print(f"收到微信支付回调: {xml_data[:200]}...")
        
        # 解析XML
        data = parse_wechat_xml(xml_data)
        
        # 提取关键字段
        out_trade_no = data.get('out_trade_no', '')
        result_code = data.get('result_code', '')
        return_code = data.get('return_code', '')
        transaction_id = data.get('transaction_id', '')
        total_fee = data.get('total_fee', '0')
        time_end = data.get('time_end', '')
        
        print(f"订单号: {out_trade_no}, 结果: {return_code}/{result_code}")
        
        # 验证签名
        if not WECHAT_APIV3_KEY:
            print("警告: WECHAT_APIV3_KEY未配置，跳过签名验证")
        else:
            # 复制数据用于验证（避免修改原始数据）
            verify_data = data.copy()
            if not verify_wechat_sign(verify_data, WECHAT_APIV3_KEY):
                print(f"签名验证失败: {out_trade_no}")
                return generate_response_xml("FAIL", "签名验证失败")
        
        # 检查支付结果
        if return_code == "SUCCESS" and result_code == "SUCCESS":
            # 支付成功，更新订单状态
            success = await update_order_status(
                db=db,
                order_no=out_trade_no,
                transaction_id=transaction_id,
                total_fee=int(total_fee) / 100,  # 分转元
                paid_at=time_end
            )
            
            if success:
                print(f"支付成功 - 订单号: {out_trade_no}, 微信订单号: {transaction_id}, 金额: {total_fee}")
                return generate_response_xml("SUCCESS", "OK")
            else:
                print(f"订单更新失败: {out_trade_no}")
                return generate_response_xml("FAIL", "订单更新失败")
        else:
            # 支付失败
            err_code = data.get('err_code', '')
            err_code_des = data.get('err_code_des', '')
            print(f"支付失败 - 订单号: {out_trade_no}, 错误: {err_code} - {err_code_des}")
            
            # 更新订单状态为失败
            await update_order_status(
                db=db,
                order_no=out_trade_no,
                status="failed",
                fail_reason=f"{err_code}: {err_code_des}"
            )
            
            return generate_response_xml("SUCCESS", "OK")  # 仍然返回SUCCESS避免微信重复通知
            
    except Exception as e:
        print(f"回调处理错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return generate_response_xml("FAIL", str(e))

async def update_order_status(
    db: Session,
    order_no: str,
    transaction_id: str = None,
    total_fee: float = None,
    paid_at: str = None,
    status: str = "paid",
    fail_reason: str = None
):
    """
    更新订单状态
    """
    try:
        # 查询订单
        order = db.query(Order).filter(Order.order_no == order_no).first()
        
        if not order:
            print(f"订单不存在: {order_no}")
            # 如果是仓酷家订单，创建新订单记录
            if order_no.startswith("CKJ-"):
                print(f"创建新订单记录: {order_no}")
                # 这里可以创建新订单，但目前先返回失败
                return False
            return False
        
        # 更新订单状态
        order.status = status
        
        if transaction_id:
            order.transaction_id = transaction_id
        
        if total_fee:
            order.paid_amount = total_fee
        
        if paid_at:
            # 转换时间格式 20240101120000 -> 2024-01-01 12:00:00
            try:
                order.paid_at = datetime.strptime(paid_at, "%Y%m%d%H%M%S")
            except:
                order.paid_at = datetime.now()
        
        if fail_reason:
            order.fail_reason = fail_reason
        
        if status == "paid":
            order.updated_at = datetime.now()
        
        db.commit()
        db.refresh(order)
        
        print(f"订单状态更新成功: {order_no} -> {status}")
        return True
        
    except Exception as e:
        print(f"更新订单状态失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False

@router.post("/create-order")
async def create_payment_order(order_data: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    创建支付订单接口
    前端调用此接口创建订单，后端调用微信统一下单API
    """
    try:
        # 生成订单号
        # 格式: CKJ-{timestamp}-{random}
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        order_no = f"CKJ-{timestamp}-{random_num}"
        
        # 创建订单记录
        new_order = Order(
            order_no=order_no,
            user_id=order_data.user_id,
            amount=order_data.amount,
            status="pending",
            product_name=order_data.product_name,
            description=order_data.description or '',
            created_at=datetime.now()
        )
        
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # 调用微信统一下单API
        trade_type = "JSAPI" if order_data.openid else "NATIVE"
        
        wechat_result = await wechat_unified_order(
            order_no=order_no,
            amount=order_data.amount,
            description=order_data.product_name,
            openid=order_data.openid,
            trade_type=trade_type
        )
        
        # 检查微信返回结果
        if wechat_result.get("return_code") != "SUCCESS":
            # 微信下单失败，更新订单状态
            new_order.status = "failed"
            new_order.fail_reason = wechat_result.get("return_msg", "微信下单失败")
            db.commit()
            
            raise HTTPException(
                status_code=400, 
                detail=f"微信下单失败: {wechat_result.get('return_msg')}"
            )
        
        if wechat_result.get("result_code") != "SUCCESS":
            # 业务失败
            new_order.status = "failed"
            new_order.fail_reason = wechat_result.get("err_code_des", "业务处理失败")
            db.commit()
            
            raise HTTPException(
                status_code=400,
                detail=f"微信下单失败: {wechat_result.get('err_code_des')}"
            )
        
        # 获取支付参数
        prepay_id = wechat_result.get("prepay_id")
        code_url = wechat_result.get("code_url")  # NATIVE支付的二维码链接
        
        # 构建返回数据
        response_data = {
            "code": 0,
            "message": "订单创建成功",
            "data": {
                "order_no": order_no,
                "amount": order_data.amount,
                "status": "pending",
                "trade_type": trade_type,
            }
        }
        
        # 根据支付类型返回不同的参数
        if trade_type == "JSAPI" and prepay_id:
            # JSAPI支付，返回调起支付所需的参数
            response_data["data"]["pay_params"] = generate_jsapi_params(prepay_id)
        elif trade_type == "NATIVE" and code_url:
            # NATIVE支付，返回二维码链接
            response_data["data"]["code_url"] = code_url
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"创建订单失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/order-status/{order_no}")
async def get_order_status(order_no: str, db: Session = Depends(get_db)):
    """
    查询订单支付状态
    """
    try:
        order = db.query(Order).filter(Order.order_no == order_no).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        return {
            "code": 0,
            "data": {
                "order_no": order_no,
                "status": order.status,  # pending, paid, failed, cancelled
                "amount": order.amount,
                "paid_amount": order.paid_amount,
                "paid_at": order.paid_at.isoformat() if order.paid_at else None,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "product_name": order.product_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{user_id}")
async def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的所有订单
    """
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
        
        return {
            "code": 0,
            "data": [
                {
                    "order_no": order.order_no,
                    "status": order.status,
                    "amount": order.amount,
                    "paid_amount": order.paid_amount,
                    "product_name": order.product_name,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "paid_at": order.paid_at.isoformat() if order.paid_at else None
                }
                for order in orders
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
