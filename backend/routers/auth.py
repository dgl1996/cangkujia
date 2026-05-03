"""
用户认证路由 - JWT 登录/注册
放弃 Clerk，改用后端自研登录，解决大陆网络问题
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os

from database import get_db
from models import User

# IP限流：同一IP 60秒内最多10次注册
# 结构: {ip: [timestamp1, timestamp2, ...]}
register_rate_limit = {}
REGISTER_LIMIT = 10  # 最多10次
REGISTER_WINDOW = 60  # 60秒窗口

def check_register_rate_limit(ip: str) -> bool:
    """检查IP是否超过注册频率限制，返回True表示允许注册"""
    now = datetime.now()
    if ip not in register_rate_limit:
        register_rate_limit[ip] = []
    
    # 清理60秒前的记录
    register_rate_limit[ip] = [
        ts for ts in register_rate_limit[ip] 
        if (now - ts).total_seconds() < REGISTER_WINDOW
    ]
    
    # 检查是否超过限制
    if len(register_rate_limit[ip]) >= REGISTER_LIMIT:
        return False
    
    # 记录本次请求
    register_rate_limit[ip].append(now)
    return True

router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-min-32-characters-long")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "30"))

security = HTTPBearer()


# ============ 数据模型 ============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str | None
    avatar_url: str | None


# ============ 辅助函数 ============

def hash_password(password: str) -> str:
    """使用 bcrypt 加密密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(token: str = Header(None, alias="Authorization"), db: Session = Depends(get_db)) -> User:
    """获取当前登录用户（从 Token 解析）"""
    if not token:
        raise HTTPException(status_code=401, detail="缺少认证信息")
    
    # 处理 "Bearer " 前缀
    if token.startswith("Bearer "):
        token = token[7:]
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的认证信息")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的认证信息")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return user


# ============ API 路由 ============

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, req: Request, db: Session = Depends(get_db)):
    """
    用户注册
    - IP限流：同一IP 60秒内最多10次注册
    - 检查邮箱是否已存在
    - bcrypt 加密密码
    - 创建用户记录
    - 返回 JWT Token
    """
    # 获取客户端IP
    client_ip = req.headers.get("X-Forwarded-For", req.client.host)
    if client_ip and "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    
    # IP限流检查
    if not check_register_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="注册过于频繁，请60秒后再试")
    
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="该邮箱已注册")
    
    # 密码长度检查
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="密码长度至少8位")
    
    # 创建新用户
    new_user = User(
        email=request.email,
        username=request.email.split('@')[0],  # 默认用户名为邮箱前缀
        password_hash=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 生成 JWT Token
    access_token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "nickname": new_user.nickname,
            "avatar_url": new_user.avatar_url
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    - 查找用户
    - bcrypt 校验密码
    - 返回 JWT Token
    """
    # 查找用户
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="邮箱或密码错误")
    
    # 检查是否有密码（旧 Clerk 用户可能没有密码）
    if not user.password_hash:
        raise HTTPException(status_code=400, detail="该账号需要重新注册")
    
    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=400, detail="邮箱或密码错误")
    
    # 生成 JWT Token
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    - 从 Authorization Header 解析 Token
    - 返回用户信息（替代 Clerk 的 useUser）
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "avatar_url": current_user.avatar_url
    }
