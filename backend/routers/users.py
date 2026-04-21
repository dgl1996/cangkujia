"""
用户管理路由
处理用户会员信息、权限检查等
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import sqlite3
import os

router = APIRouter(prefix="/api/users", tags=["users"])

# 数据库路径
DB_PATH = "/var/www/cangkujia/backend/cangkujia.db"

class LicenseResponse(BaseModel):
    license_type: str
    license_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: bool
    days_remaining: Optional[int] = None

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/{user_id}/license", response_model=LicenseResponse)
async def get_user_license(user_id: str):
    """获取用户会员许可证信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
            days_remaining = None
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                days_remaining = max(0, (end - now).days)
                is_active = days_remaining > 0 and row["is_active"]
            else:
                is_active = row["is_active"]
            
            return LicenseResponse(
                license_type=license_type,
                license_name="付费会员" if license_type != "free" else "免费版",
                start_date=row["start_date"],
                end_date=end_date,
                is_active=is_active,
                days_remaining=days_remaining
            )
        else:
            return LicenseResponse(
                license_type="free",
                license_name="免费版",
                is_active=True,
                days_remaining=None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户许可证失败: {str(e)}")
