# 仓酷家后端部署脚本
# 分步骤执行，每步需要用户确认

param(
    [string]$ServerIP = "150.158.45.157",
    [string]$Username = "root",
    [string]$Password = "Anderson2026@!"
)

function Show-Header {
    param([string]$Title)
    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
}

function Show-Step {
    param([int]$Step, [string]$Description)
    Write-Host "`n[$Step] $Description" -ForegroundColor Yellow
}

function Wait-ForKey {
    Write-Host "`n按 Enter 键继续..." -ForegroundColor Gray
    Read-Host
}

# 主菜单
Show-Header "仓酷家后端部署脚本"

Write-Host "`n部署步骤:" -ForegroundColor White
Write-Host "  1. 上传部署脚本到服务器" -ForegroundColor White
Write-Host "  2. 在服务器上执行环境配置" -ForegroundColor White
Write-Host "  3. 上传后端代码" -ForegroundColor White
Write-Host "  4. 配置环境变量" -ForegroundColor White
Write-Host "  5. 启动后端服务" -ForegroundColor White

Write-Host "`n服务器信息:" -ForegroundColor White
Write-Host "  IP: $ServerIP" -ForegroundColor White
Write-Host "  用户名: $Username" -ForegroundColor White

Write-Host "`n注意: 执行过程中需要手动输入SSH密码" -ForegroundColor Red
Wait-ForKey

# 步骤1: 上传部署脚本
Show-Step 1 "上传部署脚本到服务器"
Write-Host "命令: scp remote-setup.sh root@${ServerIP}:/tmp/" -ForegroundColor Gray
Write-Host "密码: $Password" -ForegroundColor Gray

$proc = Start-Process -FilePath "scp" -ArgumentList "-o StrictHostKeyChecking=no remote-setup.sh ${Username}@${ServerIP}:/tmp/" -Wait -PassThru

if ($proc.ExitCode -eq 0) {
    Write-Host "✓ 上传成功" -ForegroundColor Green
} else {
    Write-Host "✗ 上传失败，请手动执行:" -ForegroundColor Red
    Write-Host "  scp -o StrictHostKeyChecking=no remote-setup.sh ${Username}@${ServerIP}:/tmp/" -ForegroundColor Yellow
}
Wait-ForKey

# 步骤2: 执行环境配置
Show-Step 2 "在服务器上执行环境配置"
Write-Host "这将执行以下操作:" -ForegroundColor White
Write-Host "  - 安装Python3和依赖" -ForegroundColor White
Write-Host "  - 创建虚拟环境" -ForegroundColor White
Write-Host "  - 配置Swap分区" -ForegroundColor White
Write-Host "  - 创建systemd服务" -ForegroundColor White

Write-Host "`n命令: ssh root@${ServerIP} 'bash /tmp/remote-setup.sh'" -ForegroundColor Gray
Write-Host "密码: $Password" -ForegroundColor Gray
Write-Host "`n注意: 此步骤需要约5-10分钟" -ForegroundColor Yellow

$proc = Start-Process -FilePath "ssh" -ArgumentList "-o StrictHostKeyChecking=no ${Username}@${ServerIP} 'bash /tmp/remote-setup.sh'" -Wait -PassThru

if ($proc.ExitCode -eq 0) {
    Write-Host "✓ 环境配置完成" -ForegroundColor Green
} else {
    Write-Host "✗ 配置失败，请手动执行:" -ForegroundColor Red
    Write-Host "  ssh ${Username}@${ServerIP}" -ForegroundColor Yellow
    Write-Host "  bash /tmp/remote-setup.sh" -ForegroundColor Yellow
}
Wait-ForKey

# 步骤3: 上传后端代码
Show-Step 3 "上传后端代码"
Write-Host "将上传以下文件到服务器:" -ForegroundColor White
Write-Host "  - main.py" -ForegroundColor White
Write-Host "  - models.py" -ForegroundColor White
Write-Host "  - database.py" -ForegroundColor White
Write-Host "  - requirements.txt" -ForegroundColor White

Write-Host "`n命令: scp -r backend/* root@${ServerIP}:/var/www/cangkujia/backend/" -ForegroundColor Gray

$proc = Start-Process -FilePath "scp" -ArgumentList "-o StrictHostKeyChecking=no -r backend/* ${Username}@${ServerIP}:/var/www/cangkujia/backend/" -Wait -PassThru

if ($proc.ExitCode -eq 0) {
    Write-Host "✓ 代码上传成功" -ForegroundColor Green
} else {
    Write-Host "✗ 上传失败，请手动执行:" -ForegroundColor Red
    Write-Host "  scp -r backend/* ${Username}@${ServerIP}:/var/www/cangkujia/backend/" -ForegroundColor Yellow
}
Wait-ForKey

# 步骤4: 创建环境变量文件
Show-Step 4 "配置环境变量"
Write-Host "需要配置以下环境变量:" -ForegroundColor White
Write-Host "  - SUPABASE_URL" -ForegroundColor White
Write-Host "  - SUPABASE_KEY" -ForegroundColor White
Write-Host "  - CLERK_PUBLISHABLE_KEY" -ForegroundColor White
Write-Host "  - CLERK_SECRET_KEY" -ForegroundColor White
Write-Host "  - WECHAT_MCH_ID" -ForegroundColor White
Write-Host "  - WECHAT_APIV3_KEY" -ForegroundColor White

Write-Host "`n请手动创建.env文件:" -ForegroundColor Yellow
Write-Host "  ssh ${Username}@${ServerIP}" -ForegroundColor Yellow
Write-Host "  vim /var/www/cangkujia/backend/.env" -ForegroundColor Yellow
Wait-ForKey

# 步骤5: 启动服务
Show-Step 5 "启动后端服务"
Write-Host "命令: ssh root@${ServerIP} 'systemctl start cangkujia && systemctl enable cangkujia'" -ForegroundColor Gray

$proc = Start-Process -FilePath "ssh" -ArgumentList "-o StrictHostKeyChecking=no ${Username}@${ServerIP} 'systemctl start cangkujia && systemctl enable cangkujia && systemctl status cangkujia'" -Wait -PassThru

if ($proc.ExitCode -eq 0) {
    Write-Host "✓ 服务启动成功" -ForegroundColor Green
} else {
    Write-Host "✗ 启动失败，请手动执行:" -ForegroundColor Red
    Write-Host "  systemctl start cangkujia" -ForegroundColor Yellow
    Write-Host "  systemctl enable cangkujia" -ForegroundColor Yellow
}

# 完成
Show-Header "部署脚本执行完成"
Write-Host "`n后续检查:" -ForegroundColor White
Write-Host "  1. 测试API: curl http://${ServerIP}:8000/health" -ForegroundColor White
Write-Host "  2. 查看日志: journalctl -u cangkujia -f" -ForegroundColor White
Write-Host "  3. 管理服务: systemctl {start|stop|restart} cangkujia" -ForegroundColor White
