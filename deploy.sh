#!/bin/bash
# 仓酷家全自动部署脚本
# 适用于：腾讯云轻量服务器 2核2G + 宝塔面板

set -e

echo "=========================================="
echo "  仓酷家生产环境部署脚本"
echo "=========================================="

# 配置变量
DOMAIN="cangkujia666.com"
PROJECT_DIR="/var/www/cangkujia"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
COS_BUCKET="cangkujia-models"
COS_REGION="ap-shanghai"

echo ""
echo "[Phase 1/6] 检查服务器环境..."
echo "=========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "错误：请使用root用户运行此脚本"
    exit 1
fi

# 检查系统信息
echo "系统信息："
uname -a
echo ""
echo "磁盘空间："
df -h
echo ""
echo "内存状态："
free -h
echo ""

# 检查宝塔面板
echo "检查宝塔面板..."
if [ -f "/www/server/panel/BT-Panel" ]; then
    echo "✓ 宝塔面板已安装"
    bt status
else
    echo "✗ 宝塔面板未安装"
fi

# 检查Nginx
echo ""
echo "检查Nginx..."
if command -v nginx &> /dev/null; then
    echo "✓ Nginx已安装"
    nginx -v
    if pgrep nginx > /dev/null; then
        echo "✓ Nginx正在运行"
    else
        echo "! Nginx未运行，正在启动..."
        /etc/init.d/nginx start
    fi
else
    echo "! Nginx未安装，将通过宝塔安装..."
fi

echo ""
echo "[Phase 2/6] 创建项目目录结构..."
echo "=========================================="

# 创建项目目录
mkdir -p $PROJECT_DIR/{frontend,backend,static,logs}
echo "✓ 项目目录创建完成：$PROJECT_DIR"

# 设置目录权限
chmod -R 755 $PROJECT_DIR
chown -R www:www $PROJECT_DIR
echo "✓ 目录权限设置完成"

echo ""
echo "[Phase 3/6] 配置Python环境..."
echo "=========================================="

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "安装Python3..."
    apt-get update
    apt-get install -y python3 python3-pip python3-venv
fi

echo "Python版本：$(python3 --version)"

# 创建虚拟环境
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv $BACKEND_DIR/venv
fi

# 激活虚拟环境并安装依赖
echo "安装Python依赖..."
source $BACKEND_DIR/venv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn[standard] psycopg2-binary python-jose[cryptography] python-multipart requests python-dotenv

echo "✓ Python环境配置完成"

echo ""
echo "[Phase 4/6] 配置Swap分区..."
echo "=========================================="

# 检查Swap
if [ "$(swapon -s | wc -l)" -le 1 ]; then
    echo "创建2G Swap分区..."
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "✓ Swap分区创建完成"
else
    echo "✓ Swap分区已存在"
fi

swapon -s | head -5

echo ""
echo "[Phase 5/6] 准备后端代码..."
echo "=========================================="

# 创建后端主文件
cat > $BACKEND_DIR/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(title="仓酷家API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cangkujia666.com", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "仓酷家API服务运行中", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "cangkujia-api"}

@app.get("/api/config")
async def get_config():
    """获取前端配置"""
    return {
        "cosBucket": os.getenv("COS_BUCKET", "cangkujia-models"),
        "cosRegion": os.getenv("COS_REGION", "ap-shanghai"),
        "clerkPublishableKey": os.getenv("CLERK_PUBLISHABLE_KEY", ""),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

echo "✓ 后端主文件创建完成"

# 创建环境变量模板文件
cat > $BACKEND_DIR/.env.example << 'EOF'
# Clerk配置
CLERK_PUBLISHABLE_KEY=pk_live_YOUR_CLERK_PUBLISHABLE_KEY
CLERK_SECRET_KEY=sk_live_YOUR_CLERK_SECRET_KEY

# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# 微信支付配置
WECHAT_MCH_ID=1743582175
WECHAT_APIV3_KEY=your-apiv3-key
WECHAT_APPID=wx3e00623c71d93a65
WECHAT_NOTIFY_URL=https://cangkujia666.com/api/payment/callback

# COS配置
COS_BUCKET=cangkujia-models
COS_REGION=ap-shanghai
COS_SECRET_ID=your-secret-id
COS_SECRET_KEY=your-secret-key
EOF

echo "✓ 环境变量模板创建完成"

echo ""
echo "[Phase 6/6] 配置Systemd服务..."
echo "=========================================="

# 创建systemd服务文件
cat > /etc/systemd/system/cangkujia-api.service << EOF
[Unit]
Description=仓酷家FastAPI服务
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
systemctl daemon-reload
systemctl enable cangkujia-api.service

echo "✓ Systemd服务配置完成"

echo ""
echo "=========================================="
echo "  基础环境部署完成！"
echo "=========================================="
echo ""
echo "项目目录：$PROJECT_DIR"
echo "后端目录：$BACKEND_DIR"
echo "前端目录：$FRONTEND_DIR"
echo ""
echo "下一步操作："
echo "1. 配置环境变量：cp $BACKEND_DIR/.env.example $BACKEND_DIR/.env"
echo "2. 编辑.env文件，填入实际的API密钥"
echo "3. 启动服务：systemctl start cangkujia-api"
echo "4. 查看状态：systemctl status cangkujia-api"
echo ""
echo "Nginx配置请使用宝塔面板添加站点："
echo "  域名：$DOMAIN"
echo "  根目录：$FRONTEND_DIR/dist"
echo "  反向代理：127.0.0.1:8000 -> /api/"
echo ""
