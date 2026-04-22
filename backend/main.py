from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="仓酷家 API",
    description="物流仓库3D布局系统API",
    version="1.0.0"
)

# 从环境变量读取CORS配置
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入并注册路由
from routers import payment_v3, users
app.include_router(payment_v3.router)
app.include_router(payment_v3.user_router)
app.include_router(users.router)

# Clerk回调URL配置
CLERK_REDIRECT_URL = "https://cangkujia666.com"
CLERK_SIGN_OUT_URL = "https://cangkujia666.com"

@app.get("/")
async def root():
    return {
        "message": "仓酷家 API 服务运行中",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "cangkujia-api",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/config")
async def get_config():
    """获取前端配置（不包含敏感信息）"""
    return {
        "supabase_url": os.getenv("SUPABASE_URL", ""),
        "clerk_publishable_key": os.getenv("CLERK_PUBLISHABLE_KEY", ""),
        "wechat_mch_id": os.getenv("WECHAT_MCH_ID", ""),
        "clerk_redirect_url": CLERK_REDIRECT_URL,
    }

@app.get("/api/clerk-config")
async def get_clerk_config():
    """获取Clerk配置信息"""
    return {
        "publishable_key": os.getenv("CLERK_PUBLISHABLE_KEY", ""),
        "redirect_url": CLERK_REDIRECT_URL,
        "sign_out_url": CLERK_SIGN_OUT_URL,
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
