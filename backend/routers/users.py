"""
用户管理路由
处理用户会员信息、权限检查等
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import sqlite3
import os

router = APIRouter(prefix="/api/users", tags=["users"])

# 数据库路径
DB_PATH = os.getenv("DB_PATH", "/var/www/cangkujia/backend/cangkujia.db")

# 会员等级定义
MEMBER_LEVELS = {
    "free": {"name": "免费版", "price": 0},
    "monthly": {"name": "月付会员", "price": 19.9},
    "first_month": {"name": "首月特惠", "price": 9.9},
    "quarterly": {"name": "季度会员", "price": 49},
    "half_year": {"name": "半年会员", "price": 89},
    "yearly": {"name": "年付会员", "price": 168},
    "three_year": {"name": "3年会员", "price": 399},
    "lifetime": {"name": "终身会员", "price": 699},
}

class LicenseResponse(BaseModel):
    license_type: str
    license_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: bool
    days_remaining: Optional[int] = None

class UserLicenseCreate(BaseModel):
    user_id: str
    license_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_license_duration(license_type: str) -> int:
    """获取会员时长（天）"""
    durations = {
        "monthly": 30,
        "first_month": 30,
        "quarterly": 90,
        "half_year": 180,
        "yearly": 365,
        "three_year": 1095,
        "lifetime": 36500,  # 100年
    }
    return durations.get(license_type, 0)

@router.get("/{user_id}/license", response_model=LicenseResponse)
async def get_user_license(user_id: str):
    """
    获取用户会员许可证信息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询用户许可证
        cursor.execute("""
            SELECT license_type, start_date, end_date, is_active
            FROM user_licenses
            WHERE user_id = ? AND is_active = 1
            ORDER BY end_date DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            license_type = row["license_type"]
            end_date = row["end_date"]
            
            # 计算剩余天数
            days_remaining = None
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                days_remaining = max(0, (end - now).days)
                
                # 检查是否过期
                is_active = days_remaining > 0 and row["is_active"]
            else:
                is_active = row["is_active"]
            
            return LicenseResponse(
                license_type=license_type,
                license_name=MEMBER_LEVELS.get(license_type, {}).get("name", "未知"),
                start_date=row["start_date"],
                end_date=end_date,
                is_active=is_active,
                days_remaining=days_remaining
            )
        else:
            # 没有许可证，返回免费版
            return LicenseResponse(
                license_type="free",
                license_name="免费版",
                is_active=True,
                days_remaining=None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户许可证失败: {str(e)}")

@router.post("/{user_id}/license")
async def create_user_license(user_id: str, license_data: UserLicenseCreate):
    """
    创建或更新用户会员许可证（支付成功后调用）
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 计算开始和结束日期
        start_date = datetime.now()
        duration_days = get_license_duration(license_data.license_type)
        end_date = start_date + timedelta(days=duration_days)
        
        # 先禁用旧的许可证
        cursor.execute("""
            UPDATE user_licenses
            SET is_active = 0
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        
        # 插入新许可证
        cursor.execute("""
            INSERT INTO user_licenses
            (user_id, license_type, start_date, end_date, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (
            user_id,
            license_data.license_type,
            start_date.strftime("%Y-%m-%d %H:%M:%S"),
            end_date.strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "message": "许可证创建成功",
            "license_type": license_data.license_type,
            "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "days": duration_days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建许可证失败: {str(e)}")

@router.get("/{user_id}/can-save")
async def check_can_save(user_id: str):
    """
    检查用户是否有保存权限
    """
    license_info = await get_user_license(user_id)
    
    # 免费用户无法保存
    can_save = license_info.license_type != "free" and license_info.is_active
    
    return {
        "can_save": can_save,
        "license_type": license_info.license_type,
        "license_name": license_info.license_name,
        "is_active": license_info.is_active
    }
