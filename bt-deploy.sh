#!/bin/bash
# 仓酷家宝塔面板部署脚本
# 在服务器上执行此脚本

echo "=========================================="
echo "  仓酷家宝塔面板部署脚本"
echo "=========================================="

# 宝塔命令路径
BT=/usr/bin/bt

# 检查宝塔
if [ ! -f "$BT" ]; then
    echo "错误：宝塔面板未安装"
    exit 1
fi

echo "✓ 宝塔面板已安装"

# 创建网站
echo ""
echo "[1/5] 创建网站..."
$BT panel add_site cangkujia666.com 0 /var/www/cangkujia/frontend/dist

# 创建项目目录
mkdir -p /var/www/cangkujia/{frontend/dist,backend,static,logs}

# 设置权限
chown -R www:www /var/www/cangkujia
chmod -R 755 /var/www/cangkujia

echo "✓ 网站创建完成"

# 配置Python环境
echo ""
echo "[2/5] 配置Python环境..."
cd /var/www/cangkujia/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn[standard] psycopg2-binary python-jose python-multipart requests python-dotenv

echo "✓ Python环境配置完成"

# 创建后端代码
echo ""
echo "[3/5] 创建后端代码..."
cat > /var/www/cangkujia/backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="仓酷家API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cangkujia666.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "仓酷家API服务运行中", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/config")
async def get_config():
    return {
        "cosBucket": os.getenv("COS_BUCKET", "cangkujia-models"),
        "cosRegion": os.getenv("COS_REGION", "ap-shanghai"),
    }
EOF

cat > /var/www/cangkujia/backend/.env << 'EOF'
COS_BUCKET=cangkujia-models
COS_REGION=ap-shanghai
EOF

echo "✓ 后端代码创建完成"

# 配置Swap
echo ""
echo "[4/5] 配置Swap..."
if [ "$(swapon -s | wc -l)" -le 1 ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "✓ Swap创建完成"
else
    echo "✓ Swap已存在"
fi

# 配置Systemd服务
echo ""
echo "[5/5] 配置Systemd服务..."
cat > /etc/systemd/system/cangkujia-api.service << 'EOF'
[Unit]
Description=仓酷家FastAPI服务
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/cangkujia/backend
Environment=PATH=/var/www/cangkujia/backend/venv/bin
ExecStart=/var/www/cangkujia/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cangkujia-api
systemctl start cangkujia-api

echo "✓ 服务启动完成"

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "项目目录：/var/www/cangkujia"
echo "API服务：http://150.158.45.157:8000"
echo ""
echo "下一步："
echo "1. 上传前端dist文件到 /var/www/cangkujia/frontend/dist/"
echo "2. 在宝塔面板配置反向代理 /api/ -> 127.0.0.1:8000"
echo "3. 配置SSL证书"
echo ""
