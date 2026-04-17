#!/bin/bash
# 仓酷家服务器环境配置脚本
# 在腾讯云服务器上执行

set -e

echo "=========================================="
echo "  仓酷家服务器环境配置脚本"
echo "=========================================="

# 1. 系统更新
echo "[1/8] 更新系统软件包..."
yum update -y

# 2. 安装基础依赖
echo "[2/8] 安装基础依赖..."
yum install -y epel-release
yum install -y nginx git python3 python3-pip python3-venv wget curl vim

# 3. 检查Nginx状态
echo "[3/8] 检查Nginx状态..."
if systemctl is-active --quiet nginx; then
    echo "Nginx 已运行"
else
    echo "启动 Nginx..."
    systemctl start nginx
    systemctl enable nginx
fi

# 4. 创建项目目录结构
echo "[4/8] 创建项目目录结构..."
mkdir -p /var/www/cangkujia/{frontend,backend,static,logs}
mkdir -p /var/www/cangkujia/frontend/dist
mkdir -p /etc/nginx/ssl

# 5. 设置目录权限
echo "[5/8] 设置目录权限..."
chown -R nginx:nginx /var/www/cangkujia
chmod -R 755 /var/www/cangkujia

# 6. 配置Python虚拟环境
echo "[6/8] 配置Python虚拟环境..."
cd /var/www/cangkujia/backend
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install --upgrade pip
pip install fastapi uvicorn[standard] psycopg2-binary python-jose[cryptography] python-multipart requests httpx

echo "Python依赖安装完成"
python3 --version
pip list | grep -E "(fastapi|uvicorn|psycopg2)"

# 7. 配置Swap分区
echo "[7/8] 配置Swap分区..."
if [ ! -f /swapfile ]; then
    dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "Swap配置完成"
else
    echo "Swap已存在"
fi
free -h

# 8. 配置防火墙
echo "[8/8] 配置防火墙..."
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
    echo "防火墙配置完成"
fi

echo ""
echo "=========================================="
echo "  服务器环境配置完成！"
echo "=========================================="
echo ""
echo "项目目录: /var/www/cangkujia/"
echo "Python环境: /var/www/cangkujia/backend/venv/"
echo "Nginx状态: $(systemctl is-active nginx)"
echo ""
echo "下一步:"
echo "  1. 上传后端代码到 /var/www/cangkujia/backend/"
echo "  2. 配置环境变量"
echo "  3. 启动后端服务"
