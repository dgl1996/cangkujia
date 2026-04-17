#!/bin/bash
# 仓酷家服务器部署脚本
# 在服务器上执行

set -e

echo "=========================================="
echo "  仓酷家服务器部署脚本"
echo "=========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root用户运行此脚本"
    exit 1
fi

# 1. 系统更新和安装依赖
echo ""
echo "[1/7] 更新系统并安装依赖..."
yum update -y
yum install -y epel-release
yum install -y python3 python3-pip python3-venv git wget curl vim

# 2. 创建项目目录
echo ""
echo "[2/7] 创建项目目录结构..."
mkdir -p /var/www/cangkujia/{frontend,backend,static,logs}
mkdir -p /etc/nginx/ssl

# 3. 设置目录权限
echo ""
echo "[3/7] 设置目录权限..."
chown -R nginx:nginx /var/www/cangkujia
chmod -R 755 /var/www/cangkujia

# 4. 配置Python虚拟环境
echo ""
echo "[4/7] 配置Python虚拟环境..."
cd /var/www/cangkujia/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy psycopg2-binary python-jose[cryptography] python-multipart python-dotenv httpx requests

echo "Python依赖安装完成"
echo "Python版本: $(python3 --version)"
echo "已安装包:"
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|psycopg2)"

# 5. 配置Swap分区
echo ""
echo "[5/7] 配置Swap分区..."
if [ ! -f /swapfile ]; then
    echo "创建2G Swap文件..."
    dd if=/dev/zero of=/swapfile bs=1M count=2048 status=progress
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "Swap配置完成"
else
    echo "Swap已存在，跳过配置"
fi

echo "内存状态:"
free -h

# 6. 配置防火墙
echo ""
echo "[6/7] 配置防火墙..."
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
    echo "防火墙配置完成"
else
    echo "firewall-cmd未安装，跳过防火墙配置"
fi

# 7. 创建systemd服务文件
echo ""
echo "[7/7] 创建后端服务配置..."

cat > /etc/systemd/system/cangkujia.service << 'EOF'
[Unit]
Description=仓酷家 FastAPI 后端服务
After=network.target

[Service]
Type=exec
User=nginx
Group=nginx
WorkingDirectory=/var/www/cangkujia/backend
Environment="PATH=/var/www/cangkujia/backend/venv/bin"
EnvironmentFile=/var/www/cangkujia/backend/.env
ExecStart=/var/www/cangkujia/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "systemd服务文件创建完成"

# 重新加载systemd
systemctl daemon-reload

echo ""
echo "=========================================="
echo "  服务器环境配置完成！"
echo "=========================================="
echo ""
echo "项目目录: /var/www/cangkujia/"
echo "Python虚拟环境: /var/www/cangkujia/backend/venv/"
echo ""
echo "下一步操作:"
echo "  1. 上传后端代码到 /var/www/cangkujia/backend/"
echo "  2. 创建.env配置文件"
echo "  3. 启动服务: systemctl start cangkujia"
echo "  4. 设置开机自启: systemctl enable cangkujia"
echo ""
echo "服务管理命令:"
echo "  启动: systemctl start cangkujia"
echo "  停止: systemctl stop cangkujia"
echo "  重启: systemctl restart cangkujia"
echo "  状态: systemctl status cangkujia"
echo "  日志: journalctl -u cangkujia -f"
