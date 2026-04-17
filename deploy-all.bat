@echo off
chcp 65001 >nul
echo ==========================================
echo   仓酷家后端部署脚本
echo ==========================================
echo.
echo 服务器: 150.158.45.157
echo 用户名: root
echo.
echo 此脚本将执行以下操作:
echo   1. 上传部署脚本到服务器
echo   2. 执行服务器环境配置
echo   3. 上传后端代码
echo   4. 上传环境变量配置
echo   5. 启动后端服务
echo.
echo 密码: Anderson2026@!
echo.
pause

echo.
echo [1/5] 上传部署脚本...
scp -o StrictHostKeyChecking=no remote-setup.sh root@150.158.45.157:/tmp/
if errorlevel 1 (
    echo 上传失败，请检查网络连接
    pause
    exit /b 1
)
echo 上传成功!

echo.
echo [2/5] 执行服务器环境配置...
echo 注意: 此步骤需要约5-10分钟，请耐心等待...
ssh -o StrictHostKeyChecking=no root@150.158.45.157 "bash /tmp/remote-setup.sh"
if errorlevel 1 (
    echo 环境配置失败
    pause
    exit /b 1
)
echo 环境配置完成!

echo.
echo [3/5] 上传后端代码...
scp -o StrictHostKeyChecking=no backend/main.py root@150.158.45.157:/var/www/cangkujia/backend/
scp -o StrictHostKeyChecking=no backend/models.py root@150.158.45.157:/var/www/cangkujia/backend/
scp -o StrictHostKeyChecking=no backend/database.py root@150.158.45.157:/var/www/cangkujia/backend/
scp -o StrictHostKeyChecking=no backend/requirements.txt root@150.158.45.157:/var/www/cangkujia/backend/
echo 后端代码上传完成!

echo.
echo [4/5] 上传环境变量配置...
scp -o StrictHostKeyChecking=no backend/.env root@150.158.45.157:/var/www/cangkujia/backend/
echo 环境变量配置上传完成!

echo.
echo [5/5] 启动后端服务...
ssh -o StrictHostKeyChecking=no root@150.158.45.157 "systemctl start cangkujia && systemctl enable cangkujia && systemctl status cangkujia --no-pager"
if errorlevel 1 (
    echo 服务启动失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   部署完成!
echo ==========================================
echo.
echo 检查命令:
echo   curl http://150.158.45.157:8000/health
echo   curl http://150.158.45.157:8000/
echo.
echo 查看日志:
echo   ssh root@150.158.45.157 "journalctl -u cangkujia -f"
echo.
pause
